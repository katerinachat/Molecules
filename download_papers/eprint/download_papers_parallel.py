import os

from processes import *
from multiprocessing import cpu_count


CWD = os.getcwd()


def main():
    p = ProducerThread(name='producer', csv_file='{}/data/dig_first.csv'.format(CWD))
    c=[]
    n_procs = cpu_count() if cpu_count() > 4 else 4
    print("Using {} processes".format(n_procs))
    for i in range(n_procs):
        c.append(ConsumerThread(name='consumer_{}'.format(i)))

    p.start()
    time.sleep(2)
    [c_x.start() for c_x in c]
    time.sleep(2)


if __name__ == '__main__':
    main()
