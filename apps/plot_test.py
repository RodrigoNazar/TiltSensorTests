import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from mongoengine import connect
from db.Test import Test
from pymongo import MongoClient


def main(ip_addr: str) -> None:

    connect('iot-ripios', host=ip_addr, port=27017)

    tests = {str(indx): test for indx, test in enumerate(Test.objects())}

    print('\nOpt\tName name\t\tTest description')
    for test in tests.keys():
        print(f"{test} -\t{tests[test].name}\t{tests[test].description}")

    resp = input('\nSelect a test\n> ')

    while resp not in tests.keys():
        print('\nUnkwnown input, try again:')
        resp = input('\nSelect a test\n> ')

    test = tests[resp]

    client = MongoClient(ip_addr, 27017)
    db = client['iot-ripios']

    table = db['tilt_t_s']

    pipeline = [
        {
            '$match': {
                'devEUI': test['devEUI']
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

    data = pd.DataFrame(table.aggregate(pipeline))

    data.set_index('ts', inplace=True)
    data.index = pd.to_datetime(data.index)
    data = data.ffill()
    data.sort_index(inplace=True)
    data['x'] = data['x'].apply(lambda x: round(x))
    data['y'] = data['y'].apply(lambda x: round(x))

    data = data.loc[test["start"]:test["end"]]

    print('DATA HEAD:\n', data.head())
    print('DESCRIPCION:\n', data.describe())

    data.plot(title=test["name"], xlim=(test["start"], test["end"]))
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr)
