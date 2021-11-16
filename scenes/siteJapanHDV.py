import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJapanHDVSpider(BaseSceneScraper):
    name = 'JapanHDV'
    network = 'AV Revenue'
    parent = 'JapanHDV'
    site = 'JapanHDV'

    start_urls = [
        'https://japanhdv.com'
    ]

    selector_map = {
        'title': '//h1/span/following-sibling::text()',
        'performers': '//p/strong[contains(text(),"Actress:")]/following-sibling::a/text()',
        'description': '//div[contains(@class,"video-description")]/text()',
        'date': '',
        'image': '//div[@class="thumb"]//video/@poster',
        'tags': '//p/strong[contains(text(),"Categories:")]/following-sibling::a/text()',
        'external_id': r'.com/(.*)/',
        'trailer': '',
        'pagination': '/japan-porn/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb"]/div/a[contains(@class,"thumb")]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'JapanHDV'})

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                tags = list(map(lambda x: x.strip().title(), tags.getall()))

            series = response.xpath('//p/strong[contains(text(),"Series:")]/following-sibling::a/text()').get()
            if series:
                tags.append("JHDV Series: " + series.strip().title())

            if tags:
                return tags

        return []
