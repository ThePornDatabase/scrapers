import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'bdsmprison': 'BDSM Prison',
        'brutalpickups': 'Brutal Pickups',
        'hostelxxx': 'Hostel XXX',
        'latinapatrol': 'Latina Patrol',
        'teensinthewoods': 'Teens in the Woods',
        'brutaldungeon': 'Brutal Dungeon',
    }
    return match.get(argument, argument)


class FetishNetworkPagedSpider(BaseSceneScraper):
    name = 'FetishNetworkPaged'
    network = 'Fetish Network'
    parent = 'Fetish Network'

    start_urls = [
        ['http://www.latinapatrol.com/', '/t2/show.php?a=2079_%s&nats=typein.4.97.266.0.0.0.0.0'],
        ['http://www.hostelxxx.com/', '/t2/show.php?a=2069_%s&uvar=typein.4.96.265.0.0.0.0.0'],
        ['http://www.teensinthewoods.com/', '/t2/show.php?a=2027_%s&nats=typein.4.94.262.0.0.0.0.0'],
        ['http://www.brutalpickups.com/', '/t2/show.php?a=2015_%s&nats=typein.4.93.260.0.0.0.0.0'],
        ['http://www.bdsmprison.com/', '/t2/show.php?a=1993_%s&nats=typein.4.90.249.0.0.0.0.0'],
        ['http://www.brutaldungeon.com/', '/t2/show.php?a=2011_%s&nats=typein.4.89.248.0.0.0.0.0'],
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': r'updates\\/(.*)\\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': link[1]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        count = 0

        scenes = self.parse_scenepage(response)
        if scenes:
            count = len(scenes)
            for scene in scenes:
                yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(
            base, pagination % page)

    def parse_scenepage(self, response):
        scenelist = []
        if "brutaldungeon" in response.url:
            scenes = response.xpath('//div[contains(@class,"download-box-large")]/label/..')
        else:
            scenes = response.xpath('//div[@class="row"]/div[contains(@class,"content-image-video")]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = []
            item['title'] = ''
            item['id'] = ''

            if "brutaldungeon" in response.url:
                title = scene.xpath('.//h1/text()').get()
            else:
                title = scene.xpath('.//div[contains(@class,"vedio-text-area")]/h4/text()').get()
            if title:
                title = title.strip()
                if "Latina Patrol" in title:
                    performers = title.replace("Latina Patrol", "")
                    word_list = performers.split()
                    if len(word_list) == 2 or len(word_list) == 3:
                        item['performers'] = [performers.strip()]
                if "Teens In The Woods" in title:
                    performers = title.replace("Teens In The Woods", "")
                    performers = performers.replace("-", "")
                    performers = performers.replace("&", ",")
                    performers = performers.strip()
                    performerlist = performers.split(",")
                    for performeritem in performerlist:
                        word_list = performeritem.split()
                        if len(word_list) == 2 or len(word_list) == 3:
                            item['performers'].append(performeritem.strip())
                if "brutalpickups" in response.url or "bdsmprison" in response.url:
                    item['performers'] = [title]
                if "brutaldungeon" in response.url:
                    item['performers'] = []

            if title:
                title = title.strip()
                item['title'] = title

            if "brutaldungeon" in response.url:
                date = scene.xpath('.//span[contains(@class,"date")]/text()').get()
            else:
                date = scene.xpath('.//div[contains(@class,"image-text-area")]/h4/text()').get()

            if date:
                date = date.strip()
                item['date'] = self.parse_date(date.strip()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            if "brutaldungeon" in response.url:
                description = scene.xpath('.//p/text()').get()
            else:
                description = scene.xpath('.//h5/text()').get()
            if description:
                description = description.replace("Description: ", "").strip()
                item['description'] = description
            else:
                item['description'] = ''

            image = scene.xpath('.//video/@poster').get()
            if not image:
                image = scene.xpath('.//div[contains(@class,"image-section-blk")]/a/img/@src').get()
                if not image:
                    image = scene.xpath('.//div[contains(@class,"image-section-blk")]/a/img/@data-src').get()
                    if not image:
                        image = scene.xpath('.//label[@class="player"]//video/@poster').get()
                        if not image:
                            image = scene.xpath('.//label[@class="player"]/a/img/@src').get()

            if image:
                baseurl = re.search(r'(.*\/t2\/)', response.url).group(1)
                image = baseurl + image.strip()
            else:
                image = None

            item['image'] = image
            item['image_blob'] = None

            idcode = ''
            if re.search(r'p\d{3,4}_s\d{3,4}_\d{3,4}_', item['image']):
                idcode = re.search(r'p\d{3,4}_s\d{3,4}_(\d{3,4})_', item['image']).group(1)
                if idcode:
                    item['id'] = idcode.strip()
            else:
                if item['title']:
                    item['id'] = item['title'].replace(" ", "-")

            item['url'] = response.url
            item['tags'] = []
            item['trailer'] = ''
            item['parent'] = "Fetish Network"
            item['network'] = "Fetish Network"
            sitename = tldextract.extract(response.url).domain
            item['site'] = match_site(sitename)

            if item['id']:
                scenelist.append(item.copy())
                item.clear()

        return scenelist
