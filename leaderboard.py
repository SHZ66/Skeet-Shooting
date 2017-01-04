import csv, os, pickle

class Record():
    def __init__(self, name='', score=0):
        self.name = name.strip()
        if self.name == '':
            self.name = 'Anonymous'
        self.score = score
    
    def __str__(self):
        return '%s: %d'%(self.name, self.score)
    
    def __repr__(self):
        return self.__str__()

'''
def readRecords(filename):
    records = []
    if os.path.exists(filename):
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if len(row) >= 2:
                    record = Record(row[0], int(row[1]))
                    records.append(record)
    return records

def writeRecords(filename, records):
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for record in records:
            writer.writerow([record.name, str(record.score)])

def appendRecords(filename, records):
    with open(filename, 'ab') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for record in records:
            writer.writerow([record.name, str(record.score)])

def sortRecords(records):
    def compare(a,b):
        return a.score < b.score
    records.sort(compare)
    return records
'''

def readRecords(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return []

def writeRecords(filename, records):
    with open(filename, 'wb') as f:
        pickle.dump(records, f, pickle.HIGHEST_PROTOCOL)

def sortRecords(records):
    def compare(a,b):
        return a['score'] < b['score']
    records.sort(compare)
    return records