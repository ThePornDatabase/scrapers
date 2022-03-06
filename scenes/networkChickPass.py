import re
import html
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteChickPassSpider(BaseSceneScraper):
    name = 'ChickPass'
    network = 'Chick Pass'

    start_urls = [
        'https://www.chickpass.com',
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/span/text()',
        'description': '//span[contains(@class, "description")]/span/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class, "update_description")]//span[contains(@class,"update_models")]/a/text()',
        'tags': '//span[contains(@class,"update_tags") and contains(@class, "show")]/a/text()',
        'external_id': r'.*\/(.*?)\.html',
        'trailer': '',
        'pagination': '/tour1/allsites/page-%s.html?s=d'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            site = scene.xpath('./div/div[contains(@class, "site_title")]/text()')
            if site:
                meta['site'] = site.get().strip()
            else:
                meta['site'] = False
            meta['date'] = self.parse_date('today').isoformat()
            date = scene.xpath('.//div[@class="date"]/text()')
            if date:
                date = " ".join(date.getall())
                date = re.search(r'(\w+ \d{1,2}, \d{4})', date)
                if date:
                    meta['date'] = self.parse_date(date.group(1), date_formats=['%b %d, %Y']).isoformat()

            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return super().get_site(response)

    def get_description(self, response):
        description = response.xpath(self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = " ".join(description)
            return html.unescape(description.strip())
        return ''

    def get_date(self, response):
        return dateparser.parse('today').isoformat()
