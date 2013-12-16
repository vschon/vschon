import threading
import time

imdb = []
imdblock = threading.Lock()

class DataPlant(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.num = 10
        self.data = range(self.num)
    def run(self):
        for i in range(self.num):
            imdblock.acquire()
            imdb.append(self.data[i])
            imdblock.release()
            print 'add ' + str(self.data[i]) + '\n'
            time.sleep(1)

class DataFilter(threading.Thread):
    def __init__(self):
        self.count = 0
        self.datasource = None
        threading.Thread.__init__(self)

    def setdatasource(self,imdb):
        self.datasource = imdb

    def run(self):
        while self.count < 10:
            if imdblock.locked():
                print 'imdb not available\n'
                time.sleep(0.5)
            else:
                if self.count < len(self.datasource):
                    print 'i got ' + str(self.datasource[self.count])
                    self.count += 1
                    time.sleep(0.5)
                else:
                    print 'i got nothing'

filter = DataFilter()
filter.setdatasource(imdb)
plant = DataPlant()

filter.start()
plant.start()
plant.join()
filter.join()

print 'finished'


