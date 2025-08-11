import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSexMexAltSpider(BaseSceneScraper):
    name = 'SexMexAlt'
    network = 'SexMex'
    parent = 'SexMex'
    site = 'SexMex'

    start_urls = [
        'https://exposedlatinas.com',
        # ~ 'https://sexmexamateurs.com',
        # ~ 'https://transqueens.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': r'',
        'trailer': '//video/source/@src',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"col-lg-4 col-md-4 col-xs-16 thumb")]')
        for scene in scenes:
            item = SceneItem()

            date = scene.xpath('.//p[@class="scene-date"]/text()')
            if date:
                date = date.get()
                date = self.parse_date(date.strip()).strftime('%Y-%m-%d')
            else:
                date = None
            title = scene.xpath('.//h5/a/text()').get()
            title = title.title()
            if " . " in title:
                title = re.search(r'^(.*) \. ', title).group(1).strip()
            description = scene.xpath('.//p[contains(@class,"scene-descr")]/text()').get()
            image = scene.xpath('.//img/@src').get()
            image = image.replace(" ", "%20")
            if "transform.php" in image or "url=" in image:
                image = re.search(r'url=(.*)', image).group(1)
            performers = scene.xpath('.//a[contains(@class, "modelnamesut") and contains(@href, "/models/")]/text()').getall()

            sceneid = scene.xpath('./@data-setid').get()

            scene = scene.xpath('./div/a/@href').get()

            item['title'] = title
            item['date'] = date
            item['description'] = description
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*)\?', item['image']).group(1)
            item['performers'] = performers
            item['tags'] = ['Latina', 'South American']
            item['id'] = sceneid
            item['type'] = 'Scene'
            item['trailer'] = ''
            if "exposedlatinas" in response.url:
                item['site'] = 'Exposed Latinas'
                item['parent'] = 'SexMex'
                item['network'] = 'SexMex'
            if "sexmexamateurs" in response.url:
                item['site'] = 'Sexmex Amateurs'
                item['parent'] = 'SexMex'
                item['network'] = 'SexMex'
                item['tags'].append('Amateur')
            if "transqueens" in response.url:
                item['site'] = 'Trans Queens'
                item['parent'] = 'SexMex'
                item['network'] = 'SexMex'
                item['tags'].append('Trans')
            item['url'] = scene

            yield self.check_item(item, self.days)
