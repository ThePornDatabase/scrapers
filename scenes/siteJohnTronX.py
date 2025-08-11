import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJohnTronXSpider(BaseSceneScraper):
    name = 'JohnTronX'

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        link = "https://johntronx.com/api/?output=json&command=media.archive&type=videos"
        yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.json()
        for scene in scenes:
            item = self.init_scene()
            item['title'] = string.capwords(scene['title'])
            item['date'] = scene['scheduled_date']

            if self.check_item(item, self.days):
                item['image'] = self.filename_to_url(scene['filename'])
                if item['image']:
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    item['image_blob'] = ''

                item['id'] = scene['record_num']
                item['duration'] = scene['length']
                item['url'] = f"https://johntronx.com/video/-{item['id']}.html"
                item['network'] = 'JohnTronX'
                item['site'] = 'JohnTronX'
                item['parent'] = 'JohnTronX'

                if scene['tags']:
                    tags = scene['tags'].split(",")
                    for tag in tags:
                        if "scenes" not in tag.lower() and "john" not in tag.lower():
                            item['tags'].append(string.capwords(tag.strip()))

                yield self.check_item(item, self.days)

    def filename_to_url(self, filename):
        first_five = filename[:5]
        path_parts = list(first_five)
        base_url = "https://c81a221339.mjedge.net/thumbs"
        path = "/".join(path_parts)
        full_url = f"{base_url}/{path}/{filename}/{filename}-3.jpg"

        return full_url
