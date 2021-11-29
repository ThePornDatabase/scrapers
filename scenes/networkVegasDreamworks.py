import re
from datetime import date
import tldextract
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def get_scenedate(scene):
    scenedate = scene.xpath('.//div[contains(@class,"fsdate")]/span/text()').get()
    if scenedate:
        scenedate = dateparser.parse(scenedate.strip(), settings={'TIMEZONE': 'UTC'}).isoformat()
    else:
        poster = scene.xpath('.//amp-video/@poster').get()
        if poster:
            if re.search(r'/(\d{4})/(\d{2})', poster):
                poster_groups = re.search(r'/(\d{4})/(\d{2})', poster)
                scenedate = poster_groups.group(1) + "-" + poster_groups.group(2) + "-01T12:00:00"
        else:
            poster = scene.xpath('.//amp-img/@src').get()
            if poster:
                if re.search(r'/(\d{4})/(\d{2})', poster):
                    poster_groups = re.search(r'/(\d{4})/(\d{2})', poster)
                    scenedate = poster_groups.group(1) + "-" + poster_groups.group(2) + "-01T12:00:00"
            else:
                poster = scene.xpath('.//div[contains(@class,"entry-media")]/img/@src').get()
                if poster:
                    if re.search(r'/(\d{4})/(\d{2})', poster):
                        poster_groups = re.search(r'/(\d{4})/(\d{2})', poster)
                        scenedate = poster_groups.group(1) + "-" + poster_groups.group(2) + "-01T12:00:00"

    if scenedate:
        return scenedate
    return date.today().isoformat()


class NetworkVegasDreamworksSpider(BaseSceneScraper):
    name = 'VegasDreamworks'
    network = 'Vegas Dreamworks'
    parent = 'Vegas Dreamworks'

    start_urls = [
        ['https://asiansexdiary.com', '/category/diary/page/%s/', 'Asian Sex Diary'],
        ['https://milftrip.com/', '/all-updates/page/%s/', 'MILF Trip'],
        ['https://helloladyboy.com', '/all-updates/page/%s/', 'Hello Ladyboy'],
        ['https://paradisegfs.com', '/movies/page/%s/', 'Paradise GFs'],
        ['https://screwmetoo.com', '/all-updates/page/%s/', 'Screw Me Too'],
        ['https://trikepatrol.com/', '/all-updates/page/%s/', 'Trike Patrol'],
        ['https://tuktukpatrol.com/', '/all-updates/page/%s/', 'TukTuk Patrol'],
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"artl-cnt")]//p/text()|//span[@class="latest_update_description"]/p/text()|//div[contains(@class,"artl-cnt")]//h2/following-sibling::text()',
        'date': '',
        'image': '//div[contains(@class,"video-player")]//amp-img/@src',
        'performers': '//div[@class="update-info"]/a[contains(@href,"/model/")]/text()|//div[@class="update_bb_info"]/a[contains(@href,"/model_content/")]/text()',
        'tags': '//div[@class="amp-category"]/span/a/text()|//div[@class="cat_tag"]/a/text()',
        'external_id': r'.*/(.+)/$',
        'trailer': '//div[contains(@class,"video-player")]//amp-video/@src|//div[contains(@class,"preview_trailer")]//video/source/@src',
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': link[1], 'site': link[2], 'url': link[0]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = response.meta
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    url = meta['url']
                    yield scrapy.Request(url=self.get_next_page_url(url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article|//div[contains(@class,"entry-content")]')
        for scene in scenes:
            meta['date'] = get_scenedate(scene)
            sceneurl = scene.xpath('./a/@href').get()
            if not sceneurl:
                sceneurl = scene.xpath('./div/div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), sceneurl):
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        description = self.process_xpath(
            response, self.get_selector_map('description')).getall()
        if description:
            for desc in description:
                desc = desc.strip()
            description = ' '.join(description)
            return description.strip()

        return ''

    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return tldextract.extract(response.url).domain

    def get_date(self, response):
        meta = response.meta
        if meta['date']:
            return meta['date']
        return date.today().isoformat()

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//meta[@property="og:image"]/@content').get()
        if image:
            return self.format_link(response, image)

        return ''

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                if trailer[0:6] == "/asset":
                    return ''
                return trailer
        return ''
