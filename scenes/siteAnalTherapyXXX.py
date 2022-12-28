import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAnalTherapyXXXSpider(BaseSceneScraper):
    name = 'AnalTherapyXXX'
    network = 'Anal Therapy XXX'
    parent = 'Anal Therapy XXX'
    site = 'Anal Therapy XXX'

    start_urls = [
        'https://analtherapyxxx.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[@class="entry-content"]/p[1]/text()',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '',
        'performers': '',
        'tags': '//p[@class="post-meta"]/a[contains(@href, "category")]/text()',
        'duration': '',
        'trailer': '//div[@class="entry-content"]//video/source[contains(@src, ".mp4")]/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/page/%s/?et_blog',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article/div[contains(@class, "image_container")]')
        for scene in scenes:
            image = scene.xpath('./a/img/@src')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="entry-content"]/p[contains(text(), "Starring")]/text()')
        if performers:
            performers = re.search(r'Starring (.*)\*\*', performers.get())
            if performers:
                performers = performers.group(1).split("&")
                performers = list(map(lambda x: self.cleanup_title(x.strip()), performers))
                return performers
        return []
