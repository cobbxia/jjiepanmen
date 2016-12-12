# -*- coding: utf-8 -*-
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("./pkg")
sys.path.append("./pkg/jenkinsapi")
sys.path.append("./pkg/pytz")
sys.path.append("./pkg/requests")
import jenkinsapi
from jenkinsapi.jenkins import Jenkins
import jenkins
import common
import cfg

def getJenkinsFromFile(m2jfile,mname):
    if not os.path.exists(m2jfile):
        return ""
    for line in open(m2jfile,"r"):
        line=line.strip("\n")
        if  line == "" : continue
        kmname      =line.split(":")[0]
        jenkinsname=line.split(":")[1]
        if kmname== mname:
            return jenkinsname           

def detect_reg(gname,mname):
    jenkinsList=[]
    m2jfile=""
    jenkinsname = ""
    if gname.lower() == "5ktest":
        gname="5k"
        m2jfile="5ktest_module2jenkins.txt"
    else:
        m2jfile="%s_module2jenkins.txt" % (gname)
    print("m2jfile:%s" % (m2jfile))
    print("gname:%s mname:%s m2jfile:%s" % (gname,mname,m2jfile))
    if  m2jfile != "":
        jenkinsname=getJenkinsFromFile(m2jfile,mname)
    if jenkinsname != "":
        return jenkinsname
    for line in open(cfg.jenkinsName,"r"):
        line=line.strip("\n")
        if line == "" or line is None:
            continue
        if line.lower().find(gname.lower()) >= 0 and line.lower().find(mname.lower())>=0:
            jenkinsList.append(line)
    if len(jenkinsList) ==0:
        print("mname:%s jenkinsList is 0" % (mname))
        return 
    if cfg.debug ==True:
        print(jenkinsList)
    jenkinsname=jenkinsList[0]
    if len(jenkinsList) > 1:
        for jk in jenkinsList:
            if jk.lower().find("outman") >=0:
                jenkinsname=jk
    print(jenkinsname)
    return jenkinsname
