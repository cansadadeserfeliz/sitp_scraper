## :robot: Telegram Bot

[@sitp_bot](https://web.telegram.org/#/im?p=@sitp_bot)


## :busstop: Installation

    $ apt-get install postgis
    $ createdb  <db name>
    $ psql <db name>
    > CREATE EXTENSION postgis;

    $ cp sitp_scraper/local_settings.example.py sitp_scraper/local_settings.py

    $ mkvirtualenv sitp_scraper
    $ pip install -r requirements.txt

## :bus: Usage

Run scrapy spider to get new SITP stations and routes from www.sitp.gov.co website:

    scrapy crawl sitp

or

    python manage.py start_scraper

to run it from Django.

Run Django project:

    python manage.py runserver

### Get coordinates for bus stations from Google maps API:

    python manage.py get_station_coordinates_google

### Get coordinates for bus stations from Civico:

    python manage.py get_station_coordinates_civico

### Get pair stations form www.sitp.gov.co website

"Pair stations" are stations that are located really close so we can count them as one.

    python manage.py get_pair_stations

## :oncoming_bus: Idea

The idea is to make a map with all bus routes that would be easy to print.

For example:

* City transport map for Moscow: http://transportmap.ru/moscowtransport_en.html
* City transport map for Saint-Petersburg: http://transportmap.ru/transport-spb_en.html
* Milan: http://img3.arrivo.ru/cfcd/91/2395/0/Shema-dvizheniya-avtobusov-milan.jpg
* Atlas that you can buy in Moscow "Атлас городского транспорта": http://avtoliteratura.ru/files/gortransp_1_resize.jpg
* More atlas examples: https://www.google.com.co/search?q=%D0%90%D1%82%D0%BB%D0%B0%D1%81+%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D1%81%D0%BA%D0%BE%D0%B3%D0%BE+%D1%82%D1%80%D0%B0%D0%BD%D1%81%D0%BF%D0%BE%D1%80%D1%82%D0%B0&tbm=isch&sa=Xbiw=1410

## :trolleybus: Deployment

    $ git pull
    $ workon sitp_scraper
    $ pip install requirements.txt
    $ ./manage.py migrate
    $ ./manage.py collectstatic
    # Restart the uwsgi process

## :fire_engine: Links:

* Google geocoding: https://developers.google.com/maps/documentation/geocoding/intro?hl=ru
