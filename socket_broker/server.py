#!/usr/bin/python
#-*- coding:utf-8 -*-

import socket
import logging, logging.handlers
import select, errno
import requests

from event_process import ingress
#from parkhero.conf import BASE_URL

logger = logging.getLogger("network-server")

SERVER_IP = "120.24.249.69"
BASE_URL="http://"+SERVER_IP+"/parkhero/"
back_end = BASE_URL+"v0.1/"
operation_url = back_end + 'operation/'

RECV_BUFFER = 4096
    
def InitLog():
    LOG_FILE = "../log/network-server.log"
    logger.setLevel(logging.DEBUG)
    
    #fh = logging.FileHandler("network-server.log")
    fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 20*1024*1024, backupCount = 10)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
        
        
if __name__ == "__main__":
    InitLog()

    try:
        # 创建 TCP socket 作为监听 socket
        listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as msg:
        logger.error("create socket failed")

    try:
        # 设置 SO_REUSEADDR 选项
        listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as msg:
        logger.error("setsocketopt SO_REUSEADDR failed")

    try:
        # 进行 bind -- 此处未指定 ip 地址，即 bind 了全部网卡 ip 上
        listen_fd.bind(('', 2003))
    except socket.error as msg:
        logger.error("bind failed")

    try:
        # 设置 listen 的 backlog 数
        listen_fd.listen(10)
    except socket.error as msg:
        logger.error(msg)
    
    try:
        # 创建 epoll 句柄
        epoll_fd = select.epoll()
        # 向 epoll 句柄中注册 监听 socket 的 可读 事件
        epoll_fd.register(listen_fd.fileno(), select.EPOLLIN)
    except select.error as msg:
        logger.error(msg)
        
    connections = {}
    addresses = {}
    datalist = {}
    # entrance to fd
    gates = {}

    while True:
        # epoll all fds
        epoll_list = epoll_fd.poll()

        for fd, events in epoll_list:
            # 若为监听 fd 被激活
            if fd == listen_fd.fileno():
                # 进行 accept -- 获得连接上来 client 的 ip 和 port，以及 socket 句柄
                conn, addr = listen_fd.accept()
                logger.debug("accept connection from %s, %d, fd = %d" % (addr[0], addr[1], conn.fileno()))
                # 将连接 socket 设置为 非阻塞
                conn.setblocking(0)
                # 向 epoll 句柄中注册 连接 socket 的 可读 事件
                epoll_fd.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
                # 将 conn 和 addr 信息分别保存起来
                connections[conn.fileno()] = conn
                addresses[conn.fileno()] = addr
            elif select.EPOLLIN & events:
                # polling events EPOLLIN
                datas = ''.encode('utf-8')
                while True:
                    try:
                        # receive bytes from connected fd
                        data = connections[fd].recv(RECV_BUFFER)
                        # no data received
                        if not data and not datas:
                            # remove the fd from epoll list
                            epoll_fd.unregister(fd)
                            # server closes the fd
                            connections[fd].close()
                            logger.debug("%s, %d closed" % (addresses[fd][0], addresses[fd][1]))
                            # let backend server konw this disconnection
                            content = {}
                            headers = {'application': 'json; charset=UTF-8'}
                            content['ip_address'] = addresses[fd][0]
                            try:
                                response = requests.post(operation_url + 'parkinglot_disconnected/', headers=headers, json=content)
                            except Exception as e:
                                logger.error('Error occurred when sending disconnection info to server, info[%s]' % str(e))
                            break
                        else:
                            # data received
                            #datas += str(data)

                            #datas = data
                            #datas = 'test'.encode('utf-8')
                            #print(data.decode('utf-8'))
                            gate_id = int.from_bytes(data[0:8], byteorder='little', signed=False)
                            #print(addresses[fd][0])
                            if addresses[fd][0] == '127.0.0.1':
                                try:
                                    gate_fd = gates[gate_id]
                                # from back-end
                                    datalist[gates[gate_id]] = data
                                except KeyError:
                                    logger.error('There is NO connection to this parking lot[%d]' % gate_id)
                                #print(type(data))
                                #datas = ''.encode('utf-8')
                            else:
                                ret, result = ingress(data, addresses[fd][0])
                            #print('buffer types')
                            #print(type(result))
                                if ret:
                                    datas = result
                                    gates[gate_id] = fd
                                else:
                                    connections[fd].close()
                            #print(type(data))
                            #datas = data

                    except socket.error as msg:
                        # 在 非阻塞 socket 上进行 recv 需要处理 读穿 的情况
                        # 这里实际上是利用 读穿 出 异常 的方式跳到这里进行后续处理
                        #print('no more data received.')
                        if msg.errno == errno.EAGAIN:
                            logger.debug("%s receive %s" % (fd, datas))
                            # store the data
                            datalist[fd] = datas
                            # modify eopll events
                            if addresses[fd][0] == '127.0.0.1':
                                # from back-end
                                try:
                                    gate_fd = gates[gate_id]

                                    epoll_fd.modify(gates[gate_id], select.EPOLLET | select.EPOLLOUT)
                                except KeyError:
                                    logger.error('There is NO connection to this parking-lot[%d]' % gate_id)

                            else:
                                epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)
                            break
                        else:
                            # error processing
                            epoll_fd.unregister(fd)
                            connections[fd].close()
                            logger.error(msg)
                            # let backend server konw this disconnection
                            content = {}
                            headers = {'application': 'json; charset=UTF-8'}
                            content['ip_address'] = addresses[fd][0]
                            try:
                                response = requests.post(operation_url + 'parkinglot_disconnected/', headers=headers, json=content)
                            except Exception as e:
                                logger.error('Error occurred when sending disconnection info to server, info[%s]' % str(e))

                            break
            elif select.EPOLLHUP & events:
                # 有 HUP 事件激活
                epoll_fd.unregister(fd)
                connections[fd].close()
                logger.debug("%s, %d closed" % (addresses[fd][0], addresses[fd][1]))
                # let backend server konw this disconnection
                content = {}
                headers = {'application': 'json; charset=UTF-8'}
                content['ip_address'] = addresses[fd][0]
                try:
                    response = requests.post(operation_url + 'parkinglot_disconnected/', headers=headers, json=content)
                except Exception as e:
                    logger.error('Error occurred when sending disconnection info to server, info[%s]' % str(e))

            elif select.EPOLLOUT & events:
                # 有 可写 事件激活
                logger.debug(datalist[fd])
                sendLen = 0
                if datalist[fd]:
                # 通过 while 循环确保将 buf 中的数据全部发送出去
                    while True:
                        # 将之前收到的数据发回 client -- 通过 sendLen 来控制发送位置

                        #sendLen += connections[fd].send((datalist[fd][sendLen:]).encode('utf-8'))
                        sendLen += connections[fd].send(datalist[fd][sendLen:])

                        # 在全部发送完毕后退出 while 循环
                        if sendLen == len(datalist[fd]):
                            break
                # 更新 epoll 句柄中连接 fd 注册事件为 可读
                epoll_fd.modify(fd, select.EPOLLIN | select.EPOLLET)
            else:
                # 其他 epoll 事件不进行处理
                continue
