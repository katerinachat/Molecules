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
from eprint import Eprint


logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)
BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)
CWD = os.getcwd()


def read_data(directory):
    try:
        temp_dfs = []
        for filename in os.listdir('{}'.format(directory)):
            if 'csv' in filename:
                temp_df = pd.read_csv('{}/{}'.format(directory, filename),
                                    names=['eprint', 'doi', 'department', 'response'],
                                    sep='\t')
                temp_dfs.append(temp_df)
            else:
                continue
        print('{}: Loaded {} CSV files'.format(directory, len(temp_dfs)))
        df = pd.concat(temp_dfs, axis=0, ignore_index=True)
        return df
    except:
        return None


def record_error(eprint_id, worker, doi, department, error):
    if not os.path.isdir('{}/logs'.format(CWD)):
        os.mkdir('{}/logs'.format(CWD))
    with open('./logs/{}_error.csv'.format(worker), 'a') as f:
        f.write('{}\t{}\t{}\t{}\n'.format(eprint_id,
                                          doi,
                                          department,
                                          error))


def record_success(eprint_id, worker, doi, department, err):
    if not os.path.isdir('{}/logs'.format(CWD)):
        os.mkdir('{}/logs'.format(CWD))
    with open('./logs/{}_success.csv'.format(worker), 'a') as f:
        f.write('{}\t{}\t{}\t{}\n'.format(eprint_id,
                                          doi,
                                          department,
                                          err))


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
        df = pd.read_csv(self.csv_file)
        print("Read in {} records".format(df.shape[0]))

        df = df.drop_duplicates('Publication Id')
        print("There are {} unique records".format(df.shape[0]))

        logs = read_data("{}/logs".format(CWD))
        if logs is not None:
            print("Loaded {} records from logs".format(logs.shape[0]))

            downloaded_papers = logs['eprint'].to_list()
            to_download = df[~df['Publication Id'].isin(downloaded_papers)]
            print("There are {} papers left to download".format(to_download.shape[0]))

            papers = list(zip(to_download['Publication Id'],
                            to_download['Department'],
                            to_download['DOI']))
        else:
            papers = list(zip(df['Publication Id'],
                              df['Department'],
                              df['DOI']))

        while len(papers) > 0:
            paper = papers.pop()
            eprint_id = paper[0]
            department = paper[1]
            doi = paper[2]
            item = (eprint_id, department, doi)

            while(True):
                if not q.full():
                    q.put(item) # Add paper to download queue
                    # logging.debug('Putting ' + str(item) + ' : ' + str(q.qsize()) + ' doi in queue')
                    break                        
        return


class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, email=None):
        super(ConsumerThread,self).__init__()
        self.target = target
        self.name = name
        self.email = email
        self.eprint = Eprint()
        return

    def record_doi_map(self, doi, key):
        with open('./logs/{}_doi_map.csv'.format(self.name), 'a') as f:
            f.write('{},{}\n'.format(key, doi))

    def run(self):
        while True:
            if not q.empty():
                item = q.get()
                eprint_id = item[0]
                department = item[1]
                doi = item[2]
                logging.debug('Downloading ' + str(eprint_id) + ' : ' + str(q.qsize()) + ' items in queue')
                status, error = self.eprint.download_paper(eprint_id, department)
                if status == 1:
                    record_success(eprint_id, self.name, doi, department, error)
                else:
                    record_error(eprint_id, self.name, doi, department, error)
                time.sleep(random.random())
        return

