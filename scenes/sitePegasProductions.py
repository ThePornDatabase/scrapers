import re
import string
import unicodedata
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePegasProductionsSpider(BaseSceneScraper):
    name = 'PegasProductions'
    network = 'Pegas Productions'
    parent = 'Pegas Productions'
    site = 'Pegas Productions'

    start_urls = [
        'https://www.pegasproductions.com',
    ]

    cookies = {
        'langue': 'en',
        'consent': 'true',
        'Niche': 'Pegas',
        'AB': 'B',
        'limiteouvert': '0'
    }

    selector_map = {
        'title': '//div[@class="span10"]/h4/text()',
        'description': '//div[@class="span10"]//h5/following-sibling::p[1]/text()',
        'date': '//div[@id="date-duree"]/div[1]/p/text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//script[contains(text(), "poster")]/text()',
        're_image': r'(http.*?\.jpg)',
        'performers': '//p[contains(text(), "STARRING")]/following-sibling::div[@class="span5"]//h4/text()',
        'tags': '//div[@class="span9"]/h4/strong[contains(text(), "Tags")]/following-sibling::text()',
        'external_id': r'\.com/(.*)\?',
        'trailer': '//script[contains(text(), "poster")]/text()',
        're_trailer': r'(http.*?\.mp4)',
        'pagination': '/videos-porno-tour/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//span[contains(text(), "Latest") and not(contains(text(), "Girls"))]/following-sibling::div//div[@class="rollover_img_videotour"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                if "&nats=" in scene:
                    scene = re.search(r'(.*)&nats=', scene).group(1)
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = response.xpath(self.get_selector_map('tags')).get()
        tags = tags.split(",")
        tags = list(map(lambda x: x.strip().title(), tags))
        tags = [i for i in tags if i]
        return tags

    def get_title(self, response):
        title = super().get_title(response)
        return self.strip_accents(title)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(map(lambda x: self.strip_accents(x), performers))
        return performers

    def strip_accents(self, text):
        try:
            text = unicode(text, 'utf-8')
        except (TypeError, NameError):  # unicode is a default on python 3
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        text = re.sub('[^0-9a-zA-Z ]', '', text)
        return string.capwords(str(text))
