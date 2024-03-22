import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLadyboyGoldSpider(BaseSceneScraper):
    name = 'LadyboyGold'
    site = 'Ladyboy Gold'
    parent = 'Ladyboy Gold'
    network = 'Ladyboy Gold'

    selector_map = {
        'title': './/p[@class="setTitle"]/text()',
        'description': './/p[contains(@class, "setTRT") and contains(@class, "hidden-xs")]/text()',
        'date': '',
        'image': './/img/@src',
        'performers': './/p[@class="setModel"]/a/text()',
        'tags': './/p[contains(@class,"setTags")]/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = 'https://www.ladyboygold.com/index.php?section=1810'
        yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videoUpdate") and contains(@class, "col-xxxld")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            scenedate = scene.xpath('./comment()[contains(., "modelNames")]').getall()
            scenedate = "".join(scenedate)
            scenedate = scenedate.replace('\n', '').replace('\r', '').replace('\t', '')
            item['date'] = ''
            if scenedate:
                scenedate = re.search(r'(\w+\s+\d{1,2},\s+\d{4})', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                    item['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            item['image'] = scene.xpath('.//img/@src').get()
            if "&width" in item['image']:
                item['image'] = re.search(r'(.*)\&width', item['image']).group(1)
            if "&height" in item['image']:
                item['image'] = re.search(r'(.*)\&height', item['image']).group(1)
            if "&crop" in item['image']:
                item['image'] = re.search(r'(.*)\&crop', item['image']).group(1)
            if item['image']:
                item['image'] = "https://www.ladyboygold.com/" + item['image']
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image_blob'] = ''

            item['id'] = re.search(r'gal=(\d+)', item['image']).group(1)
            item['trailer'] = self.get_trailer(scene)
            duration = scene.xpath('.//p[@class="setTRT" and contains(text(), "Minutes")]/text()')
            if duration:
                duration = re.search(r'(\d+)', duration.get())
                if duration:
                    item['duration'] = str(int(duration.group(1)) * 60)

            item['url'] = f"https://www.ladyboygold.com/video/{item['id']}"
            item['network'] = self.network
            item['site'] = self.site
            item['parent'] = self.parent

            item['performers'] = self.get_performers(scene)
            item['tags'] = self.get_tags(scene)

            yield self.check_item(item, self.days)
