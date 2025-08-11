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
        'description': '//p[contains(@class,"description")]/text() | //div[contains(@class,"player__description")]/p/text()',
        'performers': '//a[contains(@class,"actor")]/text() | //ul/li/a[contains(@class,"btn--eptenary")]/text()|//ul[contains(@class,"category-link")]/li/a[contains(@href, "/pornstars/")]/text()',
        'date': '//div[@class="player__meta"]/div[3]/span/text() | //p[contains(@class,"player__date")]/text()',
        're_date': r'(\d{1,2} \w+, \d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'tags': '//ul[contains(@class, "category-link")]/li/a[contains(@href, "/tags/")]/text()',
        'site': '//ul[contains(@class, "category-link")]/li/a[contains(@href, "/studios/")]/text()',
        'external_id': r'.*-(\d+)$',
        'trailer': '',
        # ~ 'pagination': '/?p=%s'
        'pagination': '/studios/povr-originals?o=d&p=%s'
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
        scenes = response.xpath('//div[contains(@class, "thumbnail") and contains(@class, "scene")]/a[1]/@href').getall()
        for scene in scenes:
            if "czech-vr" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="player__meta"]/div[3]/span/text() | //p[contains(@class,"player__date")]/text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return ''

    def get_site(self, response):
        site = self.process_xpath(response, self.get_selector_map('site')).get()
        if site:
            return site
        return super().get_site(response)

    def parse_scene(self, response):
        item = self.init_scene()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['url'] = self.get_url(response)
        item['id'] = re.search(r'.*-(\d+)$', response.url).group(1)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['network'] = self.get_network(response)
        item['parent'] = item['site']
        item['type'] = 'Scene'

        shortsite = re.sub(r'[^a-z0-9]', '', item['site'].lower())
        # ~ matches = ['vr-bangers', 'vrconk', 'vrbtrans', 'vrbgay', 'sinsvr', 'realjamvr', 'baberoticavr', 'fuckpassvr', 'czechvr', 'stripzvr', 'badoink', 'realvr', 'kinkvr', 'babevr', 'vrcosplayx', '18vr', 'wankzvr', 'vrhush', 'naughtyamerica']
        # ~ if not any(x in shortsite for x in matches):
            # ~ matches = ['virtualtaboo', 'virtualrealporn', 'virtualrealtrans', 'virtualrealpassion', 'virtualrealamateur', 'realjamvr', 'only3x', 'wankzvr', 'naughtyamerica', 'vrhush', 'realitylovers', 'porncorn', 'porncornvr']
            # ~ if not any(x in shortsite for x in matches):
                # ~ matches = ['swallowbay', 'wankitnowvr', 'baberoticavr', 'vr-bangers', 'vrconk', 'vrbtrans', 'vrbgay', 'sinsvr', 'realjamvr', 'baberoticavr', 'stripzvr', 'badoink', 'slr-milfvr', 'milfvr', 'tranzvr']
                # ~ if not any(x in shortsite for x in matches):
                    # ~ yield self.check_item(item, self.days)
        if shortsite == "povroriginals":
            yield self.check_item(item, self.days)
