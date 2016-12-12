# -*- coding: utf-8 -*-
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')



#获取脚本文件的当前路径
def cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


sys.path.append(cur_file_dir())
sys.path.append(cur_file_dir()+"/pkg")
sys.path.append(cur_file_dir()+"/pkg/jenkinsapi")
sys.path.append(cur_file_dir()+"/pkg/pytz")
sys.path.append(cur_file_dir()+"/pkg/requests")
sys.path.append(cur_file_dir()+"/../testmen/testmen_upload/")
import common ,cfg ,time
import testmen_upload
import jenkins
from param import get_job_xml,get_job_slave,get_job_cfgparam,get_job_child,getAllJob,gendict,rerun,build_job_poll,build_job
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "please input the jenkinsjobname"
        exit(1)
    jenkinsname=sys.argv[1]
    rerun("newdailyrun",jenkinsname,False)
