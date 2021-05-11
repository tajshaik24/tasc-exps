import os
import random
import time

import zmq
import numpy as np
import scipy.stats as stats

from anna.client import AnnaTcpClient
from anna.lattices import LWWPairLattice as LWW

from anna.zmq_util import (
    recv_response,
    send_request
)

from anna.anna_pb2 import (
    GET, PUT,  # Anna's request types
    NO_ERROR,  # Anna's error modes
    KeyAddressRequest,
    KeyAddressResponse,
    KeyResponse
)

import requests
import socket
import threading
import argparse

def lambda_handler(event, offset, throughputList, reads, writes, lookups):
    print('Lambda started')
    num_txns = int(event["num_txns"])
    num_reads = int(event["num_reads"])
    num_writes = int(event["num_writes"])
    num_lookups = int(event["num_lookups"])
    benchmark_server = event["benchmark_ip"]
    elb = event["elb"]
    zipf = float(event["zipf"])
    prefix = event["prefix"]
    N = int(event["N"])

    x = np.arange(1, N)

    weights = x ** (-zipf)
    weights /= weights.sum()
    bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))

    read_times = reads
    write_times = writes
    lookup_times = lookups
    throughput_time = 0


    ip = requests.get('http://checkip.amazonaws.com').text.rstrip()
    sip = socket.gethostname()

    print('AWS IP Got {}'.format(ip))
    print('Socket IP Got {}'.format(sip))

    dumb_client = AnnaTcpClient(elb, ip, offset=i)

    for i in range(num_txns):
        print('*** Starting Transaction '+ str(i) +' ! ***')

        # Perform routing lookups
        for _ in range(num_lookups):
            print('Lookup')
            key = prefix + str(bounded_zipf.rvs(size=1)[0])
            port = 6450
            start = time.time()
            addresses = dumb_client._query_routing(key, port)
            end = time.time()

            lookup_times.append(end - start)
            throughput_time += (end - start)

        # Perform writes
        for _ in range(num_writes):
            key = prefix + str(bounded_zipf.rvs(size=1)[0])

            port = random.choice([6450, 6451, 6452, 6453])
            addresses = dumb_client._query_routing(key, port)
            send_sock = dumb_client.pusher_cache.get(addresses[0])

            data = os.urandom(4096)
            lww = LWW(time.time_ns(), data)
            req, tup = dumb_client._prepare_data_request([key])
            req.type = PUT

            rids = [req.request_id]
            tup = tup[0]
            tup.payload, tup.lattice_type = dumb_client._serialize(value)

            start = time.time()
            send_request(req, send_sock)
            responses = recv_response(rids, dumb_client.response_puller, KeyResponse)
            end = time.time()

            write_times.append(end - start)

            throughput_time += (end - start)

        # Perform reads
        for _ in range(num_reads):
            key = prefix + str(bounded_zipf.rvs(size=1)[0])

            port = random.choice([6450, 6451, 6452, 6453])
            addresses = dumb_client._query_routing(key, port)
            send_sock = dumb_client.pusher_cache.get(addresses[0])

            req, _ = dumb_client._prepare_data_request([key])
            req.type = GET
            rids = [req.request_id]

            start = time.time()

            send_request(req, send_sock)

            # Wait for all responses to return.

            responses = recv_response(rids, dumb_client.response_puller, KeyResponse)
            end = time.time()

            read_times.append(end - start)
            throughput_time += (end - start)

    throughput = (num_txns * (num_writes + num_reads + num_lookups)) / throughput_time
    throughputList.append(throughput)


def main():
    parser = argparse.ArgumentParser(description='Makes a call to the TASC benchmark server.')
    parser.add_argument('-c', '--clients', nargs=1, type=int, metavar='Y',
                        help='The number of clients to invoke.',
                        dest='clients', required=True)
    parser.add_argument('-a', '--address', nargs=1, type=str, metavar='A',
                        help='ELB Address for the Load Balancer Values.', 
                        dest='address', required=True)
    parser.add_argument('-t', '--txn', nargs=1, type=int, metavar='Y',
                        help='The number of txns to be done.',
                        dest='txn', required=True)
    parser.add_argument('-r', '--reads', nargs=1, type=int, metavar='Y',
                        help='The number of reads to be done.',
                        dest='reads', required=True)
    parser.add_argument('-w', '--writes', nargs=1, type=int, metavar='Y',
                        help='The number of writes to be done.',
                        dest='writes', required=True)
    parser.add_argument('-rl', '--lookups', nargs=1, type=int, metavar='Y',
                        help='The number of routing lookups to be done.',
                        dest='lookups', required=True)
    parser.add_argument('-z', '--zipf', nargs='?', type=float, metavar='Y',
                        help='Zipfian coefficient',
                        dest='zipf', required=False, default=1.0)
    parser.add_argument('-p', '--pre', nargs='?', type=str, metavar='Y',
                        help='Prefix key',
                        dest='prefix', required=False, default='tasc')
    parser.add_argument('-n', '--numkeys', nargs='?', type=int, metavar='Y',
                        help='Keyspace to choose from',
                        dest='knum', required=False, default=1000)
    parser.add_argument('-ip', '--myip', nargs=1, type=str, metavar='A',
                        help='This servers public IP', 
                        dest='ip', required=True)
    args = parser.parse_args()

    num_clients = args.clients[0]
    payload = {
        'num_txns': args.txn[0],
        'num_reads': args.reads[0],
        'num_writes': args.writes[0],
        'num_lookups': args.lookups[0],
        'benchmark_ip': args.ip[0],
        'elb': args.address[0],
        'zipf': args.zipf,
        'prefix': args.prefix,
        'N': args.knum
        }
    throughputs = []
    reads = []
    writes = []
    lookups = []

    threads = []
    for i in range(num_clients):
        t = threading.Thread(target=lambda_handler, args=(payload,i,throughputs,reads,writes,lookups,))
        threads.append(t)

    for t in threads:
        t.start()
        print('Started...')

    for t in threads:
        t.join()

    throughput = sum(throughputs)
    print('Throughput: {} ops/sec\n'.format(throughput))

    if len(lookups) > 0:
        lookups = np.array(lookups)
        l_med = np.percentile(lookups, 50)
        l_99 = np.percentile(lookups, 99)
        
        print('Routing Lookups')
        print('Median/99th: {}, {}\n'.format(l_med, l_99))

    if len(reads) > 0:
        reads = np.array(reads)
        r_med = np.percentile(reads, 50)
        r_99 = np.percentile(reads, 99)

        print('Reads')
        print('Median/99th: {}, {}\n'.format(r_med, r_99))

    if len(writes) > 0:
        writes = np.array(writes)
        w_med = np.percentile(writes, 50)
        w_99 = np.percentile(writes, 99)

        print('Writes')
        print('Median/99th: {}, {}\n'.format(w_med, w_99))



if __name__ == '__main__':
    main()

