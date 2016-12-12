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

queue = Queue.Queue()

class API:
    'server is a jenkins regression'
    def get_jenkins_instance(self):
        server = Jenkins(cfg.jenkins_url,username=cfg.username,password=cfg.apitoken)
        return server

    def get_dailyrun_config(self,headerJob):
        jn = None
        if cfg.debug==True:
            jsonfile = "".join(file("./config/dailyrun.json").readlines())
            jn = json.loads(jsonfile)
            print jn
        else:
            params = headerJob.get_params()
            print params
            for item in params:
                if item["name"] == 'jobdependencies':
                    config = item["defaultParameterValue"]['value']
                    print config
                    jn = json.loads(config)
        return jn

    def update_job_cfg(self,job,slave):
        jobconfig = job.get_config()
        tree = Etree.fromstring(jobconfig)
        '''descnodes = tree.findall("./description")
        if(descnodes != None):
            descnodes[0].text="testst"
            config = Etree.tostring(tree)
            #print config
            response = job.update_config(config)
            #print response'''
        roamnode = tree.findall("./canRoam")
        if roamnode != None:
            roamnode[0].text="false"
        nodes = tree.findall("./assignedNode")
        print nodes
        if nodes == None or len(nodes)==0:
            tree.append(Etree.fromstring('<assignedNode>'+slave+'</assignedNode>'))
        else:
            node = nodes[0]
            node.text = slave
        print Etree.tostring(tree)
        job.update_config(Etree.tostring(tree))

    
    def startIter(self,server,dependencies):
        for dependency in dependencies:
            if isinstance(dependency,list):
                self.startIter(server,dependency)
                continue
            jobname = dependency['jobname']
            job = server.get_job(jobname)
            if 'slave' in dependency: 
                slave = dependency['slave']
                self.update_job_cfg(job,slave)
            try:
                print 'startjob===>'+jobname
                response = server.build_job(jobname)
                print response
                print 'waiting build'
            
                while(job.is_queued_or_running()):
                    time.sleep(1)
                time.sleep(1)
                print 'finish'
            except Exception,e:
                print e
                continue

    def cvttree(self,dependencies,root):
        for dependency in dependencies:
            if isinstance(dependency,list):
                self.cvttree(dependency,root)
                continue
            jobname = dependency['jobname']
            if "slave" in dependency:
                slave = dependency['slave']
            else:
                slave = ""
            newnode = Node(jobname,slave)
            root.addchild(newnode)
            root = newnode

    def startTree(self,server,dependencies):
        root = Node('header')
        self.cvttree(dependencies,root)
        children = root.getchildren()

        print 'start to run jobs====>'
        for node in children:
            queue.put(node)

        while(True):
            if self.noNode(root):
                break
            item = queue.get()
            print item.getjobname()
            item.setread()
            worker = Worker(item,server)
            worker.start()
            time.sleep(1)

    def noNode(self,root):
        children = root.getchildren()
        tmpQueue = Queue.Queue()
        for child in children:
            tmpQueue.put(child)
        while(True):
            if tmpQueue.empty():
                break
            item = tmpQueue.get()
            if not item.isread():
                return False
            nodes = item.getchildren()
            for node in nodes:
                tmpQueue.put(node)

        return True

    def startbuild(self,headerJobName):
        server = self.get_jenkins_instance()
        headerJob = server.get_job(headerJobName)
        dependencies = self.get_dailyrun_config(headerJob)
        if cfg.debug == True:
            return 0
        #self.startIter(server,dependencies)
        self.startTree(server,dependencies)
        '''for dependency in dependencies:
            if isinstance(dependency,list):
                
                continue
            jobname = dependency['jobname']
            slave = dependency['slave']
            job = server.get_job(jobname)
            self.update_job_cfg(job,slave)
            response = server.build_job(jobname)
            print response
            while(job.is_queued_or_running()):
                time.sleep(0.5)'''
        


class Worker(threading.Thread):
    def __init__(self,node,server):
        threading.Thread.__init__(self)
        self._node = node
        self._server = server

    def run(self):
        print "job start to run",(self._node.getjobname())
        jobname = self._node.getjobname()
        slave = self._node.getslave()
        try:
            job = self._server.get_job(jobname)
            if slave !=None and slave != "":
                self.update_job_cfg(job,slave)
        
            print 'startjob===>'+jobname
            response = self._server.build_job(jobname)
            print response
            print 'waiting build'
            try:
                while(job.is_queued_or_running()):
                    time.sleep(1)
            except Exception,e:
                print("job:%s is_queued_or_running get error.skip waiting"  % (jobname))
                print "Error====>"
                print e
            children = self._node.getchildren()
            for child in children:
                queue.put(child)
            print 'finish'
        except Exception,e:
            print "Error====>"
            print e
        print("running %s over" % (jobname))
        

    def update_job_cfg(self,job,slave):
        if slave == None or slave == "":
            return ""
        jobconfig = job.get_config()
        tree = Etree.fromstring(jobconfig)
        '''descnodes = tree.findall("./description")
        if(descnodes != None):
            descnodes[0].text="testst"
            config = Etree.tostring(tree)
            #print config
            response = job.update_config(config)
            #print response'''
        roamnode = tree.findall("./canRoam")
        if roamnode != None:
            roamnode[0].text="false"
        nodes = tree.findall("./assignedNode")
        print nodes
        if nodes == None or len(nodes)==0:
            tree.append(Etree.fromstring('<assignedNode>'+slave+'</assignedNode>'))
        else:
            node = nodes[0]
            node.text = slave
        #print Etree.tostring(tree)
        job.update_config(Etree.tostring(tree))

def get_job_cfgparam(job):
    jobconfig = job.get_config()
    tree = Etree.fromstring(jobconfig)
    print(tree)
    nodes = tree.findall("./defaultValue")
    print nodes
    if nodes == None or len(nodes)==0:
        return None
    else:
        node = nodes[0]
        return node.text

def update_job_slave(job,slave):
    jobconfig = job.get_config()
    tree = Etree.fromstring(jobconfig)
    '''descnodes = tree.findall("./description")
    if(descnodes != None):
        descnodes[0].text="testst"
        config = Etree.tostring(tree)
        #print config
        response = job.update_config(config)
        #print response'''
    roamnode = tree.findall("./canRoam")
    if roamnode != None:
        roamnode[0].text="false"
    nodes = tree.findall("./assignedNode")
    print nodes
    if nodes == None or len(nodes)==0:
        tree.append(Etree.fromstring('<assignedNode>'+slave+'</assignedNode>'))
    else:
        node = nodes[0]
        node.text = slave
    print Etree.tostring(tree)
    job.update_config(Etree.tostring(tree))

def printbuild(b):
    print("buildnumber")
    print(b.get_number())
    print("buildstatus")
    print(b.get_status())
    print("is_good")
    print(b.is_good())
    print("is_running")
    print(b.is_running())


def phelp():
    jobname="NewdailyrunScheduler"
    jkserver=API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    configxml=job.get_config()
    #print(configxml)
    #update_job_slave(job,"1234")
    #print(dir(job))
    #print(dir(jkserver))
    #help(job)
    b=job.get_last_build()
    print("job.get_last_build")
    printbuild(b)
    gb=job.get_last_good_build()
    print("job.get_last_good_build()")
    printbuild(gb)
    cb=job.get_last_completed_build()
    print("job.get_last_completed_build()")
    printbuild(cb)
    sb=job.get_last_stable_build()
    print("job.get_last_stable_build()")
    printbuild(sb)

def test2():
    jkserver=API().get_jenkins_instance()
    jobs=jkserver.get_jobs()
    print(jobs)
    for job in jobs:
        print(job[0])


if __name__ == '__main__':
    #phelp()
    jobname="test-job"
    jkserver=API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    cfgxml=get_job_cfgparam(job)
    print(cfgxml)
