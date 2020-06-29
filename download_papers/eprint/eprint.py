import os
import urllib
import requests


CWD = os.getcwd()


class Eprint():
    def __init__(self):
        self.base_url = 'https://livrepository.liverpool.ac.uk/cgi/exportpid/eprint/'
        self.paper_dir = '{}/papers'.format(CWD)
        self.log_dir = '{}/logs'.format(CWD)

        if not os.path.isdir('{}/papers'.format(CWD)):
            os.mkdir('{}/papers'.format(CWD))

        if not os.path.isdir('{}/logs'.format(CWD)):
            os.mkdir('{}/logs'.format(CWD))

    def search_paper(self, eprint_id):
        url = self.base_url + '{}/JSON/paper.json'.format(eprint_id)

        headers = {
            'Accept': 'application/json'
        }

        try:
            response = requests.get(
                url,
                headers=headers
            )
            
            if not response.status_code == 200:
                print('[ERROR] Response code %s' % (response.status_code))
                return 0
            
            return response.json()

        except Exception as e:
            print("Error when searching for query %s:\n%s" % (url, e))

        return 0
    
    def download_paper(self, eprint_id,
                       department):
        response = self.search_paper(eprint_id)
        
        if response == 0:
            return 0

        file_dir = '{}/{}'.format(self.paper_dir,
                                  department)

        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        if 'documents' in response.keys():
            for document in response['documents']:
                for _file in document['files']:
                    if _file['mime_type'] == 'application/pdf':
                        pdf_response = requests.get(_file['uri'], stream=True)
                        if not pdf_response.status_code == 200:
                            continue
                        with open('{}/{}.pdf'.format(file_dir, eprint_id), 'wb') as f:
                            f.write(pdf_response.content)
                        return 1
        return 0
