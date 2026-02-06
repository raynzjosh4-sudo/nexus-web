import urllib.request
import urllib.error

url='http://127.0.0.1:8000/'
req=urllib.request.Request(url, headers={'Host':'chill.localhost'})
try:
    resp=urllib.request.urlopen(req, timeout=10)
    print('✓ Status:', resp.getcode())
    data=resp.read()
    print('✓ Page loaded, length:', len(data), 'bytes')
    
    # Check for errors
    if b'VariableDoesNotExist' in data or b'TemplateSyntaxError' in data:
        print('✗ Template error found in response')
        print(data[:1000].decode('utf-8', errors='replace'))
    else:
        print('✓ No template errors detected')
except urllib.error.HTTPError as e:
    print(f'✗ HTTP {e.code}: {e.reason}')
    print(e.read()[:500].decode('utf-8', errors='replace'))
except Exception as e:
    print(f'✗ Error: {type(e).__name__}: {e}')
