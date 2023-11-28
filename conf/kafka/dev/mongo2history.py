#!/usr/bin/env python3
from datetime import datetime
from operator import itemgetter
import pymongo

if __name__ == '__main__':

    mongo_client = pymongo.MongoClient( 'localhost', username='root', password='example')
    mongo_db = mongo_client["daq"]
    mongo_col = mongo_db["odb"] 
    # ogni giorno ci sono 144 record
    nday = 144*5
    cursor = mongo_col.find({}).sort([('_id', -1)]).limit(nday)
    data_struct = (255, 14, 254, 283, 285, 287)
    print ('epoch', 'date', ' '.join(['var_'+str(x) for x in data_struct]))
    for document in cursor:
        epoch = document['Alarms']['Alarms']['Gas Alarm 2']['Checked last']
        date = datetime.fromtimestamp(epoch).strftime('%Y-%m-%dT%H:%M:%S')
        data = document['Equipment']['GasSystem']['Variables']['Measured']
        data = itemgetter(*data_struct)(data)
        data = [str(x) for x in data]
        data = ' '.join(data)
        print(epoch, date, data)
        