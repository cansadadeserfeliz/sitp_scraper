import scrapy

from ..items import RouteItem, BusStationItem


class SITPSpider(scrapy.Spider):
    name = 'sitp'
    start_urls = [
        'http://www.sitp.gov.co/loader.php?lServicio=Rutas&lTipo=busqueda&lFuncion=mostrarRuta&tipoRuta=8',
        'http://www.sitp.gov.co/loader.php?lServicio=Rutas&lTipo=busqueda&lFuncion=mostrarRuta&tipoRuta=9',
        'http://www.sitp.gov.co/loader.php?lServicio=Rutas&lTipo=busqueda&lFuncion=mostrarRuta&tipoRuta=10',
    ]

    def parse(self, response):
        for href in response.css('.containerInfoListRuta a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_route)

    @staticmethod
    def parse_route_stations(route):
        stations = []
        for station_info in route.css('.estacionRecorrido .infoParada'):
            station_item = BusStationItem()
            station_item['name'] =\
                ' '.join(station_info.css('.estNombre a::text').extract()).strip()
            address = \
                station_info.css('.estDireccion::text').extract_first().strip()
            station_item['address'] = address
            station_item['sublocality'] = ''
            link = station_info.css('.estNombre a::attr(href)').extract()
            link = link[0] if type(link) == list else ''
            code = ''
            if link:
                code = link.split('/')[-1].split('_')[0]
            station_item['link'] = link
            station_item['code'] = code
            station_item['latitude'] = None
            station_item['longitude'] = None

            stations.append(station_item)
        return stations

    def parse_route(self, response):
        route_item = RouteItem()
        if 'tipoRuta=9' in response.url:
            route_item['route_type'] = 9
        elif 'tipoRuta=10' in response.url:
            route_item['route_type'] = 10
        else:
            route_item['route_type'] = 8

        route_item['code'] = response.css('.codigoRuta::text').extract_first()

        name = response.css('.rutaEstacionesNombre::text').extract_first() or ''
        route_item['name'] = name.strip()

        map_relative_link = \
            response.css('.linkMapaRuta::attr(href)').extract_first()
        route_item['map_link'] = \
            'http://www.sitp.gov.co{}'.format(map_relative_link) \
            if map_relative_link else ''

        route_item['schedule'] = [
            s.replace(' ', '') for s in
            response.css('.horarioFuncionamiento .label-horario::text').extract()
        ]
        route_item['link'] = response.url
        route_item['route_1'] = self.parse_route_stations(response.css('.recorrido1'))
        route_item['route_2'] = self.parse_route_stations(response.css('.recorrido2'))
        yield route_item
