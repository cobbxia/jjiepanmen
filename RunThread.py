'''
Job Run Thread class
'''
import threading

class JobRunThread(threading.Thread):
    def __init__(self,name=None):
        threading.Thread.__init__(self)
        self.name = name

    def start():
        self.status = True

    def stop():
        self.status = False

    def run(self):
        if(self.status):
            



