import requests
import re
import http.cookiejar

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}
session.headers = headers
session.cookies = http.cookiejar.LWPCookieJar(filename='cookies')

try:
    # 載入cookie
    session.cookies.load(filename='cookies', ignore_discard=True)
except:
    print('cookies不能載入')

params = {
    'lang': 'zh_tw',
    'source': 'pc',
    'view_type': 'page',
    'ref': 'wwwtop_accounts_index'
}
datas = {
    'pixiv_id': '',
    'password': '',
    'captcha': '',
    'g_reaptcha_response': '',
    'post_key': '',
    'source': 'pc',
    'ref': 'wwwtop_accounts_indes',
    'return_to': 'https://www.pixiv.net/'
}

def get_postkey():
    login_url = 'https://accounts.pixiv.net/login'  # 登入的URL
    res = session.get(login_url, params=params)  # 抓取登入頁面
    pattern = re.compile(r'name="post_key" value="(.*)">')  # 提取post_key
    r = pattern.findall(res.text)
    datas['post_key'] = r[0]

def already_login():
    # 嘗試進入帳號設定介面，來判斷是否登入成功
    url = 'https://www.pixiv.net/setting_user.php'
    login_code = session.get(url, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False

def login():
    account = input('請輸入用戶名或信箱\n> ')
    password = input('請輸入密碼\n> ')
    post_url = 'https://accounts.pixiv.net/api/login?lang=en'  # 發送POST的URL
    # 載入postkey
    get_postkey()
    datas['pixiv_id'] = account
    datas['password'] = password
    # 發送post模擬登入
    session.post(post_url, data=datas)
    if already_login():
        # 儲存cookies
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