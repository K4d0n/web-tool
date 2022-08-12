"""
    简单子域名爆破demo
                    """
import socket
import threading
import time
import argparse
from elasticsearch import Elasticsearch
from elasticsearch import helpers
sub_domain_filename = 'sub_domain'
all = []
# DNS解析
es = Elasticsearch([{"host":"127.0.0.1","port":"9200"}],timeout=3600)

def domainToip(domain):
    iplist = []
    try:
        results = socket.getaddrinfo(domain , None)
        for item in results:
            iplist.append(item[4][0])
    except Exception as e:
        pass
    return iplist

# 读取子域名字典
def readSubDomainList():
    subDomainList = []
    try:
        file = open(sub_domain_filename, 'r')
        for line in file:
            subDomainList.append(line[:-1])
            # 这里切片的作用是去掉换行
        file.close()
    except Exception as e:
        print(e)
    return subDomainList

# 拼接子域名
def splitSubDomain(domain,subDomainList):
    subDomains = []
    for item in subDomainList:
        subDomains.append(item + '.' + domain)
    return subDomains

# 子域名挖掘主函数
def subDominMining(domain):
    accessible = []
    subDomainList = readSubDomainList()
    subDomains = splitSubDomain(domain,subDomainList)
    for item in subDomains:
        subDomain = {}
        iplist = domainToip(item)
        if len(iplist) > 0:
            subDomain['domain'] = item
            subDomain['iplist'] = iplist
            # 判断是否可能存在CDN
            subDomain['isCDN'] = 'False'
            flag = 'False'
            if len(iplist) > 1:
                subDomain['isCDN'] = 'True'
                flag = 'True'
            elasticserarch_store(item, iplist, flag)
            accessible.append(subDomain)

    for items in accessible:
        print(items)
    try:
        elasticserach_push(all)
        print("es数据存储成功")

    except:
        print("es数据存储失败")
    end_time = time.time()
    print("用时：" + str(end_time - star_time))
    return accessible

#数据整合
def elasticserarch_store(item,iplist,cdn):
    data = []
    data.append(item)
    data.append(iplist)
    data.append(cdn)
    action = {
        "_index" : "fkd",
        "_type" : "domain",
        "_source":{
            "domainname" : data[0],
            "iplist" : data[1],
            "iscdn" : data[2],
        }
    }
    all.append(action)
    return True
#数据提交
def elasticserach_push(data):
    a = helpers.bulk(es,data)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain',type=str,default='baidu.com') #输入要扫描的域名
    args = parser.parse_args()
    domain = args.domain
    star_time = time.time()
    t = threading.Thread(target=subDominMining, args=(domain,))
    t.start()

