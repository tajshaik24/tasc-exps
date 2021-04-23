import json
import os
import random
import time

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

        for _ in range(num_writes):
            key = str(bounded_zipf.rvs(size=1)[0])
            key_str.append(key)
            keys.append(KeyPair(key=key, value=os.urandom(4096)))
        
        read_keys = []
        for i in range(num_reads):
            read_keys.append(KeyPair(key=key_str[i]))

        update = TascRequest(tid=txn_id_str, pairs=keys)

        end_write = 0
        
        if num_writes > 0:
            start_write = time.time()
            client.Write(update)
            end_write = time.time() - start_write
        
        end_read = 0
        reads = TascRequest(tid=txn_id_str, pairs=read_keys)

        if num_reads > 0:
            start_read = time.time()
            client.Read(reads)
            end_read = time.time() - start_read

        start_commit = time.time()
        client.CommitTransaction(txn)
        end_commit =  time.time() - start_commit
         
        latency = (time.time() - start_time)

        sckt = ctx.socket(zmq.REQ)
        sckt.connect('tcp://%s:6600' % benchmark_server)
        message = str(latency) + ";" + str(end_start_txn) + ";" + str(end_write) + ";" + str(end_read) + ";" + str(end_commit)
        sckt.send_string(message)

    return "Success"

