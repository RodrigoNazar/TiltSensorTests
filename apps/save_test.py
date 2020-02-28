import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from datetime import datetime
from mongoengine import connect
from db.Test import Test


def main(ip_addr: str, db_name: str, dev_eui: str) -> None:

    connect(db_name, host=ip_addr, port=27017)

    name = input('Name of the test:\n> ')
    description = input('Test\'s description:\n> ')

    start_d = input('Start date of the test, in format: dd-mm-yy HH:MM:SS\n> ')
    end_d = input('End date of the test, in format: dd-mm-yy HH:MM:SS\n> ')

    start = datetime.strptime(start_d, "%d-%m-%y %H:%M:%S")
    end = datetime.strptime(end_d, "%d-%m-%y %H:%M:%S")

    ans = input('Want to add some comments? [y/n]\n> ')

    while ans != 'y' and ans != 'n':
        print('Bad answer, try again:')
        ans = input('Want to add some comments? [y/n]\n> ')

    if ans == 'y':
        comments = input('Add the comment:\n> ')
        Test(name=name,
             description=description,
             start=start, end=end, devEUI=dev_eui.lower(),
             comments=comments).save()
    else:
        Test(name=name,
             description=description,
             start=start, end=end, devEUI=dev_eui.lower()).save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, required=True,
                        help="IP adress of the database to query")
    parser.add_argument('--db_name', type=str, default='iot-ripios',
                        help="Mongo db with tilt data")
    parser.add_argument('--dev_eui', type=str, default='DD4E54501000033A',
                        help="Date of the test, in format: dd-mm-yy HH:MM:SS")
    cmd_args = parser.parse_args()
    main(cmd_args.ip_addr, cmd_args.db_name, cmd_args.dev_eui)
