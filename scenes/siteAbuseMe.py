import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAbuseMeSpider(BaseSceneScraper):
    name = 'AbuseMe'
    network = "Abuse Me"
    parent = "Abuse Me"

    start_urls = [
        'http://abuseme.com',
    ]

    selector_map = {
        'title': '//h1[@class="shoot-title"]/text()',
        'description': '//div[@class="playerTxt"]/text()',
        'date': '//div[contains(text(),"Added")]/text()',
        'image': '//img[@class="playerPic"]/@src',
        'performers': '//script[contains(text(),"shootModels")]/text()',
        'tags': '//meta[@http-equiv="keywords"]/@content',
        'external_id': r'\/video(\d+)',
        'trailer': '//script[@type="text/javascript"]/text()',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="echMdlBlock-padd clearfix"]/div/a[contains(@class,"btn_blue")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        date = date.replace('Added:', '').strip()
        return dateparser.parse(date.strip()).isoformat()

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            if image[:4] == "////":
                image = image[4:]
                image = "http://" + image
            return self.format_link(response, image)
        return ''

    def get_site(self, response):
        return "Abuse Me"

    def get_performers(self, response):
        if 'performers' in self.get_selector_map() and self.get_selector_map('performers'):
            performers = self.process_xpath(response, self.get_selector_map('performers')).get()
            if performers:
                performers = re.findall(r'\"\d+ : (.*?)\",', performers)
                if performers:
                    return list(map(lambda x: x.strip().title(), performers))
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags')).get()
            tags = tags.split(",")
            tags = list(map(lambda x: x.strip(), tags))
            if 'abuse me' in tags:
                tags.remove('abuse me')
            if 'abuseme' in tags:
                tags.remove('abuseme')
            if 'abuseme.com' in tags:
                tags.remove('abuseme.com')
            if '4k' in tags:
                tags.remove('4k')
            if '4K' in tags:
                tags.remove('4K')
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = re.search(r'\'\/\/(.*.mp4)\'', trailer).group(1)
                if trailer:
                    trailer = "http://" + trailer
                    return trailer.strip()
        return ''
