import re
import unidecode
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTAWorshipSpider(BaseSceneScraper):
    name = 'TAWorship'
    network = 'TAWorship'
    parent = 'TAWorship'
    site = 'TAWorship'

    start_urls = [
        'https://www.taworship.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "title")]/h1/text()',
        'description': '//div[contains(@class, "pb-5")]/hr/following-sibling::text()',
        'date': '',
        'image': '//div[contains(@class,"video-cover")]/@style',
        're_image': r'url\(\/\/(.*?)\)',
        'performers': '//div[contains(@class, "title")]/h1/following-sibling::span//a[contains(@href, "/browsevideos")]/text()',
        'tags': '//div[contains(@class, "categories-icon")]/following-sibling::a[contains(@href, "/browsevideos")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'video/(\d+)/',
        'pagination': '/browsevideos?lt=latest&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "grid")]/div')
        for scene in scenes:
            scenedate = scene.xpath('.//div[contains(@class, "text-gray")]/div[contains(@class, "text-right")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
            trailer = scene.xpath('./a/video-thumb/@video')
            if trailer:
                meta['trailer'] = self.format_link(response, trailer.get())

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        title = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', title)).strip())
        return title

    def get_description(self, response):
        description = super().get_description(response)
        description = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', description)).strip())
        return description

    def get_image(self, response):
        image = response.xpath('//div[contains(@class,"video-cover")]/@style').get()
        image = re.search(r'url\(\/\/(.*?)\)', image)
        if image:
            image = image.group(1)
            image = "https://" + image
        return image
