import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDownBlouseWow_ByPerformerSpider(BaseSceneScraper):
    name = 'siteDownBlouseWow_ByPerformer'
    site = 'Downblouse Wow'
    parent = 'Downblouse Wow'
    network = 'Downblouse Wow'

    start_urls = [
        'https://downblousewow.com',
    ]

    selector_map = {
        'pagination': r'/show.php?a=147_%s',
        'external_id': r'lid=(\d+)',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="itemminfo"]/p/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.get_performer_scenes, meta=meta)

    def get_performer_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"vidblock")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('.//p[@class="vidname"]/a/text()').get())
            item['description'] = ""
            item['date'] = ""
            scenedate = scene.xpath('.//p[@class="date"]/text()')
            if scenedate:
                scenedate = scenedate.get()
                item['date'] = self.parse_date(scenedate).strftime('%Y-%m-%d')
            item['image'] = ""
            item['image_blob'] = ""
            image = scene.xpath('.//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            performer = scene.xpath('.//p[@class="vidname"]/a/text()')
            item['performers'] = []
            if performer:
                performer = performer.get()
                item['performers']. append(performer.strip())
            item['tags'] = ['Downblouse', 'Voyeur']
            item['trailer'] = ''
            sceneid = re.search(r'/(DB\d+.*?)_\d+', item['image'])
            if not sceneid:
                sceneid = re.search(r'.*/(.*?)\.', item['image'])
            item['id'] = sceneid.group(1)
            item['network'] = "Downblouse Wow"
            item['parent'] = "Downblouse Wow"
            item['site'] = "Downblouse Wow"
            item['url'] = f"https://downblousewow.com/join.html?g=content/DBW/movies/{item['id']}"
            yield self.check_item(item, self.days)
