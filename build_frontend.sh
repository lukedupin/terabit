#!/usr/bin/sh

cd frontend
npm run build
cd build
mv static/js .
rmdir static
cd ..
cd ..
./manage.py migrate
./manage.py collectstatic
chown -R www-data:www-data *

echo "Restarting apache2"
systemctl restart apache2  
