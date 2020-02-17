import unittest

loader = unittest.TestLoader()
suites = loader.discover("./tests", pattern="test_*.py")
print("start") #Don't remove this line
for suite in suites._tests:
    print(suite)
    for cls in suite._tests:
        print(cls)
        try:
            for m in cls._tests:
                print(m.id())
        except:
            pass
# Run ALL Tests ==>
# python c:\Users\star0\.vscode\extensions\ms-python.python-2020.2.63072\pythonFiles\visualstudio_py_testlauncher.py --us=./tests --up=test_*.py --uvInt=2 --result-port=58879
# Check Output "Python Test Log"