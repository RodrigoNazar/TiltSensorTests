import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from pymongo import MongoClient


def main(ip_addr: str, db_name: str, exc_file: str, exc_sheet: str) -> None:
    """

    Plots the histogram and the dataframe of the data.csv
    :param csv_file: File produced by get_csv.py
    :return: None
    """

    print('\n' + 15*'*', 'Corriendo el test QA1:', 15*'*', '\n')

    excel = pd.read_excel(exc_file, exc_sheet)
    never_seen_devices = []
    approved_devices = []
    not_approved_devices = []

    client = MongoClient(ip_addr, 27017)
    db = client[db_name]

    table = db['tilt_t_s']

    for ind in excel.index:
        device = excel['dev eui'][ind]

        if excel['Test 2'][ind] != 1:
            pipeline = [
                {
                    '$match': {
                        'devEUI': device.lower()
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

            # print('\n-----------------------')
            # print('Device:', device)

            data = pd.DataFrame(table.aggregate(pipeline)).diff(1).dropna()
            data = data.apply(lambda x: round(x / np.timedelta64(1, 'm')))

            if len(data) > 0:
                '''
                Descripción de cada dispositivo: 

                print('Datos:\n', data.describe())
                print('Moda:\n', 15.0 in data.mode().values)

                Mostrar histograma de cada dispositivo:

                data.plot(kind='hist', bins=100, title=device)
                plt.show()

                '''

                if 15.0 in data.mode().values:
                    approved_devices.append((device, ind + 2))

                else:
                    not_approved_devices.append((device, ind + 2))

            else:
                never_seen_devices.append(device.lower())

            if ind == 42:
                print('ind', ind)
                print('\n' + 100*'*' + '\n')
                print(excel['Test 2'][ind], type(excel['Test 2'][ind]))

    print('\nDispositivos de los que no se tiene información: \n')
    for device in never_seen_devices:
        print(device)

    print('\nDispositivos aprovados por el QA1:\n')
    for device in approved_devices:
        print('Índice:\t\t',
              device[1], '\nDevice EUI:\t', device[0])

    print('\nDispositivos no aprovados por el QA1:\n', '\n')
    for device in not_approved_devices:
        print('Índice:\t\t',
              device[1], '\nDevice EUI:\t', device[0], '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    parser.add_argument('--db_name', type=str, default='iot-ripios',
                        help="Mongo db with tilt data")
    parser.add_argument('--exc_file', type=str, required=True,
                        help="The excel file, where the devEUI's are")
    parser.add_argument('--exc_sheet', type=str, required=True,
                        help="The sheet of the excel file, where the devEUI's are")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr, cmd_args.db_name, cmd_args.exc_file,
         cmd_args.exc_sheet)
