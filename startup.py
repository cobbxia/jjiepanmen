# -*- coding: utf-8 -*-
import jenkins
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("./pkg")
sys.path.append("./pkg/jenkinsapi")
sys.path.append("./pkg/pytz")
sys.path.append("./pkg/requests")
sys.path.append("../testmen/testmen_upload/")
import common ,cfg ,testmen_upload
from param import get_job_xml,get_job_slave,get_job_cfgparam,get_job_child,getAllJob,gendict,rerun,build_job_poll,build_job

if __name__ == "__main__":
    print "start job dependencies"
    if len(sys.argv) < 2:
        print "please input the jobName"
        exit(1)

    args = sys.argv[1]
    print "jobName===>"+args
    api = jenkins.API()
    
    stime= common.getNow()
    api.startbuild(args)
