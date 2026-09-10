import re
from datetime import date

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteYanksSpider(BaseSceneScraper):
    name = 'Yanks'
    site = 'Yanks'
    parent = 'Yanks'
    network = 'Yanks'

    start_urls = [
        'https://www.yanks.com'
    ]

    # Yanks has withdrawn its scene pages: every /trailers/<slug>.html, every
    # /models/<name>.html and the site root itself now answer 302 back to the
    # splash page, which is why the crawl produced nothing but redirects.  The
    # category listings are the only surviving public surface, so the item is
    # built entirely from the listing card.  No synopsis or tags are published
    # there, so those stay empty.  Only the first listing page carries real scene
    # URLs -- from page 2 on every card links to the join tracker instead, so the
    # external_id check skips them and pagination stops of its own accord.
    selector_map = {
        'title': '',
        'description': '',
        'performers': '',
        'date': '',
        'image': '',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/Movies_%s_d.html'
    }

    def parse(self, response, **kwargs):
        count = 0
        for scene in self.get_scenes(response):
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse, meta=meta,
                                     headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        # The outer wrapper is div.item-updates, which contains() would also match,
        # so the card class is matched exactly.
        cards = response.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " "), " item-update ")]')

        # The cards carry the day as MM/DD with no year, listed newest first, so the
        # year is carried down the page and rolled back whenever the month jumps up.
        year = response.meta.get('year', date.today().year)
        last_month = response.meta.get('last_month', date.today().month)

        for card in cards:
            link = card.xpath('.//div[@class="item-title"]/a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            item = self.init_scene()
            item['title'] = self.cleanup_title(
                card.xpath('.//div[@class="item-title"]/a/@title').get() or '')
            if not item['title']:
                continue

            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['url'] = self.format_link(response, link)
            item['id'] = re.search(self.get_selector_map('external_id'), link).group(1)

            info = ' '.join(card.xpath('.//div[@class="item-date"]//text()').getall())

            scenedate = re.search(r'(\d{2})/(\d{2})', info)
            if scenedate:
                month, day = int(scenedate.group(1)), int(scenedate.group(2))
                if month > last_month:
                    year -= 1
                last_month = month
                item['date'] = '%04d-%02d-%02d' % (year, month, day)

            duration = re.search(r'(\d+):(\d{2})\s*$', info.strip())
            if duration:
                item['duration'] = str(int(duration.group(1)) * 60 + int(duration.group(2)))

            item['performers'] = [x.strip() for x in
                                  card.xpath('.//div[@class="item-models"]/a/text()').getall() if x.strip()]

            image = (card.xpath('.//img/@src0_4x').get()
                     or card.xpath('.//img/@src0_3x').get()
                     or card.xpath('.//img/@data-src').get() or '')
            if image:
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                # the thumbnail links are signed; drop the query once it has been fetched
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1) if '?' in item['image'] else item['image']

            item = self.check_item(item, self.days)
            if item:
                yield item

        response.meta['year'] = year
        response.meta['last_month'] = last_month
