import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkMadhotXSpider(BaseSceneScraper):
    name = 'MadhotX'
    network = 'MadhotX'

    start_urls = [
        'https://madhotx.com/videos/2',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//p[@class="desc"]/text()',
        'date': '',
        'image': '//video/@data-poster',
        're_image': r'(.*)\?',
        # Only the link's title attribute carries the name: "View all videos with X"
        'performers': '//div[@class="actor"]/a/@title',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*)',
        'pagination': '/videos/%s?order=latest',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="item"]')
        for scene in scenes:
            # The card's link class changed from gallery-item to video-item, so the
            # href came back as None and the external_id match raised on it.
            link = scene.xpath('./a[contains(@class, "video-item")]/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            site = scene.xpath('.//p[@class="project-episode"]/span[1]/text()').get() or ''
            site = re.sub(r'[^a-zA-Z ]', '', site).strip()
            if site:
                meta['site'] = site
                meta['parent'] = site
            duration = scene.xpath('.//span[contains(@class, "duration")]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())
            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath(self.get_selector_map('performers')).getall()
        return [re.sub(r'^View all videos with\s*', '', x).strip() for x in performers
                if x and x.strip()]

    def get_image_blob(self, response):
        image = response.xpath('//video/@data-poster')
        if image:
            return self.get_image_blob_from_link(image.get())
        return ''
