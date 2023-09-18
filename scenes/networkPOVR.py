import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkPOVRSpider(BaseSceneScraper):
    name = 'POVR'
    network = 'POVR'
    parent = 'POVR'

    start_urls = [
        'https://povr.com'
    ]

    selector_map = {
        'title': '//h1[@class="player__title"]/text() | //h4/text() | //h1[contains(@class,"heading-title")]/text()',
        'description': '//p[contains(@class,"description")]/text() | //div[@class="player__description"]/p/text()',
        'performers': '//a[contains(@class,"actor")]/text() | //ul/li/a[contains(@class,"btn--eptenary")]/text()|//ul[contains(@class,"category-link")]/li/a[contains(@href, "/pornstars/")]/text()',
        'date': '//div[@class="player__meta"]/div[3]/span/text() | //p[contains(@class,"player__date")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'tags': '//a[contains(@class,"tag")]/text() | //ul/li/a[contains(@class,"btn--default")]/text()',
        'site': '//a[contains(@class,"source")]/text() | //ul/li/a[contains(@class,"btn--secondary")]/text()',
        'external_id': r'.*-(\d+)$',
        'trailer': '',
        # ~ 'pagination': '/?p=%s'
        'pagination': '/studios/povr-originals?p=%s'
    }

    def start_requests(self):
        link = "https://povr.com"
        yield scrapy.Request(url=link, callback=self.change_preferences, cookies=self.cookies, headers=self.headers)

    def change_preferences(self, response):
        headers = self.headers
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8]"
        body = "ui_update_flags=t,fp&merge=1"

        yield scrapy.Request(url="https://povr.com/account/ui-settings.json", callback=self.start_requests2, method="POST", body=body, cookies=self.cookies, headers=headers)

    def start_requests2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="teaser-video"]/a/@href | //a[@class="thumbnail__link"]/@href').getall()
        for scene in scenes:
            if "czech-vr" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = self.process_xpath(response, self.get_selector_map('site')).get()
        if site:
            return site
        return super().get_site(response)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date.replace('Released:', '').replace('Added:', '').strip()
            if "min" in date or "•" in date and "," in date:
                date = re.search(r'.*\ (\d{1,2}\ .*\d{4})', date).group(1)
        return self.parse_date(date.strip()).isoformat()

    def get_performers(self, response):
        performers = self.process_xpath(
            response, self.get_selector_map('performers')).getall()
        if performers:
            return list(map(lambda x: string.capwords(x.strip()), performers))
        return []

    def get_duration(self, response):
        duration = response.xpath('//p[contains(@class,"player__date")]/text()')
        if duration:
            duration = duration.get()
            if " min" in duration:
                duration = re.search(r'(\d+) [mM]in', duration)
                if duration:
                    return str(int(duration.group(1)) * 60)
        return ''

    def parse_scene(self, response):
        item = SceneItem()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if hasattr(self, 'site'):
            item['site'] = self.site
        elif 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None

        if 'image_blob' in response.meta:
            item['image_blob'] = response.meta['image_blob']
        else:
            item['image_blob'] = self.get_image_blob(response)

        if ('image_blob' not in item or not item['image_blob']) and item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if 'image_blob' not in item:
            item['image_blob'] = None

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

        if 'markers' in response.meta:
            item['markers'] = response.meta['markers']
        else:
            item['markers'] = self.get_markers(response)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        if 'merge_id' in response.meta:
            item['merge_id'] = response.meta['merge_id']
        else:
            item['merge_id'] = self.get_merge_id(response)

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        if 'duration' in response.meta:
            item['duration'] = response.meta['duration']
        else:
            item['duration'] = self.get_duration(response)

        if 'url' in response.meta:
            item['url'] = response.meta['url']
        else:
            item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        elif 'network' in response.meta:
            item['network'] = response.meta['network']
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        elif 'parent' in response.meta:
            item['parent'] = response.meta['parent']
        else:
            item['parent'] = self.get_parent(response)

        # Movie Items

        if 'store' in response.meta:
            item['store'] = response.meta['store']
        else:
            item['store'] = self.get_store(response)

        if 'director' in response.meta:
            item['director'] = response.meta['director']
        else:
            item['director'] = self.get_director(response)

        if 'format' in response.meta:
            item['format'] = response.meta['format']
        else:
            item['format'] = self.get_format(response)

        if 'back' in response.meta:
            item['back'] = response.meta['back']
        else:
            item['back'] = self.get_back_image(response)

        if 'back' not in item or not item['back']:
            item['back'] = None
            item['back_blob'] = None
        else:
            if 'back_blob' in response.meta:
                item['back_blob'] = response.meta['back_blob']
            else:
                item['back_blob'] = self.get_image_back_blob(response)

            if ('back_blob' not in item or not item['back_blob']) and item['back']:
                item['back_blob'] = self.get_image_from_link(item['back'])

        if 'back_blob' not in item:
            item['back_blob'] = None

        if 'sku' in response.meta:
            item['sku'] = response.meta['sku']
        else:
            item['sku'] = self.get_sku(response)

        if hasattr(self, 'type'):
            item['type'] = self.type
        elif 'type' in response.meta:
            item['type'] = response.meta['type']
        elif 'type' in self.get_selector_map():
            item['type'] = self.get_selector_map('type')
        else:
            item['type'] = 'Scene'

        matches = ['virtualtaboo', 'virtualrealporn', 'virtualrealtrans', 'virtualrealpassion', 'virtualrealamateur', 'realjamvr', 'only3x', 'wankzvr', 'naughtyamerica', 'vrhush']
        if not any(x in re.sub('[^a-zA-Z0-9-]', '', item['site']).lower() for x in matches):
            yield self.check_item(item, self.days)
