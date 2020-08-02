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
                return 0, response.status_code
            
            return response.json(), None

        except Exception as e:
            # print("[ERROR] %s" % (e))
            self.record_error('request', 'request exception', e, doi)
            return 0, e
        
        return 0, None

    def download_paper(self, doi, department, name):
        response, err = self.request_doi(doi)

        if response == 0: # Request failed
            return 0, err

        file_dir = '{}/{}'.format(self.paper_dir,
                                  department)

        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        # Try best location
        if 'best_oa_location' in response.keys():
            try:
                pdf_url = response['best_oa_location']['url_for_pdf']
                urllib.request.urlretrieve(pdf_url, filename='{}/{}/{}.pdf'.format(self.paper_dir,
                                                                                   department,
                                                                                   name))
            except Exception as e:
                return 0, e
                
            if self.is_file('{}/{}/{}.pdf'.format(self.paper_dir,
                                                  department,
                                                  name)):
                return 1, None

        # If best location didn't work, try alternative locations
        if 'oa_locations' in response.keys():
            oa_locations = response['oa_locations']
            
            for i, location in enumerate(oa_locations):
                try:
                    pdf_url = location['url_for_pdf']
                    urllib.request.urlretrieve(pdf_url, filename='{}/{}/{}.pdf'.format(self.paper_dir,
                                                                                       department,
                                                                                       name))
                    
                    if self.is_file('{}/{}/{}.pdf'.format(self.paper_dir,
                                                          department,
                                                          name)):
                        return 1, None
                    
                except Exception as e:
                    continue

        else:
            return 0, "No location"

        if not self.is_file('{}/{}/{}.pdf'.format(self.paper_dir,
                                                  department,
                                                  name)):
            return 0, "Failed to download"
        
        return 0, None