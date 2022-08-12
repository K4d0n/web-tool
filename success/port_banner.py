"""
简单的端口扫描，可收集一些端口的banner信息，同时可以探测网站的存活
"""

import socket
import select
import sys
import argparse
import threading


def getbanner(host,port):

    try:
        con =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        con.connect((host,port))
        ready =select.select([con],[],[],3)
        if ready[0]:
            print(str(port))
            print(con.recv(4096))
            con.close()
    except socket.error as msg:
          pass
def start(host,ports):
    start_prot, end_port = ports.split('-')
    thread_list = []
    for port in range(int(start_prot),int(end_port)):
        t = threading.Thread(target=getbanner,args=(host,port))
        thread_list.append(t)
    for thread in thread_list:
        thread.start()
    for thread2 in thread_list:
        thread2.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',type=str,default='127.0.0.1')
    parser.add_argument('--port',type=str,default='0-10000')
    agrs = parser.parse_args()
    start(agrs.host,agrs.port)

