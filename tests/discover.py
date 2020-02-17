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