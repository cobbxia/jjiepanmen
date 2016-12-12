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

def failover(jobname):
    jkserver=jenkins.API().get_jenkins_instance()
    job=jkserver.get_job(jobname)
    buildinfo=job.get_last_build()
    print("is_good:")
    print(buildinfo.is_good())
    print("is_running:")
    print(buildinfo.is_running())
    print(buildinfo.get_number())
    if buildinfo.is_good() ==  False and buildinfo.is_running() == False:
        print("job:%s not success,failover begins" % (jobname))
    elif buildinfo.is_running == True:
        print("job:%s is running." % (jobname))
    else:
        print("job:%s is successful." % (jobname))



if __name__ == '__main__':
    print "start failover"
    if len(sys.argv) < 2:
        print "please input the jobName"
        exit(1)
    jobname= sys.argv[1]
    print "jobName===>"+jobname
    failover(jobname)
