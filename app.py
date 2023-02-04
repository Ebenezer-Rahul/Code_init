from flask import Flask,render_template,request,url_for,redirect,send_file, jsonify
import csv

app=Flask(__name__)

mythread = None
import logging

import threading

import time

from queue import Queue
from bs4 import BeautifulSoup

import requests

unvisited_links = Queue()

responses = Queue()

processed_links = {}

all_links = []
all_status_codes = []

done = False

Domain = "https://beautiful-soup-4.readthedocs.io/"

myLock = None

thread_count = None

total_links = 1;


@app.route("/",methods=["POST","GET"])
def home():
    global mythread
    global done
    global myLock
    global total_links
    # driver("https://toscrape.com/")
    print("hi")
    if request.method == "POST" :
        print(request.form)
        my_domain = request.form["domain"]
        print("Why")
        print(my_domain)
        myLock = threading.Semaphore(1)
        mythread = threading.Thread(target=driver, args=(my_domain,))
        mythread.start()
        return redirect("/") 

    return render_template("index.html")

@app.route('/recive', methods=["POST", "GET"])
def recive():
    path = "walker.png"
    global responses
    global done
    global myLock
    if myLock == None :
        return jsonify({"done" : "bro"})
    myLock.acquire()
    if done : 
        # mythread.join()
        myLock.release()
        # return jsonify({"done" : "bro"})
        return jsonify({ "isLink" : 0, "isDone" : 1, "link" : "null", "status_code" : 0, "total_links" : total_links});

    if responses.empty() : 
        myLock.release()
        return jsonify({ "isLink" : 0, "isDone" : 0, "link" : "null", "status_code" : 0, "total_links" : total_links});

    res = responses.get()
    myLock.release()
    return res

@app.route('/download')
def download():
    path = "BrokenLinks.csv"
    rows = zip(all_links, all_status_codes)
    with open("BrokenLinks.csv","w",encoding='UTF8', newline='') as f :
        writer = csv.writer(f)
        writer.writerow(zip(["link"] ,["status_code"]))
        for row in rows :
            writer.writerow(row)

    return send_file(path, as_attachment=True)



web_extension = [".com", ".in", ".us", ".co", ".io", ".me", ".net", ".org", ".wiki"]

error_codes = {
        400 : True,
        403 : True, 
        404 : True, 
        408 : True, 
        410 : True, 
        503 : True, 
        }


def driver(domain) :

    global Domain 
    global unvisited_links
    global responses 
    global all_links
    global all_status_codes
    global done
    global links
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
        
        temp = generateLinks(i,current_link)
        if temp == None :
            continue
        link, status_code = temp 

        i = i + 1
        
        # total_links += 1
        current_response = {
                "isLink" : 1,
                "isDone" : 0,
                "link" : link,
                "status_code" : status_code,
                "total_links" : total_links
                }
        all_links.append(link) 
        all_status_codes.append(status_code) 
        myLock.acquire()
        responses.put(current_response)
        print(link)
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
    print("done")
    pass


def generateLinks(i,ele):
    print("Thread {i} ".format(i=i))

    current_link, isValid = ele

    global processed_links
    global unvisited_links
    global total_links
    
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

        if processed_links.get(link) == None :
            total_links += 1
            processed_links[link] = True
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



app.run(debug=True)
