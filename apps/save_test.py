import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from datetime import datetime
from mongoengine import connect
from db.Test import Test


def main(ip_addr: str, db_name: str, test_name: str,
         start_d: str, end_d: str, dev_eui: str) -> None:

    connect(db_name, host=ip_addr, port=27017)

    start = datetime.strptime(start_d, "%d-%m-%y %H:%M:%S")
    end = datetime.strptime(end_d, "%d-%m-%y %H:%M:%S")

    Test(name=test_name,
         description='Test created for '+test_name,
         start=start, end=end, devEUI=dev_eui.lower()).save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    parser.add_argument('--db_name', type=str, default='iot-ripios',
                        help="Mongo db with tilt data")
    parser.add_argument('--test_name', type=str, required=True,
                        help="Name of the test")
    parser.add_argument('--start_d', type=str, required=True,
                        help="Date of the test, in format: dd-mm-yy HH:MM:SS")
    parser.add_argument('--end_d', type=str, required=True,
                        help="Date of the test, in format: dd-mm-yy HH:MM:SS")
    parser.add_argument('--dev_eui', type=str, default='DD4E54501000033A',
                        help="Date of the test, in format: dd-mm-yy HH:MM:SS")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr, cmd_args.db_name, cmd_args.test_name,
         cmd_args.start_d, cmd_args.end_d, cmd_args.dev_eui)
