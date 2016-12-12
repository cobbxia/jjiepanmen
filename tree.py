'''
Python Tree Structure
'''
class Node:
    def __init__(self,jobname,slave=None):
        self._jobname = jobname
        self._slave = slave
        self._children = []
        self._read = False

    def getchildren(self):
        return self._children

    def addchild(self,node):
        self._children.append(node)

    def getjobname(self):
        return self._jobname

    def getslave(self):
        return self._slave

    def setread(self):
        self._read = True

    def isread(self):
        return self._read
