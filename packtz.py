import struct
import json
import sys

with open(sys.argv[1], 'r') as f:
    tzdb = json.load(f)

ntzs = len(tzdb['tzs'])
ndstrules = len(tzdb['dstrules']) + 1
naliases = 0
for tz in tzdb['tzs']:
    naliases += len(tz['aliases'])

outf = open(sys.argv[2], 'wb')
outf.write(struct.pack("<HHH", ntzs, ndstrules, naliases + 3))
for tz in tzdb['tzs']:
    outf.write(struct.pack('<B15sh5sb', tz['cont'], tz['city'].encode(), tz['gmtmin'], tz['tznam'].encode(), tz['dstrule']))

for dstn in range(1,ndstrules):
    dst = tzdb['dstrules'][f"{dstn}"]
    def encode(rule):
        flags = 0
        if rule['dow_direction'] == 'BACKWARD':
            flags |= 1
        elif rule['dow_direction'] == 'FORWARD':
            pass
        else:
            raise ValueError(f"illegal dow_direction {rule['dow_direction']}")

        if rule['transition_tz'] == 'UTC':
            flags |= 4
        elif rule['transition_tz'] == 'STANDARD':
            flags |= 2
        elif rule['transition_tz'] == 'LOCAL':
            pass
        else:
            raise ValueError(f"illegal transition_tz {rule['transition_tz']}")
        
        outf.write(struct.pack('1sBBBBBBB', rule['label'].encode(), rule['dow'], flags, rule['month'], rule['dom'], rule['hour'], rule['minute'], 0))
    encode(dst['daylight'])
    encode(dst['standard'])

for tzid,tz in enumerate(tzdb['tzs']):
    for alias in tz['aliases']:
        outf.write(struct.pack('<H33s', tzid, alias.encode()))
