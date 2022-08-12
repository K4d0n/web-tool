import socket
import sys
import threading
import time
import argparse
server = {"ftp":21,"ssh":22,"Telnet":23,"SMTP":25,"DNS":53,"TFTP":69,"Finger":79,"http":80,"pop2":109,"pop3":110,
          "PRC":111,"Authentication Service":113,"Network News Transfer Protocol":119,"RPC":135,"netbios":137,
          "IMAP":143,"SNMP":161,"https":443,"SMB":445,"RDP":3389,"mysql":3306,"sqlserver":1433,"Tomcat":8080,"redis":6379,
          "mongodb":27017,"elasticsearch":9200
          }

def scan_port(host,port):
    count = 0
    try :
        scan = socket.socket()
        scan.settimeout(0.1)
        scan_result = scan.connect_ex((host,port))
    except socket.error as msg :
            print(msg)
            sys.exit(1)
    if scan_result == 0:
        print("[*]服务器：{0} 端口：{1}开放 >>服务:{2}".format(host,port, {k:v for k,v in server.items() if v ==port}))

        count+=1
        scan.close()

def start(host,ports):
    start_prot, end_port = ports.split('-')
    thread_list=[]
    for port in range(int(start_prot),int(end_port)):
        t = threading.Thread(target=scan_port,args=(host,port))
        thread_list.append(t)
    for thread in thread_list:
        thread.start()
    for thread2 in thread_list:
        thread2.join()


if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1')    #输入要扫描的ip地址
    parser.add_argument('--port',type=str,default='0-65535')        #输入要扫描的端口
    args = parser.parse_args()
    start_time = time.time()
    start(args.host,args.port)
    end_time = time.time()
    print(f'耗时：{end_time-start_time}')