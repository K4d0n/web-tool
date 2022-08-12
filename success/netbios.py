import os
import re
import threading
print('扫描开始')
print('请等待不要着急...........')
result = os.popen("route print").read()   #打开路由表
ip = re.search(r"0.0.0.0\s+0.0.0.0\s+\S+\s+(\S+)",result).group(1)  #选取当前上网的ip
print("[*]当前IP为："+ip)
net = re.findall(r"(\d+\.\d+\.\d+\.)\d+",ip)[0]    #截取网段
print("[*]所在网段："+net)
j = []  #存放结果
def task(cmd,newip):    #获取netbios信息
    r=os.popen(cmd).read()
    if "<00>" in r:
        r1 = re.findall(r"(\S+.+)<00>",r)    #截取主机名和工作组
        r2 = re.findall(r"\w{2}-\w{2}-\w{2}-\w{2}-\w{2}-\w{2}",r)
        r1.append(r2[0])
        r1.append(newip)
        j.append(r1)
pool=[]
for i in range(1,255):
    newip = net+str(i)
    cmd = f"nbtstat -a {newip}"   #扫描网段
    t = threading.Thread(target=task,args=(cmd,newip))
    pool.append(t)
    t.start()
for t in pool:
    t.join()
for i in j:
    hostname = i[0]
    workgroup = i[1]
    MAC = i[2]
    Remote_IP = i[3]
    print(f"[*]IP：{Remote_IP}  主机名：{hostname}  工作组：{workgroup} MAC:{MAC}")
print("---结束---")

