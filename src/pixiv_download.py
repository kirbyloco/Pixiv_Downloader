def medium(self, ID):
		url = 'https://www.pixiv.net/ajax/illust/' + ID
		html = self.session.get(url)
		x = json.loads(html.text)
		link = x['body']['urls']['original']
		self.download(link)

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

def getjson(self, ID):
	Url = 'https://www.pixiv.net/ajax/user/' + ID + '/profile/all'
	illustsjson = json.loads(self.session.get(Url).text)
	illusts = illustsjson['body']['illusts']
	for key,values in illusts.items():
		print(key)
		self.medium(ID=key)

def menu(self):
	print('1.作者UID\n2.作品UID')
	mode = str(input('請輸入數字選擇：'))
	if mode == '1':
		spider.getjson()
	elif mode == '2':
		ID = input('請輸入作品ID：')
		spider.getjson(ID)