import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKinkyMistressesSpider(BaseSceneScraper):
    name = 'KinkyMistresses'
    network = 'Kinky Mistresses'

    start_urls = [
        'https://www.kinkymistresses.com',
    ]

    selector_map = {
        'title': '//div[@class="videodetails"]/h1/text()',
        'description': '//div[@class="videodetails"]/p/text()',
        'date': '',
        'image': '//div[@class="videowrapper"]/img/@src',
        'performers': '//div[@class="featuredmodels"]/a/text()',
        'tags': '//div[@class="videocats"]/a/text()',
        'external_id': r'-(\d{5,20})-',
        'trailer': '//div[@class="videowrapper"]/video/source/@src',
        'pagination': '/Kinky-Mistresses-%s-videos.htm'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="spot"]/a[2]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Kinky Mistresses"

    def get_parent(self, response):
        return "Kinky Mistresses"

    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            image = response.xpath('//div[@class="videowrapper"]/video/@poster')
            if image:
                image = self.format_link(response, image.get())

        return image.replace(" ", "%20")

    def get_title(self, response):
        title = super().get_title(response)
        title = title.replace("`", "'")
        return title

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        trailer = trailer.replace("mp4_720", "mp4_360")
        return trailer
