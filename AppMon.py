# coding:utf-8
import urllib.request
from bs4 import BeautifulSoup
import os
import hashlib
import sys
import time
import datetime
import requests


def getdata(status='ERROR'):
    msg = []
    #status = 'WARNING'
    cont = None
    myurl = 'http://10.41.10.200/status.html'
    htmldoc = urllib.request.urlopen(myurl).read().decode('UTF-8')
    soup = BeautifulSoup(htmldoc, features="html.parser")
    tds = soup.findAll(onmouseover=True)
    qs = [td['onmouseover'] for td in tds if status in td.text]
    #qs = [td['onmouseover'] for td in tds if 'WARNING' in td.text]
    for i in qs:
        reason = []
        tar = str(i).replace("javascript:toggle_app(", "").replace(")", "").replace("'", "").replace(",", "-").replace(";", "")
        for x in soup.findAll('div', id=tar):
            for y in x.findAll('tr'):
                if y.findAll('td', text=status):
                    txt = [ z.text.strip() for z in y.findAll('td') if z.text != status ]
                    reason.append(' '.join(txt))
        reason_txt = '\n'.join(reason)
        if reason_txt:
            msg.append('status ' + status + ' founded on ' + tar + '. reason: ' + reason_txt)
            cont = '\n'.join(msg)
        else:
            sys.exit()
            #text = 'status error founded on test'
            #with open(sys.path[0]+'/tmp','w') as file:
            #    file.write(text)
    if cont:
        with open(sys.path[0] + '/tmp', 'w') as file:
            file.write(cont)
    return cont


class AppMon:

    @staticmethod
    def toalertmanager(myurl, myalertname, myinstance, myservice, myseverity, mysummary, mydescription, myauthor):
        alerts1 = '''[
          {
            "labels": {
               "alertname": "%s",
               "instance": "%s",
               "service": "%s",
               "severity": "%s"
             },
             "annotations": {
                "summary": "%s",
                "description": "%s",
                "author": "%s"
              }
          }
        ]''' % (myalertname, myinstance, myservice, myseverity, mysummary, mydescription, myauthor)

        data = alerts1
        response = requests.post(myurl, data=data)
        return response.text


    @staticmethod
    def get_md5(file_path):
        md5sum = None
        if os.path.isfile(file_path):
            with open(file_path,'rb') as file:
                md5_obj = hashlib.md5()
                md5_obj.update(file.read())
                hash_code = md5_obj.hexdigest()
                file.close()
                md5sum = str(hash_code).lower()
        return md5sum
        
if __name__ == "__main__":
    url = 'http://10.41.15.16:9093/api/v1/alerts'
    interval = 0
    duration = 5
    omd5 = None
    mon = AppMon()
    text = None
    if len(sys.argv) == 1:
        text = getdata()
    if not text:
        sys.exit()
    md5 = mon.get_md5(sys.path[0]+'/tmp')
    if os.path.getsize(sys.path[0]+'/tmp'):
        try:
            with open(sys.path[0]+'/maildt','r') as f:
                tmp = f.readline().strip().split('|')
                omd5 = tmp[1]
                lastdt = datetime.datetime.strptime(tmp[0],'%Y-%m-%d %H:%M:%S')
                now = datetime.datetime.now()
                etime = now-lastdt
                interval = etime.seconds
        except IOError:
            pass
        if omd5 == md5 and interval<duration:
            m,s = divmod(duration-interval,duration)
            h,m = divmod(m,duration)
            print("%d seconds elapsed from last alert sending.will be remind again after %02d:%02d:%02d." % (interval,h,m,s))
            exit()
        else:
            with open(sys.path[0]+'/tmp','r') as f:
                content = f.read()
            alertname = 'ob_status'
            severity = 'error'
            author = 'Knight.Ni'
            cbegin = len('status Error founded on ')
            for summary in text.split('\n'):
                warninfo = summary.replace(' ',',').replace('.','').split(',')[4]
                instance,service = warninfo.split('-')
                reason = summary.split('reason:')[1].strip()
                warntxt = 'status Error founded on ' + warninfo
                res = mon.toalertmanager(url, alertname, instance, service, severity, warntxt, reason, author)
            with open(sys.path[0]+'/maildt','w') as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+'|'+md5)
    else:
        exit()
