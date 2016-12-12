# -*- coding: utf-8 -*-
import sys
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
from util import detect_reg,getJenkinsFromFile

def chlink(jobname):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    
def get_jenkinsname(gname,mname):
    jenkinsname=detect_reg(gname,mname)
 
def initCodeModule():
    for line in open("./codeModule.txt","r"):   
        line=line.strip("\n")
        if line == "" : continue
        codeModuleName=line.split()[0]
        owners=line.split()[1].split("\\")
        owner1=""
        owner2=""
        if len(owners) == 2:
            owner1=owners[0]
            owner2=owners[1]
        elif len(owners) == 1:
            owner1=owners[0]
        query='''INSERT INTO `codemodule`(id,  name,owner1,owner2,modules,extend) values(NULL,"%s","%s","%s",NULL,NULL);'''% (codeModuleName,owner1,owner2)
        print(query)
        common.exec_query(query)

def updateModule():   
    for line in open("./codeModule.txt","r"):   
        line=line.strip("\n")
        if line == "" : continue
        codeModuleName=line.split()[0]
        query='''SELECT name,owner1,owner2,modules FROM `codemodule` WHERE name="%s";''' % (codeModuleName) 
        (name,owner1,owner2,modules)=("","","","")
        (name,owner1,owner2,modules)=common.exec_query(query).rstrip("\n").split("\t")
        if owner2 == "": 
            owner2=owner1
        for mname in modules.split(","):
            mquery='''SELECT comment FROM `module` WHERE name="%s" ''' % (mname)
            comment=common.exec_query(mquery)
            comment="%s/%s/%s" % (codeModuleName,owner1,owner2)
            cntQuery='''SELECT COUNT(1) FROM `module` WHERE name="%s" ''' % (mname)
            strCnt=common.exec_query(cntQuery).strip("\n")
            cnt=0
            if strCnt !="": cnt=int(strCnt)
            if cnt == 0 : 
                print("module:%s count is zero,exit!" % (mname))
                continue
            uquery='''UPDATE `module` SET comment="%s" WHERE name="%s" ''' % (comment,mname) 
            print(uquery)
            common.exec_query(uquery)

def update_regression(gname,mname):
    jenkinsname=detect_reg(gname,mname)
    if gname == "newdailyrun":
        gname="gcc492"
    rname="%s_%s" % (gname,mname)
    query='''select count(1) from regression where name="%s";''' % (rname)
    cnt=int(common.exec_query(query))
    print(cnt)
    if cnt == 1:
        query='''update regression set jkurl="%s/job/%s" where name="%s" ''' %  (cfg.jenkins_url,jenkinsname,rname)
    else:
        query='''INSERT INTO `regression`(id,  name,jkurl  ,fullname,machine,jkdir,controller,computer,cltdir,jkjob,mutex,dependency,deadline,priority) 
                                   values(NULL,"%s","%s/job/%s","%s"     ,""      ,""        ,"" ,""      ,""     ,"%s",""    ,"","","");''' % (rname,cfg.jenkins_url,jenkinsname,rname,jenkinsname)
        print(query)
    common.exec_query(query)

def get_all_jenkins_name(gname,mname):
    jkserver=jenkins.API().get_jenkins_instance()
    jobs=jkserver.get_jobs()
    fp=open("jenkinsName.txt","w")
    for job in jobs:
        fp.write(job[0]+"\n")
    fp.close()

if __name__ == '__main__':
    #updateModule()
    #exit(0) 
    print "start failover"
    if len(sys.argv) < 3:
        print "please input the groupName and jobName"
        exit(1)
    #test-trunk test-release 5ktest
    gname=sys.argv[1]
    mfile= sys.argv[2]
    print "regFileName===>"+mfile
    for mname in open(mfile,"r"):
        mname=mname.strip("\n")
        update_regression(gname,mname)
