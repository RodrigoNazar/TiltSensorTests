import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from pymongo import MongoClient
from datetime import datetime


def main(ip_addr: str, db_name: str, dev_eui: str) -> None:
    """

    Plots the histogram and the dataframe of the data.csv
    :param csv_file: File produced by get_csv.py
    :return: None
    """
    dev_eui = dev_eui.lower()

    client = MongoClient(ip_addr, 27017)
    db = client[db_name]

    table = db['tilt_t_s']

    pipeline = [
        {
            '$match': {
                'devEUI': dev_eui
            }
        }, {
            '$sort': {
                'updatedAt': -1
            }
        }, {
            '$project': {
                'data': 1,
                '_id': 0
            }
        }, {
            '$unwind': {
                'path': '$data'
            }
        }, {
            '$project': {
                'x': '$data.x',
                'y': '$data.y',
                'ts': '$data.ts'
            }
        }
    ]

    print('\n-----------------------')
    print('Device:', dev_eui.lower())

    data = pd.DataFrame(table.aggregate(pipeline))

    # % of data loss
    nan = data.isna().sum()
    print('Nan registered:\t\t', nan['x'])
    print('Entries registered:\t', data.count()['x'])

    print('Lost data: \t\t', nan['x']/data.count()['x']*100, "%")

    data.set_index('ts', inplace=True)
    data.index = pd.to_datetime(data.index)
    # data.index = data.index.map(lambda x: x.replace(second=0, microsecond=0))
    data = data.ffill()
    data.sort_index(inplace=True)
    data['x'] = data['x'].apply(lambda x: round(x))
    data['y'] = data['y'].apply(lambda x: round(x))

    # start_h = datetime(year=2020, month=2, day=26, hour=21, minute=15)
    # end_h = datetime(year=2020, month=2, day=26, hour=21, minute=50)

    # data = data.loc[start_h:end_h]

    # print(data.describe())

    print(data.tail())
    print(datetime.utcnow())

    # data['x'].plot(xlim=(start_h, end_h), ylim=(-90, 25))
    # plt.show()
    # data['y'].plot(xlim=(start_h, end_h), ylim=(-90, 25))
    data.plot()
    plt.show()

    '''
    # Show data hist
    pipeline.remove(pipeline[-1])
    pipeline.append({
        '$project': {
            'ts': '$data.ts'
        }
    })

    hist_data = pd.DataFrame(table.aggregate(pipeline))

    hist_data = hist_data.diff(1).dropna()
    hist_data = hist_data.apply(lambda x: round(x / np.timedelta64(1, 'm')))

    if len(hist_data) > 0:
        print('Datos:\n', hist_data.describe())

        hist_data.plot(kind='hist', bins=100, title=dev_eui, xlim=(-1, 50))
        plt.show()
    else:
        print('Dispositivo sin datos')
    '''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    parser.add_argument('--db_name', type=str, default='iot-ripios',
                        help="Mongo db with tilt data")
    parser.add_argument('--dev_eui', type=str, required=True,
                        help="Device thats being queried")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr, cmd_args.db_name, cmd_args.dev_eui)
