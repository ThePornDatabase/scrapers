import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class LegalPornoSpider(BaseSceneScraper):
    name = 'LegalPornoPornworld'
    network = 'Legal Porno'

    start_urls = [
        # ~ 'https://www.analvids.com',  # Located in netowkrLegalPorno.py
        'https://pornworld.com'
    ]

    selector_map = {
        'title': '//h1[contains(@class,"watch__title")]//text()',
        'description': '//div[contains(text(), "Description")]/following-sibling::div//text()',
        'date': '//i[contains(@class,"calendar")]/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//video/@data-poster',
        'performers': '//h1[contains(@class,"watch__title")]//a/text()',
        'tags': '//div[contains(@class,"genres-list")]/a/text()',
        'external_id': r'\/watch\/(\d+)',
        'trailer': '//video//source/@src',
        'pagination': '/new-videos/%s'
    }

    def get_site(self, response):
        return "Porn World"

    def get_parent(self, response):
        return "Porn World"

    def get_scenes(self, response):
        """ Returns a list of scenes
        @url https://pornworld.com/new-videos/1
        @returns requests 50 150
        """
        scenes = response.xpath('//div[@class="card-scene__view"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = " ".join(title.getall()).lower()
            titlesearch = re.search(r'(.*) featuring', title)
            if titlesearch:
                title = titlesearch.group(1).strip()
                return string.capwords(title.replace("  ", " ").strip())
            return string.capwords(title.replace("  ", " ").strip())
        return ''

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = " ".join(description.getall()).replace("...", "").replace("  ", " ").strip()
            description = re.sub(u'\u0096', u"\u0027", description)
            description = re.sub(u'\u0092', u"\u0027", description)
            return description
        return ''

    def get_trailer(self, response):
        trailer = response.xpath(self.get_selector_map('trailer'))
        if trailer:
            trailers = trailer.getall()
            for trailer in trailers:
                if "_1080" in trailer:
                    return trailer.replace(" ", "%20").strip()
            for trailer in trailers:
                if "_720" in trailer:
                    return trailer.replace(" ", "%20").strip()
            for trailer in trailers:
                if "_2160" in trailer:
                    return trailer.replace(" ", "%20").strip()
        return ''
