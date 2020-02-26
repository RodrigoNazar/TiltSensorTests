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

    never_seen_devices = []

    client = MongoClient(ip_addr, 27017)
    db = client[db_name]

    table = db['tilt_t_s']

    pipeline = [
        {
            '$match': {
                'devEUI': dev_eui.lower()
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
                'ts': '$data.ts'
            }
        }
    ]

    print('\n-----------------------')
    print('Device:', dev_eui.lower())

    data = pd.DataFrame(table.aggregate(pipeline)).diff(1).dropna()
    data = data.apply(lambda x: round(x / np.timedelta64(1, 'm')))

    if len(data) > 0:
        print('Datos:\n', data.describe())

        data.plot(kind='hist', bins=100, title=dev_eui)
        plt.show()
    else:
        never_seen_devices.append(dev_eui.lower())

    print('Dispositivos de los que no se tiene información: \n',
          never_seen_devices)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    parser.add_argument('--db_name', type=str, default='iot-ripios',
                        help="Mongo db with tilt data")
    parser.add_argument('--exc_file', type=str, required=True,
                        help="The excel file, where the devEUI's are")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr, cmd_args.db_name, cmd_args.exc_file)
