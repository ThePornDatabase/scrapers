import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPinkVisualSpider(BaseSceneScraper):
    name = 'PinkVisual'
    network = 'Pink Visual'

    start_urls = [
        'http://www.pvlocker.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//p[@class="summary"]/text()',
        'image': '//div[@id="featured_photo"]/a/img/@src',
        'performers': '//p[contains(@class,"starView")]/a/text()',
        'tags': '//p[contains(@class,"nichesView")]/a/text()',
        'trailer': '',
        'external_id': r'episode/(.*?)/',
        'pagination': '/s2/recent/%s/?sort=updates&revid=57503'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="freeBanner"]/following-sibling::a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[@id="summary"]/h1/a/text()')
        if site:
            site = site.get()
            if "Acid Rain" in site:
                return "PinkVisual Acid Rain"
            if "Confessions" in site:
                return "PinkVisual Confessions"
            if "Demolition" in site:
                return "PinkVisual Demolition"
            if "Wastland" in site:
                return "PinkVisual Wasteland"
            return site.strip()
        return super().get_site(response)

    def get_parent(self, response):
        site = response.xpath('//div[@id="summary"]/h1/a/text()')
        if site:
            site = site.get()
            if "Acid Rain" in site:
                return "PinkVisual Acid Rain"
            if "Confessions" in site:
                return "PinkVisual Confessions"
            if "Demolition" in site:
                return "PinkVisual Demolition"
            if "Wastland" in site:
                return "PinkVisual Wasteland"
            return site.strip()
        return super().get_parent(response)

    def get_url(self, response):
        url = super().get_url(response)
        if re.search(r'(.*?)\?', url):
            return re.search(r'(.*?)\?', url).group(1)
        return url

    def check_item(self, item, days=None):
        if "Elegant Angel" in item['site'] or "Holly Randall" in item['site'] or "ThirdWorldMedia" in item['site']:
            return None
        if days:
            if days > 27375:
                filter_date = '0000-00-00'
            else:
                days = self.days
                filter_date = date.today() - timedelta(days)
                filter_date = filter_date.strftime('%Y-%m-%d')

            if self.debug:
                if not item['date'] > filter_date:
                    item['filtered'] = 'Scene filtered due to date restraint'
                print(item)
            if filter_date:
                if item['date'] > filter_date:
                    return item
                return None
        else:
            return item
