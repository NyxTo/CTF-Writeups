import requests
import json

def guess(payload):
    resp = requests.post(f'http://{SERVER}:{PORT}/api/compare', params={'guess': payload})
    return ''.join(res['letter'] for res in json.loads(resp.text))

flag = ''
for i in range(32):
    try:
        target = guess('a' * (31-i))
    except Exception:
        break
    for ch in range(32, 127):
        if guess('a' * (31-i) + flag + chr(ch)) == target:
            flag += chr(ch)
            break
    print(flag)
