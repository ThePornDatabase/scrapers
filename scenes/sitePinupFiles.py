import scrapy
import re
import html
import string
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper


class sitePinupFilesSpider(BaseSceneScraper):
    name = 'PinupFiles'
    network = 'Pinup Files'


    start_urls = [
        'https://www.pinupfiles.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="update-info-block"]/h3/following-sibling::text()',
        'date': '//strong[contains(text(),"Added")]/following-sibling::text()',
        'image': '//script[contains(text(),"video_content")]/text()',
        're_image': '(http.*\.jpg)',
        'performers': '//div[contains(@class,"models-list-thumbs")]/ul/li/a/span/text()',
        'tags': '//h3[contains(text(),"Tags")]/following-sibling::ul/li/a/text()',
        'external_id': '.*\/(.*?).html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        're_trailer': '(\/trailers.*?\.mp4)',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Pinup Files"

    def get_parent(self, response):
        return "Pinup Files"
        
    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            description = description.replace("\r","").replace("\n","").replace("&nbsp;","").strip()
            description = re.sub('\s{3,100}',' ', description)
            return html.unescape(description.strip())

        return ''


    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return "https://www.pinupfiles.com" + trailer.replace(" ", "%20")

        return ''
