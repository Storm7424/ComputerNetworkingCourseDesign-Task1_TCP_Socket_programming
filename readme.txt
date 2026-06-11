# Task1 TCP Socket programming

## 运行环境
- Windows 11
- Python 3.14.3

## 配置选项

### 运行

#### 服务器端
python reversetcpserver.py <端口号>
python reversetcpserver.py 8888

#### 客户端
python reversetcpclient.py <服务端IP> <端口> <文件路径> <Lmin> <Lmax> <随机种子>
例：python reversetcpclient.py localhost 8888 text.txt 50 100 36

参数说明：
- 服务器端IP：服务器端所在IP地址
- 端口：服务器端监听的端口号
- 文件路径：要发送的ASCII文本文件
- Lmin：每块的最小字节数（最后一块可能不符合）
- Lmax：每块的最大字节数
- 随机种子：用于复现分块结果

### 服务器端终止
netstat -ano | findstr 8888
taskkill /F /PID 29224