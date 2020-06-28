import os
import urllib
import requests

class Unpaywall:
    def __init__(self, email):
        self.url = 'https://api.unpaywall.org/v2/'
        self.email = email
        self.paper_dir = '{}/papers'.format(os.getcwd())

        if not os.path.isdir('{}/papers'.format(os.getcwd())):
            os.mkdir('{}/papers'.format(os.getcwd()))

    def record_error(self, action, message, err_message, doi):
        with open('logs/unpaywall_error.log', 'a') as f:
            f.write('{},{},{},{}\n'.format(action, message, err_message, doi))
    
    def is_file(self, file):
        return os.path.isfile(file)
    
    def request_doi(self, doi):
        url = self.url + doi
        
        params = {
            'email': self.email
        }

        try:
            response = requests.get(
                url,
                params=params,
            )

            if not response.status_code == 200:
                # print('[ERROR] Response code %s' % (response.status_code))
                self.record_error('request', 'invalid status code', response.status_code, doi)
                return 0
            
            return response.json()

        except Exception as e:
            # print("[ERROR] %s" % (e))
            self.record_error('request', 'request exception', e, doi)
            return 0

    def download_paper(self, doi, name):
        response = self.request_doi(doi)

        if response == 0: # Request failed
            return 0
        
        # Try best location
        if 'best_oa_location' in response.keys():
            try:
                pdf_url = response['best_oa_location']['url_for_pdf']
                urllib.request.urlretrieve(pdf_url, filename='{}/{}.pdf'.format(self.paper_dir, name))
            except Exception as e:
                self.record_error('download', 'failed best location', e, doi)
                
            if self.is_file('{}/{}.pdf'.format(self.paper_dir, name)):
                return 1

        # If best location didn't work, try alternative locations
        if 'oa_locations' in response.keys():
            oa_locations = response['oa_locations']
            
            for i, location in enumerate(oa_locations):
                try:
                    pdf_url = location['url_for_pdf']
                    urllib.request.urlretrieve(pdf_url, filename='{}/{}.pdf'.format(self.paper_dir, name))
                    
                    if self.is_file('{}/{}.pdf'.format(self.paper_dir, name)):
                        return 1
                    
                except Exception as e:
                    self.record_error('download', 'failed location {}'.format(i), e, doi)
                    continue

        else:
            self.record_error('download', 'no download locations', None, doi)
            return 0

        if not self.is_file('{}/{}.pdf'.format(self.paper_dir, name)):
            self.record_error('download', 'failed all locations', None, doi)
            return 0