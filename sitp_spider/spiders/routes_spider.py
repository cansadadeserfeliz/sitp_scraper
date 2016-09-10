import scrapy

from ..items import RouteItem, BusStationItem


class SITPSpider(scrapy.Spider):
    name = 'sitp'
    start_urls = [
        'http://www.sitp.gov.co/loader.php?lServicio=Rutas&lTipo=busqueda&lFuncion=mostrarRuta&tipoRuta=8',
    ]

    def parse(self, response):
        count = 0
        for href in response.css('.containerInfoListRuta a::attr(href)'):
            full_url = response.urljoin(href.extract())
            count += 1
            if count > 2:
                return
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
            station_item['latitude'] = None
            station_item['longitude'] = None

            stations.append(station_item)
        return stations

    def parse_route(self, response):
        route_item = RouteItem()
        route_item['code'] = response.css('.codigoRuta::text').extract_first()
        route_item['name'] = \
            response.css('.rutaEstacionesNombre::text').extract_first().strip()
        route_item['map_link'] = 'http://www.sitp.gov.co{}'.format(
                response.css('.linkMapaRuta::attr(href)').extract_first()
            )
        route_item['schedule'] = [
            s.replace(' ', '') for s in
            response.css('.horarioFuncionamiento .label-horario::text').extract()
        ]
        route_item['link'] = response.url
        route_item['route_1'] = self.parse_route_stations(response.css('.recorrido1'))
        route_item['route_2'] = self.parse_route_stations(response.css('.recorrido2'))
        yield route_item
