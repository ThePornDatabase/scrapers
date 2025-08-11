import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMajorHotwifeSpider(BaseSceneScraper):
    name = 'MajorHotwife'
    network = 'MajorHotwife'
    parent = 'MajorHotwife'
    site = 'MajorHotwife'

    start_urls = [
        'https://majorhotwife.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "customcontent")]/h1/text()',
        'description': '//div[contains(@class, "customcontent")]/h2/text()',
        'date': '//span[contains(@class, "date")]/text()',
        'date_formats': ['%B %d %Y'],
        'duration': '//span[contains(text(), "duration")]/strong/text()',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/videos/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h3/a[contains(@href, "videos")]/..')
        for scene in scenes:
            image = scene.xpath('./following-sibling::div[1]/div[contains(@class, "video_pic")][1]/a/img/@src')
            if image:
                image = image.get()
                meta['image'] = "https://majorhotwife.com/" + image
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('./a[contains(@href, "videos")]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = response.xpath('//h4/text()')
        if tags:
            tags = tags.get()
            tags = tags.split(",")
            tags = list(map(lambda x: string.capwords(x.strip()), tags))
            return tags
        return []

    def get_performers(self, response):
        performers = response.text
        performers = performers.replace("\r", "").replace("\n", "").replace("\t", "")
        performers = re.search(r'customcontent.*?h3 style.*?\>(.*?)\<', performers)
        if performers:
            performers = performers.group(1)
            performers = performers.replace("&nbsp", "")
            performers = performers.split(",")
            performers = list(map(lambda x: string.capwords(x.strip()), performers))
            return performers
        return []

    def get_image(self, response):
        sceneid = super().get_id(response)
        return f"https://majorhotwife.com/sd3.php?show=file&path=/videos/{sceneid}/thumb_1.jpg"
