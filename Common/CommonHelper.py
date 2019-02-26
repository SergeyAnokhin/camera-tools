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

    # def toJson(self, obj):
    #     return json.dumps(self.__dict__, default= self.dumper, indent=4)
    # def dumper(self, obj):
    #     print("JSON : ", type(obj))
    #     try:
    #         return obj.toJSON()
    #     except:
    #         return obj.__dict__
