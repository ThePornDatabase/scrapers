import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class DickDrainersSpider(BaseSceneScraper):
    name = 'DickDrainers'
    network = 'Dick Drainers'
    parent = 'Dick Drainers'

    start_urls = [
        'http://www.dickdrainers.com/'
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//div[@class="videoDetails clear"]//span[@style="color:#00ff00;"]/text()',
        'date': '//span[contains(text(),"Added")]/following-sibling::text()',
        'image': '//div[@class="player full_width"]//img/@src0_1x',
        'performers': '//div[@class="featuring clear"]//a[contains(@href,"/models/")]/text()',
        'tags': '//div[@class="featuring clear"]//a[contains(@href,"/categories/")]/text()',
        'external_id': r'\/trailers\/(.+)\.html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videoDetails clear"]/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        description = self.process_xpath(
            response, self.get_selector_map('description')).getall()
        if description:
            for desc in description:
                desc = desc.strip()
            description = '\n'.join(description)
            return description.strip()

        return ''

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = re.search(r'video src=\"(.*.mp4)\"', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    trailer = trailer.replace('//', '/')
                    trailer = 'http://www.dickdrainers.com' + trailer.strip()
                    return self.format_link(response, trailer)

        return ''

    def get_site(self, response):
        return 'Dick Drainers'
