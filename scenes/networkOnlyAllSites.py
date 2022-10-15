import re
from datetime import datetime
import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'OT': "Only Tease",
        'OO': "Only Opaques",
        'OS': "Only Secretaries",
        'OSS': "Only Silk and Satin",
        'OSW': "Only Sportswear",
        'OCO': "Only Costumes",
        'OAS': "Only All Sites",
    }
    return match.get(argument, '')


class NetworkOnlyAllSitesSpider(BaseSceneScraper):
    name = 'OnlyAllSites'
    network = 'Only All Sites'

    start_urls = [
        'https://www.onlyallsites.com/',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/index.cfm/updates/searcharchive/?page={}&intYear={}&intMonth={}'
    }

    cookies = {
        'cookieconsent_status': 'dismiss',
    }

    def start_requests(self):
        url = "https://www.onlyallsites.com/updates"
        yield scrapy.Request(url, callback=self.start_requests2,
                             headers=self.headers,
                             cookies=self.cookies)

    def start_requests2(self, response):
        currentmonth = datetime.now().month
        currentyear = datetime.now().year
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, currentmonth, currentyear),
                                 callback=self.parse,
                                 meta={'page': self.page, 'month': int(currentmonth), 'year': int(currentyear)},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if not count:
            meta['month'] = meta['month'] - 1
            if meta['month'] == 0:
                meta['month'] = 1
                meta['year'] = meta['year'] - 1

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['month'], meta['year']),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_next_page_url(self, base, page, month, year):
        return self.format_url(base, self.get_selector_map('pagination').format(page, str(year), str(month)))

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-row" and .//i[contains(@class,"fa-film")]]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//div[contains(@class,"personalContent")]//p//text()')
            if title:
                title = title.getall()
                title = "".join(title)
                item['title'] = title.strip()

            date = scene.xpath('.//div[contains(@class,"personalContent")]/div/span[1]/span[2]/following-sibling::text()')
            if date:
                date = date.get().strip()
                item['date'] = dateparser.parse(date, date_formats=['%m.%d.%Y']).isoformat()

            site = scene.xpath('.//div[contains(@class,"personalContent")]/div/span[1]/span[1]/text()')
            if site:
                item['site'] = match_site(site.get().strip())
                item['parent'] = "Only All Sites"
                item['network'] = "Only All Sites"

            image = scene.xpath('./div/img/following-sibling::a/img/@data-src')
            if image:
                item['image'] = image.get().strip()
                item['id'] = re.search(r'.*\/(.*?)\/.*\.jpg$', item['image']).group(1)
            else:
                item['image'] = None
                item['id'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            performers = scene.xpath('.//div[contains(@class,"personalContent")]//p/a/text()')
            if performers:
                performers = list(map(lambda x: x.strip(), performers.getall()))

            url = scene.xpath('./div/img/following-sibling::a/@href')
            if url:
                item['url'] = "https://www.onlyallsites.com" + url.get().strip()

            item['trailer'] = ''
            item['tags'] = ''

        return item
