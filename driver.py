
import logging

import threading

import time

from queue import Queue
from bs4 import BeautifulSoup

import requests


error_codes = {
        400 : True,
        403 : True, 
        404 : True, 
        405 : True, 
        406 : True, 
        408 : True, 
        409 : True, 
        500 : True, 
        501 : True, 
        502 : True, 
        503 : True, 
        504 : True, 
        505 : True, 
        506 : True, 
        508 : True,
        510 : True
        }


unvisited_links = Queue()

processed_links = {}

Domain = "https://beautiful-soup-4.readthedocs.io"

threads = []

queue_lock = threading.Semaphore(1)
sync_lock = threading.Semaphore(1)
dict_lock = threading.Semaphore(1)
lock = threading.Semaphore(1)

def driver(domain) :

    global Domain 
    global unvisited_links

    global queue_lock
    global sync_lock

    Domain = domain + '/'

    assert(type(domain) == str)

    queue_lock.acquire()
    unvisited_links.put((domain, True))
    queue_lock.release()

    i = 0

    while True :
       
        sync_lock.acquire()

        queue_lock.acquire()

        if unvisited_links.empty() : 
            break
        
        current_link = unvisited_links.get()

        queue_lock.release()

        # generateLinks(current_link)

        thread = threading.Thread(target=generateLinks, args=(i,current_link))
        i = i + 1
        print(current_link) 
        thread.start()

        threads.append(thread)

        # if not generateLinks(current_link) :
            # print("Broken Link")
            # createJsonObject()
        # else :
            # createJsonObject()

        # sendJsonObject()

        pass

    for thread in threads :
        thread.join()
        print("joined")

    pass


def generateLinks(i,ele):
    print("Thread {i} ".format(i=i))

    current_link, isValid = ele

    global queue_lock
    global sync_lock
    global dict_lock
    global processed_links
    global unvisited_links
    
    queue_lock.acquire()
    processed_links[ele] = True
    print(len(processed_links.keys()))
    queue_lock.release()
    
    ## SEND GET REQUEST TO CURRENT LINK

    response = requests.get(current_link)

    if error_codes.get(response.status_code) != None :
        return False

    if not isValid :
        return True

    ## BeautifulSoup Parsing
    
    soup = BeautifulSoup(response.text, "lxml")

    ## FILTER LINKS FROM THE RESPONSE

    links = filterLinks(soup)

    while True :

        link = next(links)
        
        if link == None :
            break


        queue_lock.acquire()

        isProcessed = processed_links.get(link)

        if isProcessed == None :
            unvisited_links.put(link)
            sync_lock.release()

        queue_lock.release()

    return True

def filterLinks(soup) :

    link_tags = soup.find_all('a')

    global Domain

    for link_tag in link_tags :
        
        if link_tag.get('href') == None or len(link_tag['href']) == 0 or  link_tag['href'][0] == "#":
            continue

        if link_tag['href'][0] == '_':
            continue

        if len(link_tag) >= 4 and link_tag["href"][0 : 5] == "http" :
            yield (link_tag['href'] , False)
        
        if link_tag['href'][0] == '/' or link_tag['href'][0] == '.':
           yield (Domain + link_tag['href'], True)


    yield None


print("hello")

driver(Domain)

print(unvisited_links)
