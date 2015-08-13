#https://github.com/dgrtwo/ParsePy
from parse_rest.connection import register
import parse_rest
import datetime
import time
from tables import *
import json
import codecs
import os
import cmd
from cmd import Cmd
import subprocess
import re

import requests
from bs4 import BeautifulSoup

from parse_rest.user import User
import util
import file_util
import dateutil.parser

from datetime import datetime
from pytz import timezone

pacific_zone = timezone('US/Pacific')

DATE_FORMAT = "%m/%d/%Y"
DATE_FORMAT_AVAILABLE = "%B %m, %Y"
DATE_FORMAT_FILE = "%d-%m-%Y"

'''
url:
    reserve_url: a url that can buy a ticket directly
    dates_url: a url that shows the available dates
    museum_list_url: a url that list all the museums
'''

class TicketServer:
    def __init__(self, app_id, api_key, master_key):
        register(app_id, api_key)
        
        self.updated_museums = {}
        self.museums = None
        self.post_url = 'http://www.libraryinsight.net/mpPostCheckOut.asp?jx=y9p'
        self.museum_list_url = 'http://www.libraryinsight.net/mpbymuseum.asp?jx=y9'
        self.tables = {'Museum':Museum, 
                        'PassID':PassID
                    }
        self.datadir = '../data/'
        self.passid_local = 'PassID_local.json'
    
    def download_databases(self):
        for table_name, table in self.tables.items():
            data = self.get_data(table)
            
            filename = os.path.join(self.datadir, table_name + '.json')
            
            with codecs.open(filename, 'w', 'utf-8') as fout:
                json.dump(data, fout, indent=2)
    
    def upload_databases(self):
        for table_name, table in self.tables.items():
            filename = os.path.join(self.datadir, table_name + '.json')
            with codecs.open(filename, 'r', 'utf-8') as fin:
                data = json.load(fin)
            
            for item in data['results']:
                if 'objectId' in item: continue
                
                #TODO
                
    def get_data_top(self, table, topK, cid=None, order_by = None):
        data = {'results':[]}

        if order_by != None:
            rows = table.Query.all().order_by(order_by)
        else:
            rows = table.Query.all()
        
        assert(topK <= 100)
        page = rows.limit(topK)
    
        dict = {}
        for row in page:
            for key in row.__dict__.keys():
                if key in ['_created_at', '_updated_at']: continue
                dict[key] = row.__dict__[key]
        
        data['results'].append(dict)
               
        return data
    
    def get_data_objects(self, table, order_by = None):
        objects = []

        if order_by != None:
            rows = table.Query.all().order_by(order_by)
        else:
            rows = table.Query.all()
        
        totalN = 0
        N = 100
        page = rows.limit(N)
        while(True):
            for row in page:
                objects.append(row)
            
            totalN += N
            page = rows.skip(totalN).limit(N)
            
            if len(page) == 0:
                break
            
        return objects
        
    def get_data(self, table, order_by = None):
        data = {'results':[]}

        if order_by != None:
            rows = table.Query.all().order_by(order_by)
        else:
            rows = table.Query.all()
        
        totalN = 0
        N = 100
        page = rows.limit(N)
        while(True):
            for row in page:
                dict = {}
                for key in row.__dict__.keys():
                    if key in ['_created_at', '_updated_at']: continue
                    dict[key] = row.__dict__[key]
            
                data['results'].append(dict)
            
            totalN += N
            page = rows.skip(totalN).limit(N)
            
            if len(page) == 0:
                break
            
        return data

    def get_museums(self):
        if self.museums != None: return self.museums
        
        try:
            self.museums = self.get_data_objects(Museum)
            return self.museums
        except Exception as e:
            print e
            return []
    
    def get_root_url(self, url):
        k = url.rfind('/')
        return url[:k+1]
    
    def get_measume_slots(self, reserve_url):
        response = requests.get(reserve_url, verify=False)
        page = BeautifulSoup(response.text, 'html.parser')
        
        tags = page.find_all('input')
        
        data = {}
        
        for tag in tags:
            if tag.get('name') == None: continue
            data[tag.get('name')] = tag.get('value')
        
        return data
            
    def get_available_dates(self, dates_url):
        results = {}
        
        try:
            html = util.getPage(dates_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            for link in soup.find_all('a'):
                href = link.get('href')
                
                if href != None:
                    if href.startswith('mpSignUp.asp'):
                        date = link.get('title')
                        parsed_date = dateutil.parser.parse(date)
                        format_date = parsed_date.strftime(DATE_FORMAT)
                        results[format_date] = href
                
        except:
            print "exception"
            return results
        
        return results
    
    def update_museum_passID(self):
        '''
        only update the museum passid in the database
        '''
        #load cache
        filename = os.path.join(self.datadir, self.passid_local)
        if file_util.is_exist(filename):
            with codecs.open(filename, 'r', 'utf-8') as fin:
                cache = json.load(fin)
        else:
            cache = {}
        
        while True:
            changed = False
            
            #get the list of museums
            for museum in self.get_museums():
                museum_id = museum.MuseumID
                
                ticket_url = museum.ticket_url
                
                results = self.get_available_dates(ticket_url)
                
                if len(results) > 0:
                    print museum.name
                    
                for date, href in results.items():
                    p = href.rfind('=')
                    passid = href[p+1:]
                    
                    key = '@'.join([museum_id, date, passid])
                    if key in cache: continue
                    
                    cache[key] = False
                    changed = True
                    
            if not changed: break
    
        #save the cache
        with codecs.open(filename, 'w', 'utf-8') as fout:
            json.dump(cache, fout, indent=2)
    
    def upload_museum_passID(self):
        filename = os.path.join(self.datadir, self.passid_local)
        if file_util.is_exist(filename):
            with codecs.open(filename, 'r', 'utf-8') as fin:
                cache = json.load(fin)
        else:
            cache = {}
        
        count = 0
        for info in cache:
            if cache[info]: continue #already uploaded
            
            museum_id, date, passid = info.split('@')
            query = PassID.Query.filter(PassID=passid, MuseumID=museum_id, Date=date)
            if len(query) == 0:
                m_PassId = PassID(PassID=passid, MuseumID=museum_id, Date=date)
                m_PassId.save()
                count += 1
            cache[info] = True
            
        print "%d passID is updated" % count
                
        #save the cache
        with codecs.open(filename, 'w', 'utf-8') as fout:
            json.dump(cache, fout, indent=2)
        
    def update_museum_passID_remote(self):
        '''
        only update the museum passid in the database
        '''
        while True:
            changed = False
            
            #get the list of museums
            for museum in self.get_museums():
                museum_id = museum.MuseumID
                
                ticket_url = museum.ticket_url
                
                results = self.get_available_dates(ticket_url)
                
                if len(results) > 0:
                    print museum.name
                    
                for date, href in results.items():
                    p = href.rfind('=')
                    passid = href[p+1:]
                    
                    query = PassID.Query.filter(PassID=passid, MuseumID=museum_id, Date=date)
                    if len(query) == 0:
                        m_PassId = PassID(PassID=passid, MuseumID=museum_id, Date=date)
                        m_PassId.save()
                        changed = True
                        
            if not changed: break
    
    def update_museum_info(self):
        '''
        only update the museum info in the database
        '''
        
        success = True
        
        #get the list of museums
        for museum in self.get_museums():
            name = museum.name
            if name in self.updated_museums: continue
            
            success = False
            
            ticket_url = museum.ticket_url
            
            results = self.get_available_dates(ticket_url)
            
            for date, href in results.items():
                reserve_url = self.get_root_url(museum_list_url) + href
                data = self.get_measume_slots(reserve_url)
                
                museum.DonatedBy = data['DonatedBy']
                museum.iAddress = data['iAddress']
                museum.mdescription = data['mdescription']
                museum.mgraphic = data['mgraphic']
                museum.MuseumID = data['MuseumID']
                museum.iState = data['iState']
                museum.iTitle = data['iTitle']
                museum.iCity = data['iCity']
                museum.Institution = data['Institution']
                museum.PassID = data['PassID']
                
                self.updated_museums[name] = True
                museum.save()
                
                print "%s %s is updated, passid = %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), name, data['PassID'])
                break
        return success
    
    def update_museum_info_full(self, museum_list_url = None):
        '''
        extract the museum info from the orginal url
        '''
        if museum_list_url == None:
            museum_list_url = self.museum_list_url
            
        response = requests.get(museum_list_url, verify=False)
        page = BeautifulSoup(response.text, 'html.parser')
    
        tags = page.find_all('div', {'class':"museumlinkxml"})
        
        body = []
        head = []
        
        for tag in tags:
            for link in tag.find_all('a'):
                if len(link.text) == 0: continue
                
                name = link.text
                
                if name in self.updated_museums: continue
                
                ticket_url = self.get_root_url(museum_list_url) + link.get('href')
                
                museum_query = Museum.Query.filter(name=name)
                if len(museum_query) == 0: # this is a new museum
                    # create a new one
                    museum = Museum(name=name, ticket_url=ticket_url)
                    
                else:
                    #update the old one
                    museum = museum_query[0]
                    museum.ticket_url = ticket_url
                
                results = self.get_available_dates(ticket_url)
                
                for date, href in results.items():
                    reserve_url = self.get_root_url(museum_list_url) + href
                    data = self.get_measume_slots(reserve_url)
                    
                    head = data.keys()
                    body.append([name, ticket_url, date] + data.values()+ [reserve_url] ) 
                    
                    museum.DonatedBy = data['DonatedBy']
                    museum.iAddress = data['iAddress']
                    museum.mdescription = data['mdescription']
                    museum.mgraphic = data['mgraphic']
                    museum.MuseumID = data['MuseumID']
                    museum.iState = data['iState']
                    museum.iTitle = data['iTitle']
                    museum.iCity = data['iCity']
                    museum.Institution = data['Institution']
                    museum.PassID = data['PassID']
                    
                    break
                
                self.updated_museums[name] = True
                museum.save()
     
        #head = ['name', 'ticket_url', 'date'] + head + ['reserve_url']
        #file_util.write_matrix('../data/museum %s.txt' % (datetime.date.today().strftime(DATE_FORMAT_FILE)) , body, head)
    
    def check_result(self, html):
        ret = -1
        
        if html.find('Print out the pass by clicking the button blow') != -1: #succeed
            ret = 1
            
        if html.find('You have reached the max # of reservations') != -1: #failed
            ret = 2
        
        if html.find('the  Pass  you selected is not available') != -1: #failed
            ret = 3
        
        return ret
    
    def buy_ticket(self, reserve_url, library_cards):#work version
        results = {}
        
        response = requests.get(reserve_url, verify=False)
        page = BeautifulSoup(response.text, 'html.parser')
        
        tags = page.find_all('input')
        
        data = {}
        
        for tag in tags:
            if tag.get('name') == None: continue
            data[tag.get('name')] = tag.get('value')
        
        print data['PassID']
        
        for card, password in library_cards:
            data['iTitle'] = card
            data['Password'] = password
            
            r = requests.post(self.post_url, data=data)
            
            ret = self.check_result(r.text)
            
            #if ret != 1: print r.text
                
            results[card] = ret
            
            if ret == 1: #update the PassID
                passID = PassID(MuseumID=data['MuseumID'], Date=data['SignUpDate'])
                passID.PassID = data['PassID']
                passID.save()
                
        
        return results
        
    def test(self):
        pass
    
    def ticket_time_from_now_in_seconds(self):
        '''
        get the ticket time from now in seconds
        '''
        t = datetime.now(pacific_zone)
        ticket_time = datetime(t.year, t.month, t.day, hour=21, minute=0, second=0, microsecond=0, tzinfo=t.tzinfo)
        dt = ticket_time - t
        return dt.seconds
        
    def schedule_update_passid(self, dt=60):
        while True:
            try:
                self.update_museum_passID()
            except Exception as e:
                print e
            
            if self.ticket_time_from_now_in_seconds <= dt: continue #if there is enough time, sleep
            
            print "%s job will start %.2f mins later" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), dt/60.)
            
            if dt >= 5*60:
                self.upload_museum_passID()
            
            time.sleep(dt)
    
    def schedule_update_museum_info(self, dt=3600):
        while True:
            if self.update_museum_info():
                print 'All museums\' info are update to date'
                break
            
            #print "%s job will start %.2f mins later" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), dt/60.)
            time.sleep(dt)
    
    def profile_function(self):
        dates_url = 'http://www.libraryinsight.net/mpCalendar.asp?t=4553106&jx=y9p&pInstitution=Nordic%20Heritage%20Museum&mps=1929'
        
        time_start = time.clock()
        results = server.get_available_dates(dates_url)
        time_end = time.clock()
        
        print "decoding time: %s" % (time_end - time_start)
    

if __name__ == '__main__':
    
    import ConfigParser
    
    config = ConfigParser.RawConfigParser()
    config.read('../config/default.cfg')

    server = TicketServer(config.get('Parse', 'PARSE_APP_ID'), 
                                        config.get('Parse', 'PARSE_REST_API_KEY'), 
                                        config.get('Parse', 'PARSE_MASTER_KEY')
                                        )
    
    #server.profile_function()
    
    print server.check_time()
    
    
    
    
    
    