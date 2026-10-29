import hashlib, hmac, base64, time, uuid, requests
from datetime import datetime
from pathlib import Path

TOKEN = 'eb94b4ef989b8d19f1ce2e8ae9a1e0b5626fa91104f5924b3b86eb12c0c0b4bd036a0a4cfc00fa2a9b3d22f1f7b4ec23'
SECRET = 'e0e7ff2f544f3c0fef7e4b98f4429b61'
DEVICE_ID = 'B0E9FEB5A1B4'
TEMPLATE_ID = 1834
COMPONENT_ID_TOPIC = 1490856980
COMPONENT_ID_JAPAN_NEWS = 1796094733
COMPONENT_ID_WORLD_NEWS = 456432528
COMPONENT_ID_AI_NEWS = 43149190

SCRIPT_DIR = Path(__file__).resolve().parent

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
    current_date = datetime.now().astimezone().strftime('%m月%d日 %H:%M')

    messages = (
        (COMPONENT_ID_TOPIC, f'最新トピック（{current_date}）'),
        (COMPONENT_ID_JAPAN_NEWS,
         (SCRIPT_DIR / 'japan_news.txt').read_text(encoding='utf-8').rstrip('\r\n')),
        (COMPONENT_ID_WORLD_NEWS,
         (SCRIPT_DIR / 'world_news.txt').read_text(encoding='utf-8').rstrip('\r\n')),
        (COMPONENT_ID_AI_NEWS,
         (SCRIPT_DIR / 'ai_news.txt').read_text(encoding='utf-8').rstrip('\r\n')),
    )

    for component_id, message in messages:
        update_component(TEMPLATE_ID, component_id, message)

if __name__ == '__main__':
    main()
