import datetime
import re
import json

class CommonHelper:

    def get_datetime(self, input: str):
        re_groups = re.search("(20\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)", 
            input)
        if not re_groups:
            print('Cant parse datetime in : {}'.format(input))
            raise ValueError('Cant parse datetime in file : {}'.format(input))
        year = int(re_groups.group(1))
        month = int(re_groups.group(2))
        day = int(re_groups.group(3))
        hour = int(re_groups.group(4))
        minute = int(re_groups.group(5))
        seconds = int(re_groups.group(6))
        return datetime.datetime(year, month, day, hour, minute, seconds)

    def size_human(self, size):
        _suffixes = ['bytes', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb']
        # determine binary order in steps of size 10 
        # (coerce to int, // still returns a float)
        order = int(log2(size) / 10) if size else 0
        # format file size
        # (.4g results in rounded numbers for exact matches and max 3 decimals, 
        # should never resort to exponent values)
        return '{:.4g} {}'.format(size / (1 << (order * 10)), _suffixes[order])

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        #print("type: ", type(obj))
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)
