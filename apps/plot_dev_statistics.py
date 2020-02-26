import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from pymongo import MongoClient


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
                'y': '$data.y'
            }
        }
    ]

    print('\n-----------------------')
    print('Device:', dev_eui.lower())

    data = pd.DataFrame(table.aggregate(pipeline))

    nan = data.isna().sum()

    print('Nan registered:\t\t', nan['x'])
    print('Entries registered:\t', data.count()['x'])

    print('Lost data: \t\t', nan['x']/data.count()['x']*100, "%")
    print(data)


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
