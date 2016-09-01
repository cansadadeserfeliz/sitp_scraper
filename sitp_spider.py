import scrapy


class StackOverflowSpider(scrapy.Spider):
    name = 'sitp'
    start_urls = ['http://www.sitp.gov.co/loader.php?lServicio=Rutas&lTipo=busqueda&lFuncion=mostrarRuta&tipoRuta=8']

    def parse(self, response):
        for href in response.css('.containerInfoListRuta a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_route)

    def parse_route(self, response):
        yield {
            'code': response.css('.codigoRuta::text').extract_first(),
            #'color': response.css('.backCodigo::style').extract_first(),
            'name': response.css('.rutaEstacionesNombre::text').extract_first().strip(),
            'map_link': response.css('.linkMapaRuta::attr(href)').extract(),
            'link': response.url,
        }
