import re
import scrapy
import os
import json
import datetime
from dateutil.relativedelta import relativedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePPPTVSpider(BaseSceneScraper):
    name = 'PPPTV'
    site = 'P-P-P TV'
    parent = 'P-P-P TV'
    network = 'P-P-P TV'

    start_urls = [
        'https://p-p-p.tv',
    ]

    selector_map = {
        'title': './/strong/text()[1]',
        'description': '',
        'date': './/i[contains(@class, "calendar")]/following-sibling::text()',
        'image': './/img/@src',
        'performers': '',
        'tags': '',
        'duration': './/i[contains(@class, "fa-clock")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/en/videos/list?page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        performer_list = './datafiles/PPPTV_Performers.json'
        if os.path.isfile(performer_list):
            f = open(performer_list)
            meta['performer_list'] = json.load(f)
            f.close()
        else:
            meta['performer_list'] = []

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        performer_list = meta['performer_list']['scenes']
        scenes = response.xpath('//turbo-frame//div[contains(@class, "col-md-4")]')
        for scene in scenes:
            datetest = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if datetest:
                datetest = datetest.get()
                if "in" not in datetest:
                    item = SceneItem()

                    item['title'] = self.get_title(scene)
                    item['duration'] = self.get_duration(scene)
                    item['description'] = ''
                    item['tags'] = ['European']
                    item['performers'] = []
                    for model in performer_list:
                        if model['name'] in item['title']:
                            if model['name'] == "Cat":
                                if "Cathaleya" not in item['title']:
                                    item['performers'].append(model['name'])
                            else:
                                item['performers'].append(model['name'])
                    for model in performer_list:
                        if " " in model['name']:
                            if model['name'].replace(" ", "").lower() in item['title'].replace(" ", "").lower():
                                item['performers'].append(model['name'])

                    item['performers'] = list(set(item['performers']))

                    item['date'] = self.get_date(scene)

                    item['image'] = self.get_image(scene, response)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                    item['url'] = self.format_link(response, scene.xpath('./a/@href').get())
                    item['id'] = re.search(r'.*/(.*?)$', item['url']).group(1)

                    item['trailer'] = ''
                    item['type'] = 'Scene'
                    item['site'] = "P-P-P TV"
                    item['parent'] = "P-P-P TV"
                    item['network'] = "P-P-P TV"

                    if item['id'] and item['title']:
                        yield self.check_item(item, self.days)

    def get_image(self, scene, response, path=None):
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        if not force_update or (force_update and "image" in force_fields):
            if 'image' in self.get_selector_map():
                image = self.get_element(scene, 'image', 're_image')
                if isinstance(image, list):
                    image = image[0]
                image = image.replace(" ", "%20")
                if path:
                    return self.format_url(path, image)
                else:
                    return self.format_link(response, image)
            return ''

        return []

    def get_date(self, response):
        today = datetime.datetime.now()
        datestring = self.process_xpath(response, self.get_selector_map('date')).get()
        datestring = datestring.lower()
        intervalcount = re.search(r'(\d+)', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
        if "minute" in datestring:
            date = today - relativedelta(minutes=intervalcount)
        if "hour" in datestring:
            date = today - relativedelta(hours=intervalcount)
        if "day" in datestring:
            date = today - relativedelta(days=intervalcount)
        if "today" in datestring:
            date = today
        if "yesterday" in datestring:
            date = today - relativedelta(days=1)
        if "week" in datestring:
            date = today - relativedelta(weeks=intervalcount)
        if "month" in datestring:
            date = today - relativedelta(months=intervalcount)
        if "year" in datestring:
            date = today - relativedelta(years=intervalcount)

        return date.isoformat()
