#!/usr/bin/env python3

import datetime
import os

files = os.listdir('gc-logs')

second_gcs = {}

zero_time = datetime.datetime.strptime('2019-11-01 01:21:12', '%Y-%m-%d %H:%M:%S')

for logfile in files:
    with open(os.path.join('gc-logs', logfile), 'r') as f:
        lines = f.readlines()

        for line in lines:
            if line[0:4] != '2019':
                continue

            splits = line.split(' ')
            time = ' '.join([splits[0], splits[1]])
            time_seconds = time.split('.')[0]
            tm = datetime.datetime.strptime(time_seconds, '%Y-%m-%d %H:%M:%S')

            if zero_time > tm:
                continue # before the benchmark started

            diff = tm - zero_time
            elapsed = diff.seconds

            if elapsed % 2 != 0:
                elapsed += 1
            if elapsed not in second_gcs:
                second_gcs[elapsed] = 0

            second_gcs[elapsed] += int(splits[6])

with open('gcs.txt', 'w') as f:
    f.write('0\t0\n')
    for sid in second_gcs:
        f.write('%d\t%d\n' % (sid, second_gcs[sid]/2))
