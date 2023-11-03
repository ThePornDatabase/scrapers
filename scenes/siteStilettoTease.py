import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteStilettoTeaseSpider(BaseSceneScraper):
    name = 'StilettoTease'
    network = 'Stiletto Tease'
    parent = 'Stiletto Tease'
    site = 'Stiletto Tease'

    start_url = 'http://www.stilettotease.com/tour.html#updates'

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        yield scrapy.Request(url=self.start_url, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//comment()[contains(., "InstanceBeginRepeatEntry")]/following-sibling::table[1]//tr')
        for scene in scenes:
            item = SceneItem()
            item['title'] = ''
            title = scene.xpath('.//td[@class="whitebody"]/p[contains(text(), "Title")]/text()')
            if title:
                title = title.get()
                title = title.replace("Title", "").replace(":", "").strip()
                item['title'] = self.cleanup_title(title)

            item['date'] = ''
            scenedate = scene.xpath('.//td[@class="whitebody"]/p[contains(text(), "Added")]/text()')
            if scenedate:
                scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{2})', scenedate.get())
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%d%m/%y']).strftime('%Y-%m-%d')

            item['description'] = ''
            description = scene.xpath('.//td[@class="whitebody"]/p[5]/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())

            item['image'] = ''
            item['image_blob'] = ''
            image = scene.xpath('.//td[contains(@style, "padding-left: 15px;")]/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get()).replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)\.\w{3,4}$', item['image']).group(1)
                urlsnip = re.search(r'.*(/legend.*?)\.\w{3,4}$', item['image']).group(1)
                item['url'] = f"http://www.stilettotease.com/newsite{urlsnip}.html"
            item['tags'] = ['Foot Fetish', 'Feet', 'Stiletto']
            item['site'] = 'Stiletto Tease'
            item['parent'] = 'Stiletto Tease'
            item['network'] = 'Stiletto Tease'
            item['trailer'] = ''
            item['type'] = 'Scene'
            item['performers'] = []

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
