import requests
from datetime import datetime, timezone
import hashlib
import sys

session = requests.Session()
local_time = datetime.utcnow().replace(
    microsecond=0).replace(tzinfo=timezone.utc).isoformat()
headers = {
    'X-Client-Time': local_time,
    'X-Client-Hash': hashlib.md5((local_time + '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c').encode('utf-8')).hexdigest(),
    'App-OS': 'ios',
    'App-OS-Version': '12.0.1',
    'App-Version': '7.6.2',
    'User-Agent': 'PixivIOSApp/7.6.2 (iOS 12.2; iPhone8,2)',
    'Accept-Language': 'English'
}
session.headers.update(headers)

datas = {
    'get_secure_url': 1,
    'client_id': 'KzEZED7aC0vird8jWyHM38mXjNTY',
    'client_secret': 'W9JZoJe00qPvJsiyCGT3CCtC6ZUtdpKpzMbNlUGP',
    'grant_type': 'password',
    'username': '',
    'password': ''
}


def login():
    username = input('請輸入用戶名或信箱\n> ')
    password = input('請輸入密碼\n> ')
    post_url = 'https://oauth.secure.pixiv.net/auth/token'  # 發送POST的URL
    # 載入postkey
    datas['username'] = username
    datas['password'] = password
    # 發送post模擬登入
    try:
        r = session.post(post_url, data=datas).json()
        access_token = r['response']['access_token']
    except:
        print('登入失敗')
        sys.exit(1)
    session.headers.update(
        {'Authorization': f'Bearer {access_token}'}
    )
    return session


if __name__ == "__main__":
    login()
