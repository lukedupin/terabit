#!/usr/bin/sh

cd frontend
npm run build
cd build
mv static/js .
rmdir static
cd ..
cd ..
./manage.py collectstatic
