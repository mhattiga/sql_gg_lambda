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

from configparser import ConfigParser
import logging as log
import psycopg2
import os
import datetime
from random import randint 

CMD_CREATE_TABLE = 'create_table'
CMD_TABLE_EXISTS = 'table_exists'
CMD_DELETE_TABLE = 'delete_table'
CMD_ENTER_RANDOM_DATA = 'enter_random_data'
CMD_GET_DATA = 'get_data'

cmd_list = [
    CMD_CREATE_TABLE,
    CMD_DELETE_TABLE,
    CMD_TABLE_EXISTS,
    CMD_ENTER_RANDOM_DATA,
    CMD_GET_DATA
    ]

MAX_PERCENT = 100
ALARM_ID_COUNT = 10
ALARM_ID_0 = 'SMOKE'
ALARM_ID_1 = 'FIRE'
ALARM_ID_2 = 'CO2'
ALARM_ID_3 = 'CO'
ALARM_ID_4 = 'Cl2'
ALARM_ID_5 = 'SO2'
ALARM_ID_6 = 'H20'
ALARM_ID_7 = 'C2N2'
ALARM_ID_8 = 'CNCI'
ALARM_ID_9 = 'AsF5'

alarm_ids = [
    ALARM_ID_0,
    ALARM_ID_1,
    ALARM_ID_2,
    ALARM_ID_3,
    ALARM_ID_4,
    ALARM_ID_5,
    ALARM_ID_6,
    ALARM_ID_7,
    ALARM_ID_8,
    ALARM_ID_9
    ]

class sql_db():
    def __init__(self, database_ini_pathname):
        self.db_config_dict = self.db_config(database_ini_pathname)
        log.info('db_config_dict = {}'.format(str(self.db_config_dict)))

        self.table_config_dict = self.table_config(database_ini_pathname)
        log.info('table_config_dict = {}'.format(str(self.table_config_dict)))

    def db_config(self, database_ini_pathname):
        db_dict = {}

        cf = ConfigParser()
        cf.optionxform = str

        section = 'postgressql'

        if os.path.exists(database_ini_pathname):
            cf.read(database_ini_pathname)
            try: 
                db_dict = dict(cf.items(section))
            except Exception as e:
                log.error('ConfigPaser error: {}'.format(str(e)))
        else:
            log.error('Missing database ini file = {}'.format(database_ini_pathname))

        return db_dict

    def table_config(self, database_ini_pathname):
        table_dict = {}

        cf = ConfigParser()
        cf.optionxform = str

        section = 'table'

        if os.path.exists(database_ini_pathname):
            cf.read(database_ini_pathname)
            try: 
                table_dict = dict(cf.items(section))
            except Exception as e:
                log.error('ConfigPaser error: {}'.format(str(e)))
        else:
            log.error('Missing database ini file = {}'.format(database_ini_pathname))

        return table_dict

    def gen_random_values(self, tab_name, prime_key, fields):
        ''' 
        If table name, primary key, or columns change, then modify this function for 
        the new schema.
        '''

        value_str = ''
        prime_key_value = ''
        if tab_name == 'alarms':
            if prime_key == 'utc':
                prime_key_value = '{}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

            first = True
            for field in fields:
                if field == 'utc':
                    value = prime_key_value
                elif field == 'alarm_id':
                    id_index = randint(0, ALARM_ID_COUNT)
                    value = alarm_ids[id_index]
                elif field == 'alarm_value':
                    value = randint(0, MAX_PERCENT)
                else:
                    log.error('Unexpected field value')
                    value_str = ''
                    prime_key_value = ''
                    break

                if first:
                    first = False
                    value_str += '\'{}\''.format(value)
                else:
                    value_str += ', \'{}\''.format(value)
                    
        log.info('value str = {}'.format(value_str))
        return prime_key_value, value_str

    def create_command_str(self, command):
        rc = ''
        if command in cmd_list:
            tab_dict = self.table_config_dict
            tab_name = tab_dict.get('name', None)
            prime_key = tab_dict.get('prime_key', None)
            field_count = tab_dict.get('field_count', None) 
            fc = int(field_count)
            fields = []
            for i in range(fc):
                key_value = 'field{}'.format(i)
                fields.append(tab_dict.get(key_value, 'MISSING'))

            '''
            # Save log.info() for debugging 
            log.info('tab_name = {}'.format(tab_name))
            log.info('prime_key = {}'.format(prime_key))
            log.info('fields = {}'.format(fields))
            log.info('field_count = {}'.format(fc))
            '''

            if command == CMD_TABLE_EXISTS:
                rc = 'select exists(select * from information_schema.tables where table_name=\'{}\')'.\
                    format(tab_name)

            elif command == CMD_CREATE_TABLE:
                rc = 'CREATE TABLE {} ( {} TEXT PRIMARY KEY, '.format(tab_name, prime_key)
                for i in range(1,fc-1):
                    rc += '{} TEXT, '.format(fields[i])
                rc += '{} TEXT) '.format(fields[fc-1])

            elif command == CMD_DELETE_TABLE:
                rc = 'DROP TABLE {};'.\
                    format(tab_name)

            elif command == CMD_ENTER_RANDOM_DATA:
                prime_key_value, value_str = self.gen_random_values(tab_name, prime_key, fields)
                rc = 'INSERT INTO {} values({});'.\
                    format(tab_name, value_str)

            elif command == CMD_GET_DATA:
                utc_now_str = tab_dict.get('utc_now_str', None)
                # TBD:
                # Tried just getting alarms from datetime but did not work.
                # Now just get all the data, then sort out later.
                # Not practical for a real world implementation.
                rc = 'SELECT * FROM {} where \'{}\' > \'{}\';'.\
                     format(tab_name, prime_key, utc_now_str)

        return rc

    def db_exists(self):
        rc = False
        cur = None
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config_dict)
            cur = conn.cursor()
            cur.execute('SELECT version()')
            db_version = cur.fetchone()
            log.info('PostgreSQL database version: {}'.format(db_version))

            rc = True
                   
        except (Exception, psycopg2.DatabaseError) as error:
            log.error('Error = {}'.format(error))
        finally:
            if conn is not None:
                conn.close()
            if cur is not None:
                cur.close()

        return rc

    def table_exists(self):
        rc = False
        cur = None
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config_dict)
            command = self.create_command_str(CMD_TABLE_EXISTS)
            log.info('table_exists command = {}'.format(command))
            cur = conn.cursor()
            cur.execute(command)
            rc = cur.fetchone()[0]

        except (Exception, psycopg2.DatabaseError) as error:
            log.error('Error = {}'.format(error))

        finally:
            if conn is not None:
                conn.close()
            if cur is not None:
                cur.close()

        return rc

    def create_table(self):
        rc = False
        cur = None
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config_dict)
            command = self.create_command_str(CMD_CREATE_TABLE)
            log.info('create table command = {}'.format(command))
            cur = conn.cursor()
            cur.execute(command)
            cur.close()
            cur = None
            conn.commit()
            rc = True

        except (Exception, psycopg2.DatabaseError) as error:
            log.error('Error = {}'.format(error))

        finally:
            if conn is not None:
                conn.close()
            if cur is not None:
                cur.close()

        return rc

    def delete_table(self):
        rc = False
        cur = None
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config_dict)
            command = self.create_command_str(CMD_DELETE_TABLE)
            log.info('delete table command = {}'.format(command))
            cur = conn.cursor()
            cur.execute(command)
            cur.close()
            cur = None
            conn.commit()
            rc = True

        except (Exception, psycopg2.DatabaseError) as error:
            log.error('Error = {}'.format(error))

        finally:
            if conn is not None:
                conn.close()
            if cur is not None:
                cur.close()

        return rc

    def add_random_data(self):
        rc = False
        cur = None
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config_dict)
            command = self.create_command_str(CMD_ENTER_RANDOM_DATA)
            log.info('create table command = {}'.format(command))
            cur = conn.cursor()
            cur.execute(command)
            cur.close()
            cur = None
            conn.commit()
            rc = True

        except (Exception, psycopg2.DatabaseError) as error:
            log.error('Error = {}'.format(error))

        finally:
            if conn is not None:
                conn.close()
            if cur is not None:
                cur.close()

        return rc

    def get_data_since(self, utc_now_str):
        rc = []
        cur = None
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config_dict)
            self.table_config_dict.update({'utc_now_str':utc_now_str})
            command = self.create_command_str(CMD_GET_DATA)
            log.info('get data command = {}'.format(command))
            cur = conn.cursor()
            cur.execute(command)
            rc = cur.fetchall()
            cur.close()
            cur = None

        except (Exception, psycopg2.DatabaseError) as error:
            log.error('Error = {}'.format(error))

        finally:
            if conn is not None:
                conn.close()
            if cur is not None:
                cur.close()

        return rc

        
