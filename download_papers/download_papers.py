from processes import *

p = ProducerThread(name='producer', csvfile='./data/digital_first.csv', authorsfile='./data/turing_fellows.csv')
c=[]
for i in range(4):
    c.append(ConsumerThread(name='consumer_{}'.format(i), email='d1901417@urhen.com'))

p.start()
time.sleep(2)
[c_x.start() for c_x in c]
time.sleep(2)