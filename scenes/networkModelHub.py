import scrapy
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper


class ModelHubScraper(BaseSceneScraper):
    name = 'ModelHub'
    network = 'Pornhub'
    network = 'Pornhub'

    models = [
        'Alice Redlips',
        'Anisyia',
        'Brandi Love',
        'Britney Amber',
        'Cherie DeVille',
        'Dani Daniels',
        'DeNata',
        'Diane Andrews',
        'Diana Daniels',
        'Eva Elfie',
        'Jada Kai',
        'Jane Cane',
        'Joibae',
        'kisankanna',
        'Kriss Kiss',
        'Kyle Balls WCA',
        'Larkin Love',
        'Madeincanarias',
        'Meana Wolf',
        'Mia Melano Official',
        'Mila Fox',
        'Mini Diva',
        'MissArianaxxx',
        'Miss Banana',
        'Morgpie',
        'PrincessHaze',
        'Purple Bitch',
        'Reislin',
        'Shaiden Rogue',
        'Spring Blooms',
        'Taylor Noir',
        'Via Hub',
        'Xev Bellringer',
        'Yinyleon'
    ]

    selector_map = {
        'title': '.videoShortInfo h1::text',
        'tags': '.videoCategories a::text',
        'date': '.videoAdded p::text',
        'image': '//meta[@property="og:image"]/@content',
        'external_id': 'video/(.+)',
        'trailer': '',
    }

    def start_requests(self):
        for model in self.models:
            yield scrapy.Request(url=self.get_next_page_url(model, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'model': model},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            count = 0
            for scene in response.css(
                    'li.videoBox a.videoTitle::attr(href)').getall():
                count += 1
                yield response.follow(
                    url='https://www.modelhub.com' + scene,
                    callback=self.parse_scene,
                    meta={'model': response.meta['model']},
                    headers=self.headers,
                    cookies=self.cookies
                )

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    next_page = response.meta['page'] + 1
                    print('NEXT PAGE: ' + str(next_page))
                    yield scrapy.Request(url=self.get_next_page_url(response.meta['model'], next_page),
                                         callback=self.parse,
                                         meta={
                        'page': next_page, 'model': response.meta['model']},
                        headers=self.headers,
                        cookies=self.cookies)

    def get_performers(self, response):
        return [
            response.meta['model']
        ]

    def get_site(self, response):
        return 'PornHub Premium: ' + response.meta['model']

    def get_next_page_url(self, model: str, page: int):
        return 'https://www.modelhub.com/%s/videos?t=mr&page=%s' % (
            slugify(model), page)
