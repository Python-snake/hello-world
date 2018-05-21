# -*- coding:utf-8 -*-
# @Author: zy
# @Time: 2018/5/15 19:21
# @说明:实现简单网页操作
# -*-encoding:utf-8 -*-
import socket
import multiprocessing
import re
# import dynamic.mini_frame
import sys


class WebServer(object):
    # def __init__(self, port, app, static_path, templates_path):
    def __init__(self, port, app, static_path):
        # 初始化对象属性
        # 创建tcp套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置超时关闭响应
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定本地地址
        self.server_socket.bind(("", port))
        # 设置监听
        self.server_socket.listen()
        # 接收框架函数
        self.app = app
        # 接收路径
        self.static_path = static_path
        # self.templates_path = templates_path

    def server_client(self, new_socket):
        # 为客户端发送信息
        request = new_socket.recv(1024).decode("utf-8")
        print(request)
        # 使用splitlines()切割字符串
        request_lines = request.splitlines()
        # 使用正则匹配
        file_name = ""
        res = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        # print(res)
        if res:
            file_name = res.group(1)
            if file_name == "/":
                file_name += "index.html"
                # print("1111{}1111".format(file_name))
        if not file_name.endswith(".html"):
            try:
                # if file_name.endswith(".html"):
                #     f = open(self.templates_path + file_name, "rb")
                # else:
                f = open(self.static_path + file_name, "rb")
            except Exception as res:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "------file not found-----"
                new_socket.send(response.encode("utf-8"))
            else:
                html_content = f.read()
                f.close()
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 2.2 准备发送给浏览器的数据---boy
                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                new_socket.send(html_content)
        else:
            env = dict()
            env['PATH_INFO'] = file_name
            # 要导入框架函数
            body = self.app(env, self.set_response_header)
            header = "HTTP/1.1 %s\r\n" % self.status
            for temp in self.headers:
                header += "%s:%s\r\n" % (temp[0], temp[1])
            header += "\r\n"
            response = header + body
            # 发送response给浏览器
            new_socket.send(response.encode("utf-8"))
        # 关闭套接字
        new_socket.close()

    def set_response_header(self, status, headers):
        # 生成headers
        self.status = status
        self.headers = [("server", "mini_web v8.8")]
        self.headers += headers

    def run(self):
        # 控制整体布局
        # 不断响应用户
        while True:
            # 等待用户响应
            new_socket, add = self.server_socket.accept()
            # 使用进程multiprocessing为客户端服务
            p = multiprocessing.Process(target=self.server_client, args=(new_socket,))
            p.start()
            # 关闭子进程套接字
            new_socket.close()
        # 关闭主进程套解字
        self.server_socket.close()


def main():
    # 编写服务器
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[1])  # 7890
            frame_app_name = sys.argv[2]  # mini_frame:application
        except Exception as ret:
            print("端口输入错误。。。。。")
            return
    else:
        print("请按照以下方式运行:")
        print("python3 xxxx.py 7890 mini_frame:application")
        return
    # port = 7890
    # frame_app_name = "mini_frame:application"
    # mini_frame:application
    ret = re.match(r"([^:]+):(.*)", frame_app_name)
    if ret:
        frame_name = ret.group(1)  # mini_frame
        app_name = ret.group(2)  # application
    else:
        print("请按照以下方式运行:")
        print("python3 xxxx.py 7890 mini_frame:application")
        return
    with open("./web_server.conf") as f:
        conf_info = eval(f.read())
    # 此时 conf_info是一个字典里面的数据为：
    # {
    #     "static_path":"./static",
    #     "dynamic_path":"./dynamic",
    #      "templates_path":"./templates"
    # }
    sys.path.append(conf_info['dynamic_path'])
    # import frame_name --->找frame_name.py
    frame = __import__(frame_name)  # 返回值标记这 导入的这个模板
    app = getattr(frame, app_name)  # 此时app就指向了 dynamic/mini_frame模块中的application这个函数
    # 创建实例对象
    # web_server = WebServer(port, app, conf_info["static_path"], conf_info["templates_path"])
    web_server = WebServer(port, app, conf_info["static_path"])
    # 调用run方法
    web_server.run()


if __name__ == "__main__":
    main()
