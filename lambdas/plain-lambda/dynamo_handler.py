import json
import os
import pickle
import random
import time
import uuid

import boto3
import numpy as np
import scipy.stats as stats

from aft_pb2 import *

ddb = boto3.client('dynamodb')
lmbd = boto3.client('lambda')
table = 'AftData'

N = 1000
x = np.arange(1, N)
a = 1.0
weights = x ** (-a)
weights /= weights.sum()
bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))

key_template = 'data/%s'

def handler(event, context):
    is_first = bool(int(event['count']) == 1)
    written = []

    storage = Storage()

    if is_first:
        tid, tts = (str(uuid.uuid4()), int(time.time() * 1000))

        # Determine the two write keys.
        key1 = str(bounded_zipf.rvs(size=1)[0])
        key2 = str(bounded_zipf.rvs(size=1)[0])
        local_written = [key1]
        written = [key1, key2]
        read = []

        key = key1
    else:
        tid, tts = event['metadata'][0], event['metadata'][1]
        written = event['written']
        local_written = written
        read = []
        for rv in event['read']:
            val = event['read'][rv]
            kvp = KeyValuePair()
            kvp.key = rv
            kvp.timestamp = int(val['tts'])
            kvp.cowrittenKeys.extend(['cowritten'])
            kvp.tid = val['tid']

            read.append(kvp)
        key = written[1]

    kv_pair = KeyValuePair()
    kv_pair.key = key
    kv_pair.value = os.urandom(4096)
    kv_pair.cowrittenKeys.extend(written)
    kv_pair.tid = tid
    kv_pair.timestamp = tts

    # Do the write.
    storage.put(key, kv_pair.SerializeToString())

    wr_inconsistencies = 0
    rr_inconsistencies = 0

    # Do two reads.
    keys = []
    for _ in range(2):
        key = str(bounded_zipf.rvs(size=1)[0])
        keys.append(key)

    for key in keys:
        kv_pair = KeyValuePair()
        bts = storage.get(key)
        kv_pair.ParseFromString(bts)

        # Check to see if it conflicts with a written key.
        if key in local_written:
            if kv_pair.tid != tid or kv_pair.timestamp != tts:
                wr_inconsistencies += 1

        # Check to see if it conflicts with another key we read.
        for read_key in read:
            if key in read_key.cowrittenKeys:
                # Check to see if this key conflicts with something we read earlier.
                if kv_pair.timestamp < read_key.timestamp or (kv_pair.timestamp == read_key.timestamp and kv_pair.tid < read_key.tid):
                    rr_inconsistencies += 1

            # Check to see if something we read earlier conflicts with what we just read.
            if read_key.key in kv_pair.cowrittenKeys:
                if read_key.timestamp < kv_pair.timestamp or (read_key.timestamp == kv_pair.timestamp and read_key.tid < kv_pair.tid):
                    rr_inconsistencies += 1

        kv_pair.value = b'' # Clear the data field, so we don't lug it around unnecessarily.
        read.append(kv_pair)

    if is_first:
        read_pass = {}
        for rv in read:
            read_pass[rv.key] = {
                'tid': rv.tid,
                'tts': rv.timestamp,
                'cowritten': list(rv.cowrittenKeys)
            }

        response = lmbd.invoke(FunctionName='no-aft',
                               Payload=json.dumps(
                                   {'count': 2,
                                    'metadata': (tid, tts),
                                    'written': written,
                                    'read': read_pass}))
        second_ics = json.loads(response['Payload'].read())
        print(second_ics)
        return [second_ics[0] + wr_inconsistencies, second_ics[1] +
                rr_inconsistencies]

    return [wr_inconsistencies, rr_inconsistencies]

class Storage:
    def __init__(self):
        pass

    def put(self, key, value):
        ddb.put_item(TableName=table,
                    Item={
                        'DataKey': {
                            'S': key_template % key
                        },
                        'Value': {
                            'B': value
                        }
                    })

    def get(self, key):
        return ddb.get_item(TableName=table,
                     Key={
                         'DataKey': {
                             'S': key_template % key
                         }
                     })['Item']['Value']['B']

