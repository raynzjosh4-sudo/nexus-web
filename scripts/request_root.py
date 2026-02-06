import urllib.request
url='http://chill.localhost:8000/'
try:
    resp=urllib.request.urlopen(url, timeout=10)
    print('Status:', resp.getcode())
    data=resp.read()
    print('Length:', len(data))
except Exception as e:
    print('Request error:', repr(e))
