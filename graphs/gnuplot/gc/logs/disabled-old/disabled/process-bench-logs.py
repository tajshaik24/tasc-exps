#!/usr/bin/env python3

import os

files = os.listdir('bench-logs')

epoch_throughputs = {}

for logfile in files:
    with open(os.path.join('bench-logs', logfile), 'r') as f:
        lines = f.readlines()
        for line in lines:
            splits = line.split(':')
            epoch = splits[5].strip()
            tput = float(splits[6].strip())

            epoch_id = int(epoch.split(' ')[1])

            if epoch_id not in epoch_throughputs:
                epoch_throughputs[epoch_id] = 0

            epoch_throughputs[epoch_id] += tput

with open('throughputs.txt', 'w') as f:
    f.write('0\t0')
    for eid in epoch_throughputs:
        f.write('%d\t%f\n' % ((eid+1) * 5, epoch_throughputs[eid]))

