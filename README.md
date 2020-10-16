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

Following the postgres installation instructions add a database called rasp_pi_db. Commands something like this:

~~~
> sudo su postgres
> psql
# CREATE DATABASE rasp_pi_db;
# \l
# \q
> exit
~~~

# Start Simulation Data

Configure the databas.ini file for your local database. Specifically change the user and password.

~~~
> cp database_ini database.ini
> vi database.ini
~~~

Start the python program that streams data into the rasp_pi_db database.

~~~
> cd sim_data
> python3 sim_data.py
~~~

Data is streamed into the database for as long as this program is running.

Start the program with a -d flag to delete all previous entries in the database before starting to stream new data.

~~~
> python3 sim_data.py -d
~~~

# Load the greengrass lambda

Follow the instructions to load the code from the gg_lambda directory into your AWS account used when following these instructions:

~~~
> cd ../gg_lambda
~~~

~~~
https://docs.aws.amazon.com/greengrass/latest/developerguide/quick-start.html
~~~
