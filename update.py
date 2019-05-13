import requests
import json
import os
import subprocess

metaversion = 'V0.0.4'

def update():
	print('檢查更新中...')
	updatedata = requests.get('https://raw.githubusercontent.com/kirbyloco/Pixiv_Downloader/master/version.json')
	updatejson = json.loads(updatedata.text)
	if updatejson['Version'] > metaversion:
		print('有可以更新的檔案，版本：' + updatejson['Version'])
		newrelease = requests.get(updatejson['URL'], verify=True)
		with open (os.path.join('.','pixiv_downloader_new.exe') ,'wb') as file:
			file.write(newrelease.content)
		WriteRestartCmd('pixiv_downloader.exe')
		print('更新完成')
	else:
		print('目前為最新版本')

def WriteRestartCmd(exe_name):
	b = open("upgrade.bat",'w')
	TempList = "@echo off\n";
	TempList += "if not exist " + exe_name + " exit \n";
	TempList += "ping 127.0.0.1 > NUL \n";
	TempList += "del pixiv_downloader.exe \n"
	TempList += "rename pixiv_downloader_new.exe pixiv_downloader.exe \n"
	TempList += "start " + exe_name
	b.write(TempList)
	b.close()
	subprocess.Popen("upgrade.bat")
	return

if __name__ == "__main__":
	#WriteRestartCmd('pixiv_downloader.exe')
	update()