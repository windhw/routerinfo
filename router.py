#!/usr/bin/python
# -*- coding: utf-8 -*-
from time import sleep
import urllib2
import urllib
import sys
import syslog
import re
import signal
import httplib
import time
import smtplib
import os
import subprocess
from   subprocess import Popen, PIPE
from email.mime import text

def call_sys(cmd, **kwarg):
    kwarg["stdout"] = PIPE
    kwarg["stderr"] = PIPE
    p= Popen(cmd,**kwarg)
    p.wait()
    stdo = p.stdout.read()
    stde = p.stderr.read()
    return (p.returncode, stdo,stde)



class RouterReporter:
    def __init__(self, router_url, repo_path, headers={} ):
        self.my_opener = urllib2.build_opener()
        self.router_url = router_url
        self.repo_path  = repo_path
        self.router_req_hdr=headers
        self.router_data = ""
        syslog.openlog(logoption=syslog.LOG_INFO, facility=syslog.LOG_LOCAL7)
    
    def log(self,data):
        syslog.syslog(data.encode("utf-8"))

    def fetch_data(self):
        req = urllib2.Request(router_url,None,self.router_req_hdr)
        try:
            r1 = self.my_opener.open(req,data=None,timeout=5)
            cont = r1.read()
            r1.close()
            finder = re.compile(r"var\swanPara\s=\snew\sArray\(([^;]+)\);",re.S|re.M)
            res = finder.search(cont)
            a = res.group(1).replace("\n","").replace('"','').split(",")
        except Exception,e:
            self.log(str(e)) 
            return 1
        self.router_data =  "|".join(a)
        self.log("Fetched: %s" % self.router_data)
        return 0

    def report_to_github(self):
        f=open(os.path.join(self.repo_path,"status"),"wb")
        f.write(self.router_data)
        f.close()
        git_add_cmd = ["git", "add","status"]
        git_commit_cmd = ["git", "commit", "-m", '"Automated commited by router.py"']
        git_push_cmd = ["git", "push","origin","master"]
        (rt,stdo,stde) = call_sys(git_add_cmd,cwd=self.repo_path)
        (rt,stdo,stde) = call_sys(git_commit_cmd,cwd=self.repo_path)
        if rt and (not "nothing to commit" in stdo ) :
            return 1
        (rt,stdo,stde) = call_sys(git_push_cmd,cwd=self.repo_path)
        return rt

    def start_task(self):
        while(1):
            try:
                self.fetch_data()
                self.report_to_github()
                #break
            except Exception, e:
                self.log("Get an error: %s" % e) 
            sleep(7200)

def daemon():
    try:
        if os.fork() > 0:
            os._exit(0) # exit father
    except OSError, error:
        print 'fork failed: %d (%s) '%  (error.errno, error.strerror)
        os._exit(1)
    os.chdir("/")
    os.setsid()
    os.umask(0)

    #signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    #sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    #si = file("/dev/null", 'r')
    #so = file("/var/log/tmp_1234.log", 'a+', 0)
    #se = file("/tmp/tmp_1234.log", 'a+', 0)
    #os.dup2(si.fileno(), sys.stdin.fileno())
    #os.dup2(so.fileno(), sys.stdout.fileno())
    #os.dup2(so.fileno(), sys.stderr.fileno())

if __name__ == '__main__':
    daemon()
    router_url =  "http://192.168.1.1/userRpm/StatusRpm.htm"    #
    header     = { "Authorization" : "Basic XXXXXXXXXXXXXXXX" } #
    repo_path  = "/root/cubiebox/"
    reporter = RouterReporter(router_url, repo_path, header)
    reporter.start_task()
