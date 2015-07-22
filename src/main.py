import json
import urllib
import os
import urllib2
import io
import gzip
import sys
import urllib
import re
import smtplib
from email.mime.text import MIMEText

import time

from bs4 import BeautifulSoup
from StringIO import StringIO

def getPage(url):
    response = urllib2.urlopen(url)
    data = response.read()
    return data
    
def get_available_dates(url):
    dates = []
    
    try:
        html = getPage(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            
            if href != None:
                if href.startswith('mpSignUp.asp'):
                    dates.append(link.get('title'))
            
    except:
        return dates
    
    return dates
    

def send_result(meseum, url, dates):
    content = '%s\r\n%s\r\n%s' % (meseum, url, ', '.join(dates))
    msg = MIMEText(content)
    
    # me == the sender's email address
    # you == the recipient's email address
    me = 'wencanluo.cn@gmail.com'
    you = 'wencanluo.cn@gmail.com'
    
    msg['Subject'] = '%s' % url
    msg['From'] = me
    msg['To'] = you
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()

    
if __name__ == "__main__":
    meseums = {
            #'Henry Art Gallery':'http://www.libraryinsight.net/mpCalendar.asp?t=2825676&jx=y9p&pInstitution=Henry%20Art%20Gallery&mps=1927',
            'EMP Museum':'http://www.libraryinsight.net/mpCalendar.asp?t=1186290&jx=y9p&pInstitution=EMP%20Museum&mps=1925',
            'Museum of Flight':'http://www.libraryinsight.net/mpCalendar.asp?t=2494794&jx=y9p&pInstitution=Museum%20of%20Flight&mps=2259',
            'Seattle Aquarium':'http://www.libraryinsight.net/mpCalendar.asp?t=2644944&jx=y9p&pInstitution=Seattle%20Aquarium&mps=2160',
            'Museum of History & Industry':'http://www.libraryinsight.net/mpCalendar.asp?t=9005982&jx=y9p&pInstitution=Museum%20of%20History%20%26amp%3B%20Industry&mps=2258'
            }
    
    while True:
        for meseum, url in meseums.items():
            dates = get_available_dates(url)
            
            if len(dates) > 0:
                print "%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                
                print meseum
                print url
                print dates
                print 
                #send_result(meseum, url, dates)
                
                time.sleep(60)
            
        