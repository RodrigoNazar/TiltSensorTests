import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from mongoengine import connect
from db.Test import Test
from pymongo import MongoClient
from datetime import datetime


def main(ip_addr: str) -> None:

    connect('iot-ripios', host=ip_addr, port=27017)

    test = Test.objects(id="5e5922314ef27da492b801ab").first()

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

    drill_on_date = datetime.strptime('28-02-20 13:01:00', "%d-%m-%y %H:%M:%S")
    change_dr_date = datetime.strptime('28-02-20 13:37:00', "%d-%m-%y %H:%M:%S")
    drill_off_date = datetime.strptime('28-02-20 14:06:00', "%d-%m-%y %H:%M:%S")

    start_df = data.loc[test["start"]:drill_on_date]
    drill_1_df = data.loc[drill_on_date:change_dr_date]
    drill_2_df = data.loc[change_dr_date:drill_off_date]
    end_df = data.loc[drill_off_date:test["end"]]

    '''
    print('\nStart DF\n', start_df.describe(), '\n')
    print('\nFirst drill orientation\n', drill_1_df.describe(), '\n')
    print('\nSecond drill orientation\n', drill_2_df.describe(), '\n')
    print('\nEnd DF\n', end_df.describe(), '\n')
    '''

    # print('DATA:\n', data)
    # print('DESCRIPCION:\n', data.describe())

    mean_df = pd.DataFrame({
        'ts': [test["start"], drill_on_date, change_dr_date,
               drill_off_date, test["end"]],
        'x': [start_df.mean()["x"], start_df.mean()["x"],
              drill_1_df.mean()["x"], drill_2_df.mean()["x"],
              end_df.mean()["x"]],
        'y': [start_df.mean()["y"], start_df.mean()["y"],
              drill_1_df.mean()["y"], drill_2_df.mean()["y"],
              end_df.mean()["y"]]
    })

    mean_df.set_index('ts', inplace=True)
    mean_df.index = pd.to_datetime(mean_df.index)

    fig, axes = plt.subplots(nrows=2, ncols=1)
    mean_df['x'].plot(drawstyle='steps', ax=axes[0])
    data['x'].plot(ax=axes[0], title='X axis')

    mean_df['y'].plot(drawstyle='steps', ax=axes[1])
    data['y'].plot(ax=axes[1], title='y axis')

    # fig, axs = plt.subplots(2)
    # axs[0, 0].plot(mean_df['x'], drawstyle='steps')
    # axs[0, 0].plot(data['x'])
    # axs[0, 0].set_title('Eje x')
    # plt.plot(mean_df['y'], drawstyle='steps')
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr)
