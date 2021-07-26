import scrapy
import re
import html

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteLukesPOVSpider(BaseSceneScraper):
    name = 'LukesPOV'
    network = 'Lukes POV'
    parent = 'Lukes POV'

    start_urls = [
        'https://lukespov.com/',
    ]

    selector_map = {
        'title': '//span[@class="entry-title"]/text()',
        'description': '//div/h2/following-sibling::p[1]/text()',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//div/img[contains(@class,"fp-splash")]/@data-orig-src',
        'performers': '//strong[contains(text(),"Starring")]/following-sibling::a/text()',
        'tags': '',
        'external_id': '.*\/(.*?)\/',
        'trailer': '//center/div[1]/@data-item',
        're_trailer': 'src\":\"(http.*?(?:mp4|mov))',
        'pagination': '/pov-blowjob-videos/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Lukes POV"
        

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return trailer.replace(" ", "%20").replace("\\","")

        return ''        
