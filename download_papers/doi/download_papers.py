from processes import *

p = ProducerThread(name='producer', csv_file='C:/Users/sgmcart3/Documents/PhD Code/Digital_First/download_papers/data/dig_first.csv')
c=[]
for i in range(4):
    c.append(ConsumerThread(name='consumer_{}'.format(i), email='me@me.com'))

p.start()
time.sleep(2)
[c_x.start() for c_x in c]
time.sleep(2)