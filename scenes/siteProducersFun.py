import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class ProducersFunSpider(BaseSceneScraper):
    name = 'ProducersFun'
    network = "Producers Fun"
    parent = "Producers Fun"

    start_urls = [
        'https://producersfun.com'
    ]

    selector_map = {
        'title': '//div[@class="shadow video-details"]/h1/text()',
        'description': '(//div[@class="shadow video-details"]/p[not(@class)])[1]/text()',
        'date': '//p[@class="video-date"]/text()[2]',
        'image': '//section[@class="top-wrapper"]/div//video/@poster',
        'performers': '//h1/text()',
        'tags': '//p[@class="video-tags"]/a/text()',
        'external_id': 'video\\/(.*)',
        'trailer': '',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//article[@class="shadow video"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Producers Fun"

    def get_trailer(self, response):
        trailer = response.xpath(
            '//input[@type="hidden" and @id="videoJsConfig"]/@value').get()
        try:
            trailer = re.search(
                '480\\},\\{\"src\":\"(.*?)\".\"type',
                trailer).group(1)
        except BaseException:
            trailer = re.search(
                '1080\\},\\{\"src\":\"(.*?)\".\"type',
                trailer).group(1)

        trailer = trailer.replace("\\", "")

        if trailer:
            return trailer
        return ''

    def get_description(self, response):
        description = response.xpath(
            '//div[@class="shadow video-details"]/p[not(@class="video-date") and not(@class="video-tags")][1]/text()').get()
        if description:
            return description.strip()
        return ''

    def get_performers(self, response):
        performers = response.xpath('//h1/text()').get()
        if " - " in performers:
            performers = re.search('(.*)\\ -\\ ', performers).group(1)
            performers = performers.strip()

        if performers and "Volume" not in performers and "Compilation" not in performers:
            return [performers]
        return ''
