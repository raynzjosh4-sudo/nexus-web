import urllib.request
url='http://127.0.0.1:8000/'
req=urllib.request.Request(url, headers={'Host':'chill.localhost'})
try:
    resp=urllib.request.urlopen(req, timeout=10)
    print('Status:', resp.getcode())
    data=resp.read()
    print('Length:', len(data))
    # Check for template errors
    if b'TemplateSyntaxError' in data or b'--bg-page: {' in data:
        print('\nFirst 1000 chars:')
        print(data[:1000].decode('utf-8', errors='replace'))
    else:
        print('Page loaded OK, no obvious template errors in CSS')
except Exception as e:
    print('Request error:', repr(e))
