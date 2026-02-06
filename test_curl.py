import subprocess
import time

# Give server a moment to pick up template changes
time.sleep(1)

# Make a request to the server
result = subprocess.run(
    ['curl', '-H', 'Host: chill.localhost', 'http://127.0.0.1:8000/', '-w', '\\nHTTP Status: %{http_code}\\n', '-s'],
    capture_output=True,
    text=True,
    timeout=10
)

print("=== HTTP Response ===")
lines = result.stdout.split('\n')
# Show first few lines and last few lines
for line in lines[:10]:
    print(line)
print("...")
for line in lines[-5:]:
    print(line)

# Check for errors
if 'VariableDoesNotExist' in result.stdout or 'TemplateSyntaxError' in result.stdout or '500' in result.stdout:
    print("\n✗ ERROR found in response")
elif '200' in result.stdout:
    print("\n✓ SUCCESS: Page returned 200 OK")
else:
    print(f"\n? Unknown status, last output: {result.stdout[-100:]}")
