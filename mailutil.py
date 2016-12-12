# -*- coding: utf-8 -*-
import sys
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


class SMTP_SSL(smtplib.SMTP):
    def __init__(self, host=''):
        self.host = host

    def SendHTML(self,account,passwd,fromAdd,toList,ccList,subject,content):
        msg = Message()
        msg['Mime-Version']='1.0'
        msg['Content-Type']='text/html;charset=UTF-8'
        msg['From'] = fromAdd
        msg['To'] = toList
        msg['CC'] = ccList
        msg['Subject'] = subject
        msg['Date']    = email.Utils.formatdate()
        msg.set_payload(content)
        smtp = smtplib.SMTP(host=self.host, port=25)
        smtp.login(account, passwd)
        smtp.sendmail(fromAdd, toList.split(',')+ccList.split(','), msg.as_string())
        smtp.quit()
    def SendMail(self,account,passwd,fromAdd,toList,ccList,msgRoot):
        msgRoot['From'] = fromAdd
        smtp = smtplib.SMTP(host=self.host, port=25)
        smtp.login(account, passwd)
        smtp.sendmail(fromAdd, toList.split(',')+ccList.split(','), msgRoot.as_string())
        smtp.quit()

def send_orignal_mail(msg,mail_to="mingchao.xiamc@"):
    mail_from = ""
    mail_passwd = ""
    mail_cc = "mingchao.xiamc@"
    emailSender = SMTP_SSL('smtp-inc.*.com')
    emailSender.SendMail(mail_from, mail_passwd, mail_from,mail_to, mail_cc,msg)

def send_mail(mtitle,mcontent,mail_to):
    mail_from = ""
    mail_passwd = ""
    mail_to = "mingchao.xiamc"
    mail_cc = "mingchao.xiamc"
    emailSender = SMTP_SSL('smtp-inc.*.com')
    emailSender.SendHTML(mail_from, mail_passwd, mail_from, mail_to, mail_cc,mtitle, mcontent)

def genCHTML(mjson):
    retstr=u'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"><html lang="zh-cn"> \
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bootstrap 101 Template</title>
    <link href="//cdn.bootcss.com/bootstrap/3.3.5/css/bootstrap.min.css" rel="stylesheet">
  </head>'''
    url=mjson['url']
    retstr=retstr+u'''<!-- jQuery (necessary for Bootstrap's JavaScript plugins) --> \
    <script src="//cdn.bootcss.com/jquery/1.11.3/jquery.min.js"></script>  \
    <script src="//cdn.bootcss.com/bootstrap/3.3.5/js/bootstrap.min.js"></script> \
<table class="display"><thead></thead><tbody><tr>您所负责的测试模块未通过，请尽快到 <a href='''+url+u'''>testmen</a> 中确认</tr>'''
    for k in mjson:
        if k=="url":
            continue
        retstr=retstr+"<tr><td>"+mjson[k]+"</td><td>"+k+"</td></tr>"
    retstr=retstr+"</tbody></table></html>"
    return retstr

def sendjson(mcontent,mail_to):
    outfp=open("./sendmail.log","w")   
    outfp.write(mcontent)
    mjson=json.loads("".join(open(mcontent,"r").readlines()))
    outfp.write("url:"+mjson["url"])
    print("url:"+mjson["url"])
    outfp.close()
    mail_to="mingchao.xiamc@"
    mcontent=genCHTML(mjson)
    sendMail(mtitle,mcontent,mail_to)
    sys.exit(0)

def main():
    if len(sys.argv) !=4 :
        print("length:"+str(len(sys.argv))+" not 4,mtitle mcontent mail_to ,exit")
        sys.exit(1)
    mtitle=sys.argv[1]
    mcontent="".join(open(sys.argv[2],"r").readlines())
    mail_to=sys.argv[3]
    sendMail(mtitle,mcontent,mail_to)

if __name__ == '__main__':
    if len(sys.argv) !=4 :
        print("length:"+str(len(sys.argv))+" not 4,exit")
        sys.exit(1)
    mtitle=sys.argv[1]
    mcontent="".join(open(sys.argv[2],"r").readlines())
    mail_to=sys.argv[3]
    send_mail(mtitle,mcontent,mail_to)
