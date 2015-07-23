from splinter import Browser

import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('default.cfg')
library_card_number1 = config.get('library', 'library1')
library_card_password1 = config.get('library', 'password1')

library_card_number2 = config.get('library', 'library2')
library_card_password2 = config.get('library', 'password2')

print library_card_number2, type(library_card_number2)
print library_card_password2, type(library_card_password2)

def buy_ticket(url):#work version
    import requests
    from bs4 import BeautifulSoup
    
    response = requests.get(url, verify=False)
    page = BeautifulSoup(response.text, 'html.parser')
    
    tags = page.find_all('input')
    
    data = {}
    
    for tag in tags:
        if tag.get('name') == None: continue
        
        print tag.get('name'), tag.get('value')
        
        data[tag.get('name')] = tag.get('value')
    
    
    data['iTitle'] = library_card_number2
    data['Password'] = library_card_password2
    
    post_url = 'http://www.libraryinsight.net/mpPostCheckOut.asp?jx=y9p'
    r = requests.post(post_url, data=data)
    
    if r.text.find('Email and Phone Saved') != -1:
        return True
    
    #failed, use the second card
    data['iTitle'] = library_card_number1
    data['Password'] = library_card_password1
    
    post_url = 'http://www.libraryinsight.net/mpPostCheckOut.asp?jx=y9p'
    r = requests.post(post_url, data=data)
    
    if r.text.find('Email and Phone Saved') != -1:
        return True
    
    return False
    
    
if __name__ == "__main__":
    url = 'http://www.libraryinsight.net/mpSignUp.asp?t=1173441&jx=y9p&mps=1927&cFocus=title&pInstitution=Henry Art Gallery&etad=7/31/2015&pc=5645'
    buy_ticket(url)
    