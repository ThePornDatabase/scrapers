import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class LittleCapriceSpider(BaseSceneScraper):
    name = 'LittleCaprice'
    network = 'Little Caprice Dreams'

    start_urls = [
        'https://www.littlecaprice-dreams.com'
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': "//article/div[@class='entry-content']//div[contains(@class,'et_section_regular')]//div[contains(@class,'et_pb_row_1-4_3-4')]//div[contains(@class,'et_pb_column_3_4')]//div[contains(@class,'et_pb_text')]/text()",
        'performers': '//div[contains(@class, "et_pb_text_align_left")]/ul/li[contains(., "Models")]/a/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '',
        'external_id': 'project/([a-z0-9-_]+)/?',
        'trailer': '',
        'pagination': '/videos/?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.css(
            '.et_pb_portfolio_items .et_pb_portfolio_item a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
