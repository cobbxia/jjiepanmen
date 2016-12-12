# -*- coding: utf-8 -*-
import sys
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../")
import json
import re
import os
import smtplib
import email
import datetime
from email.Message import Message
import logging
import cgi
import time
from mailutil import send_mail
import smtplib  
from email.mime.text import MIMEText  
import common ,cfg 


def send_html_mail(mtitle,mcontent,to_list):  #to_list：收件人；sub：主题；content：邮件内容
    msg = Message()
   # msg['Mime-Version']='1.0'
   # msg['Content-Type']='text/html;charset=UTF-8'
   # msg['Subject'] = mtitle
   # msg['Date']    = email.Utils.formatdate()
    msg.set_payload(mcontent)
    send_mail(mtitle,msg.as_string(),to_list)


def test_mail(mtitle,mcontent):
    mcontent="<html><head></head><body>"+mcontent+"</body></html>"
    mail_to="mingchao.xiamc"
    print(mcontent)
    send_html_mail(mtitle,mcontent,mail_to)

def dailyReport(groupname):
    try:
        today=common.getToday()
        groupId=(str)(cfg.group_id_dict[groupname])
        (stime,etime,totalnum,failnum) = common.getdailyrunStatByToday(today, groupId)
        duringhours=0
        duringmins=0
        duringhours=etime.split()[1].split(":")[0]
        duringmins=etime.split()[1].split(":")[1]
        moduleList=common.getTotalModule(groupname)
        unrunedModuleList=common.getUnrunedModule(groupId,moduleList,today)
        mtitle="NewDaily(%s)回归日报" % (today)
        mcontent='''<h1>详情请查看<a href="%s">testmen</a>和<a href="%s">帮助文档</a></H1>''' % (cfg.testmen_url,cfg.help_url)
        mcontent=mcontent+'''<H1>一、Daily质量报告</h1>
开始时间: %s  结束时间: %s  整体运行%s小时%s分钟
case数目: %s 失败个数: %s ，昨天69个，与昨天相同
回归集合：共%d个，未执行回归%d个数:%s ''' % (stime,etime,duringhours,duringmins,totalnum,failnum,len(moduleList),len(unrunedModuleList),",".join([mname for mname in unrunedModuleList]))
        test_mail(mtitle,mcontent)
        print("send mail title:%s over" % (mtitle))
    except Exception,e:
        print e

if __name__ == '__main__':
    dailyReport("newdailyrun")
    #send_mail(mtitle,mcontent,mail_to)
