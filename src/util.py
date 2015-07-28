import urllib2

def getPage(url):
    response = urllib2.urlopen(url)
    data = response.read()
    return data
    