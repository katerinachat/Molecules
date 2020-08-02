from processes import *


def main():
    p = ProducerThread(name='producer', csv_file='./data/eprint_errors.csv')
    c=[]
    for i in range(4):
        c.append(ConsumerThread(name='consumer_{}'.format(i), email='me@me.com'))

    p.start()
    time.sleep(2)
    [c_x.start() for c_x in c]
    time.sleep(2)


if __name__ == '__main__':
    main()
