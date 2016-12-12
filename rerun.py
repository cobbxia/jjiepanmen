# -*- coding: utf-8 -*-
import jenkins,time
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
    #if newdailyrun,then rerun
    if args.lower().find("newdailyrun") >= 0:
        groupname="newdailyrun"
        rerundict=common.genRerunDict()
        for mname in rerundict:
            try:
                print("rerun:groupname:%s jenkinsname:%s"   % (groupname,rerundict[mname]))
                rerun(groupname,rerundict[mname])
            except Exception as e:
                print(format(str(e)))
            time.sleep(1)
