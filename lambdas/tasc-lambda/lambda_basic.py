import os
import time

import boto3
from google.protobuf import empty_pb2
import numpy as np
import scipy.stats as stats
import zmq

from tasc_pb2 import *
from tasc_pb2_grpc import *

lmbd = boto3.client('lambda')

N = 1000
x = np.arange(1, N)
SEED = 123456789

def lambda_handler(event, context):
    num_txns = int(event["num_txns"])
    num_reads = int(event["num_reads"])
    num_writes = int(event["num_writes"])
    benchmark_server = event["benchmark_ip"]
    lb_addr = event["elb"]
    zipf = float(event["zipf"])

    weights = x ** (-zipf)
    weights /= weights.sum()
    bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights), seed=SEED)

    latencies = []
    ip_resolution_times = []
    start_txn_times = []
    read_txn_times = []
    write_txn_times = []
    commit_txn_times = []

    num_aborts = 0
    num_failed_reads = 0

    throughput_time = 0
    for i in range(num_txns):
        print('*** Starting Transaction '+ str(i) +' ! ***')
        ctx = zmq.Context(1)
        sckt = ctx.socket(zmq.REQ)
        sckt.connect('tcp://%s:8000' % lb_addr)
        ip_resolt_start = time.time()
        sckt.send_string('')
        address = sckt.recv_string()
        ip_resolt_end = time.time()
        ip_resolution_times.append(ip_resolt_end - ip_resolt_start)

        with grpc.insecure_channel(address + ':9000') as channel:
            client = TascStub(channel)
            start_time = time.time()
            txn = client.StartTransaction(empty_pb2.Empty())
            end_start = time.time()
            start_txn_times.append(end_start - start_time)

            txn_id_str = txn.tid
            write_keys = []
            for _ in range(num_writes):
                key = str(bounded_zipf.rvs(size=1)[0])
                write_keys.append(TascRequest.KeyPair(key=key, value=os.urandom(4096)))
            
            read_keys = []
            for i in range(num_reads):
                key = str(bounded_zipf.rvs(size=1)[0])
                read_keys.append(TascRequest.KeyPair(key=key))

            write = TascRequest(tid=txn_id_str, pairs=write_keys)

            write_time = 0
            
            if num_writes > 0:
                start_write = time.time()
                client.Write(write)
                end_write = time.time()
                write_time += end_write - start_write
            write_txn_times.append(write_time)
            
            read_time = 0
            read = TascRequest(tid=txn_id_str, pairs=read_keys)

            if num_reads > 0:
                start_read = time.time()
                client.Read(read)
                end_read = time.time()
                read_time += end_read - start_read
            read_txn_times.append(read_time)

            start_commit = time.time()
            commit_resp = client.CommitTransaction(txn)
            end_commit =  time.time()

            if commit_resp.status != COMMITTED:
                num_aborts += 1
            else:
                commit_txn_times.append(end_commit - start_commit)
                latency = (time.time() - start_time)
                latencies.append(latency)
                throughput_time += latency
    
    throughput = num_txns / throughput_time

    # Turn latencies to milliseconds
    convert = lambda x: x * 1000
    latencies = list(map(convert, latencies))
    ip_resolution_times = list(map(convert, ip_resolution_times))
    start_txn_times = list(map(convert, start_txn_times))
    read_txn_times = list(map(convert, read_txn_times))
    write_txn_times = list(map(convert, write_txn_times))
    commit_txn_times = list(map(convert, commit_txn_times))

    latency = ",".join(map(str, latencies))
    end_ip_resolt = ",".join(map(str, ip_resolution_times))
    end_start_txn = ",".join(map(str, start_txn_times))
    end_write = ",".join(map(str, write_txn_times))
    end_read = ",".join(map(str,read_txn_times))
    end_commit = ",".join(map(str,commit_txn_times))

    sckt = ctx.socket(zmq.PUSH)
    sckt.connect('tcp://%s:6600' % benchmark_server)
    message = str(throughput) + ";" + str(latency) + ";" + str(end_ip_resolt) + ";" + str(end_start_txn) + ";" + str(end_write) + ";" + str(end_read) + ";" + str(end_commit) + ";" + str(num_aborts) + ";" + str(num_failed_reads)
    sckt.send_string(message)

    return "Success"

