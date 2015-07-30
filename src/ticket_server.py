#https://github.com/dgrtwo/ParsePy
from parse_rest.connection import register
import parse_rest
import datetime
import time
from tables import *
import json
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

DATE_FORMAT = "%d/%m/%Y"
DATE_FORMAT_FILE = "%d-%m-%Y"

class TicketServer:
    def __init__(self, app_id, api_key, master_key):
        register(app_id, api_key)
        
        self.updated_museums = {}
        self.museums = None
    
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
            
    def get_available_dates(self, ticket_url):
        dates = []
        hrefs = []
        
        try:
            html = util.getPage(ticket_url)
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
            
            dates, hrefs = self.get_available_dates(ticket_url)
            
            for date, href in zip(dates, hrefs):
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
        
    def update_museum_info_full(self, museum_list_url):
        '''
        extract the museum info from the orginal url
        '''
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
                
                dates, hrefs = self.get_available_dates(ticket_url)
                
                for date, href in zip(dates, hrefs):
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
                    
                    self.updated_museums[name] = True
                    museum.save()
                    
                    print "%s is updated, passid = %s" % (name, data['PassID'])
                    break
     
        #head = ['name', 'ticket_url', 'date'] + head + ['reserve_url']
        #file_util.write_matrix('../data/museum %s.txt' % (datetime.date.today().strftime(DATE_FORMAT_FILE)) , body, head)
    
    def test(self):
        pass

if __name__ == '__main__':
    
    import ConfigParser
    
    config = ConfigParser.RawConfigParser()
    config.read('../config/default.cfg')

    server = TicketServer(config.get('Parse', 'PARSE_APP_ID'), 
                                        config.get('Parse', 'PARSE_REST_API_KEY'), 
                                        config.get('Parse', 'PARSE_MASTER_KEY')
                                        )
    
    
    museum_list_url = config.get('Library', 'museum_list_url')
    
    dt = 1
    while True:
        if server.update_museum_info():
            print 'All museums\' info are update to date'
            break
        
        #print "%s job will start %.2f mins later" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), dt/60.)
        time.sleep(dt)
    
    #server.test()
    #course_mirror_server.run(cid)
    #course_mirror_server.change_demo_user()