import re
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLegsJapanSpider(BaseSceneScraper):
    name = 'LegsJapan'
    network = 'Digital J Media'
    parent = 'Legs Japan'

    start_urls = [
        'https://www.legsjapan.com'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'performers': '',
        'date': '',
        'image': '',
        'tags': '',
        'trailer': '',
        'external_id': '',
        'pagination': '/en/samples?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('(//div[@class="tContent left"]|//div[@class="tContent right"])')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//h3[1]/strong/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)
            else:
                item['title'] = ''

            description = scene.xpath('.//h3[1]/strong/text()').get()
            if description:
                item['description'] = self.cleanup_description(description)
            else:
                item['description'] = ''

            performers = scene.xpath('.//h1/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip(), performers))
            else:
                item['performers'] = []

            tags = scene.xpath('.//h4[contains(text(),"tags")]/strong/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: x.strip(), tags))
            else:
                item['tags'] = []

            scenedate = scene.xpath('.//h3[contains(text(),"released")]/strong/text()').get()
            if scenedate:
                item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('./preceding-sibling::div[1]/@style').get()
            if image:
                image = re.search('(https:.*.jpg)', image).group(1)
                if image:
                    item['image'] = image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            if item['image']:
                extern_id = re.search(r'samples/(.*?)/', item['image']).group(1)
                if extern_id:
                    item['id'] = extern_id.strip()
                    item['trailer'] = "https://cdn.legsjapan.com/samples/" + extern_id.strip() + "/sample.mp4"

            item['site'] = "Legs Japan"
            item['parent'] = "Legs Japan"
            item['network'] = "Digital J Media"

            item['url'] = "https://www.legsjapan.com/en/samples/" + item['id']

            days = int(self.days)
            if days > 27375:
                filterdate = "0000-00-00"
            else:
                filterdate = date.today() - timedelta(days)
                filterdate = filterdate.strftime('%Y-%m-%d')

            if self.debug:
                if not item['date'] > filterdate:
                    item['filtered'] = "Scene filtered due to date restraint"
                print(item)
            else:
                if filterdate:
                    if item['date'] > filterdate:
                        yield item
                else:
                    yield item
