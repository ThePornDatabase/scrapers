import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFreakMobMediaSpider(BaseSceneScraper):
    name = 'FreakMobMedia'
    network = 'Freak Mob Media'

    start_urls = [
        'https://www.freakmobmedia.com/',
    ]

    selector_map = {
        'title': '//div[@class="title"]/div[@class="heading"]/h3[not(contains(text(),"Suggestions"))]/text()',
        'description': '//div[@class="description"]/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="meta-info" and contains(text(),"Model")]/following-sibling::a/text()',
        'tags': '//div[@class="post-info"]//a/text()',
        'external_id': r'.*\/(.*?)\/',
        'trailer': '//script[contains(text(),"var jw")]/text()',
        're_trailer': r'.*(http.*?\.(?:mp4|mov)).*',
        'pagination': '/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="itemsarea"]/div[@class="item"]/div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Freak Mob Media"

    def get_parent(self, response):
        return "Freak Mob Media"

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                if trailer:
                    trailer = trailer.replace("www. freakmobmedia", "www.freakmobmedia").replace("///", "//").replace("////", "//")
                    if "http:www" in trailer:
                        trailer = trailer.replace("http:www", "https://www")
                    return trailer.replace(" ", "%20")

        return ''
