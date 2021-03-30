# Terabit

The TERABIT README

# Installation

sudo apt install python3-memcached python3-pip python3-django yarn nodjs npm

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

# Set up django

1. Setup Django to run on your platform. There are tons of walk throughs out there, go read one.
2. Open a terminal in the base directory of the project
3. cd pysite
4. ln -s code.settings.py settings.py **This will pick which settings file django should use, code is for local code development**

# Compiling and updating the frontend

1. ./manage.py runserver **In the future, only run this to start the local djanog web server**

You should see output like this:
March 28, 2021 - 16:17:04
Django version 3.1.7, using settings 'pysite.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

# Running django webserver

1. Open a terminal in the frontend dir
2. yarn install **Run this only once after initial checkout** 
3. npm run build **Run this every time you make a change on the frontend**
4. With the django server running, open your browser: http://localhost:8000/
