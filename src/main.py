import json
import urllib
import os
import io
import gzip
import sys
import urllib
import re
import smtplib
from gmail import send_email
import sys

import time
from ticket import buy_ticket

from bs4 import BeautifulSoup
from StringIO import StringIO

import util

def get_available_dates(url):
    dates = []
    hrefs = []
    
    try:
        html = util.getPage(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            
            if href != None:
                if href.startswith('mpSignUp.asp'):
                    dates.append(link.get('title'))
                    hrefs.append(href)
            
    except:
        return dates, hrefs
    
    return dates, hrefs
    

def send_result(meseum, url, dates, hrefs):
    content = '%s\r\n%s\r\n%s' % (meseum, url, ', '.join(dates))
    
    # me == the sender's email address
    # you == the recipient's email address
    me = 'wencanluo.cn@gmail.com'
    you = 'wencanluo.cn@gmail.com'
    
    for herf in hrefs:
        href = 'http://www.libraryinsight.net/' + herf
        
        if buy_ticket(href):
            subject = '%s is revserved now' % meseum
            send_email(subject, me, [you], content)
            return True
        else:
            subject = '%s is not revserved but available now' % meseum
            send_email(subject, me, [you], content)
            return True
    
    return False
    
if __name__ == "__main__":
    meseums = {
            #'Henry Art Gallery':'http://www.libraryinsight.net/mpCalendar.asp?t=2825676&jx=y9p&pInstitution=Henry%20Art%20Gallery&mps=1927',
            #'3_Museum of History & Industry':'http://www.libraryinsight.net/mpCalendar.asp?t=9005982&jx=y9p&pInstitution=Museum%20of%20History%20%26amp%3B%20Industry&mps=2258',
            '4_Museum of Flight':'http://www.libraryinsight.net/mpCalendar.asp?t=2494794&jx=y9p&pInstitution=Museum%20of%20Flight&mps=2259',
            '5_Burke Museum': 'http://www.libraryinsight.net/mpCalendar.asp?t=1613178&jx=y9p&pInstitution=Burke%20Museum&mps=1926',
            #'1_EMP Museum':'http://www.libraryinsight.net/mpCalendar.asp?t=1186290&jx=y9p&pInstitution=EMP%20Museum&mps=1925',
            #'2_Seattle Aquarium':'http://www.libraryinsight.net/mpCalendar.asp?t=2644944&jx=y9p&pInstitution=Seattle%20Aquarium&mps=2160',
            #'Wing Luke Museum': 'http://www.libraryinsight.net/mpCalendar.asp?t=2539302&jx=y9p&pInstitution=Wing%20Luke%20Museum&mps=1905',
            #'Living Computer Museum': 'http://www.libraryinsight.net/mpCalendar.asp?t=4650414&jx=y9p&pInstitution=Living%20Computer%20Museum&mps=2295',
            #'Center for Wooden Boats': 'http://www.libraryinsight.net/mpCalendar.asp?t=4780662&jx=y9p&pInstitution=Center%20for%20Wooden%20Boats&mps=1906',
            }
    
    success = False
    
    dt = 60
    
    for meseum in sorted(meseums):
        print meseum
        
    while True:
        for meseum in sorted(meseums):
            url = meseums[meseum]
            dates, hrefs = get_available_dates(url)
            
            if len(dates) > 0:
                print "%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                
                print meseum
                print url
                print dates
                print 
                if send_result(meseum, url, dates, hrefs):
                    success = True
        
        if success: break
        
        print "%s job will start %.2f mins later" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), dt/60.)
        sys.stdout.flush()
        
        time.sleep(dt)
