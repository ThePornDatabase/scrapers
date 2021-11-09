import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBAMVisionsBTSSpider(BaseSceneScraper):
    name = 'BAMVisionsBTS'
    network = 'BAM Visions'
    parent = 'BAM Visions'
    site = 'BAM Visions'

    start_urls = [
        'https://tour.bamvisions.com/'
    ]

    selector_map = {
        'title': '//h4/a/text()',
        'performers': '//h5/a/text()',
        'description': '//p[@class="description"]/text()',
        'date': '//li/i[@class="fa fa-calendar"]/following-sibling::strong/following-sibling::text()',
        'image': '//script[contains(text(),"poster")]/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': r'trailers/(.*)\.html',
        'trailer': '//script[contains(text(),"poster")]/text()',
        'pagination': '/categories/BTS/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-info"]//h3/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'BAM Visions'})

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search(r'poster=\"(.*.jpg)\"', image).group(1)
            if image:
                image = "https://tour.bamvisions.com/" + image
                return self.format_link(response, image)
        return ''

    def get_trailer(self, response):
        trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
        if trailer:
            trailer = re.search(r'video\ src=\"(.*.mp4)\"', trailer).group(1)
            if trailer:
                trailer = "https://tour.bamvisions.com/" + trailer
                trailer = trailer.replace(" ", "%20")
                return self.format_link(response, trailer)
        return ''
