# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from param import get_job_xml,get_job_slave,get_job_cfgparam,get_job_child,getAllJob,gendict,rerun,build_job_poll,build_job,batch_scm_modify
from chlink import get_jenkinsname,get_all_jenkins_name,update_regression

g_fdict={"get_job_xml":get_job_xml,
	 "get_job_slave":get_job_slave,
	 "get_job_cfgparam":get_job_cfgparam,
         "get_job_child":get_job_child,
         "getAllJob":getAllJob,
         "gendict":gendict,
         "get_jenkinsname":get_jenkinsname,
         "get_all_jenkins_name":get_all_jenkins_name,
         "rerun":rerun,
         "update_regression":update_regression,
         "batch_scm_modify":batch_scm_modify
      #   "build_job_poll":build_job_poll,
      #   "build_job":build_job
        }

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "please input the funcname,groupName and jobName"
        exit(1)
    #test-trunk test-release 5ktest
    fname=sys.argv[1]
    gname=sys.argv[2]
    mname= sys.argv[3]
    print("funcName===>%s\ngname===>%s\nmname===>%s" % (fname,gname,mname))
    g_fdict[fname](gname,mname)
