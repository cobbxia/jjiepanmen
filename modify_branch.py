# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from param import modify_branch 



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "please input the jobname and new branch name"
        exit(1)
    jobname=sys.argv[1]
    new_branch = sys.argv[2]
    modify_branch(jobname,new_branch)
