import os
import random
import time
from warnings import resetwarnings

import boto3
import grpc
from google.protobuf import empty_pb2
import numpy as np
import scipy.stats as stats
import zmq

from tasc_pb2 import *
from tasc_pb2_grpc import *

lmbd = boto3.client('lambda')

N = 99999
x = np.arange(1, N)
a = 1.5
weights = x ** (-a)
weights /= weights.sum()
bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))

sys_random = random.SystemRandom()

def lambda_handler(event, context):
    num_reads = int(event["num_reads"])
    num_writes = int(event["num_writes"])
    benchmark_server = event["benchmark_ip"]

    print('*** Starting Transaction! ***')
    lb_addr = event["elb"]
    ctx = zmq.Context(1)
    sckt = ctx.socket(zmq.REQ)
    sckt.connect('tcp://%s:8000' % lb_addr)
    sckt.send_string('')
    address = sckt.recv_string()

    with grpc.insecure_channel(address + ':9000') as channel:
        client = TascStub(channel)

        start_time = time.time()
        txn = client.StartTransaction(empty_pb2.Empty())
        end_start_txn = time.time() - start_time
        txn_id_str = txn.tid

        keys = []
        key_str = []
        value_str = []

        for _ in range(num_writes):
            key = str(bounded_zipf.rvs(size=1)[0])
            value = os.urandom(4096)
            key_str.append(key)
            value_str.append(value)
            keys.append(KeyPair(key=key, value=value))

        update = TascRequest(tid=txn_id_str, pairs=keys)
        
        start_write = time.time()
        client.Write(update)
        end_write = time.time() - start_write

        start_commit = time.time()
        client.CommitTransaction(txn)
        end_commit =  time.time() - start_commit

        start_txn = client.StartTransaction(empty_pb2.Empty())

        start_read = time.time()
        for i in range(num_reads):
            key_str = key_str[i]
            value_str = value_str[i]
            read_keys = []
            read_keys.append(KeyPair(key=key_str))
            read = TascRequest(tid=start_txn.tid, pairs=read_keys)
            while True:
                values = client.Read(read)
                rv_keys = values.pairs
                read_value = rv_keys[0].value
                if(read_value == value_str):
                    break
        end_read = time.time() - start_read
         
        latency = (time.time() - start_time)

        sckt = ctx.socket(zmq.REQ)
        sckt.connect('tcp://%s:6600' % benchmark_server)
        message = str(latency) + ";" + str(end_start_txn) + ";" + str(end_write) + ";" + str(end_read) + ";" + str(end_commit)
        sckt.send_string(message)

    return "Success"

