import aiohttp
import asyncio
import json
import os
import shutil
import sys
import time

import imageio
import zipfile

from modules import login
from modules import update
from modules import rank

update.update()
login_session = login.test_login()
if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
dir = os.path.join('.', 'pixiv', '')
tempdir = os.path.join('.', 'temp')
adult = '0'
cookies = {}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36', 'Referer': 'https://www.pixiv.net/'}
ImgID = []
ImgID2 = []
ImgUrl = []
gifID = []

try:
    if not os.path.exists(dir):
        os.makedirs(dir)
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
except OSError:
    print('無法建立資料夾' + dir)

def web(ID):
    if adult == '0':
        if ID in ImgID2:
            pass  # print('檢查到有R-18的圖片即將略過')
        else:
            ImgID.append(ID)
    else:
        ImgID.append(ID)

async def medium_manga(ID):
    url = 'https://www.pixiv.net/ajax/illust/' + ID + '/pages'
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        html = await session.get(url)
        x = json.loads(await html.text())
        if x['body'][0]['urls']['original'].find('ugoira') == -1:
            for url in x['body']:
                ImgUrl.append(url['urls']['original'])
        else:
            gifID.append(ID)

async def gif(ID):
    ID_temp = os.path.join('.', 'temp', ID)
    url = 'https://www.pixiv.net/ajax/illust/' + ID + '/ugoira_meta'
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        html = await session.get(url)
        x = json.loads(await html.text())
        link = x['body']['originalSrc']
        delay = (x['body']['frames'][0]['delay'] / 1000)
        urlsplit = str.split(link, '/')
        gif_name = urlsplit[-1][0:-4] + '.gif'
        if os.path.isfile(dir + gif_name):
            print(gif_name + ' 已下載過了')
        else:
            imgzip = await session.get(link, headers=headers)
            content = await imgzip.read()
            with open(os.path.join('.', 'temp', urlsplit[-1]), 'wb') as file:
                file.write(content)
                file.close()
            with zipfile.ZipFile(os.path.join('.', 'temp', urlsplit[-1]), 'r') as file:
                os.makedirs(ID_temp)
                file.extractall(ID_temp)
                image_list = file.namelist()
            await create_gif(image_list, gif_name, delay, ID_temp)
            print('ID：' + ID + ' GIF建立成功')

async def create_gif(image_list, gif_name, delay, ID_temp):
    frames = []
    for image_name in image_list:
        frames.append(imageio.imread(os.path.join(ID_temp, image_name)))
    imageio.mimsave(dir + gif_name, frames, 'GIF', duration=delay)
    return

async def download(link):
    urlsplit = str.split(link, '/')
    if os.path.isfile(dir + urlsplit[-1]):
        print(link + ' 已下載過了')
    else:
        async with aiohttp.ClientSession() as session:
            response = await session.get(link, headers=headers)
            content = await response.read()
        with open(dir + urlsplit[-1], 'wb') as file:
            file.write(content)
        print(link + ' 下載完成')
    return

def getjson():
    urlID = input('請輸入作者ID：')
    print('正在收集圖片URL')
    Url = 'https://www.pixiv.net/ajax/user/' + urlID + '/profile/all'
    IDjson = json.loads(login_session.get(Url).text)
    illusts = IDjson['body']['illusts']
    manga = IDjson['body']['manga']
    for key, values in illusts.items():
        web(ID=key)
    for key, values in manga.items():
        web(ID=key)
    tagcheck(urlID)

def tagcheck(urlID):
    Url = 'https://www.pixiv.net/ajax/user/' + urlID + '/illustmanga/tag?tag=R-18&offset=0&limit=9999'
    v = json.loads(login_session.get(Url).text)
    tag = v['body']['works']
    for total in tag:
        ImgID2.append(total['id'])

def switchadult():
    global adult
    print('0 關閉下載R-18  1 開啟下載R-18')
    mode = str(input('請輸入數字選擇：'))
    if mode == '0':
        adult = '0'
    else:
        adult = '1'

def main():
    start = time.time()
    for item in login_session.cookies:
        cookies[item.name] = item.value
    loop = asyncio.get_event_loop()
    if ImgID != []:
        idtasks = [asyncio.ensure_future((medium_manga(ID))) for ID in ImgID]
        loop.run_until_complete(asyncio.wait(idtasks))
    if ImgUrl != []:
        imgtasks = [asyncio.ensure_future((download(link))) for link in ImgUrl]
        loop.run_until_complete(asyncio.wait(imgtasks))
    if gifID != []:
        giftasks = [asyncio.ensure_future((gif(ID))) for ID in gifID]
        loop.run_until_complete(asyncio.wait(giftasks))
    end = time.time()
    print('總共花了' + str(int(end - start)) + '秒')
    shutil.rmtree(tempdir)

if __name__ == "__main__":
    while True:
        print('1.作者UID    3.是否下載R-18圖片 目前=' + adult + ' 0=關閉 1=開啟\n2.作品UID    4.抓取排行榜')
        mode = str(input('請輸入數字選擇：'))
        if mode == '1':
            getjson()
            main()
        elif mode == '2':
            ID = input('請輸入圖片ID：')
            ImgID.append(ID)
            main()
        elif mode == '4':
            ImgID = rank.rank_content(login_session, modenum=int(input('0：每日    1：每週    2：每月    3.：新人\n請輸入要抓取的時間：')), contentnum=int(input('0：插圖illust    1：動圖ugoira    2：漫畫manga\n請輸入要抓取的內容：')), r18=int(adult))
            main()
        else:
            switchadult()