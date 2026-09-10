import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAssumeThePositionStudiosSpider(BaseSceneScraper):
    name = 'AssumeThePositionStudios'
    network = 'Spanking Online'

    # The JSON API the spider was built on is gone: /api/site/<n>/updates/0 and
    # /api/update/<id>/trailer/ both 308 to the bare domain and then 404.  Every
    # site in the network now renders server-side -- /updates?page=N lists
    # div.atp-video-card cards linking to /trailer/<id> -- so the producer list the
    # API used to supply is enumerated from the network's own site switcher instead.
    sites = {
        'https://assumethepositionstudios.com': 'Assume The Position Studios',
        'https://canedschoolgirls.com': 'Caned School Girls',
        'https://disciplinaryarts.com': 'Disciplinary Arts',
        'https://fetishflixx.com': 'Fetish Flixx',
        'https://goodspanking.com': 'Good Spanking',
        'https://goodspankingclassics.com': 'Good Spanking Classics',
        'https://markedbutts.com': 'Marked Butts',
        'https://otkspank.com': 'OTK Spank',
        'https://spankedschoolgirl.com': 'Spanked School Girl',
        'https://spankingdigital.com': 'Spanking Digital',
        'https://spankingimages.com': 'Spanking Images',
        'https://spankingonline.com': 'Spanking Online',
        'https://spankmybottom.com': 'Spank My Bottom',
        'https://spankpass.com': 'SpankPass',
        'https://strictlyenglishonline.com': 'Strictly English Online',
        'https://strictspanking.com': 'Strict Spanking',
        'https://uspanking.com': 'Universal Spanking',
        'https://worstbehaviorproductions.com': 'Worst Behavior Productions',
    }

    selector_map = {
        'title': '//h1//text()',
        'description': '//div[contains(@class, "atp-video-details")]/preceding-sibling::div[1]/p//text()',
        'date': '//span[contains(text(), "Release Date")]/following-sibling::span[1]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '',
        'performers': '//span[contains(text(), "Models")]/following-sibling::div[1]//a[contains(@class, "atp-model-tag")]//text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'/trailer/(\d+)',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    async def start(self):
        for site_url, site_name in self.sites.items():
            meta = {'page': self.page, 'site': site_name, 'site_url': site_url}
            yield scrapy.Request(url=self.get_next_page_url(site_url, self.page), callback=self.parse,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "atp-video-card")]'):
            link = card.xpath('.//a[contains(@href, "/trailer/")]/@href').get()
            if not link:
                link = card.xpath('./ancestor::a[contains(@href, "/trailer/")]/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            meta['id'] = re.search(self.get_selector_map('external_id'), link).group(1)

            # the still and the runtime are only on the card
            image = card.xpath('.//img/@src').get()
            if image:
                meta['image'] = self.format_link(response, image)
            runtime = card.xpath('.//span[contains(@class, "atp-video-duration")]/text()').get()
            if runtime:
                runtime = re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})', runtime)
                if runtime:
                    hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
                    meta['duration'] = str(hours * 3600 + minutes * 60 + seconds)

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        return response.meta.get('image', '')

    def get_duration(self, response):
        return response.meta.get('duration')

    def get_tags(self, response):
        return ['Spanking']

    def get_parent(self, response):
        return response.meta.get('site', 'Spanking Online')
