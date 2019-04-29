def medium_manga(self, ID):
	url = 'https://www.pixiv.net/ajax/illust/' + ID + '/pages'
	html = self.session.get(url)
	x = json.loads(html.text)
	if x['body'][0]['urls']['original'].find('ugoira') == -1:
		for url in x['body']:
			self.download(url['urls']['original'])
	else:
		self.gif(ID)

def gif(self, ID):
	url = 'https://www.pixiv.net/ajax/illust/' + ID + '/ugoira_meta'
	html = self.session.get(url)
	x = json.loads(html.text)
	link = x['body']['originalSrc']
	delay = (x['body']['frames'][0]['delay'] / 1000)
	urlsplit = str.split(link,'/')
	gif_name = urlsplit[-1][0:-4] + '.gif'
	if os.path.isfile('./pixiv/' + gif_name):
		print(gif_name + ' 已下載過了')
	else:
		imgzip = requests.get(link,headers={'Referer':'https://www.pixiv.net/'})
		with open(urlsplit[-1], 'wb') as file:
			file.write(imgzip.content)
			file.close
		with zipfile.ZipFile(urlsplit[-1] ,'r') as file:
			file.extractall()
			image_list = file.namelist()
		os.remove(urlsplit[-1])
		self.create_gif(image_list, gif_name, delay)
		print('ID：' + ID + ' GIF建立成功')
		for i in image_list:
			os.remove(i)

def create_gif(self, image_list, gif_name, delay):
	frames = []
	for image_name in image_list:
		frames.append(imageio.imread(image_name))
	imageio.mimsave('./pixiv/' + gif_name, frames, 'GIF', duration = delay)
	return

def download(self, link):
	urlsplit = str.split(link,'/')
	if os.path.isfile('./pixiv/' + urlsplit[-1]):
		print(link + ' 已下載過了')
	else:
		img = requests.get(link,headers={'Referer':'https://www.pixiv.net/'})
		with open ('./pixiv/' + urlsplit[-1] ,'wb') as file:
			file.write(img.content)
			file.close
		print(link + ' 下載完成')
	return

def getjson(self, ID):
	Url = 'https://www.pixiv.net/ajax/user/' + ID + '/profile/all'
	illustsjson = json.loads(self.session.get(Url).text)
	illusts = illustsjson['body']['illusts']
	for key,values in illusts.items():
		self.medium_manga(ID=key)

def menu(self):
	print('1.作者UID\n2.作品UID')
	mode = str(input('請輸入數字選擇：'))
	if mode == '1':
		spider.getjson()
	elif mode == '2':
		ID = input('請輸入作品ID：')
		spider.getjson(ID)