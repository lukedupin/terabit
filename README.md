# Terabit

The TERABIT README

# Installation

sudo apt install python3-memcached

sudo pip3 install psycopg2
sudo pip3 install psycopg2-binary
sudo pip3 install pillow
sudo pip3 install boto3
sudo pip3 install tzwhere
sudo pip3 install pyfcm 
sudo pip3 install pykml
sudo pip3 install django-nested-admin
sudo pip3 install twilio
sudo pip3 install sendgrid
sudo pip3 install newspaper3k
sudo pip3 install cffi
sudo pip3 install scipy
sudo pip3 install pycairo

# Please note

Posix Spawn requires write access to website/libs/posix_spawner/__pycache__. If write access doesn't exist (Not the owner, or permissions of 777) then course logo building will fail

# run in python
python3
import nltk
nltk.download('punkt')

sudo mv ~/nltk_data /var/www/
sudo chown -R www-data:www-data /var/www/nltk_data
