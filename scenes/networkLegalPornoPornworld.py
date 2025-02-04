import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.utils.project import get_project_settings


class LegalPornoSpider(BaseSceneScraper):
    name = 'LegalPornoPornworld'
    network = 'Legal Porno'

    # ~ settings = get_project_settings()
    # ~ proxy_address = settings.get('PROXY_ADDRESS')

    start_urls = [
        # ~ 'https://www.analvids.com',  # Located in networkLegalPorno.py
        'https://pornworld.com'
    ]

    selector_map = {
        'title': '//h1[contains(@class, "text-primary scene__title")]//text()',
        'description': '//p/span[@class="text-body-tertiary" and contains(text(), "Description")]/following-sibling::text()',
        'date': '//p/strong[@class="text-body-tertiary" and contains(text(), "Publication date:")]/following-sibling::span[1]/text()',
        'image': '//video[@class="video-player"]/@poster',
        'performers': '//a[contains(@class,"link-secondary") and contains(@href, "/model/")]/text()',
        'tags': '//a[contains(@class, "link-secondary") and contains(@href, "/videos?tags=")]/text()',
        'duration': '//p/i[@class="bi bi-clock-fill"]/following-sibling::text()',
        'external_id': r'/watch/(\d+)',
        'trailer': '//video[@class="video-player"]/source/@src',
        'pagination': 'videos?page=%s',
    }

    def get_site(self, response):
        return "Porn World"

    def get_parent(self, response):
        return "Legal Porno"

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[@class="card scene"]/a[1]/@href').getall()
        for scene in scenes:
            if "http:" not in scene:
                scene = "https:" + scene
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)

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
