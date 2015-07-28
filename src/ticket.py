from splinter import Browser

import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('../config/default.cfg')
library_card_number1 = config.get('library', 'library1')
library_card_password1 = config.get('library', 'password1')

library_card_number2 = config.get('library', 'library2')
library_card_password2 = config.get('library', 'password2')

library_card_number3 = config.get('library', 'library3')
library_card_password3 = config.get('library', 'password3')

library_cards = {library_card_number1:library_card_password1,
                library_card_number2:library_card_password2,
                library_card_number3:library_card_password3,
    }

def check_result(html):
    ret = -1
    
    if html.find('Print out the pass by clicking the button blow') != -1: #succeed
        ret = 1
        
    if html.find('You have reached the max # of reservations') != -1: #failed
        ret = 2
    
    return ret
    
def buy_ticket(url):#work version
    import requests
    from bs4 import BeautifulSoup
    
    response = requests.get(url, verify=False)
    page = BeautifulSoup(response.text, 'html.parser')
    
    tags = page.find_all('input')
    
    data = {}
    
    for tag in tags:
        if tag.get('name') == None: continue
        data[tag.get('name')] = tag.get('value')
    
    print data['PassID']
    
    for card, password in library_cards.items():
        print card, password
        
        data['iTitle'] = card
        data['Password'] = password
        #data['PassID'] = "4827"
        
        post_url = 'http://www.libraryinsight.net/mpPostCheckOut.asp?jx=y9p'
        r = requests.post(post_url, data=data)
        
        ret = check_result(r.text)
        
        print ret
        if ret == -1: 
            print r.text
            
        if  ret == 1: #success
            return True
    
    return False
    
    
if __name__ == "__main__":
    url = 'http://www.libraryinsight.net/mpSignUp.asp?t=1168245&jx=y9p&mps=1927&cFocus=title&pInstitution=Henry%20Art%20Gallery&etad=8/6/2015&pc=5645'
    
    success = buy_ticket(url)
    print success
    