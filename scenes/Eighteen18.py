import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class EighteenSpider(BaseSceneScraper):
    name = 'Eighteen18'

    start_urls = [
        'https://www.18eighteen.com'
    ]

    selector_map = {
        'title': "#videos_page-page h1::text",
        'description': "//meta[@itemprop='description']/@content | //*[@class='p-desc']/text()",
        'date': "//div[contains(@class, 'stat')]//span[contains(text(),'Date:')]/following-sibling::span/text()",
        'image': '//meta[@property="og:image"]/@content',
        'performers': "//div[contains(@class, 'stat')]//span[contains(text(),'Featuring:')]/following-sibling::span/a/text()",
        'tags': "",
        'external_id': 'xxx-teen-videos\\/.+\\/(\\d+)',
        'trailer': '',
        'pagination': 'xxx-teen-videos/?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.css(".video").css('a').xpath("@href").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)
