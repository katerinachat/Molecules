import sys
import os
import threading
import time
import logging
import random
import string
import queue
import wget
from unpaywall import Unpaywall
import json

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)
BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, csvfile=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.csvfile = csvfile
        
    def is_file(self, file):
        return os.path.isfile(file)
    
    def save_queue(self, queue):
        with open('./data/queue.txt', 'w') as filehandle:
            json.dump(basicList, filehandle)
    
    def load_queue(self):
        with open('./data/queue.txt', 'r') as filehandle:
            _list = json.load(filehandle)
        
        return _list
        
    def run(self):
        
        if self.is_file():
            dois = self.load_queue()
        else:
            # Read in csv file
            df = pd.read_csv('data/dig_first.csv', names=['Department', 'Name', 'Staff', 'Authors', 'Title', 'DOI'], header=0)

            # Find unique dois
            dois = df['DOI'].unique()
        
        # Add items to queue until dois is empty
        ind = 0
        while dois:
            if ind % 10:
                self.save_queue(dois)
                
            doi = dois.pop() # Get last doi
        
            while(True):
                if not q.full():
                    item=(doi,i)
                    q.put(item) # Add paper to download queue
                    logging.debug('Putting ' + str(item) + ' : ' + str(q.qsize()) + ' doi in queue')
                    break
            
            ind += 1
                        
        return

class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, email=None):
        super(ConsumerThread,self).__init__()
        self.target = target
        self.name = name
        self.email = email
        self.un = unpaywall.Unpaywall(self.email)
        return

    def run(self):
        while True:
            if not q.empty():
                item = q.get()
                doi = item[0]
                _id = item[1]

                logging.debug('Downloading ' + str(item) 
                              + ' : ' + str(q.qsize()) + ' items in queue')

                self.un.download_paper(doi, _id)

                time.sleep(random.random())
        return

