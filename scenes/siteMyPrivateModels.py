import string
import json
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMyPrivateModelSpider(BaseSceneScraper):
    name = 'MyPrivateModel'
    network = ''
    parent = ''
    site = ''

    start_urls = [
        ['https://private-lola.com', 'Private Lola', 'Lola Myluv'],
        ['https://sexy-lexi.com', 'Sexy Lexi', 'Lexi Dona'],
        ['https://victoriapure.net', 'Victoria Pure', 'Victoria Pure']
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': ''
    }

    def start_requests(self):
        categories = requests.get("https://private-lola.com/subdomain/categories/1")
        if categories:
            categories = json.loads(categories.content)
            tags = []
            for category in categories:
                tags.append({'id': category['id'], 'name': category['name']['en']['title']})

        for link in self.start_urls:
            url = link[0] + "/subdomain/videos"
            yield scrapy.Request(url, callback=self.get_scenes,
                                 meta={'page': self.page, 'tag_list': tags, 'link': link[0], 'site_name': link[1], 'performer': link[2]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        categories = response.meta['tag_list']
        site_name = response.meta['site_name']
        performer = response.meta['performer']
        link = response.meta['link']
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()
            if scene['name']['en']['title']:
                item['title'] = string.capwords(scene['name']['en']['title'].strip())
            else:
                item['title'] = string.capwords(scene['name']['de']['title'].strip())
            if scene['name']['en']['description']:
                item['description'] = string.capwords(scene['name']['en']['description'].strip())
            else:
                item['description'] = string.capwords(scene['name']['de']['description'].strip())
            item['date'] = self.parse_date(scene['date']).isoformat()
            item['id'] = scene['id']
            item['url'] = f"{link}/video.php/?url={item['id']}/"
            item['image'] = self.format_link(response, scene['thumbnail'])
            item['image_blob'] = ''
            item['trailer'] = ''
            item['tags'] = []
            if 'categories' in scene and scene['categories']:
                for tag in scene['categories']:
                    for category in categories:
                        if category['id'] == tag:
                            item['tags'].append(string.capwords(category['name']))

            item['performers'] = [performer]
            item['site'] = site_name
            item['parent'] = site_name
            item['network'] = "My Private Model"
            yield item
