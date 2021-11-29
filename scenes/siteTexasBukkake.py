import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTexasBukkakeSpider(BaseSceneScraper):
    name = 'TexasBukkake'
    network = 'Texas Bukkake'

    start_urls = [
        'https://texasbukkake.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"title")]/h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '',
        'image': '//div[contains(@class,"video-cover")]/@style',
        're_image': r'url\((.*\.(?:jpeg|png|jpg))',
        'performers': '//div[@class="flex flex-wrap-reverse"]/div/span/a/text()',
        'tags': '//div[contains(@class,"categories-icon")]/following-sibling::a/text()',
        'external_id': r'video/(\d+)?/',
        'trailer': '',
        'pagination': '/browsevideos?lt=latest&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "grid")]/div')
        for scene in scenes:
            scenedate = scene.xpath('.//div[@class="w-1/2 text-right"]/text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                scenedate = self.parse_date(scenedate, date_formats=['%b %d, %Y']).isoformat()
            else:
                scenedate = self.parse_date('today').isoformat()
            scene = scene.xpath('./a/@href').get()
            if scene:
                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': scenedate})

    def get_site(self, response):
        site = response.xpath('//div[@class="flex flex-wrap-reverse"]/div/span/span/text()')
        if site:
            return site.get().strip().title()
        return "Texas Bukkake"

    def get_parent(self, response):
        return "Texas Bukkake"

    def get_image(self, response):
        image = response.xpath(self.get_selector_map('image'))
        if image:
            image = image.get()
            image = re.search(self.get_selector_map('re_image'), image).group(1)
            image = self.format_link(response, image)
            return image
        return ''
