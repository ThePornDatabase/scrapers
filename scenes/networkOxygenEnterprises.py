import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'dreamtranny': "Dream Tranny",
        'jeffsmodels': "Jeffs Models",
    }
    return match.get(argument, argument)


class Spider(BaseSceneScraper):
    name = 'OxygenEnterprises'
    network = 'Oxygen Enterprises'

    start_urls = [
        'https://dreamtranny.com',
        'https://jeffsmodels.com',
    ]

    selector_map = {
        'title': '//div[@class="section-title"]/h4/text()',
        'description': '//p[@class="read-more"]/text()',
        'date': '//small[@class="updated-at"]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@class="model-player"]//video/@poster',
        'performers': '//div[@class="model-rich"]/h4/a[contains(@href, "/models/")]/text()',
        'tags': '//span[contains(text(), "Categories")]/following-sibling::a[contains(@href, "tag")]/text()',
        'trailer': '//div[@class="model-player"]//video/source/@src',
        'external_id': r'update/(\d+)/',
        'pagination': '/updates/?page=%s'
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="item-wrapper"]/a/@href').getall()
        for scene in scenes:
            if "?nats" in scene:
                scene = re.search(r'(.*)\?nats', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "dreamtranny" in response.url:
            tags.append('Trans')
        if "jeffsmodels" in response.url:
            tags.append('BBW')
        return tags

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_title(self, response):
        if "jeffsmodels" in response.url:
            title = response.xpath('//div[@class="section-title"]/h4/text()|//div[@class="section-title"]/h1/text()').get()
            if title:
                title = string.capwords(title.strip())
                return title
        else:
            return super().get_title(response)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.xpath('//div[@class="model-player"]//img/@src')
            if image:
                image = image.get()
                image = self.format_link(response, image)
        if image:
            return image
        return None