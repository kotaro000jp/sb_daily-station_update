#!/usr/bin/env python3

import base64
import getpass
import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
import uuid


API_URL = "https://api.switch-bot.com/v1.1/devices"

token = getpass.getpass("SwitchBot Token: ").strip()
secret = getpass.getpass("SwitchBot Secret: ").strip()

timestamp = str(int(time.time() * 1000))
nonce = str(uuid.uuid4())

string_to_sign = f"{token}{timestamp}{nonce}".encode("utf-8")
signature = base64.b64encode(
    hmac.new(
        secret.encode("utf-8"),
        string_to_sign,
        hashlib.sha256,
    ).digest()
).decode("utf-8")

headers = {
    "Authorization": token,
    "sign": signature,
    "nonce": nonce,
    "t": timestamp,
    "Content-Type": "application/json",
}

request = urllib.request.Request(
    API_URL,
    headers=headers,
    method="GET",
)

try:
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.load(response)
except urllib.error.HTTPError as error:
    print(f"HTTPエラー: {error.code}")
    print(error.read().decode("utf-8", errors="replace"))
    raise SystemExit(1)
except urllib.error.URLError as error:
    print(f"通信エラー: {error.reason}")
    raise SystemExit(1)

if result.get("statusCode") != 100:
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit("SwitchBot APIがエラーを返しました")

body = result.get("body", {})

print("\n=== 物理デバイス ===")
for device in body.get("deviceList", []):
    print(
        f"{device.get('deviceName', '(名前なし)')}\n"
        f"  ID   : {device.get('deviceId')}\n"
        f"  種類 : {device.get('deviceType')}\n"
        f"  Cloud: {device.get('enableCloudService')}\n"
    )

print("=== 赤外線リモコン ===")
for device in body.get("infraredRemoteList", []):
    print(
        f"{device.get('deviceName', '(名前なし)')}\n"
        f"  ID   : {device.get('deviceId')}\n"
        f"  種類 : {device.get('remoteType')}\n"
        f"  Hub  : {device.get('hubDeviceId')}\n"
    )
