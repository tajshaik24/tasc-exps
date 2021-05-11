import os
import random
import time

import zmq

from anna.client import AnnaTcpClient
from anna.lattices import LwwPairLattice as LWW

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

def lambda_handler(event, context):
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

	read_times = []
	write_times = []
	lookup_times = []
	throughput_time = 0

	dumb_client = AnnaTcpClient(elb, None)

	for i in range(num_txns):
		print('*** Starting Transaction '+ str(i) +' ! ***')

		# Perform routing lookups
		for _ in range(num_lookups):
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

	throughput = (num_txns * (num_writes + num_reads)) / throughput_time
	convert = lambda x: x * 1000
	read_lat = list(map(convert, read_times))
	write_lat = list(map(convert, write_times))
	lookup_lat = list(map(convert, lookup_times))
	read_msg = ",".join(map(str, read_lat))
	write_msg = ",".join(map(str, write_lat))
	lookup_msg = ",".join(map(str, lookup_lat))

	ctx = zmq.Context(1)
	sckt = ctx.socket(zmq.PUSH)
	sckt.connect('tcp://%s:6600' % benchmark_server)

	message = str(throughput) + ";" + str(read_msg) + ";" + str(write_msg) + ";" + str(lookup_msg)

	sckt.send_string(message)
	return "Success"




