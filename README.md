# Introduction

This code is an AWS Greengrass Lambda that reads IoT data from an SQL Database then sends it to the IoT Core. 

This code was implemented on a Raspberry Pi 3. A local SQL database is running on the RP3 using Postgres SQL. Simulated data is streamed into the SQL Database locally on the RP3.

## Prerequists:

Follow the steps here to install prepare your RP3 for Greengrass.

~~~
https://docs.aws.amazon.com/greengrass/latest/developerguide/quick-start.html
~~~

Be sure to following the instructions through the steps of creating a lambda function and sending data to IoT Core.

Enable SSH on the RP3, then SSH into the RP3, then enter the following commands:

~~~
> cd
> sudo apt update -y
> sudo apt upgrade -y
> sudo apt-get install python3-pip -y
> sudo apt install python3.7 -y
> sudo apt install git -y
> vi ~/.gitconfig
~~~

Privileges to clone this github repository are required. Add user information with these privileges to the .gitconfig file. Something like the following:

~~~
[user]
        name = AshokKumar
        email = AshokKumar@org.com
~~~

Now clone the repository and install the python modules.

~~~
> git clone https://github.com/mhattiga/sql_gg_lambda.git
> cd sql_gg_lambda
> pip3 install -r requirements.txt
~~~

Install Postgress SQL on the RP3. Instructions here:

~~~
https://kb.objectrocket.com/postgresql/how-to-install-and-set-up-postgresql-on-a-raspberry-pi-part-2-1165
~~~

These instructions create a Linux systemd service with the postgre SQL database server running on the RP3. The service is automatically started when the RP3 is rebooted.

Following the postgres installation instructions add a database called rasp_pi_db and set the password to 'postgres'; commands something like this:

~~~
> sudo su postgres
> psql
# CREATE DATABASE rasp_pi_db;
# ALTER USER postgres PASSWORD 'postgres';
# \l
# \c rasp_pi_db
# \dt 
# \q
> exit
~~~

Remember the password.

Two more useful references:

~~~
python postgres commands - https://www.postgresqltutorial.com/postgresql-python/create-tables/
psql commands - https://www.tutorialspoint.com/postgresql/index.htm
~~~

# Start Simulation Data

Configure the database.ini file for your local database. Specifically change the user and password.

~~~
> cp database_ini database.ini
> vi database.ini
~~~

Edit the user and password in the database.ini file to match the above, the default is:

~~~
    user=postgres
    password=postgres
~~~

Start the python program that streams data into the rasp_pi_db database.

~~~
> cd sim_data
> python3 main.py
~~~

Data is streamed into the database for as long as this program is running.

Start the program with a -d flag to delete all previous entries in the table before starting to stream new data.

To change the table name or the column names of the table edit table section of the database.ini file. Make sure the field_count, field0, field1, etc match.

The random data generated then insterted into the DB comes from fuction sql_db.gen_random_values). If the table or the fields change, then this routine must be modified to match the new table and fields. All other functions should work generically with any table.

~~~
> cd sim_data
> python3 main.py -d
<ctrl-c> to stop streaming data
~~~

# Load the greengrass lambda

Follow the instructions to load the code from the gg_lambda directory into your AWS account used when following these instructions:

~~~
> cd ../gg_lambda
~~~

~~~
https://docs.aws.amazon.com/greengrass/latest/developerguide/quick-start.html
~~~
