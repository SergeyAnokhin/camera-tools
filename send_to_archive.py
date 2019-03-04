import os
import json
import shutil
import re
import sys
import datetime
from pprint import pprint
import json
from Archiver.CameraArchiveHelper import CameraArchiveHelper

helper = CameraArchiveHelper()
# ['FoscamHut', 'FoscamPTZ', 'Foscam', 'FoscamPlay', 'DLinkCharles', 'DLinkFranck', 'KonxHD']
configs = helper.load_configs('configs', ['DLinkCharles'])

for config in configs:
    print('#################################################')
    print(config)
    files = helper.get_files(config)
    helper.move_files(files, config)
