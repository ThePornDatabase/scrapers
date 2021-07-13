import scrapy
import time
import datetime
import dateparser
import re


from tpdb.BaseSceneScraper import BaseSceneScraper


class PornCZSpider(BaseSceneScraper):
    name = 'PornCZ'
    network = 'PornCZ'
    parent = 'PornCZ'

    start_urls = [
        'https://www.porncz.com'
        # 'https://www.amateripremium.com',
        # 'https://www.amateursfrombohemia.com',
        # 'https://www.boysfuckmilfs.com',
        # 'https://www.chloelamour.com',
        # 'https://www.czechanalsex.com',
        # 'https://www.czechbiporn.com',
        # 'https://www.czechboobs.com',
        # 'https://www.czechdeviant.com',
        # 'https://www.czechescortgirls.com',
        # 'https://www.czechexecutor.com',
        # 'https://www.czechgaycity.com',
        # 'https://www.czechgypsies.com',
        # 'https://www.czechhitchhikers.com',
        # 'https://www.czechrealdolls.com',
        # 'https://www.czechsexcasting.com',
        # 'https://www.czechsexparty.com',
        # 'https://www.czechshemale.com',
        # 'https://www.dellaitwins.com',
        # 'https://www.dickontrip.com',
        # 'https://www.fuckingoffice.com',
        # 'https://www.fuckingstreet.com',
        # 'https://www.girlstakeaway.com',
        # 'https://www.hornydoctor.com',
        # 'https://www.hornygirlscz.com',
        # 'https://www.hunterpov.com',
        # 'https://www.ladydee.com',
        # 'https://www.publicfrombohemia.com',
        # 'https://www.retroporncz.com',
        # 'https://www.sexintaxi.com',
        # 'https://www.sexwithmuslims.com',
        # 'https://www.susanayn.com',
        # 'https://www.teenfrombohemia.com',
        # 'https://www.vrporncz.com',
    ]

    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    cookies = {
        'age-verified': '1',
    }

    selector_map = {
        'title': '//div[@class="heading-detail"]/h1/text()',
        'description': '//div[@class="heading-detail"]/p/text()',
        'performers': '//div[contains(text(), "Actors")]/a/text()',
        'date': '//meta[@property="video:release_date"]/@content',
        'date_formats': ['%d.%m.%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(text(), "Genres")]/a/text()',
        'external_id': r'\/(\d+)$',
        'trailer': '//meta[@property="og:video"]/@content',
        'pagination': '/en/new-videos?do=next&_=%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, '/en/new-videos'),
                                 callback=self.parse,
                                 meta={'page': 0},
                                 headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        count = 0
        if response.meta['page']:
            scenes = self.get_scenes(response)
            for scene in scenes:
                count += 1
                yield scene

        if count or not response.meta['page']:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                timestamp = str(int(time.time()))
                yield scrapy.Request(url=self.get_next_page_url(response.url, timestamp),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['snippets']['snippet-videosGrid-videoItemsAppend']

        scenes = re.findall(r'a\ href=\"(.*)\"', jsondata)
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url

    def get_site(self, response):
        site = response.xpath('//a[contains(@class, "logo")]/img/@alt').get()
        if site:
            return site.strip().title()
        else:
            return super().get_site(response)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        date = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        return dateparser.parse(date.strip()).isoformat()

    def get_network(self, response):
        return "Porn CZ"

    def get_parent(self, response):
        return "Porn CZ"
