from datetime import datetime
import socket
import struct
import sys
import threading

# log recording
def log(address,content):
    try:
        with open("run_log.txt","a") as run_log:
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            run_log.write("【"+timestamp+"】Server["+str(address)+"]: "+content+"\n")
    except:
        print("日志记录失败")

# 对单个线程的处理
def cope(client,address):
    try:
        # Initialization
        init_message=client.recv(6)
        if(len(init_message)<6):
            raise RuntimeError
        state,N=struct.unpack("!hi",init_message)
        log(address,f"接收Initialization报文，Type=1，N={N}")
        if(state!=1):
            raise RuntimeError
        # agree
        log(address,"发送agree报文，Type=2")
        client.sendall(struct.pack("!h",2))

        # reverseRequest and reverseAnswer
        for i in range(N):
            request_message=client.recv(6)
            # log(f"接收第{i+1}个reverseRequest报文的前6个字节")
            if(len(request_message)<6):
                raise RuntimeError
            state,length=struct.unpack("!hi",request_message)
            if(state!=3):
                raise RuntimeError
            # data=client.recv(length).decode()
            data_bytes=b''
            while len(data_bytes)<length:
                chunk=client.recv(length-len(data_bytes))
                # log(f"接收第{i+1}个reverseRequest报文的{length-len(data_bytes)}个字节")
                if not chunk:
                    raise RuntimeError
                data_bytes+=chunk
            data=data_bytes.decode()
            log(address,f"接收第{i+1}个reverseRequest报文，Type=3，长度为{length}，数据为{data}")
            data=data[::-1]
            log(address,f"发送第{i+1}个reverseAnswer报文，Type=4，长度为{length}，数据为{data}")
            client.sendall(struct.pack("!hi",4,length)+data.encode())
    except:
        print(f"与{address}通信时出错")
        log(address,f"与{address}通信时出错")
    finally:
        client.close()

# 读取命令行参数
if(len(sys.argv)!=2):
    print("命令行参数个数错误")
    sys.exit(1)
try:
    port=int(sys.argv[1])
except:
    print("读命令行参数失败")
    sys.exit(1)

# startover the server
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(("0.0.0.0",port))
    sock.listen()
except:
    print("启动服务失败")
    sock.close()
    sys.exit(1)

while (True):
    try:
        client,address=sock.accept()
        thread=threading.Thread(target=cope,args=(client,address))
        thread.start()
    except:
        print("连接失败")