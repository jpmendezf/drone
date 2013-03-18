import urllib
import Queue
from google import search
import urlparse
import re
import operator
from time import sleep
from Form import Form
from Scraper import ScrapeThread
from Worker import WorkThread
import sys

class Crawler:
  def __init__(self,base,proxy=False,proxy_port=False,robots=False):
    self.url_queue = Queue.Queue()
    self.html_queue = Queue.Queue()
    self.sqli_queue = Queue.Queue()
    self.visited_queue = Queue.Queue()
    self.pending = [] 
    self.visited = [] 

    self.emails = []
    self.sqli = []
    self.forms = []
    self.juicy = []
    self.base = base
    self.convert_base()
    self.robots = robots
    self.proxy = proxy
    self.proxy_port = proxy_port
    

  def check_proxy(self):
    proxy = {}
    proxy['http'] = 'http://' + str(self.proxy) + ":" + str(self.proxy_port)
    html = urllib.urlopen('http://icanhazip.com',proxies=proxy).read()
    html_no_proxy = urllib.urlopen('http://icanhazip.com').read()
    print "####Checking Proxy####"
    print "Using IP: " + html.strip()

    print "Original IP: " + html_no_proxy
    sleep(3)


  def convert_base(self):
    if not self.base.startswith('http'):
      self.base = "http://" + self.base
    self.base = urlparse.urlparse(self.base)

  def update_status(self):
    sys.stdout.write("\rVisited: %d | Pending: %d" % (self.visited_queue.qsize(), self.url_queue.qsize()))
    sys.stdout.flush()

  def spawn_threads(self):

    worker = WorkThread(self.html_queue, self.url_queue,self.base, self.sqli_queue)
    worker.setDaemon(True)
    worker.start()


    scrapers = []
    for i in range(5):
      t = ScrapeThread(self.url_queue, self.html_queue,self.visited_queue,self.proxy,self.proxy_port,worker)
      t.setDaemon(True)
      t.start()
      scrapers.append(t)

    while worker.isAlive():
      self.update_status()
      sleep(0.1)

    sys.stdout.write("\rKillin Scrapers..........")
    sys.stdout.flush()
    for thread in scrapers:
      thread.join()



  def start(self):
    self.url_queue.put(self.base)
    if self.proxy:
      self.check_proxy()
    if self.robots:
      self.url_queue.put(urlparse.urlparse(self.base.geturl() + "/robots"))
    self.spawn_threads()
    sys.stdout.write("\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r")
    sys.stdout.flush()

    self.status()

  def clean(self):
    self.visited = []
    self.pending = [] 
    self.emails = []

  def status(self):
    print "##################################"
    print "###########Drone Status###########"
    print "##################################"
    print "urls visited: " + str(self.visited_queue.qsize())
    print "possible sqli found: " + str(self.sqli_queue.qsize())
    print
    print "##Possible SQLi##"
    while not self.sqli_queue.empty():
      i = self.sqli_queue.get()
      print "sqli: " + i.geturl()
      self.sqli_queue.task_done()
    print
    if len(self.juicy) > 0:
      print "##Possible Juicy Files##"
      for i in self.juicy:
        print "juicy: " + i.geturl()
    print
    if len(self.forms) > 0:
      print "##Forms Detected##"
      for i in self.forms:
        print "forms: " + str(i)
    



