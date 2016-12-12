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

'''
extract the total number and failed number of  every single regression result today
and yesterday,sum them and insert,update
'''
def compute():
    rerundict={}
    max_case_time=None
    sumtotalcase=0
    sumfailcase=0
    try:
        groupname="newdailyrun"
        groupid=cfg.group_id_dict["newdailyrun"]
        m2jfile="%s_module2jenkins.txt" % (groupname)
        today= common.getToday()
        yesterday=common.getYesterday()
        for line in open(m2jfile,"r"):
            try:
                line=line.strip("\n")
                if line == "": continue
                mname=line.split(":")[0]
                jkname=line.split(":")[1]
                (failcase,totalcase,case_time)=common.get_report_info(mname,today,groupid)
                if failcase is None or failcase == "" or totalcase is None or totalcase == "" or case_time is None or case_time =="":
                    continue
                failcase=int(failcase)
                totalcase=int(totalcase)
                if max_case_time is None or max_case_time < case_time:
                    max_case_time=case_time
                if totalcase ==0:
                    ratio=0.0  
                else:
                    ratio=(failcase*1.00)/totalcase
                sumtotalcase=sumtotalcase+totalcase
                sumfailcase=sumfailcase+failcase
                print("mname:%s\tfailcase:%d\tratio:%f\tmax_case_time:%s\tsumtotalcase:%d\tsumfailcase:%d" % (mname,failcase,ratio,max_case_time,sumtotalcase,sumfailcase))
            except Exception,e:
                print e
                continue
        print "start calculate time span"
        stime= "%s 00:00:05" % (today)
        etime= max_case_time
        print("today:%s etime:%s stime:%s groupid:%d groupname:%s\tsumtotalcase:%d\tsumfailcase:%d" % (today,etime,stime,groupid,groupname,sumtotalcase,sumfailcase))
        testmen_upload.add_group_stat(groupid,groupname,stime,etime,sumtotalcase,sumfailcase)
        today_sum_fail_case=common.get_total_fail_case(today,groupid)
        common.update_total_fail_case(today_sum_fail_case,today,groupid)
        yesterday_sum_fail_case=common.get_total_fail_case(yesterday,groupid)
        common.update_total_fail_case(yesterday_sum_fail_case,yesterday,groupid)
    except Exception,e:
        print e

if __name__ == "__main__":
    compute()
