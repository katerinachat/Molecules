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


def read_data(directory):
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
        
    def run(self):
        df = pd.read_csv(self.csv_file)
        print("Read in {} records".format(df.shape[0]))

        df = df.drop_duplicates('Publication Id')
        print("There are {} unique records".format(df.shape[0]))

        logs = read_data("{}/logs".format(CWD))
        print("Loaded {} records from logs".format(logs.shape[0]))

        downloaded_papers = logs['eprint'].to_list()
        to_download = df[~df['Publication Id'].isin(downloaded_papers)]
        print("There are {} papers left to download".format(to_download.shape[0]))

        papers = list(zip(to_download['Publication Id'],
                          to_download['Department'],
                          to_download['DOI']))

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
        self.unpaywall = Unpaywall(self.email)
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

                logging.debug('Downloading ' + str(item) + ' : ' + str(q.qsize()) + ' items in queue')

                key = str(uuid.uuid1()).replace('-', '') # Create a random unique key
                status = self.unpaywall.download_paper(doi, key)
                # If successful, append record to csv
                if status == 1:
                    self.record_doi_map(doi, key)

                time.sleep(random.random())
        return

