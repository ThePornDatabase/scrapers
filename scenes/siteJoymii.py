import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class JoyMiiSpider(BaseSceneScraper):
    name = 'JoyMii'
    network = 'JoyMii'
    parent = 'JoyMii'

    start_urls = [
        'https://joymii.com'
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//p[@class="text"]/text()',
        'date': "//span[@class='post-date']/text()",
        'image': '//div[@id="video-set-details"]//video[@id="video-playback"]/@poster',
        'performers': '//h2[@class="starring-models"]/a/text()',
        'tags': "",
        'external_id': 'code\\/(.+)',
        'trailer': '',
        'pagination': '/get-content-list?blockName=latest&sortType=release_date&limit=36&onlyPhotos=&onlyVideos=1&sorting=date&tags=&actors=&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[contains(@class, 'box-results')]//div[contains(@class, 'set')]")
        for scene in scenes:
            meta = {
                'date': self.parse_date(scene.css('.release_date::text').get()).isoformat()
            }

            link = self.format_link(response, scene.css('a::attr(href)').get())

            yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta)
