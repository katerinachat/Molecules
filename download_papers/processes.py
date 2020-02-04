import sys
import os
import threading
import time
import logging
import random
import string
import queue
import wget
import unpaywall

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, csvfile=None, authorsfile=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.csvfile = csvfile
        self.authorsfile = authorsfile
        self.start_iter = 0

        if os.path.isfile('./logs/last_iter.txt'):
            with open('./logs/last_iter.txt') as f:
                start_iter = f.read()
                self.start_iter = int(start_iter)

    def check_non_priority_queue(self):
        downloaded_papers = os.listdir('./papers/')

        with open('./logs/non_priority_authors.txt', 'r') as f:
            last_doi = None
            same_doi = []

            for i, line in enumerate(f):
                if '{}.pdf'.format(i) in downloaded_papers: continue

                if i % 10 == 0:
                    print('Downloading paper {}'.format(i))

                _line = line.replace('\n', '').split(',')
                doi = _line[-1]

                # Check if DOI is equal to last DOI
                if not doi == last_doi and not i == 0:
                    with open('./logs/doi_mapping.csv', 'a') as f:
                        f.write('%s,%s\n' % (doi, same_doi))
                    same_doi = []
                else:
                    same_doi.append(i)
                    continue
                    
                last_doi = doi

                while(True):
                    if not q.full():
                        item=(doi,i)
                        q.put(item) # Add paper to download queue
                        logging.debug('Putting ' + str(item)  
                              + ' : ' + str(q.qsize()) + ' doi in queue')
                        break
        return

    def run(self):        
        authors = {}

        with open(self.authorsfile, 'r') as f:
            for line in f:
                line = line.replace('\n', '').split(',')

                if not line[0] in authors:
                    authors[line[0]] = [{
                        'last name': line[0],
                        'first name': line[1],
                        'email': line[2],
                        'department': line[3],
                        'faculty': line[4]}]
                else:
                    authors[line[0]].append(
                        {
                        'last name': line[0],
                        'first name': line[1],
                        'email': line[2],
                        'department': line[3],
                        'faculty': line[4]}
                    )

        downloaded_papers = os.listdir('./papers/')

        with open(self.csvfile, 'r') as f:
            last_doi = None
            same_doi = []

            for i, line in enumerate(f):
                if i == 0: continue
                if i < self.start_iter: continue
                if '{}.pdf'.format(i) in downloaded_papers: continue

                if i % 10 == 0:
                    print('Downloading paper {}'.format(i))
                
                with open('./logs/last_iter.txt', 'w') as f:
                    f.write(str(i))

                _line = line.replace('\n', '').split(',')
                doi = _line[-1]

                # Check if DOI is equal to last DOI
                if not doi == last_doi and not i == 0:
                    with open('./logs/doi_mapping.csv', 'a') as f:
                        f.write('%s,%s\n' % (doi, same_doi))
                    same_doi = []
                else:
                    same_doi.append(i)
                    continue
                    
                last_doi = doi

                line_authors = ' '.join(_line[1:-2])
                author_in=False
                for last_name in authors:
                    if last_name in line_authors:
                        author_in=True
                        break

                if not author_in:
                    with open('./logs/non_priority_authors.txt', 'a') as f:
                        f.write('%s' % (line))
                    continue

                while(True):
                    if not q.full():
                        item=(doi,i)
                        q.put(item) # Add paper to download queue
                        logging.debug('Putting ' + str(item)  
                              + ' : ' + str(q.qsize()) + ' doi in queue')
                        break
                    
        self.check_non_priority_queue()
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

