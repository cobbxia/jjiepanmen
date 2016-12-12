# -*- coding: utf-8 -*-
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import subprocess
import cfg,time,datetime
def initModduleDict():
    moduleFile="modulelist.txt"
    moduleDict={}
    cmd='''mysql -N -e"select id,name,comment from module" > %s '''  % (moduleFile)
    do_cmd(cmd)
    for line in open(moduleFile):
        line=line.strip("\n")
        if line == "": continue
        mid=line.split("\t")[0]
        mname=line.split("\t")[1]
        moduleDict[mid]=mname
    print(moduleDict)
    return moduleDict

def getNow():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def getToday():
    today=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    return today

def getYesterday():
    yesterday = (datetime.date.today()  - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return yesterday

def do_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out, err 

def exec_query(query,hasHead="N"):
    resultList=[]
    headerList=[]
    print("query:%s" % (query))
    cmd = ''' %s -N -e '%s' ''' % (cfg.loginwm,query)
    if hasHead != "N":
        cmd = ''' %s -e '%s' ''' % (cfg.loginwm,query)
    print(cmd)
    r=do_cmd(cmd)
    if r[0] != 0:
        print("stdout:%s\nstderr:%s" % (r[1],r[2]))
    print(r[1])
    if hasHead == "N":
        return r[1]
    else:
        lineno=0
        for line in r[1].split("\n"):
            fieldList=line.split("\t")
            if lineno == 0:
                headerList=fieldList
                lineno=lineno+1
                continue
            valcnt=0
            resultDict={}
            for fieldval in fieldList:
                resultDict[headerList[valcnt]]=fieldval
                valcnt=valcnt+1
            lineno=lineno+1
            resultList.append(resultDict)
        return resultList

def get_new_dailyrun_m2jdict():
    dstfp=open("newdailyrun_module2jenkins.txt","w")
    for line in open("./newdailyrun_module_list.txt","r"):
        mname=line.strip("\n")
        jkurl=exec_query('''SELECT jkurl FROM regression  where name="gcc492_%s" ''' % (mname))
        jkname=jkurl.split("job/")[-1].strip("/")
        dstfp.write("%s:%s" % (mname,jkname))
    dstfp.close()

def get_total_fail_case(day,groupid):
    sum_fail_case="0"
    try:
        sumSql = ''' SELECT SUM( failure_case ) 
FROM  `reportStat` r
WHERE r.dt =  "%s"
AND r.group_id =%s
AND r.failure_case >0'''  % (day,groupid)
        sum_fail_case=exec_query(sumSql)
    except Exception,e:
        print e
    return sum_fail_case

def getdailyrunStatByToday(day, groupId): 
    (stime,etime,totalnum,failnum) = ("","","","")
    try:
        querySql='''select stime,etime,totalnum,failnum from dailyrunStat where today="%s" and groupid="%s" order by stime  ASC  limit 1 ''' % (day,groupId)
        (stime,etime,totalnum,failnum) = exec_query(querySql).split("\t")
        etime=etime.strip("\n")
    except Exception,e:
        print e
    return (stime,etime,totalnum,failnum)

def update_total_fail_case(sum_fail_case,day,groupid):
    try:
        updateSql='''UPDATE `dailyrunStat` SET failnum=%s WHERE today="%s" and groupid=%s ''' % (sum_fail_case,day,groupid)
        exec_query(updateSql)
    except Exception,e:
        info=sys.exc_info()
        print info[0],":",info[1]
        print e

def getFailReports(groupname,day,moduleList):
    reportList=[]
    predicate='''status != "3" '''
    for moduleName in moduleList:
        try:
            reportDict={}
            moduleId=getModuleId(moduleName)
            reportDict=getReportByDayModule(groupname,day,moduleId,predicate)
            if reportDict != None and "failure_case" in reportDict and int(reportDict["failure_case"]) > 0:
                reportList.append(reportDict)
        except Exception,e:
            info=sys.exc_info()
            print info[0],":",info[1]
            print e
    return reportList    

'''
get report by day and moduleId
'''
def getReportByDayModule(groupname,day,moduleId,predicate=""):
    reportList=[]
    groupId=cfg.group_id_dict[groupname]
    try:
        print("moduleId:"+moduleId)
        reportQuery='''SELECT module_id,group_id,case_time,dt,link,status,latency,comment,total_case,failure_case FROM `report` WHERE dt="%s" and group_id="%s" and module_id=%s  ''' % (day,groupId,moduleId)
        if predicate != "":
            reportQuery='''SELECT module_id,group_id,case_time,dt,link,status,latency,comment,total_case,failure_case FROM `report` WHERE dt="%s" and group_id="%s" and module_id=%s and %s order by case_time desc limit 1 ''' % (day,groupId,moduleId,predicate)
        reportList=exec_query(reportQuery,"Y")
        print("report-len:%d reportList:%s" % (len(reportList),reportList))
    except Exception,e:
        print e
        info=sys.exc_info()
        print info[0],":",info[1]
    return reportList[0]


'''
get latest report info from report table
'''
def get_report_info(mname,day,gid="9"):
    try:
        mid=exec_query(''' SELECT id FROM module where name="%s" ''' % (mname))
        #SELECT * FROM  `report` WHERE group_id =9AND module_id =1 AND dt =  "2016-03-03" ORDER BY case_time ASC 
        sql='''select failure_case,total_case,case_time  from report where module_id=%d and group_id=%d and dt="%s" and status!=3 order by case_time ASC limit 1''' % (int(mid),int(gid),day)
        (failcase,totalcase,case_time)=(0,0,"")
        (failcase,totalcase,case_time)=exec_query(sql).split("\t")
    except Exception,e:
        print e
        info=sys.exc_info()
        print info[0],":",info[1]
        return (None,None,"")
    return (failcase,totalcase,case_time)

def getModuleId(mname):
    mid=""
    try:
        mquery='''select id from `module` where name="%s" ''' % (mname)
        mid=exec_query(mquery)
    except Exception,e:
        print e
        info=sys.exc_info()
        print info[0],":",info[1]
    return mid

def getUnrunedModule(groupId,moduleList,day):
    unrunedModuleList=[]
    try:
        for mname in moduleList:
            mid=getModuleId(mname)
            if mid == "":
                continue
            McntQuery='''select count(1) from report where group_id="%s" and module_id="%s" and dt="%s" and status!="3" ''' % (groupId,mid,day) 
            ModuleCnt=exec_query(McntQuery)
            if ModuleCnt == 0 :
                unrunedModuleList.append(mname)
    except Exception,e:
        print e
    return unrunedModuleList

def getTotalModule(groupname):
    moduleList=[]
    m2jfile="%s/%s_module2jenkins.txt" % (cfg.cur_path,groupname)
    print("m2jfile:%s" % m2jfile)
    for line in open(m2jfile,"r"):
        line=line.strip("\n")
        if line == "":continue
        mname=line.split(":")[0]
        moduleList.append(mname)
    return moduleList
    
def genRerunDict():
    rerundict={}
    groupname="newdailyrun"
    groupid=cfg.group_id_dict[groupname]
    m2jfile="%s/%s_module2jenkins.txt" % (cfg.cur_path,groupname)
    print("m2jfile:%s" % m2jfile)
    today=getToday()
    yesterday=getYesterday()
    for line in open(m2jfile,"r"):
        try:
            line=line.strip("\n")
            mname=line.split(":")[0]
            jkname=line.split(":")[1]
            (failcase,totalcase,case_time)=get_report_info(mname,today,groupid)
            if failcase is None or failcase == "":
                continue
            if totalcase is None or totalcase == "":
                continue
            failcase=int(failcase)
            totalcase=int(totalcase)
            if  totalcase ==0:
                ratio=0.0  
            else:
                ratio=(failcase*1.00)/totalcase
            #20% rerun
            print("mname:%s\tfailcase:%d\tratio:%f\tcase_time:%s" % (mname,failcase,ratio,case_time))
            if failcase !=0 :
            #and ratio<0.2: 
                rerundict[mname]=jkname
                print("rerun:%s" % (mname))
        except Exception,e:
            print e
    return rerundict


def flush():
    dayList=("2016-03-25","2016-03-26","2016-03-27","2016-03-28","2016-03-29","2016-03-30")
    groupid="9"
    for day in dayList:
        sum_fail_case=get_total_fail_case(day,groupid)
        print("day:%s\tsum_fail_case:%s" % (day,sum_fail_case))
        update_total_fail_case(sum_fail_case,day,groupid)

if __name__ == '__main__':
    #query='''select * from report where dt="2016-03-10" limit 1;'''
    #r=exec_query(query)
    #open("r.txt","w").write(r)
    #print(r)
    #get_new_dailyrun_m2jdict()
    flush()
