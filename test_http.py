import urllib.request
import urllib.error

headers = {'Host': 'chill.localhost'}
req = urllib.request.Request('http://127.0.0.1:8000/', headers=headers)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.getcode()
        data = resp.read()
        
        print(f"✓ Status: {status}")
        print(f"✓ Content length: {len(data)} bytes")
        
        # Check for errors in response
        if b'VariableDoesNotExist' in data or b'TemplateSyntaxError' in data or b'Internal Server Error' in data:
            print("✗ ERROR found in response body")
            # Print first 1000 chars
            preview = data[:1000].decode('utf-8', errors='replace')
            print("Preview:", preview)
        else:
            print("✓ No template/Django errors detected")
            
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}: {e.reason}")
    try:
        error_page = e.read()
        if b'VariableDoesNotExist' in error_page or b'TemplateSyntaxError' in error_page:
            print("✗ Template error found")
    except:
        pass
except Exception as e:
    print(f"✗ Connection error: {type(e).__name__}: {e}")
