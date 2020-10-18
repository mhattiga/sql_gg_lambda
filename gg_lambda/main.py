#!/usr/bin/env python3
'''
MIT No Attribution

Copyright Amazon Web Services

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
import os
root_dir = os.getcwd() + '/..'
sys.path.append(root_dir)

import logging as log
from sql_db import sql_db
import argparse
import time
import datetime

log.basicConfig(format='%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s: %(message)s', level=log.INFO, datefmt="%Y-%m-%d %H:%M:%S")
database_ini_pathname = '{}/database.ini'.format(root_dir)
WAIT_TIME = 20 # seconds between data entires being added to db

def stream_from_sql(local_db):
    while(1):
        utcnow_datetime = datetime.datetime.utcnow()
        utcnow_str = '{}'.format(utcnow_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        # Now wait for record to accumulate in the DB
        time.sleep(WAIT_TIME)

        # Get data from DB
        data_row_2d_list = local_db.get_data_since(utcnow_str)
        log.info('************** {} ********************'.format(utcnow_str))
        for data_row_list in data_row_2d_list:
            data_utc_str = data_row_list[0]
            data_utc_datetime = datetime.datetime.strptime(data_utc_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            if data_utc_datetime > utcnow_datetime:
                log.info('data row utc = {}'.format(data_row_list))

            # Have a bug in the SQL query. Because the query returns all values instead of 
            # just the values since utcnow_str.
            #
            # Go to the GET_DATA command in sql_db.py to change the query for a fix. Just 
            # don't know the right query now.
            #
            # Uncomment the next two lines to see the bug.
            # else:
                # log.info('BEFORE UTC {}: data row utc = {}'.format(utcnow_str, data_row_list))
                

def main():
    arg_parser = argparse.ArgumentParser(description='Stream data into SQL Database')
    arg_parser.add_argument('-d','--delete',action='store_true',help='delete table and all entries of the database before starting')
    args = arg_parser.parse_args()

    local_db = sql_db(database_ini_pathname)
    if local_db.db_exists():
        if local_db.table_exists():
            stream_from_sql(local_db)
    else:
        log.error('db does not exist')

if __name__ == '__main__':
    main()
