# -*- coding: utf-8 -*-
import subprocess,os,sys,socket,time, random, re, sys ,traceback
import zlib
from  xml.dom import  minidom,Node

#获取脚本文件的当前路径
def cur_file_dir():
     #获取脚本路径
     path = sys.path[0]
     #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)

g_conf={}
g_conffile="./dryrun/script/conf.sh"
def loadconf(filename):
    for line in open(filename,"r"):
        line=line.strip("\n")
        if line == "": continue
        k=line.split("=")[0].strip("'").strip("\"")
        v="=".join([i for i in line.split("=")[1:] ])
        g_conf[k]=v.strip("\"").strip("'")
    g_conf["inputfile"]=g_conf["downloaddir"]+"/"+g_conf["projectname"]
    print(g_conf)
    return g_conf

def do_cmd(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    print("%s\n" % (cmd))
    p = subprocess.Popen(cmd, shell=True,close_fds=True, stdout=stdout, stderr=stderr)
    out, err = p.communicate()
    if p.returncode !=0:
        print("stdout:%s\n" % (out))
        print("stderr:%s\n" % (err))
    return p.returncode, out, err 

def setting2str(settings):
    setdict=eval(settings)
    return "".join("set "+k+"="+setdict[k]+";"  for k in setdict.keys() if setdict[k].find(" ")<0)

def get_attrvalue(node, attrname):
     return node.getAttribute(attrname) if node else ''

def get_nodevalue(node, index = 0):
    return node.childNodes[index].nodeValue if node else ''

#返回所有复合名称的节点数组
def get_xmlnode(node,name):
    return node.getElementsByTagName(name) if node else []

def get_sql_property(node,name):
    property={}
    confignode=node.getElementsByTagName(name)[0]
    #print("confignode:%s" % (confignode))
    for propertynode in confignode.getElementsByTagName("Property"):
        if propertynode.nodeType == Node.ELEMENT_NODE :
            name=get_xml_val(propertynode,"Name")
            value=get_xml_val(propertynode,"Value")
            property[name]=value
            #print("name:%s value:%s" % (name,value))
    #print("property:%s" % (property))
    return property

def xml_to_string(filename):
    doc = minidom.parse(filename)
    return doc.toxml('UTF-8')

def get_xml_val(node,tagname):
    return get_nodevalue(get_xmlnode(node,tagname)[0]).encode('utf-8','ignore') 

def get_xml_data(filename):
    doc = minidom.parse(filename) 
    root = doc.documentElement
    sql_nodes = get_xmlnode(root,'SQL')
    instid_nodes = get_xmlnode(root,'instid')
    nodenum=len(sql_nodes)
    repeatednum=0
    processnum=0
    print(type(sql_nodes))
    print("nodenum:%d" % (nodenum))
    sqldict={}
    #projectname="alimama_algo_dev"
    #sqlDataPath="/home/admin/mingchao.xiamc/pydata/verify/logs/sqldata/"+projectname
    projectname=g_conf["projectname"]
    sqlDataPath=g_conf["sqldir"]+"/" + projectname
    do_cmd("mkdir -p %s" % (sqlDataPath))
    for i in range(nodenum):
        #if not sql_nodes[i] : continue
        #if not instid_nodes[i]: continue
        node=sql_nodes[i]
        instid=get_nodevalue(instid_nodes[i]).encode('utf-8','ignore')
        #print("instid:%s" % (instid))
        #sql_id = get_attrvalue(node,'id') 
        node_name = get_xmlnode(node,'Name')
        node_query = get_xmlnode(node,'Query')

        sql_name =get_nodevalue(node_name[0]).encode('utf-8','ignore')
        sql_query = get_nodevalue(node_query[0]).encode('utf-8','ignore') 
        sql_query_c=zlib.compress(sql_query)
        sql_property = get_sql_property(node,'Config')
        if "settings" in sql_property:
            sql_settings= setting2str(sql_property["settings"] if "settings" in sql_property else "")
        else:
            print("instid:%s settings not found,posible not dml." % (instid))
            continue
        sql = {}
        if sql_query.lower().find("datax") >=0 or sql_query.lower().find("insert ")<0:
            continue
        if sql_query_c in sqldict:
            sqldict[sql_query_c]=sqldict[sql_query_c]+1
            repeatednum=repeatednum+1
            continue
        sqldict[sql_query_c]=0
        content="%s%s" % (sql_settings,sql_query)
        open(sqlDataPath+"/"+instid,"w").write(content)
        processnum=processnum+1
    print("repeatednum:%s\tnodenum:%d\tprocessnum:%d\n" % (repeatednum,nodenum,processnum))
    return sqldict

def test_xmltostring():
    print xml_to_string(g_conf["inputfile"])

def test_laod_xml():
    sqldict = get_xml_data(g_conf["inputfile"])
    return 0
    for sql in sqldict : 
        if sqldict[sql]>0:
            print '-----------------------------------------------------' 
            print("name:%s\n%s\n" % (zlib.decompress(sql),sqldict[sql]))
            print '====================================================='

if __name__ == "__main__": 
    loadconf(g_conffile) #test_xmltostring()
    test_laod_xml()
