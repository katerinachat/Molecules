import os
import pandas as pd

from eprint import Eprint


CWD = os.getcwd()
ep = Eprint()


def record_error(eprint_id, doi, department, error):
    if not os.path.isdir('{}/logs'.format(CWD)):
        os.mkdir('{}/logs'.format(CWD))
    with open('./logs/error.csv', 'a') as f:
        f.write('{},{},{},{}\n'.format(eprint_id,
                                       doi,
                                       department,
                                       error))


def record_success(eprint_id, doi, department):
    if not os.path.isdir('{}/logs'.format(CWD)):
        os.mkdir('{}/logs'.format(CWD))
    with open('./logs/success.csv', 'a') as f:
        f.write('{},{},{}\n'.format(eprint_id,
                                    doi,
                                    department))


def main():
    df = pd.read_csv('./data/digital_first_papers.csv')
    print("Read in {} records".format(df.shape[0]))

    df = df.drop_duplicates('Publication Id')
    print("There are {} unique records".format(df.shape[0]))

    papers = list(zip(df['Publication Id'],
                      df['Department'],
                      df['DOI']))

    while len(papers) > 0:
        paper = papers.pop()
        eprint_id = paper[0]
        department = paper[1]
        doi = paper[2]
        resp = ep.download_paper(eprint_id,
                                 department)
        if resp == 1:
            record_success(eprint_id,
                           department,
                           doi)


if __name__ == '__main__':
    main()
