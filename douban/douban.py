from urllib import request, parse, error
from bs4 import BeautifulSoup
import os
import json
import re
import time
import random



_url = 'http://book.douban.com/tag/'

classify = ''
label = ''
path = ''


def getClassify():
    f = open('classify.json', 'r', encoding='utf-8')
    data = f.read()
    d = json.loads(data)
    return d


def getHtml(url):
    time.sleep(1)
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
    ]
    agent = random.choice(user_agents)
    _header = {
        "Accept": '*/*',
        "Connection": "keep-alive",
        'User-Agent': agent,
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        "Host": "book.douban.com",
        "Cookie": 'bid=QUgZBkegVJE; ct=y; __yadk_uid=1HDmw6QozQq6tGqLsLJjKn81Fq0oDYt0; gr_user_id=6c8d0477-1d4e-465a-9eb0-3ebddf2efd9f; _vwo_uuid_v2=DAB46A53BD8744A56039B27DC0F769F1B|f83f044f13cbbb4849e9e5dfe76ca581; ap_6_0_1=1; __utmc=30149280; __utmc=81379588; viewed="26698660_25862578_27614904_4820710"; ap_v=0,6.0; ps=y; ck=o_1V; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1536062166%2C%22https%3A%2F%2Fwww.douban.com%2Faccounts%2Flogin%3Fredir%3Dhttps%3A%2F%2Fbook.douban.com%2Ftag%2F%25E5%25B0%258F%25E8%25AF%25B4%26source%3DNone%26login_type%3Dsms%22%5D; _pk_id.100001.3ac3=7b5654f540f1d88f.1535957455.9.1536062166.1536057064.; _pk_ses.100001.3ac3=*; __utma=30149280.565248757.1535957455.1536057064.1536062166.6; __utmz=30149280.1536062166.6.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/accounts/login; __utmt_douban=1; __utmb=30149280.1.10.1536062166; __utma=81379588.752767777.1535957455.1536057064.1536062166.6; __utmz=81379588.1536062166.6.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/accounts/login; __utmt=1; __utmb=81379588.1.10.1536062166; push_noty_num=0; push_doumail_num=0'
    }
    query = request.Request(url, headers=_header)
    try:
        response = request.urlopen(query)
    except error.HTTPError as e:
        print(e.code)
        print(e.info())
        print(e.geturl())

    html = response.read().decode('utf-8').replace('&nbsp;', '').replace('<br>', '')
    time.sleep(1)
    return html


def downloadImg(img_url, img_path):
    print('---downloadImg:' + img_path + '-----')
    request.urlretrieve(img_url, img_path)


def urlDecode (s):
    return parse.quote(s)


def getImgName(img_url):
    name = re.search(r's\d+.(jpg|png|gif)$', img_url)
    return name.group()

def writeFile(content, f_path):
    print('----------------开始写入数据-----------------')
    f = open(f_path, 'a', encoding='utf-8')
    f.write(content)
    f.close()


def getInfoData(url, dist):
    print('--------------开始获取主体数据-----------------')
    _id = re.search(r'\d+', url).group()
    html = getHtml(url)
    soup = BeautifulSoup(html, 'html.parser')
    pl = soup.find('div', id='info').find_all('span', class_='pl')

    # 图书信息
    info = {}
    for p in pl:
        title_str = str(p.string).replace(':', '').strip()
        if(re.search(r'\n+', str(p.next_sibling)) or (type(p.next_sibling) == type(p.find_next_sibling('a')))):
            _str = p.find_next_sibling('a').string
        else:
            _str = p.next_sibling
        response_str = str(_str).replace('\n', '').replace(' ', '')
        info[title_str] = response_str

    # print(info)
    # info存入dist
    dist['info'] = info

    # 内容和作者简介
    intro = soup.find_all('div', class_='intro')
    x = 1
    synopsis = {}
    for item in intro:
        if(item.find('a')):
            print('this content is not complete')
            continue
        ps = item.find_all('p')
        p_list = []
        for p in ps:
            p_list.append(str(p.string))
        if(x == 1):
            synopsis['content'] = p_list
        if(x == 2):
            synopsis['author'] = p_list
        x = x + 1
    # print(synopsis)
    # synopsis存入dist
    dist['synopsis'] = synopsis

    # 目录
    s_id = 'dir_' + _id
    short = s_id + '_short'
    e = soup.find('div', id=short)
    if(e):
        catalog = []
        if(e.find('a')):
            full = s_id + '_full'
            e = soup.find('div', id=full)
        c = re.finditer(r'.*?<br(/*?)>', str(e), re.I)
        for i in c:
            cat = i.group().replace('<br>', '').replace('<br/>', '').strip()
            catalog.append(cat)

        # print(catalog)
        dist['catalog'] = catalog


def mkdir(d_path):
    d_path = d_path.strip()
    isExist = os.path.exists(d_path)
    if not isExist:
        os.makedirs(d_path)
        print(d_path + '创建成功')
    else:
        print(d_path + '目录文件夹已存在')


def getData(list, data):
    subjectItem = list

    # print(subjectItem)

    for item in subjectItem:

        dist = {}
        # 获取图片

        _src = item.find('img').get('src')
        img_path = path + '/img/' + getImgName(_src)
        downloadImg(_src, img_path)

        # 获取主体数据

        info_href = item.h2.a.get('href')
        info_title = item.h2.a.get('title')
        # print(info_href, info_title)

        dist['name'] = info_title
        dist['cover'] = _src

        print('--------------------' + info_title + '---------------')

        getInfoData(info_href, dist)

        data.append(dist)



def loopUrl(tag_url, json_path):
    start = 0
    data = []
    while True:
        query_url = tag_url + '?start=' + str(start) + '&type=T'
        print('----' + query_url + '----')
        time.sleep(1)
        h = getHtml(query_url)
        s = BeautifulSoup(h, 'html.parser')
        exist = s.find_all('li', class_='subject-item')
        if(exist):
            getData(exist, data)
        else:
            break
        start = start + 20

    ndata = json.dumps(data)
    writeFile(ndata, json_path)





def loopTag(x):
    global classify
    global label
    global path
    label = x['label']
    classify = x['classify']

    print('-------------------' + classify + '--------------------')
    # print(label)

    length = len(label)
    i = 1
    for item in label:
        path = classify + '/' + item['name']
        dir = path + '/img'
        j_path = path + '/' + item['name'] + '.json'
        mkdir(dir)
        name = urlDecode(item['name'])
        url = _url + name
        # print(url)
        print('-------------------' + item['name'] + '--------------------')
        loopUrl(url, j_path)


if __name__ == "__main__":
    for item in getClassify():
        loopTag(item)

