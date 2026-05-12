import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBondageMischiefSpider(BaseSceneScraper):
    name = 'BondageMischief'
    network = 'Bondage Mischief'
    parent = 'Bondage Mischief'
    site = 'Bondage Mischief'

    start_urls = [
        'https://bondagemischief.com',
    ]

    selector_map = {
        'description': '//div[contains(@class, "videoDescription")]/p//text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "tags")]/ul/li/a/text()',
        'performers': '//div[@class="models"]/ul/li/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videoBlock")]')
        for scene in scenes:
            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get().strip()).strftime('%Y-%m-%d')

            title = scene.xpath('.//h3/a/text()')
            if title:
                meta['title'] = string.capwords(title.get().strip())

            duration = scene.xpath('.//i[contains(@class, "clock")]/following-sibling::text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get().strip())

            sceneurl = scene.xpath('.//h3/a/@href').get()

            if re.search(self.get_selector_map('external_id'), sceneurl):
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = response.xpath('//div[@class="models"]/ul/li/a')
        perf_data = []
        for performer in performers:
            perf = {}
            perf['name'] = performer.xpath('./text()').get().strip()
            url = performer.xpath('./@href').get()
            perf['url'] = self.format_link(response, url)
            perf['extra'] = {'gender': 'female'}
            perf['site'] = self.site
            perf['network'] = self.network

            perf_slug = re.search(r'.*/(.*?)$', url)
            if perf_slug:
                perf['image'] = f"https://bondagemischief.com/content/performer/{perf_slug.group(1)}.jpg"
                perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
            perf_data.append(perf)
        return perf_data