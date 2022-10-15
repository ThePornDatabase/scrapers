import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJerkaokeSpider(BaseSceneScraper):
    name = 'Jerkaoke'
    network = 'Model Media'

    start_urls = [
        'https://www.delphinefilms.com',
        'https://www.jerkaoke.com',
        'https://www.modelmediaasia.com',
        'https://www.povadventure.com/',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//main[@id="MusContainer"]//p[contains(@class, "fw-lighter")]/text()',
        'date': '//div[contains(text(), "Released")]/following-sibling::div/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//main[@id="MusContainer"]/div/div/img/@src',
        'performers': '//div[contains(text(), "Cast")]/following-sibling::div/a/text()',
        'tags': '//main[@id="MusContainer"]//a[contains(@href, "tags")]/span/text()',
        'trailer': '',
        'external_id': r'trailers/(.*)',
        'pagination': '/videos?sort=published_at&page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "mb-3")]/a/@href').getall()
        for scene in scenes:
            if "?" in scene:
                link = re.search(r'(.*)\?', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        if "delphine" in response.url:
            return "Delphine Films"
        if "modelmediaasia" in response.url:
            return "Model Media Asia"
        if "jerkaoke" in response.url:
            return "Jerkaoke"
        if "povadventure" in response.url:
            return "POV Adventure"
        return super().get_site(response)

    def get_parent(self, response):
        if "delphine" in response.url:
            return "Delphine Films"
        if "jerkaoke" in response.url:
            return "Jerkaoke"
        if "modelmediaasia" in response.url:
            return "Model Media Asia"
        if "povadventure" in response.url:
            return "POV Adventure"
        return super().get_parent(response)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Delphine" in tags:
            tags.remove("Delphine")
        if "POV Adventure" in tags:
            tags.remove("POV Adventure")
        if "Jerkaoke" in tags:
            tags.remove("Jerkaoke")
        if "modelmediaasia" in response.url:
            tags.append("Asian")
        return tags

    def get_title(self, response):
        title = super().get_title(response)
        if "modelmediaasia" in response.url and "/" in title:
            title = re.search(r'(.*)/', title).group(1)
        return title

    def get_description(self, response):
        description = super().get_description(response)
        if "modelmediaasia" in response.url and "/" in description:
            description = re.search(r'(.*)/', description).group(1)
        return description

    def get_performers(self, response):
        performers = super().get_performers(response)
        if "modelmediaasia" in response.url:
            performers_asia = []
            for performer in performers:
                if "/" in performer:
                    performer = re.search(r'/(.*)', performer).group(1)
                    performers_asia.append(performer.strip())
            return performers_asia
        return performers
