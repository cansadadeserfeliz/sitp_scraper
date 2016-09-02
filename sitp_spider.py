import scrapy


class StackOverflowSpider(scrapy.Spider):
    name = 'sitp'
    start_urls = ['http://www.sitp.gov.co/loader.php?lServicio=Rutas&lTipo=busqueda&lFuncion=mostrarRuta&tipoRuta=8']

    def parse(self, response):
        count = 0
        for href in response.css('.containerInfoListRuta a::attr(href)'):
            full_url = response.urljoin(href.extract())
            count += 1
            if count > 5:
                return
            yield scrapy.Request(full_url, callback=self.parse_route)

    @staticmethod
    def parse_route_stations(route):
        stations = []
        for station_info in route.css('.estacionRecorrido .infoParada'):
            stations.append({
                'name': ' '.join(station_info.css('.estNombre a::text').extract()).strip(),
                'direction': station_info.css('.estDireccion::text').extract_first().strip(),
            })
        return stations

    def parse_route(self, response):
        yield {
            'code': response.css('.codigoRuta::text').extract_first(),
            'name': response.css('.rutaEstacionesNombre::text').extract_first().strip(),
            'map_link': 'http://www.sitp.gov.co{}'.format(
                response.css('.linkMapaRuta::attr(href)').extract_first()
            ),
            'shcedule': [
                s.replace(' ', '') for s in
                response.css('.horarioFuncionamiento .label-horario::text').extract()
            ],
            'link': response.url,
            'route_1': self.parse_route_stations(response.css('.recorrido1')),
            'route_2': self.parse_route_stations(response.css('.recorrido2')),
        }
