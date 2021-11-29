import re
import string
from datetime import date, timedelta, datetime
from tpdb.items import SceneItem

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkAndomarkIndexSpider(BaseSceneScraper):
    name = 'AndomarkIndex'
    network = "Andomark"

    start_urls = [
        'https://www.humiliation4k.com',
        'https://www.nylons4k.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': '',
        'trailer': '',
        'pagination': '/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):

        sceneresponses = response.xpath('//div[@class="updateItem"]')

        items = []

        for sceneresponse in sceneresponses:
            item = SceneItem()
            item['network'] = 'Andomark'
            if "humiliation" in response.url:
                item['parent'] = 'Humiliation 4k'
                item['site'] = 'Humiliation 4k'
            if "nylons" in response.url:
                item['parent'] = 'Nylons 4k'
                item['site'] = 'Nylons 4k'

            # Trailer
            item['trailer'] = ''
            trailer = sceneresponse.xpath('.//h4/a/@onclick')
            if trailer:
                trailer = trailer.get().strip()
                trailer = re.search(r'(\/.*mp4)', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    item['trailer'] = self.format_link(response, trailer.strip())

            # Date
            scenedate = sceneresponse.xpath('.//p/span[contains(text(),"/")]/text()').get()
            if not scenedate:
                scenedate = datetime.now()
            item['date'] = self.parse_date(scenedate.strip(), date_formats=['%m/%d/%Y']).isoformat()

            # Performer
            item['performers'] = []
            performer = sceneresponse.xpath('.//p/span/a/text()')
            if performer:
                performer = performer.getall()
                item['performers'] = list(map(lambda x: x.strip(), performer))

            # Tags
            tags = []
            if "humiliation" in response.url:
                tags.extend(['Femdom', 'Humiliation', 'Fetish', 'Submission'])
            if "nylons" in response.url:
                tags.extend(['Pantyhose', 'Fetish', 'Legs'])
            item['tags'] = list(map(lambda x: x.strip(), tags))

            # Title
            title = sceneresponse.xpath('.//h4/a/text()').get()
            if not title:
                title = performer[0]
            item['title'] = string.capwords(title.strip())

            # Description
            item['description'] = ''

            # Image
            item['image'] = ''
            image = sceneresponse.xpath('./a/img/@src0_4x')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image.strip())

            item['image_blob'] = None

            # URL
            url = sceneresponse.xpath('./a/img/@src').get()
            url = re.search('(.*)\\.(?:jpg|png|gif)', url).group(1)
            url = url.replace('/1', '')
            item['url'] = self.format_link(response, url.strip())

            # ID
            itemid = sceneresponse.xpath('./a/img/@alt').get()
            item['id'] = itemid.strip().lower().replace(" ", "")

            # ~ print(f"Date: {item['date']}")
            # ~ print(f"Perf: {item['performers']}")
            # ~ print(f"Tags: {item['tags']}")
            # ~ print(f"Title: {item['title']}")
            # ~ print(f"Image: {item['image']}")
            # ~ print(f"Desc: {item['description']}")
            # ~ print(f"URL: {item['url']}")
            # ~ print(f"ID: {item['id']}")
            # ~ print("\n\n")

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
                        items.append(item)
                else:
                    items.append(item)

        return items
