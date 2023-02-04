import logging

import threading

import time

from queue import Queue
from bs4 import BeautifulSoup

import requests

web_extension = [".com", ".in", ".us", ".co", ".io", ".me", ".net", ".org", ".wiki"]

error_codes = {
        400 : True,
        403 : True, 
        404 : True, 
        408 : True, 
        410 : True, 
        503 : True, 
        }


unvisited_links = Queue()

responses = Queue()

processed_links = {}

done = False

Domain = "https://beautiful-soup-4.readthedocs.io/"

myLock = None

thread_count = None

def driver(domain) :

    global Domain 
    global unvisited_links
    global responses 
    global done
    global myLock

    print(myLock, "hello")
    Domain = domain + '/'

    assert(type(domain) == str)

    unvisited_links.put((domain, True))

    i = 0

    while True :

        if unvisited_links.empty() :
            break

        current_link = unvisited_links.get()

        link, status_code = generateLinks(i,current_link)

        i = i + 1
        
        current_response = {
                "isLink" : 1,
                "isDone" : 0,
                "link" : link,
                "status_code" : status_code
                }

        myLock.acquire()
        responses.put(current_response)
        myLock.release()
        
        # if not generateLinks(current_link) :
            # print("Broken Link")
            # createJsonObject()
        # else :
            # createJsonObject()

        # sendJsonObject()

        pass

    myLock.acquire()
    responses.put({"isLink" : 0, "isDone" : 1, "link" : "null", "status_code" : 0 })
    myLock.release()

    done = True
    pass


def generateLinks(i,ele):
    print("Thread {i} ".format(i=i))

    current_link, isValid = ele

    global processed_links
    global unvisited_links
    
    processed_links[ele] = True
    
    ## SEND GET REQUEST TO CURRENT LINK
    try : 
        response = requests.get(current_link)
    except requests.exceptions.MissingSchema :
        try :
            response = requests.get("http:" + current_link)
        except :
            return None
    except :
        return None


    if error_codes.get(response.status_code) != None :
        print(current_link, "error")
        return (current_link, response.status_code)

    if not isValid :
        return (current_link, response.status_code)

    ## BeautifulSoup Parsing
    
    soup = BeautifulSoup(response.text, "lxml")

    ## FILTER LINKS FROM THE RESPONSE

    links = filterLinks(soup)

    while True :

        link = next(links)
        
        if link == None :
            break

        isProcessed = processed_links.get(link)

        if isProcessed == None :
            unvisited_links.put(link)
    
    return (current_link, response.status_code)

def filterLinks(soup) :

    link_tags = soup.find_all('a')

    global Domain

    for link_tag in link_tags :
        
        if link_tag.get('href') == None or len(link_tag['href']) == 0 or  link_tag['href'][0] == "#":
            continue

        if link_tag['href'][0] == '_':
            continue

        if len(link_tag) >= 4 and link_tag["href"][0 : 5] == "http" or match(link_tag['href']) :
            yield (link_tag['href'] , False)
        
        if link_tag['href'][0] == '/' or link_tag['href'][0] == '.':
           yield (Domain + link_tag['href'], True)


    link_tags = soup.find_all('link')
    for link_tag in link_tags :
        
        if link_tag.get('href') == None or len(link_tag['href']) == 0 or  link_tag['href'][0] == "#":
            continue

        if link_tag['href'][0] == '_':
            continue

        if len(link_tag) >= 4 and link_tag["href"][0 : 5] == "http" or match(link_tag['href']):
            yield (link_tag['href'] , False)
        
        if link_tag['href'][0] == '/' or link_tag['href'][0] == '.':
           yield (Domain + link_tag['href'], True)

    link_tags = soup.find_all('img')
    for link_tag in link_tags :
        
        if link_tag.get('src') == None or len(link_tag['src']) == 0 or  link_tag['src'][0] == "#":
            continue

        if link_tag['src'][0] == '_':
            continue

        if len(link_tag) >= 4 and link_tag["src"][0 : 5] == "http" or match(link_tag['src']):
            yield (link_tag['src'] , False)
        
        if link_tag['src'][0] == '/' or link_tag['src'][0] == '.':
           yield (Domain + link_tag['src'], True)

    link_tags = soup.find_all('script')
    for link_tag in link_tags :
        
        if link_tag.get('src') == None or len(link_tag['src']) == 0 or  link_tag['src'][0] == "#":
            continue

        if link_tag['src'][0] == '_':
            continue

        if len(link_tag) >= 4 and link_tag["src"][0 : 5] == "http" or match(link_tag['src']):
            yield (link_tag['src'] , False)
        
        if link_tag['src'][0] == '/' or link_tag['src'][0] == '.':
           yield (Domain + link_tag['src'], True)


    # print("What")
    yield None


def match(mylink) :
    for dotcom in web_extension :
        if dotcom in mylink :
            return True

    return False

# print("hello")

# driver("http://example.webscraping.com//")
# driver("https://toscrape.com/")

# print(unvisited_links)
