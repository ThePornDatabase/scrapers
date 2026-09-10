import re
import html
import json
import requests
import string
import unidecode
import scrapy
from scrapy import Selector
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteILoveFrenchGirlsSpider(BaseSceneScraper):
    name = 'ILoveFrenchGirls'

    start_urls = [
        'https://www.ilovefrenchgirls.blog',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php/wp-json/wp/v2/posts?page=%s&per_page=20',
        'type': 'Scene',
    }

    async def start(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://ilovefrenchgirls.blog/index.php/wp-json/wp/v2/tags?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                tagtemp = json.loads(req.text)
                tagdata = tagdata + tagtemp
            else:
                break

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'tagdata': tagdata},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = self.init_scene()

            desc_block = scene['content']['rendered']
            desc_block = html.unescape(desc_block)
            desc_block = desc_block.replace("\\", "")

            item['trailer'] = ""

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip())
            item['title'] = re.sub(r'[^a-zA-Z0-9 \-&]', '', item['title'].replace("FRESH & NEW!", "").replace("NEW!", "")).strip()
            item['title'] = self.cleanup_title(item['title'])

            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['excerpt']['rendered'])).strip())
            if "Please purchase" in item['description'] or "To purchase" in item['description']:
                item['description'] = ''
            for tag_id in scene['tags']:
                for tag in meta['tagdata']:
                    if tag['id'] == tag_id:
                        item['tags'].append(string.capwords(tag['name']))

            item['site'] = 'I Love French Girls'
            item['parent'] = 'I Love French Girls'
            item['network'] = 'I Love French Girls'
            item['url'] = scene['link']

            sel = Selector(text=scene['content']['rendered'])
            image = sel.xpath('//img[contains(@src, "thumbnail")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            meta['item'] = item.copy()
            if 5 in scene['categories']:
                yield self.check_item(item, self.days)
