import uuid
import pandas as pd
from unpaywall import Unpaywall


csv_file = './data/dig_first.csv'
paper_dir = './papers'

unpaywall = Unpaywall('me@me.com')


def record_doi_map(doi, key):
    with open('./logs/doi_map.csv', 'a') as f:
        f.write('{},{}\n'.format(doi, key))


def main():
    # Read in csv file
    df = pd.read_csv(csv_file, names=['Department', 'Name', 'Staff', 'Authors', 'Title', 'DOI'], header=0)

    # Find unique dois
    dois = df['DOI'].unique().tolist()

    while len(dois) > 0:
        key = str(uuid.uuid1()).replace('-', '') # Create a random unique key
        doi = dois.pop() # Fetch doi at top of queue
        status = unpaywall.download_paper(doi, key) # Try download paper

        # If successful, append record to csv
        if status == 1:
            record_doi_map(doi, key)


if __name__ == '__main__':
    main()
