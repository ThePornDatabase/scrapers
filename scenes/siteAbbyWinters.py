import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class AbbyWintersSpider(BaseSceneScraper):

    name = 'AbbyWinters'
    network = 'Abby Winters'
    parent = 'Abby Winters'
    site = 'Abby Winters'

    custom_settings = {'CONCURRENT_REQUESTS': '4',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'ITEM_PIPELINES': {
                           'tpdb.pipelines.TpdbApiScenePipeline': 400,
                       },
                       'DOWNLOADER_MIDDLEWARES': {
                           'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
                       }
                       }

    start_urls = [
        'https://www.abbywinters.com'
    ]

    selector_map = {
        'title': '//div[@class="container"]/h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//li/i[@class="icon-eye-open"]/following-sibling::span/following-sibling::text()',
        'image': '//div[@class="feature-image"]/div/img/@src|//div[contains(@class,"video-player-container")]/@data-poster',
        'image_blob': '//div[@class="feature-image"]/div/img/@src|//div[contains(@class,"video-player-container")]/@data-poster',
        'performers': '//table[@class="table table-summary"]//th[contains(text(),"Girls in this Scene")]/following-sibling::td/a/text()',
        'tags': '//a[contains(@href,"/fetish/")]/text()',
        'external_id': 'abbywinters\\.com\\/(.*)',
        'trailer': '',
        'pagination': '/updates/raves?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//span[@class="icon_videoclip"]/../..')
        for scene in scenes:
            date = scene.xpath('./h2/span[contains(text()," 20")]/text()').get()
            date = self.parse_date(date.strip()).isoformat()
            scene = scene.xpath('./div[@class="thumb"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})

    def get_id(self, response):
        search = re.search(self.get_selector_map('external_id'), response.url, re.IGNORECASE)
        search = search.group(1).replace("/", "-")
        return search
