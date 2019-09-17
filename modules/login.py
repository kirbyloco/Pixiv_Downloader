import requests
from datetime import datetime
import hashlib
import http.cookiejar

session = requests.Session()
local_time = datetime.now().isoformat()
headers = {
    'X-Client-Time': local_time,
    'X-Client-Hash': hashlib.md5((local_time+'28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c').encode('utf-8')).hexdigest(),
    'User-Agent': 'PixivAndroidApp/5.0.64 (Android 9.0)'}
session.headers = headers
session.cookies = http.cookiejar.LWPCookieJar(filename='cookies')

try:
    # 載入cookie
    session.cookies.load(filename='cookies', ignore_discard=True)
except:
    print('cookies不能載入')

datas = {
    'get_secure_url': 1,
    'client_id': 'MOBrBDS8blbauoSck0ZfDbtuzpyT',
    'client_secret': 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj',
    'grant_type': 'password',
    'username': '',
    'password': ''
}

def already_login():
    # 嘗試進入帳號設定介面，來判斷是否登入成功
    url = 'https://www.pixiv.net/setting_user.php'
    login_code = session.get(url).status_code
    if login_code == 200:
        return True
    else:
        return False

def login():
    username = input('請輸入用戶名或信箱\n> ')
    password = input('請輸入密碼\n> ')
    post_url = 'https://oauth.secure.pixiv.net/auth/token'  # 發送POST的URL
    # 載入postkey
    datas['username'] = username
    datas['password'] = password
    # 發送post模擬登入
    session.post(post_url, data=datas)
    if already_login():
        session.cookies.save(ignore_discard=True, ignore_expires=True)
        return session
    else:
        login()

def test_login():
    if already_login():
        print('用戶已經登入')
        return session
    else:
        login()

if __name__ == "__main__":
    test_login()
