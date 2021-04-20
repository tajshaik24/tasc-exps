import json
import os
import pickle
import random
import time
import uuid
import boto3
import botocore
import numpy as np
import scipy.stats as stats

from aft_pb2 import *

ddb = boto3.client('dynamodb')
lmbd = boto3.client('lambda')
table = 'AftData'

N = 99999
x = np.arange(1, N)
a = 1.0
weights = x ** (-a)
weights /= weights.sum()
bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))

key_template = 'data/%s'

def handler(event, context):
    is_first = bool(int(event['count']) == 1)
    storage = Storage()
    read_keys = []
    read = []
    original_read = []

    if is_first:
        tid, tts = (str(uuid.uuid4()), int(time.time() * 1000))
    else:
        tid, tts = event['metadata'][0], int(event['metadata'][1])
        for rv in event['read']:
            val = event['read'][rv]
            kvp = KeyValuePair()
            kvp.key = rv
            kvp.timestamp = int(val['tts'])
            kvp.cowrittenKeys.extend(['cowritten'])
            kvp.tid = val['tid']

            original_read.append(kvp)
            read_keys.append(kvp.key)

    # Do two reads.
    keys = []
    while len(keys) < 2:
        key = key_template % str(bounded_zipf.rvs(size=1)[0])
        if key not in keys and key not in read_keys:
            keys.append(key)

    for resp in storage.txn_get(keys):
        kvp = KeyValuePair()
        kvp.ParseFromString(resp)
        read.append(kvp)

    if not is_first:
        # Do two writes.
        key1 = key_template % str(bounded_zipf.rvs(size=1)[0])
        key2 = key_template % str(bounded_zipf.rvs(size=1)[0])
        while key2 == key1: # Make sure that it's not the same key.
            key2 = str(bounded_zipf.rvs(size=1)[0])

        bts = []

        kvp = KeyValuePair()
        kvp.key = key1
        kvp.value = os.urandom(4096)
        kvp.cowrittenKeys.extend([key1, key2])
        kvp.tid = tid
        kvp.timestamp = tts

        bts.append(kvp.SerializeToString())
        kvp.key = key2
        bts.append(kvp.SerializeToString())

        storage.txn_put([key1, key2], bts)

        rr_inconsistencies = 0
        for orig in original_read:
            for new in read:
                if orig.key in new.cowrittenKeys:
                    if orig.timestamp < new.timestamp or (orig.timestamp == new.timestamp and orig.tid < new.tid):
                        rr_inconsistencies += 1

    if is_first:
        read_pass = {}
        for rv in read:
            read_pass[rv.key] = {
                'tid': rv.tid,
                'tts': rv.timestamp,
                'cowritten': list(rv.cowrittenKeys)
            }

        response = lmbd.invoke(FunctionName='ddb-txn',
                               Payload=json.dumps(
                                   {'count': 2,
                                    'metadata': (tid, tts),
                                    'read': read_pass}))
        return json.loads(response['Payload'].read())


    return [0, rr_inconsistencies]

class Storage:
    def __init__(self):
        pass

    def txn_get(self, keys):
        success = False

        inp = []
        for key in keys:
            struct = {
                'Get': {
                    'Key': {
                        'DataKey': {
                            'S': key
                        }
                    },
                    'TableName': table
                }
            }
            inp.append(struct)

        while not success:
            try:
                result = ddb.transact_get_items(TransactItems=inp)
                success = True
            except botocore.exceptions.ClientError as e:
                success = False

        data = []
        for resp in result['Responses']:
            data.append(resp['Item']['Value']['B'])

        return data

    def txn_put(self, keys, values):
        success = False
        inp = []

        for idx in range(len(keys)):
            key = keys[idx]
            val = values[idx]
            struct = {
                'Put': {
                    'Item': {
                        'DataKey': {
                            'S': key
                        },
                        'Value': {
                            'B': val
                        }
                    },
                    'TableName': table
                }
            }

            inp.append(struct)


        while not success:
            try:
                ddb.transact_write_items(TransactItems=inp)
                success = True
            except botocore.exceptions.ClientError:
                success = False

