from datetime import datetime
import os
import random
import socket
import struct
import sys

# log recording
def log(content):
    try:
        with open("run_log.txt","a") as run_log:
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            run_log.write("【"+timestamp+"】Client-"+str(os.getpid())+": "+content+"\n")
    except:
        print("日志记录失败")

# 逐个读取命令行参数
if(len(sys.argv)!=7):
    print("命令行参数个数错误")
    sys.exit(1)
try:
    serverIP=sys.argv[1]
    serverPort=int(sys.argv[2])
    path=sys.argv[3]
    Lmin=int(sys.argv[4])
    Lmax=int(sys.argv[5])
    chunk_seed=int(sys.argv[6])
except:
    print("读命令行参数失败")
    sys.exit(1)
if(Lmin<0 or Lmax<=0 or Lmin>Lmax):
    print("Lmin、Lmax值不合法")
    sys.exit(1)

# reading file
try:
    with open(path,'r') as text:
        content=text.read()
except:
    print("读文件失败")
    sys.exit(1)

# generate the length of each block
random.seed(chunk_seed)
blocks=[]
while(sum(blocks)!=len(content)):
    if(len(content)-sum(blocks)>=Lmax):
        cur=random.randint(Lmin,Lmax)
        blocks.append(cur)
    else:
        blocks.append(len(content)-sum(blocks))
N=len(blocks)
print(f"共{N}块，各块大小分别为{blocks}")

# 建立TCP连接
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((serverIP, serverPort))
    log("正在建立连接")
except:
    print(f"连接服务器失败")
    log("建立连接失败")
    sock.close()
    sys.exit(1)

# Initialization
try:
    log(f"发送Initialization报文，Type=1，N={N}")
    sock.sendall(struct.pack("!hi", 1, N))
except:
    print("Initializaion报文发送失败")
    log("发送Initialization报文失败")
    sock.close()
    sys.exit(1)

# agree
try:
    agree_message=sock.recv(2)
    if(len(agree_message)<2):
        raise RuntimeError
    receive_message,=struct.unpack("!h", agree_message)
    log("接收agree报文，Type=2")
    if(receive_message!=2):
        raise RuntimeError
except:
    print("初始化连接失败")
    log("接收agree报文失败")
    sock.close()
    sys.exit(1)

# reverseRequest and reverseAnswer
reversedtext=""
curpos=0
for i in range(N):
    try:
        size=blocks[i]
        data=content[curpos:curpos+size]
        # print(data)
        curpos+=size
        log(f"发送第{i+1}个reverseRequest报文，Type=3，长度为{size}，数据为{data}")
        sock.sendall(struct.pack("!hi", 3, size) + data.encode())
        answer_message=sock.recv(6)
        # log(f"接收第{i+1}个reverseAnswer报文的前6个字节")
        if(len(answer_message)<6):
            raise RuntimeError
        state,length=struct.unpack("!hi", answer_message)
        if(state!=4):
            raise RuntimeError
        # reverseddata=sock.recv(length).decode()
        rev_bytes=b''
        while len(rev_bytes)<length:
            chunk=sock.recv(length-len(rev_bytes))
            # log(f"接收第{i+1}个reverseAnswer报文的{length-len(rev_bytes)}个字节")
            if not chunk:
                raise RuntimeError
            rev_bytes+=chunk
        reverseddata=rev_bytes.decode()
        log(f"接收第{i+1}个reverseAnswer报文，Type=4，长度为{length}，数据为{reverseddata}")
        print(f"{i+1}: {reverseddata}")
        reversedtext=reverseddata+reversedtext
    except:
        print(f"处理第{i+1}块时发生错误")
        log(f"处理第{i+1}块时发生错误")
        sock.close()
        sys.exit(1)

sock.close()

# reverse的结果写入文件
try:
    with open("reversedVersion_"+path,'w') as output:
        output.write(reversedtext)
except:
    print("写入文件失败")
    sock.close()
    sys.exit(1)