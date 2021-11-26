import re
from datetime import date, timedelta
import string
import base64
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteThisIsGlamourSpider(BaseSceneScraper):
    name = 'ThisIsGlamour'
    network = 'This Is Glamour'

    start_urls = [
        'http://www.thisisglamour.com',
    ]

    phpsessid = ''

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': '',
        'trailer': '',
        'pagination': '/glamour-videos/?start=%s&count=28'
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 25)
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url

    def get_scenes(self, response):
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            if "PHPSESSID" in str(cookie):
                self.phpsessid = re.search(r'SESSID=(.*?);', str(cookie)).group(1)

        scenes = response.xpath('//div[@class="product-item"]')
        for scene in scenes:
            item = SceneItem()
            item['network'] = "This Is Glamour"
            item['parent'] = "This Is Glamour"
            item['site'] = "This Is Glamour"

            title = scene.xpath('./h3/a/text()')
            item['title'] = ''
            if title:
                item['title'] = string.capwords(title.get().replace("...", ""))

            image = scene.xpath('./div/a/img/@src')
            item['image'] = None
            if image:
                image = image.get().strip().replace("https://", "http://")
                item['image'] = image
                item['id'] = re.search(r'galid\/(\d+)\/', item['image']).group(1)
                if self.phpsessid:
                    imagereq = requests.get(image, cookies={'PHPSESSID': self.phpsessid})
                    item['image_blob'] = base64.b64encode(imagereq.content).decode('utf-8')

            if not item['image_blob']:
                item['image_blob'] = None

            performers = scene.xpath('./div[@class="pi-model"]/a/text()')
            item['performers'] = []
            if performers:
                performers = performers.getall()
                item['performers'] = list(map(lambda x: x.replace(" TIG", "").strip().title(), performers))

            scenedate = scene.xpath('./div[@class="pi-added"]/text()')
            item['date'] = self.parse_date('today').isoformat
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%d %b %Y']).isoformat()

            item['url'] = response.url

            item['tags'] = ["Erotica"]
            if "bts" in item['title'].lower() or "bts" in response.url:
                item['tags'].append("BTS")

            item['trailer'] = ''
            item['description'] = ''

            if item['id'] and item['title']:
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
