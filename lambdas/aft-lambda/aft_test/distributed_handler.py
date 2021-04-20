import json
import os
import random

import boto3
import grpc
from google.protobuf import empty_pb2
import numpy as np
import scipy.stats as stats

from aft_pb2 import *
from aft_pb2_grpc import *

lmbd = boto3.client('lambda')

N = 99999
x = np.arange(1, N)
a = 1.5
weights = x ** (-a)
weights /= weights.sum()
bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))

sys_random = random.SystemRandom()

def handler(event, context):
    is_first = bool(int(event['count']) == 1)
    if is_first:
        address = sys_random.choice(event['replicas'])
    else:
        address = event['address']
        txn = TransactionTag()
        txn.ParseFromString(bytes(event['txn'], 'utf-8'))

    num_keys = 3 # 2 reads, 1 write

    with grpc.insecure_channel(address + ':7654') as channel:
        client = AftStub(channel)

        if is_first:
            txn = client.StartTransaction(empty_pb2.Empty())

        keys = []
        for _ in range(num_keys):
            key = str(bounded_zipf.rvs(size=1)[0])
            keys.append(str(key))

        # Do the write.
        update = KeyRequest(tid=txn.id)
        pair = update.pairs.add()
        pair.key = keys[0]
        pair.value = os.urandom(4096)
        client.Write(update)

        # Do the reads.
        for i in range(1, num_keys):
            update = KeyRequest(tid=txn.id)
            pair = update.pairs.add()
            pair.key = keys[i]
            client.Read(update)

        if not is_first:
            client.CommitTransaction(txn)

    if is_first:
        response = lmbd.invoke(FunctionName='aft-test',
                               Payload=json.dumps({
                                   'count': 2,
                                   'txn': str(txn.SerializeToString(),
                                              'utf-8'),
                                   'address': address
                               }),
                               InvocationType='RequestResponse')

        return response['Payload'].read()

    return "Success"

