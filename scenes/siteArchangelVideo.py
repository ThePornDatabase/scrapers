import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ArchangelVideoSpider(BaseSceneScraper):
    name = 'ArchangelVideo'
    network = "Archangel"
    parent = "Archangel"

    start_urls = [
        'https://www.archangelvideo.com/',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?)\.html',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-episode"]')
        scenelist = []
        for scene in scenes:
            item = SceneItem()
            item['site'] = "Arch Angel"
            item['parent'] = "Arch Angel"
            item['network'] = "Arch Angel"
            title = scene.xpath('.//h3/a/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = 'No Title Available'

            date = scene.xpath('.//strong[contains(text(),"Date")]/following-sibling::text()')
            if date:
                item['date'] = self.parse_date(date.get()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            performers = scene.xpath('./div[@class="item-info"]//a[contains(@href,"/models/") or contains(@href,"sets.php")]/text()').getall()
            if len(performers):
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                item['performers'] = []

            image = scene.xpath('.//span[@class="left"]/a/img/@src0_1x').get()
            if image:
                image = image.replace('//', '/').strip()
                image = image.replace('#id#', '').strip()
                image = "https://www.archangelvideo.com" + image
                item['image'] = image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            item['trailer'] = ''

            url = scene.xpath('.//span[@class="left"]/a/@href').get()
            if url:
                item['url'] = url.strip()
                external_id = re.search(r'.*/(.*).html', url).group(1)
                if external_id:
                    item['id'] = external_id.strip().lower()
                else:
                    item['id'] = ''
            else:
                item['url'] = ''

            item['description'] = ''
            item['tags'] = []

            if item['title'] and item['id']:
                scenelist.append(item.copy())

            item.clear()

        return scenelist
