import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkMeanBitchesSpider(BaseSceneScraper):
    name = 'MeanBitches'
    network = 'MeanBitches'

    start_urls = [
        'https://megasite.meanworld.com',
    ]

    selector_map = {
        'title': '//div[@class="vidImgTitle"]//h4/a[last()]/following-sibling::text()',
        'description': '//div[contains(@class,"vidImgContent")]/p//text()',
        'date': '//ul[@class="videoInfo"]//comment()[contains(.,"Date")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//p[@class="link_light"]/a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="blogTags"]/ul/li/a/text()',
        'duration': '//ul[@class="videoInfo"]/li/text()[contains(., "min")]',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@id, "packageinfo")]')
        for scene in scenes:
            sceneid = scene.xpath('./@id').get()
            meta['id'] = re.search(r'_(\d+)', sceneid).group(1)

            scene = scene.xpath('./following-sibling::h4[@class="link_bright"]/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        title = title.strip('/').strip()
        return title

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration')).get()
        if duration:
            duration = re.search(r'(\d+).*?min', duration.lower())
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return duration
    
    def get_site(self, response):
        site = response.xpath('//div[contains(@class,"latestUpdateBinfo")]/a[@class="link_bright"]/text()').get()
        return site.strip()
    
    def get_parent(self, response):
        return "MeanBitches"
    
    def get_network(self, response):
        return "MeanBitches"