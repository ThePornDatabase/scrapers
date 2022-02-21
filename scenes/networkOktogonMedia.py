import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'loveherboobs': "Love Her Boobs",
        'loveherfeet': "Love Her Feet",
        'shelovesblack': "She Loves Black",
    }
    return match.get(argument, argument)


class OktogonMediaSpider(BaseSceneScraper):
    name = 'OktogonMedia'
    network = 'Oktogon Media'

    start_urls = [
        'https://www.shelovesblack.com',
        'https://www.loveherboobs.com',
        'https://www.loveherfeet.com'
    ]

    paginations = [
        '/tour/categories/interviews/%s/latest/',
        '/tour/categories/movies/%s/latest/',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//p[contains(@class, "description")]/text()',
        'performers': '//div[contains(@class, "featured")]/a/text()',
        'date': '../div//p[contains(@class, "video-date")]/text()',  # handled in get_scenes()
        'date_formats': ['%m/%d/%Y', '%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "video-tags")]/a/text()',
        'trailer': '',
        'external_id': r'trailers/(.*)\.html',
        'pagination': '/%s/latest/'
    }

    def start_requests(self):
        for url in self.start_urls:
            for pagination in self.paginations:
                meta = {'page': self.page, 'pagination': pagination}
                yield scrapy.Request(url=self.get_next_page_url(url, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"item-video-overlay")]/a')
        for scene in scenes:
            link = scene.xpath('./@href').get()

            date_formats = self.get_selector_map('date_formats') if 'date_formats' in self.get_selector_map() else None
            date = scene.xpath(self.get_selector_map('date')).get()
            date = self.parse_date(date, date_formats=date_formats).isoformat()
            meta = {'date': date}

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        return super().get_id(response).lower()

    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)
