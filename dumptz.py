import struct
import json
import sys

def unpack_from_file(f, desc):
    sz = struct.calcsize(desc)
    data = f.read(sz)
    return struct.unpack(desc, data)

tzs = []
dstrules = []

with open(sys.argv[1], 'rb') as f:
    ntzs, ndstrules, naliases = unpack_from_file(f, '<HHH')
    for i in range(ntzs):
        cont, city, gmtmin, tznam, dstrule = unpack_from_file(f, '<B15sh5sb')
        city = city.decode().rstrip('\0')
        tznam = tznam.decode().rstrip('\0')
        tzs.append({'cont': cont, 'city': city, 'gmtmin': gmtmin, 'tznam': tznam, 'dstrule': dstrule, 'aliases': []})
    
    for i in range(ndstrules - 1):
        dlabel, dow, flags, month, dom, hour, minute, pad = unpack_from_file(f, '1sBBBBBBB')
        daylight = {'label': dlabel.decode(), 'dow': dow, 'dow_direction': 'BACKWARD' if flags & 1 else 'FORWARD', 'month': month, 'dom': dom, 'hour': hour, 'minute': minute, 'transition_tz': 'UTC' if flags & 4 else 'STANDARD' if flags & 2 else 'LOCAL'}
        dlabel, dow, flags, month, dom, hour, minute, pad = unpack_from_file(f, '1sBBBBBBB')
        standard = {'label': dlabel.decode(), 'dow': dow, 'dow_direction': 'BACKWARD' if flags & 1 else 'FORWARD', 'month': month, 'dom': dom, 'hour': hour, 'minute': minute, 'transition_tz': 'UTC' if flags & 4 else 'STANDARD' if flags & 2 else 'LOCAL'}
        # hour >= 24 is 'midnight the following day'
        dstrule = {'daylight': daylight, 'standard': standard}
        dstrules.append(dstrule)

    for i in range(naliases - 3):
        tzid,name = unpack_from_file(f,"<H33s")
        name = name.decode().rstrip('\0')
        tzs[tzid]['aliases'].append(name)
    
    #for i,tz in enumerate(tzs):
    #    print(f"tz{i}: {tz}")
    #for i,rule in enumerate(dstrules):
    #    print(f"dstrule{i+1}: {rule}")
    
tzdb = {
    'tzs': tzs,
    'dstrules': { i+1: rule for i,rule in enumerate(dstrules) }
}

print(json.dumps(tzdb))
