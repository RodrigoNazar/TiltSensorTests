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
    pipeline = [{'$match': {'devEUI': dev_eui}},
                {'$project': {'data': 1, '_id': 0}}, {'$unwind': '$data'},
                {'$project': {'ts': '$data.ts'}}]

    # table = table.find({"devEUI": dev_eui}, projection={"data": 1, "_id": 0})
    # print(table.aggregate(pipeline))

    df = pd.DataFrame(table.aggregate(pipeline))
    df = df.diff().dropna()
    # df['ts'] = df['ts'].apply(lambda x: x.seconds())

    df['ts'] = df['ts'].apply(lambda x: x / np.timedelta64(1, 'm'))
    df.plot.hist(bins=100)
    plt.show()
    # print(df['ts'].dt.seconds())
    # df.ts = pd.to_datetime(df.ts)
    # df.ts = df.ts.dt.total_seconds()
    # df.diff(-1)['ts'].dropna().plot(kind='hist')
    # plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    parser.add_argument('--db_name', type=str, default='iot-ripios',
                        help="Mongo db with tilt data")
    parser.add_argument('--dev_eui', type=str, required=True,
                        help="The device EUI to query")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr, cmd_args.db_name, cmd_args.dev_eui)
