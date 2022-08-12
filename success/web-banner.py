"""
获取网站的一些banner信息
"""
from threading import activeCount
import chardet
import requests,re
from threading import *
from sys import argv
from queue import Queue
from elasticsearch import Elasticsearch
from elasticsearch import helpers
es = Elasticsearch([{"host":"127.0.0.1","port":"9200"}],timeout=3600) #连接数据库
requests.packages.urllib3.disable_warnings()  #不显示任何requests下的urllib3的警告信息
new_targets = []
result = []
def get_banner(url):
        if 'http://' or 'https://' not in url.strip(): #判断有无协议
            target = 'http://' + url.strip()            #采用http的请求方式
        try:
            req = requests.get(target,verify=False,allow_redirects=False,timeout=(5,20))    #移除SSL认证，不允许重定向
            if 'charset' not in req.headers.get('Content-Type', " "):
                req.encoding = chardet.detect(req.content).get('encoding')  # 解决网页编码问题
            code = req.status_code
            if '30' in str(code):       #判断状态码是否为30X系列
                if req.headers['Location'] == 'https://' + target.strip('http://') + '/':
                    req_30x = requests.get('https://{}'.format(target.strip('http://')),verify=False,timeout=(5,20))    #采用https协议请求
                    code_30x = str(req_30x.status_code).strip()
                    if 'charset' not in req_30x.headers.get('Content-Type', " "):
                        req_30x.encoding = chardet.detect(req_30x.content).get('encoding')  # 解决网页编码问题
                    try:
                        title_30x = re.findall(r'<title>(.*?)</title>',req_30x.text,re.S)[0].strip()    #参试获取标题信息
                    except:
                        title_30x = 'None'
                    if 'Server' in req_30x.headers:
                        server_30x = req_30x.headers['Server'].strip()  #获取Server
                    else:
                        server_30x = ''
                    if 'Content-Type' in req_30x.headers:
                        type_30x = req_30x.headers['Content-Type'].strip()  #获取Content-Type
                    else:
                        type_30x = ''
                    if 'X-Powered-By' in req_30x.headers:   #获取X-Powered-By
                        x_powered_by_30x = req_30x.headers['X-Powered-By'].strip()
                    else:
                      x_powered_by_30x = ''
                    print('[+] {} {} {} {} {} {} '.format(code_30x,target,title_30x,server_30x,type_30x,x_powered_by_30x))
                    write_info(target,code_30x,title_30x, server_30x, type_30x,x_powered_by_30x)
                else:
                    title = '302_redirection'   #获取重定向的信息
                    location = req.headers['Location']
                    print('[+] {} {} {} Location：{}'.format(code,target,title,location))
                    write_info(target,code,title,location=location)
            else:
                try:
                    title = re.findall(r'<title>(.*?)</title>',req.text,re.S)[0].strip()
                except:
                    title = 'None'
                if 'Server' in req.headers:
                    server = req.headers['Server'].strip()
                else:
                    server = ''
                if 'Content-Type' in req.headers:
                    type = req.headers['Content-Type'].strip()
                else:
                    type = ''
                if 'X-Powered-By' in req.headers:
                    x_powered_by = req.headers['X-Powered-By'].strip()
                else:
                    x_powered_by = ''
                write_info(target,code,title,server,type,x_powered_by)
                handler(code,target,title,server,type,x_powered_by)
                print('[+] {} {} {} {} {}'.format(code,target,title,server,x_powered_by))
        except Exception as e:
            print('[-]Error {} {} '.format(target,str(e)))


def write_info(url,code,title='',server='',type='',x_power_by='',location=''):
    with open('websites_banner.txt', 'a+') as f:
        f.write('状态码：{} | 目标：{} | 标题：{} | server:{} | type:{} | x_power_by:{} \n'.format(code,url,title,server,type,x_power_by,location))

#整合数据
def handler(code,target,title,server,type,x_powered_by):
    data = [code,target,title,server,type,x_powered_by]
    action = {
        "_index": "fkd2",
        "_type": "web-banner",
        "_source": {
            "code": data[0],
            "target": data[1],
            "title": data[2],
            "server" : data[3],
            "type" : data[4],
            "x_powered_by" : data[5],
        }
    }
    result.append(action)
    return True

#将数据存储到数据库

def elasticsearch_push(data):
    a = helpers.bulk(es,data)
    return True




if __name__ == '__main__':
    try:
        queue = Queue()     #线程安全的队列，采用first in first out的模式
        filename = argv[1]
        new_filename = argv[2]
        with open(filename,'r+') as f:
            for url in f:
                url = url.strip()
                if url not in new_targets:
                    new_targets.append(url)
        for new_url  in new_targets:
            queue.put(new_url)
            with open(new_filename,'a+') as f:
                f.write(new_url + '\n')
        while queue.qsize() > 0:
            if activeCount() <= 10:
                Thread(target=get_banner, args=(queue.get(),)).start()
        try:
            elasticsearch_push(result)
            print("es数据库存储成功")
        except Exception as e:
            print(e)
    except IndexError:
        print('Usage：python3 get_banner.py urls.txt new_urls.txt')