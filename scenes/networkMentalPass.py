import re
from urllib.parse import urlparse
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkMentalPassSpider(BaseSceneScraper):
    name = 'MentalPass'
    network = 'Mental Pass'

    paginations = [
        ['http://www.amateursexteens.com', '/home?next=%s', 10, 'Amateur Sex Teens'],
        ['https://www.bitchstop.com', '/?next=%s', 10, 'Bitch Stop'],
        ['http://www.czasting.com', '/?next=%s', 7, 'Czasting'],
        ['http://www.lesbianpickups.com', '/?&next=%s', 5, 'Lesbian Pickups']
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//p[@class="mg-md"]/text()',
        'date': '//div[@class="row"]/div[contains(@class,"text-right")]/span/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@id="videoPlayer"]//video/@poster',
        'performers': '//h4[contains(text(), "Featured")]/following-sibling::p/a/text()',
        'tags': '//h4[contains(text(), "Tags")]/following-sibling::a/text()',
        'external_id': r'movies/(.*)/',
        'trailer': '//div[@id="videoPlayer"]//video/source/@src',
        'pagination': '/movies/page-%s/?tag=&q=&model=&sort=recent'
    }

    def start_requests(self):
        for pagination in self.paginations:
            url = self.get_next_page_url(pagination[0], self.page, pagination[1], pagination[2])
            print(f'Url: {url}')
            yield scrapy.Request(url, callback=self.parse, meta={'page': self.page, 'url': pagination[0], 'pagination': pagination[1], 'site': pagination[3], 'items': pagination[2]}, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
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
                    url = self.get_next_page_url(meta['url'], meta['page'], meta['pagination'], meta['items'])
                    yield scrapy.Request(url,
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination, items):
        page = int(page)
        page = ((page - 1) * items) + 1
        return self.format_url(url, pagination % str(page))

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article')
        for scene in scenes:
            item = SceneItem()

            if "czechgf" in response.url:
                title = scene.xpath('.//h2//text()').getall()
                title = " ".join(title)
            else:
                title = scene.xpath('.//h2/a/text()').get()
            if title:
                item['title'] = title.strip()

            image = scene.xpath('.//img[contains(@src,"right")][1]/@src|.//div[@id="Foto"]/img[1]/@src').get()
            if not image:
                image = scene.xpath('.//img[contains(@src,"left")][1]/@src').get()
            if image:
                uri = urlparse(response.url)
                base = uri.scheme + "://" + uri.netloc
                image = image[1:]
                item['image'] = base + image.strip()
                item['id'] = re.search(r'category/(.*?)/', image).group(1)
            else:
                item['image'] = None
                item['id'] = ''

            item['image_blob'] = None

            description = scene.xpath('.//div[@id="Text"]/div[@class="getAccess"]/following-sibling::text()').getall()
            if description:
                description = " ".join(description)
                item['description'] = description.strip()
            else:
                item['description'] = ''

            if "czechgf" not in response.url:
                performers = scene.xpath('.//h2/a/text()').get()
                if performers:
                    item['performers'] = [performers.strip()]
                else:
                    item['performers'] = ''
            else:
                item['performers'] = ''

            item['tags'] = ['European']
            if "czechgf" in response.url:
                item['tags'].append('Lesbian')

            item['date'] = self.parse_date('today').isoformat()
            item['url'] = response.url
            item['trailer'] = ''
            item['site'] = meta['site']
            item['parent'] = meta['site']
            item['network'] = "Mental Pass"

            if item['id'] and item['title']:
                yield item
