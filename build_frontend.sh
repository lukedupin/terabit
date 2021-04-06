#!/usr/bin/sh

chown -R www-data:www-data *
cd frontend
npm run build
cd build
mv static/js .
rmdir static
cd ..
cd ..
./manage.py collectstatic
systemctl restart apache2  
