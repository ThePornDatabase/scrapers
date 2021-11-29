import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePornstarPlatinumSpider(BaseSceneScraper):
    name = 'PornstarPlatinum'
    network = "Pornstar Platinum"
    parent = "Pornstar Platinum"
    site = "Pornstar Platinum"

    start_urls = [
        'https://www.pornstarplatinum.com/',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-slider")]/h3/text()',
        'description': '//div[@class="panel-content"]/p/text()',
        'date': '//div[@class="panel-content"]/div/span[contains(text(),"Added")]/following-sibling::span/text()',
        'image': '//div[contains(@class, "video-tour")]/div/a/img/@src',
        'performers': '//div[@class="row"]/div[contains(@class,"columns info")]/h2/span[contains(text(),"eaturing")]/following-sibling::a/text()',
        'tags': '//div[@class="panel-content"]/div[@class="widget"]/div[@class="tagcloud"]/a/text()',
        'external_id': r'.*/(.*)\.html',
        'trailer': '',
        'pagination': '/tour/latest.php?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@id="videos-list"]//div[@class="item no-nth"]')
        for scene in scenes:
            meta = response.meta
            performers = []
            performers = scene.xpath('./div[@class="item-content"]/div/span[@class="marker left"]/text()')
            if performers:
                performers = performers.getall()
                meta['performers'] = list(map(lambda x: x.strip().title(), performers))

            image = scene.xpath('./div[@class="item-header"]/a/img/@rel')
            if image:
                image = image.get()
                meta['image'] = image.strip()

            scene = scene.xpath('./div[@class="item-content"]/h3/a/@href').get()
            if ".html" in scene:
                if re.search(self.get_selector_map('external_id'), scene) and "signup.php" not in scene:
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        search = re.search(self.get_selector_map('external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        search = search.replace("_", "-").strip().lower()
        search = re.sub('[^a-zA-Z0-9-]', '', search)
        return search
