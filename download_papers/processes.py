import sys
import os
import threading
import time
import logging
import random
import string
import queue
import json
import pandas as pd
import uuid
from unpaywall import Unpaywall

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)
BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, csv_file=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.csv_file = csv_file
        
    def is_file(self, file):
        return os.path.isfile(file)
    
    def save_queue(self, queue):
        with open('./logs/queue.txt', 'w') as f:
            json.dump(queue, f)
    
    def load_queue(self):
        with open('./logs/queue.txt', 'r') as f:
            _list = json.load(f)
        
        return _list
        
    def run(self):
        
        if self.is_file('./logs/queue.txt'):
            dois = self.load_queue()
        else:
            # Read in csv file
            df = pd.read_csv(self.csv_file, names=['Department', 'Name', 'Staff', 'Authors', 'Title', 'DOI'], header=0)

            # Find unique dois
            dois = df['DOI'].unique().tolist()
        
        # Add items to queue until dois is empty
        ind = 0
        while len(dois) > 0:
            if ind % 10:
                self.save_queue(dois)
                
            doi = dois.pop() # Get last doi
        
            while(True):
                if not q.full():
                    item=(doi,ind)
                    q.put(item) # Add paper to download queue
                    # logging.debug('Putting ' + str(item) + ' : ' + str(q.qsize()) + ' doi in queue')
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
        self.unpaywall = Unpaywall(self.email)
        return

    def record_doi_map(self, doi, key):
        with open('./logs/{}_doi_map.csv'.format(self.name), 'a') as f:
            f.write('{},{}\n'.format(doi, key))

    def run(self):
        while True:
            if not q.empty():
                item = q.get()
                doi = item[0]
                _id = item[1]

                logging.debug('Downloading ' + str(item) + ' : ' + str(q.qsize()) + ' items in queue')

                key = str(uuid.uuid1()).replace('-', '') # Create a random unique key
                status = self.unpaywall.download_paper(doi, key)
                # If successful, append record to csv
                if status == 1:
                    self.record_doi_map(doi, key)

                time.sleep(random.random())
        return

