import sys
_fails = 0
for _n, _f in list(globals().items()):
    if _n.startswith('test_') and callable(_f):
        try:
            _f(); print('PASS', _n)
        except Exception as _e:
            _fails += 1; print('FAIL', _n, repr(_e))
print(('%d failed' % _fails) if _fails else 'all tests passed')
sys.exit(1 if _fails else 0)
