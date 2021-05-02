import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VnaNetworkSpider(BaseSceneScraper):
    name = 'MagmaFilm'

    start_urls = [
        'http://www.magmafilm.tv/',
    ]

    selector_map = {
        'title': 'h2:first-of-type::text',
        'description': '//div[@class="infobox"]/div/p/text()',
        'date': '',
        'image': '//div[@class="imgbox full"]/@style',
        'performers': '//div[@class="infobox"]/div/table//td/div/text()',
        'tags': '//div[@class="infobox"]/div/table//td/a/span/text()',
        'external_id': '/([a-z0-9-]+?)/?$',
        'trailer': '',
        'pagination': '/de/List/Neu?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="clipbox medium"]/a[1]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
    
    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get().split("url('//")[1][:-2]
        return self.format_link(response, image)
    
    #### no date aviable, is there a better solution?

    def get_date(self,desponse):
        date = '1970-01-01'
        return dateparser.parse(date).isoformat()

