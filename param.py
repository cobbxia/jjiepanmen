'''
This file contains jenkins api
'''
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
import json
import xml.etree.ElementTree as Etree
import cfg
import time
from tree import Node
import Queue
import threading
import ConfigParser 

import jenkins
from util import detect_reg

class myconf(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr


def printnode(nodes):
    for node in nodes:
        print(node.tag,node.attrib,node.text)


def get_job_cfgparam(groupname,jobname):
    print(groupname,jobname)
    paramconffile="%s.conf" % (jobname)
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    jobconfig = job.get_config()
    tree = Etree.fromstring(jobconfig)
    pnodes = tree.findall("./properties")
    printnode(pnodes)
    if pnodes == None or len(pnodes)==0:
        return None
    pnode=pnodes[0]
    print(pnode)
    textParamNodes=pnode.find("hudson.model.ParametersDefinitionProperty").find("parameterDefinitions").findall("hudson.model.TextParameterDefinition")
    printnode(textParamNodes)
    confignode=None
    for node in textParamNodes:
        print(node)
        if node.find('name').text== "config":
            confignode=node
    if confignode != Node:
        outmancfg=confignode.find("defaultValue").text
        print("cfg:%s" % outmancfg)
    else:
        print("config node is empty")
        return
    cfgfile=open(paramconffile,"w")
    cfgfile.write(outmancfg)
    cfgfile.close()
    cf = myconf()      
    cf.read(paramconffile)
    return cf


def add_job_cfgparam(groupname,jobname,section,option,val,isupdate=False):
    print(groupname,jobname)
    paramconffile="%s.conf" % (jobname)
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    jobconfig = job.get_config()
    tree = Etree.fromstring(jobconfig)
    pnodes = tree.findall("./properties")
    printnode(pnodes)
    if pnodes == None or len(pnodes)==0:
        return None
    pnode=pnodes[0]
    print(pnode)
    textParamNodes=pnode.find("hudson.model.ParametersDefinitionProperty").find("parameterDefinitions").findall("hudson.model.TextParameterDefinition")
    printnode(textParamNodes)
    confignode=None
    for node in textParamNodes:
        print(node)
        if node.find('name').text== "config":
            confignode=node
    if confignode != Node:
        outmancfg=confignode.find("defaultValue").text
        print("cfg:%s" % outmancfg)
    else:
        print("config node is empty")
        return
    cfgfile=open(paramconffile,"w")
    cfgfile.write(outmancfg)
    cfgfile.close()
    cf = myconf()      
    cf.read(paramconffile)
    if cf.has_section(section):
        cf.set(section,option,val)
    else:
        cf.add_section(section)
        cf.set(section,option,val)
    cf.write(open(paramconffile, "w"))
    if isupdate==True:
        confignode.find("defaultValue").text="".join(open(paramconffile,"r").readlines())
        if cfg.debug == True:
            print(confignode.find("defaultValue").text)
            open("%s.xml" % (jobname),"w").write(Etree.tostring(tree))
        job.update_config(Etree.tostring(tree))
    return cf

def get_element_children(element):
    '''return the element children if the element is not None.'''
    if element is not None:
        if cfg.debug:
            print('begin to handle the element : [{}]'.format(element))
        return [c for c in element]
    else:
        print('the element is None!')

def get_job_slave(groupname,jobname):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    jobconfig = job.get_config()
    tree = Etree.fromstring(jobconfig)
    roamnode = tree.findall("./canRoam")
    if roamnode != None:
        roamnode[0].text="false"
    nodes = tree.findall("./assignedNode")
    print nodes
    if nodes == None or len(nodes)==0:
        tree.append(Etree.fromstring('<assignedNode>'+slave+'</assignedNode>'))
    else:
        node = nodes[0]
        print(node.text)
    return node.text

def get_job_xml(groupname,jobname):
    #phelp()
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    jobxml=job.get_config()
    print(jobxml)


'''
    waiting until job done
'''
def build_job_poll(jobname,params=None):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    if params==None:
        params={'block':True}
    else:
        params['block']=True
    try:
        print 'startjob===>'+jobname
        response = jkserver.build_job(jobname, params)
        print response
        print 'waiting build'
        while(job.is_queued_or_running()):
            time.sleep(1)
        time.sleep(1)
        print 'finish'
    except Exception,e:
        print e


'''
    trigger the job and exits
'''
def build_job(jobname, params=None):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    try:
        print 'startjob===>'+jobname
        response = jkserver.build_job(jobname, params)
    except Exception,e:
        print e

def get_job_child(groupname,jobname):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    jobconfig = job.get_config()
    tree = Etree.fromstring(jobconfig)
    children = tree.find("publishers").find("hudson.tasks.BuildTrigger").find("childProjects").text
    print(children)

'''
generate module name and jenkins job dict
'''
def gendict(gname,jobname):
    m2jdict={}
    srcfile="%s_module_list.txt" % (gname)
    dstfile="%s_module2jenkins.txt" % (gname)
    dstfp=open(dstfile,"w")
    for mname in open(srcfile,"r"):
        mname=mname.strip("\n")
        dstfp.write("%s:%s\n" % (mname,detect_reg(gname,mname)) )
    dstfp.close()


def get_child_job(gname,jobname):
    m2jdict=loadm2jdict(gname)
    joblist=[]
    jobdict={}
    jobdict["jobname"]=jobname
    slave=get_job_slave(gname,jobname)
    jobdict["slave"]=slave
    joblist.append(jobdict)
    children=get_job_children(gname,jobname)
    if children != "":
        for child in children.split(","):
            slave=get_job_slave(gname,child)
            childdict={"jobname":child,"slave":slave}
            filterdict.append(child)
            joblist.append(childdict)
    else:
        return joblist


'''
get all jenkins jobname and slave in one group
'''
def getAllJob(gname,jobname):
    m2jdict=loadm2jdict(gname)
    filterdict={}
    allJobList=[]
    for mname in m2jdict:
        joblist=[]
        jobdict={}
        jobname=m2jdict[mname]
        if jobname is None or jobname == "None":
            print("module:%s not found" % mname)
            continue
        slave=get_job_slave(gname,jobname)
        jobdict["slave"]=slave
        jobdict["jobname"]=jobname
        joblist.append(jobdict)
        allJobList.append(joblist)
    encodedjson = json.dumps(allJobList)
    print(encodedjson)
    open("%s.txt" % (gname),"w").write(encodedjson)

def loadm2jdict(gname):
    m2jdict={}
    srcfile="%s_module2jenkins.txt" % (gname)
    for line in open(srcfile,"r"):
        line=line.strip("\n")
        if cfg.debug == True:
            print(line)
        (key,val)=line.split(":")
        m2jdict[key]=val
    return m2jdict


def modify_branch(jobname,new_branch):
    print(jobname)
    if jobname=="None" or jobname is None :
        return 
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    try:
        branch=job.get_scm_branch()
    except Exception,e:
        print e
        return
    print(branch)
    job.modify_scm_branch(new_branch)
    branch=job.get_scm_branch()
    print(branch)


'''
modify scm branch in batch,groupname and new_branch
"5ktest" "*/release/20151230_sprint21"
'''
def batch_scm_modify(gname,new_branch):
    new_branch=cfg.new_branch
    srcfile="%s_module2jenkins.txt" % (gname)
    for line in open(srcfile,"r"):
        jobname=line.strip("\n").split(":")[1]
        if jobname is None or jobname == "" or jobname == "None":
            continue
        modify_branch(jobname,new_branch)

def modify_5k_scm():
    gname="5ktest"
    new_branch="*/release/20151230_sprint21"
    batch_scm_modify(gname,new_branch)

'''
'''
def get_cfg(jobname):
    print(jobname)
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    print(job.get_config())

def rerun(groupname,jobname,block=True):
    #jobname="mztest_git"
    #groupname="5ktest"
    secname="runtime"
    optname="failed"
    val="True"
    params={}
    cf=add_job_cfgparam(groupname,jobname,secname,optname,val)
    paramconffile="%s.conf" % (jobname)
    params["config"]="".join(open(paramconffile,"r").readlines())
    #print(params["config"])
    if jobname.lower().find("outman") >=0:
        if block==True:
            build_job_poll(jobname, params)
        else:
            build_job(jobname, params)
    else:
        print("job:%s not outman,cann't rerun" % (jobname))

class Rerun:
    def __init__(gname):
        self.gname=gname
        self.m2jfile="%s_module2jenkins.txt" % (self.gname)
        self.mlist=[]
        self.failJobList=[]
        self.m2jdict={}
        for line in open(self.m2jfile,"r"):
            line=line.strip("\n")
            mname=line.split(":")[0]
            jenkinsname=line.split(":")[1]
            self.m2jdict[mname]=jenkinsname
    def get_fail_jobname(self):
        today=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        for mname in self.m2jdict:
            pass


def batch_modify_endpoint(gname):
    for line in open("%s_module2jenkins.txt" % (gname),"r"):
        line =line.strip("\n")        
        jobname=line.split(":")[1]
        if jobname.lower().find("outman") < 0:
            print(jobname)
            continue
        isupdate=True
        section=""
        option="end_point"
        val=""
        try:
            add_job_cfgparam(gname,jobname,section,option,val,isupdate)
        except Exception,e:
            print e


def batch_modify_clt(gname):
    for line in open("%s_module2jenkins.txt" % (gname),"r"):
        line =line.strip("\n")        
        jobname=line.split(":")[1]
        if jobname.lower().find("outman") < 0:
            print(jobname)
            continue
        isupdate=True
        section="client"
        option="console_download"
        val=cfg.newdailyrunconsole
        try:
            add_job_cfgparam(gname,jobname,section,option,val,isupdate)
        except Exception,e:
            print e

def get_build_status(jobname):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    builddict=job.get_build_dict()
    print(builddict)

def get_last_console(jobname):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    build=job.get_last_build()
    content=build.get_console() 
    open("content.txt","w").write(content)

if __name__ == '__main__':
    gname="release"
    batch_modify_endpoint(gname)
