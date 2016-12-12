# -*- coding: utf-8 -*-
import sys,os
def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

jenkins_url=""
username=""
apitoken=""
loginwm="mysql"
jenkinsName="./jenkinsName.txt"
debug=False
group_id_dict={}
group_testsuite_dict={}
new_branch="*/release/20160530_sprint23"
testmen_url=""
testmen_base_url=""
help_url=""
cur_path=cur_file_dir()
