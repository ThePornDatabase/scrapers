import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


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
        'performers': '//a[contains(@class,"actor")]/text() | //ul/li/a[contains(@class,"btn--eptenary")]/text()',
        'date': '//div[@class="player__meta"]/div[3]/span/text() | //p[contains(@class,"player__date")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'tags': '//a[contains(@class,"tag")]/text() | //ul/li/a[contains(@class,"btn--default")]/text()',
        'site': '//a[contains(@class,"source")]/text() | //ul/li/a[contains(@class,"btn--secondary")]/text()',
        'external_id': r'.*-(\d+)$',
        'trailer': '',
        'pagination': '/?p=%s'
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
        return ["No Performers Listed"]
