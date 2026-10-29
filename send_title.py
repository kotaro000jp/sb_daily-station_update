import argparse
import hashlib, hmac, base64, time, uuid, requests

TOKEN = 'eb94b4ef989b8d19f1ce2e8ae9a1e0b5626fa91104f5924b3b86eb12c0c0b4bd036a0a4cfc00fa2a9b3d22f1f7b4ec23'
SECRET = 'e0e7ff2f544f3c0fef7e4b98f4429b61'
DEVICE_ID = 'B0E9FEB5A1B4'

def get_headers():
    t = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    sign = base64.b64encode(
        hmac.new(SECRET.encode(), (TOKEN+t+nonce).encode(),
                 hashlib.sha256).digest()
    ).decode()
    return {'Authorization': TOKEN, 'sign': sign, 't': t,
            'nonce': nonce, 'Content-Type': 'application/json'}

def update_component(template_id, component_id, text):
    url = f'https://api.switch-bot.com/v1.1/devices/{DEVICE_ID}/commands'
    payload = {'commandType': 'command', 'command': 'customPutComponent',
               'parameter': {'templateID': template_id,
                             'componentID': component_id,
                             'text': text[:100]}}
    print(requests.post(url, json=payload, headers=get_headers()).json())

def main():
    parser = argparse.ArgumentParser(
        description='Send a title message to SwitchBot.'
    )
    parser.add_argument('message', help='message to send')
    args = parser.parse_args()

    update_component(1834, 1490856980, args.message)

if __name__ == '__main__':
    main()
