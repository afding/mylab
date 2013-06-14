#!/usr/bin/env python
# -*- coding: gbk -*-

import re
import telnetlib
import time

RET = "\n"

def loginBBS():
    user = "whille02"
    password = "whille7"
    tn = telnetlib.Telnet("bbs.newsmth.net")
    # tn.set_debuglevel(1)
    tn.read_until("���������:")
    time.sleep(1)
    tn.write(user + RET)
    tn.read_until("����������:")
    time.sleep(1)
    tn.write(password + RET)
    for i in range(3):
        tn.write(RET)
    time.sleep(3)
#     tn.write("eq")
#     print tn.read_very_eager()
    tn.read_until("S) ѡ���Ķ�������")
    time.sleep(1)
    return tn
    
def readBoard(tn):
    tn.write("s" + RET)
    tn.read_until("���������������� ")
    time.sleep(1)
    tn.write("ticket" + RET)
    tn.write("$")
    tn.read_until("[һ��ģʽ] ")
    tn.read_until("\x1b[m")
    postlist = tn.read_very_eager()
    info = search(postlist)
    if info:
        msg(tn, info)
    # unread = re.search('(\s+\d+ \* .*)', postlist)
    # if unread:
    # print unread.group()
    while re.search(' \* ', postlist):
        tn.write("P")
    postlist = tn.read_very_eager()
    info = search(postlist)
    if info:
        msg(tn, info)
    time.sleep(1)
    tn.write("$")
    tn.read_very_eager()
    time.sleep(1)
    tn.write("c")
    tn.read_very_eager()
    time.sleep(1)
    tn.write("e")
    
def search(string):
    pattern = '����'
    line = re.search(pattern, string)
    if line:
        print line.group()
    print "\a"
    title = re.search('', line.group())
    # print title.group()
    return title.group()
    return 0
    
def msg(tn, message):
    # tn.set_debuglevel(1)
    tn.write("w")
    tn.read_until("��ѶϢ��:")
    tn.write("" + RET)
    tn.read_until("�������������ݣ�Ctrl+Q ����:")
    tn.write(message)
    tn.write("" + RET)
    tn.read_until("ȷ��Ҫ�ͳ���")
    tn.write("y" + RET)
    # tn.set_debuglevel(0)
    
def logout(tn):
    tn.read_until("G) �뿪ˮľ")
    tn.write("g" + RET)
    tn.read_until("�뿪��BBSվ")
    tn.write("" + RET)
    time.sleep(1)
    tn.write("" + RET)
    tn.read_all
    tn.close()
    
def loop():
    tn = loginBBS()
    while 1:
        readBoard(tn)
        time.sleep(60)
    logout(tn)
    
if __name__ == '__main__':
    loop()
