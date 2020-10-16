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
import os

log.basicConfig(format='%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s: %(message)s', level=log.INFO, datefmt="%Y-%m-%d %H:%M:%S")

def db_config():
    db_dict = {}

    cf = ConfigParser()
    cf.optionxform = str

    database_ini_pathname = '../database.ini'
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


def main():
    db_dict = db_config()
    log.info('{}'.format(str(db_dict)))


if __name__ == '__main__':
    main()
