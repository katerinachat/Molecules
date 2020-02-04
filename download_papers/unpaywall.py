import os
import wget
import requests

class Unpaywall:
    def __init__(self, email):
        self.url = 'https://api.unpaywall.org/v2/'
        self.email = email

        if not os.path.isdir('./papers'):
            os.mkdir('./papers')

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
                print('[ERROR] Response code %s' % (response.status_code))
                return 0
            
            return response.json()

        except Exception as e:
            print("[ERROR] %s" % (e))
            return 0

    def download_paper(self, doi, name):
        response = self.request_doi(doi)

        if response == 0:
            return
        
        if 'oa_locations' in response:
            oa_locations = response['oa_locations']
        else:
            with open('./logs/failed.txt', 'a') as f:
                f.write('%s\n' % doi)
                
            return

        for i, location in enumerate(oa_locations):
            pdf_url = location['url_for_pdf']

            try:
                wget.download(pdf_url, out='./papers/{}.pdf'.format(name))

                break
            except Exception as e:
                print('\nError occurred whilst downloading DOI {} \n{}'.format(doi, e))