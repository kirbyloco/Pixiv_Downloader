import json

imgid = []
mode = ['daily', 'weekly', 'monthly', 'rookie']
content = ['illust', 'ugoira', 'manga']


def rank_content(login_session, modenum, contentnum, r18):
    url = ['https://www.pixiv.net/ranking.php?mode=' + mode[modenum] + '&content=' + content[contentnum] + '&p=1&format=json',
           'https://www.pixiv.net/ranking.php?mode=' + mode[modenum] + '_r18&content=' + content[contentnum] + '&p=1&format=json']
    return get_rank(login_session, url[r18])


def get_rank(login_session, url):
    a = login_session.get(url).text
    b = json.loads(a)
    for id in b['contents']:
        imgid.append(str(id['illust_id']))
    return imgid


if __name__ == "__main__":
    import requests
    print(rank_content(requests, 0, 0, 0))
