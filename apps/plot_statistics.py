import argparse
import matplotlib.pyplot as plt
import pandas as pd

from pymongo import MongoClient


def main(db_name: str, dev_eui: str) -> None:
    """
    Plots the histogram and the dataframe of the data.csv
    :param csv_file: File produced by get_csv.py
    :return: None
    """

    client = MongoClient()
    db = client[db_name]
    # client_sample_rate = '30T'
    table = db['tilt_t_s']
    pipeline = [{'$project': {'data': 1, '_id': 0}}, {'$unwind': '$data'},
                {'$project': {'ts': "$data.ts", 'T': "$data.val"}}]


    df = pd.DataFrame(table.aggregate(pipeline))
    # df.set_index('ts', inplace=True)

    print(df)
    # df.index = pd.to_datetime(df.index)
    # df = df.resample(client_sample_rate).mean()
    # df = df.diff(1).ffill().dropna()
    # df.to_csv(csv_file)
    #
    # df = pd.read_csv(csv_file, parse_dates=['ts'], index_col='ts')
    # print(df.describe())
    # print("numpy", df.values)
    #
    # gauss_mean, gauss_std = df['T'].mean(), df['T'].std()
    # print(f"gaussian params for data mean:{gauss_mean}, std: {gauss_std}"
    #
    # df.plot(kind='hist', bins=30, density=True)
    # df.plot()
    # plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_name', type=str, required=True,
                        help="Mongo db with tilt data")
    parser.add_argument('--dev_eui', type=str, required=True,
                        help="The device EUI to query")
    cmd_args = parser.parse_args()
    main(cmd_args.csv_file)
