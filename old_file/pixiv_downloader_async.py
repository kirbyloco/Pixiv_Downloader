#Version V0.1
import requests
import re
import http.cookiejar
import json
import os, shutil, sys
import time
import imageio, zipfile
import asyncio, aiohttp
from update import update

class PixivSpider(object):
	def __init__(self):
		if sys.platform == 'win32':
			loop = asyncio.ProactorEventLoop()
			asyncio.set_event_loop(loop)
		if os.path.isfile('upgrade.bat'):
			os.remove('upgrade.bat')
		self.dir = os.path.join('.','pixiv','')
		self.tempdir = os.path.join('.','temp')
		self.adult = '0'
		self.cookies = {}
		self.ImgID = []
		self.ImgID2 = []
		self.ImgUrl = []
		self.gifID = []
		self.session = requests.Session()
		self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
		self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
		self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}
		self.session.headers = self.headers
		self.session.cookies = http.cookiejar.LWPCookieJar(filename='cookies')
		try:
			# 載入cookie
			self.session.cookies.load(filename='cookies', ignore_discard=True)
		except:
			print('cookies不能載入')
		try:
			if not os.path.exists(self.dir):
				os.makedirs(self.dir)
		except OSError:
			print ('無法建立資料夾' + self.dir)
		self.params ={
			'lang': 'zh_tw',
			'source': 'pc',
			'view_type': 'page',
			'ref': 'wwwtop_accounts_index'
		}
		self.datas = {
			'pixiv_id': '',
			'password': '',
			'captcha': '',
			'g_reaptcha_response': '',
			'post_key': '',
			'source': 'pc',
			'ref': 'wwwtop_accounts_indes',
			'return_to': 'https://www.pixiv.net/'
			}

	def get_postkey(self):
		login_url = 'https://accounts.pixiv.net/login' #登入的URL
		res = self.session.get(login_url, params=self.params) #抓取登入頁面
		pattern = re.compile(r'name="post_key" value="(.*?)">') #提取post_key
		r = pattern.findall(res.text)
		self.datas['post_key'] = r[0]

	def already_login(self):
		# 嘗試進入帳號設定介面，來判斷是否登入成功
		url = 'https://www.pixiv.net/setting_user.php'
		login_code = self.session.get(url, allow_redirects=False).status_code
		if login_code == 200:
			return True
		else:
			return False

	def login(self):
		account = input('請輸入用戶名或信箱\n> ')
		password = input('請輸入密碼\n> ')
		post_url = 'https://accounts.pixiv.net/api/login?lang=en' # 發送POST的URL
		# 載入postkey
		self.get_postkey()
		self.datas['pixiv_id'] = account
		self.datas['password'] = password
		# 發送post模擬登入
		result = self.session.post(post_url, data=self.datas)
		if self.already_login():
			self.session.cookies.save(ignore_discard=True, ignore_expires=True)
			return
		else:
			self.login()
		# 儲存cookies
	
	def web(self, ID):
		if self.adult == '0':
			if ID in self.ImgID2:
				#print('檢查到有R-18的圖片即將略過')
				pass
			else:
				self.ImgID.append(ID)
		else:
			self.ImgID.append(ID)

	async def medium_manga(self,ID):
		url = 'https://www.pixiv.net/ajax/illust/' + ID + '/pages'
		async with aiohttp.ClientSession(cookies=self.cookies) as session:
			html = await session.get(url)
			x = json.loads(await html.text())
			if x['body'][0]['urls']['original'].find('ugoira') == -1:
				for url in x['body']:
					self.ImgUrl.append(url['urls']['original'])
			else:
				self.gifID.append(ID)

	async def gif(self,ID):
		ID_temp = os.path.join('.','temp',ID)
		url = 'https://www.pixiv.net/ajax/illust/' + ID + '/ugoira_meta'
		async with aiohttp.ClientSession(cookies=self.cookies) as session:
			html = await session.get(url)
			x = json.loads(await html.text())
			link = x['body']['originalSrc']
			delay = (x['body']['frames'][0]['delay'] / 1000)
			urlsplit = str.split(link,'/')
			gif_name = urlsplit[-1][0:-4] + '.gif'
			if os.path.isfile(self.dir + gif_name):
				print(gif_name + ' 已下載過了')
			else:
				imgzip = await session.get(link,headers={'Referer':'https://www.pixiv.net/'})
				content = await imgzip.read()
				with open(os.path.join('.','temp',urlsplit[-1]), 'wb') as file:
					file.write(content)
					file.close
				with zipfile.ZipFile(os.path.join('.','temp',urlsplit[-1]) ,'r') as file:
					os.makedirs(ID_temp)
					file.extractall(ID_temp)
					image_list = file.namelist()
				await self.create_gif(image_list, gif_name, delay, ID_temp)
				print('ID：' + ID + ' GIF建立成功')

	async def create_gif(self, image_list, gif_name, delay, ID_temp):
		frames = []
		for image_name in image_list:
			frames.append(imageio.imread(os.path.join(ID_temp,image_name)))
		# Save them as frames into a gif 
		imageio.mimsave(self.dir + gif_name, frames, 'GIF', duration = delay)
		return

	async def download(self, link):
		urlsplit = str.split(link,'/')
		if os.path.isfile(self.dir + urlsplit[-1]):
			print(link + ' 已下載過了')
		else:
			async with aiohttp.ClientSession() as session:
				response = await session.get(link,headers={'Referer':'https://www.pixiv.net/'})
				content = await response.read()
			with open (self.dir + urlsplit[-1] ,'wb') as file:
				file.write(content)
			print(link + ' 下載完成')
		return

	def getjson(self):
		urlID = input('請輸入作者ID：')
		print('正在收集圖片URL')
		Url = 'https://www.pixiv.net/ajax/user/' + urlID + '/profile/all'
		IDjson = json.loads(self.session.get(Url).text)
		illusts = IDjson['body']['illusts']
		manga = IDjson['body']['manga']
		for key,values in illusts.items():
			self.web(ID=key)
		if manga != []:
			for key,values in manga.items():
				self.web(ID=key)
		self.tagcheck(urlID)

	def tagcheck(self, urlID):
		Url = 'https://www.pixiv.net/ajax/user/' + urlID + '/illustmanga/tag?tag=R-18&offset=0&limit=9999'
		v = json.loads(self.session.get(Url).text)
		tag = v['body']['works']
		for total in tag:
			self.ImgID2.append(total['id'])

	def menu(self):
		print('1.作者UID    3.是否下載R-18圖片 目前=' + self.adult + ' 0=關閉 1=開啟\n2.作品UID')
		mode = str(input('請輸入數字選擇：'))
		if mode == '1':
			self.getjson()
			self.main()
		elif mode == '2':
			ID = input('請輸入ID：')
			self.ImgID.append(ID)
			self.main()
		else:
			self.switchadult()

	def switchadult(self):
		print('0 關閉下載R-18  1 開啟下載R-18')
		mode = str(input('請輸入數字選擇：'))
		if mode == '0':
			self.adult = '0'
		else:
			self.adult = '1'
		self.menu()

	def main(self):
		os.makedirs(self.tempdir)
		start = time.time()
		for item in self.session.cookies:
			self.cookies[item.name] = item.value
		loop = asyncio.get_event_loop()
		if self.ImgID != []:
			idtasks = [asyncio.ensure_future((self.medium_manga(ID))) for ID in self.ImgID]
			loop.run_until_complete(asyncio.wait(idtasks))
		if self.ImgUrl != []:
			imgtasks = [asyncio.ensure_future((self.download(link))) for link in self.ImgUrl]
			loop.run_until_complete(asyncio.wait(imgtasks))
		if self.gifID != []:
			giftasks = [asyncio.ensure_future((self.gif(ID))) for ID in self.gifID]
			loop.run_until_complete(asyncio.wait(giftasks))
		end = time.time()
		print('總共花了' + str(int(end-start)) + '秒')
		shutil.rmtree(self.tempdir)

if __name__ == "__main__":
	update()
	spider = PixivSpider()
	if spider.already_login():
		print('用戶已經登入')
	else:
		spider.login()
	spider.menu()