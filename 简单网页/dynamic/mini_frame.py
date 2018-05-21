# -*-encoding:utf-8 -*-
import re
from pymysql import connect
import urllib.parse
import logging

# 文件路径以及函数应用
URL_FUNC_DICT = dict()
templates = "./templates"


def link_sql(sql):
    conn = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_info', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    cs.execute(sql)
    stock_infos = cs.fetchall()
    cs.close()
    conn.close()
    return stock_infos


def route(file_name):
    def set_func(func, *args, **kwargs):
        URL_FUNC_DICT[file_name] = func

        def call_func(func, *args, **kwargs):
            return func

        return call_func

    return set_func


@route(r"/add/(\d+)\.html")
def add_info(file_name, temp):
    """实现数据的添加功能"""
    stock_code = temp.group(1)
    conn = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_info', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    # 查询数据表info中是否存在
    sql = "select * from info where code = %s;"
    cs.execute(sql, stock_code)
    if cs.fetchone():
        # 查询是否已经添加
        sql = "select * from V_masg where code = %s;"
        cs.execute(sql, stock_code)
        if not cs.fetchone():
            # 向数据库中添加股票
            sql = """insert into focus (info_id) select id from info where code=%s;"""
            cs.execute(sql, stock_code)
            conn.commit()
            cs.close()
            conn.close()
            return "添加成功！"
    cs.close()
    conn.close()
    return "你已经关注了！"


@route(r"/del/(\d+)\.html")
def del_info(file_name, temp):
    """删除功能"""
    stock_code = temp.group(1)
    conn = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_info', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    # 查询数据表info中是否存在
    sql = "select * from info where code = %s;"
    cs.execute(sql, stock_code)

    if cs.fetchone():
        # 查询是否已经添加
        sql = "select * from V_masg where code = %s;"
        cs.execute(sql, stock_code)
        if cs.fetchone():
            # 向数据库中删除股票
            sql = """delete from focus where info_id = (select id from info where code =%s);"""
            cs.execute(sql, stock_code)
            conn.commit()
            cs.close()
            conn.close()
            return "删除成功！"
    cs.close()
    conn.close()
    return "你还没有关注！"


@route(r"/(update)/(\d+)\.html")
def update(file_name, temp):
    """更新数据"""
    file_name = temp.group(1)
    stock_code = temp.group(2)
    try:
        f = open(templates + "/" + file_name + ".html", "rb")
    except Exception as res:
        print(res)
        return res
    else:
        content = f.read().decode("utf-8")
        f.close()
        conn = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_info',
                       charset='utf8')
        cs = conn.cursor()
        sql = """select f.note_info from focus as f inner join info as i on i.id=f.info_id where i.code=%s;"""
        cs.execute(sql, (stock_code,))
        stock_infos = cs.fetchone()
        note_info = stock_infos[0]  # 获取这个股票对应的备注信息
        cs.close()
        conn.close()

        content = re.sub(r"\{%note_info%\}", note_info, content)
        content = re.sub(r"\{%code%\}", stock_code, content)

        return content


@route(r"/update/(\d+)/(.*).html")
def Update_info(file_name, temp):
    stock_code = temp.group(1)
    comment = temp.group(2)
    comment = urllib.parse.unquote(comment)
    conn = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_info', charset='utf8')
    cs = conn.cursor()
    sql = """update focus set note_info=%s where info_id = (select id from info where code=%s);"""
    cs.execute(sql, (comment, stock_code))
    conn.commit()
    cs.close()
    conn.close()

    return "修改成功..."


@route(r"/index.html")
def index(file_name, temp):
    """首页"""
    try:
        f = open(templates + file_name, "rb")
    except Exception as res:
        return res
    else:
        content = f.read().decode("utf-8")
        f.close()
        sql = "select * from info;"
        my_stock_info = link_sql(sql)
        tr_template = """<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
                </td>
                </tr>
            """
        html = ""
        for line_info in my_stock_info:
            html += tr_template % (
                line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6],
                line_info[7], line_info[1])

        content = re.sub(r"\{%content%\}", html, content)
        print(connect)
        return content


@route(r'/center.html')
def center(file_name, temp):
    try:
        f = open(templates + file_name, "rb")
    except Exception as res:
        return res
    else:
        content = f.read().decode("utf-8")
        f.close()
        sql = "select * from V_masg;"
        my_stock_info = link_sql(sql)
        tr_template = """
                <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>
                        <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                    </td>
                    <td>
                        <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
                    </td>
                </tr>
            """

        html = ""
        for line_info in my_stock_info:
            html += tr_template % (
                line_info[0],
                line_info[1],
                line_info[2],
                line_info[3],
                line_info[4],
                line_info[5],
                line_info[6],
                line_info[0],
                line_info[0])

        content = re.sub(r"\{%content%\}", html, content)
        return content


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])

    file_name = env['PATH_INFO']
    # file_name = "/index.py"

    # if file_name == "/index.py":
    #     return index()
    # elif file_name == "/center.py":
    #     return center()
    # else:
    #     return 'Hello World! 我爱你中国....'
    logging.basicConfig(level=logging.INFO,
                        filename='./log.txt',
                        filemode='a',
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    logging.info(("访问的是，.....%s" % file_name))
    try:
        for url, func in URL_FUNC_DICT.items():
            temp = re.match(url, file_name)
            if temp:
                return func(file_name, temp)
    except Exception as res:
        return "产生了异常：%s" % res
