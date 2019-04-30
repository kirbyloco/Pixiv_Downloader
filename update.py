import requests
import json

metaversion = 'V0.0.3'

updatedata = requests.get('https://raw.githubusercontent.com/kirbyloco/Pixiv_Downloader/master/version.json')
updatejson = json.loads(updatedata.text)
if updatejson['Version'] > metaversion:
    print('有可以更新的檔案，版本：' + updatejson['Version'])
    newrelease = requests.get(updatejson['URL'], verify=True)
    with open ('pixiv_downloader.exe' ,'wb') as file:
        file.write(newrelease.content)
    print('更新完成')