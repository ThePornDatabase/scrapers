from tpdb.BaseSceneScraper import BaseSceneScraper
from urllib.parse import urlencode
import scrapy


class SiteStockyDudesSpider(BaseSceneScraper):
    name = 'StockyDudes'

    start_urls = [
        'https://www.stockydudes.com',
    ]

    selector_map = {
        'title': '//h2[contains(@class,"sectionMainTitle")]/text()',
        'description': '//div[@class="row container_styled_1"]'
        '//div[@class="p-5"]/p/text()',
        'date': '//div[@class="row container_styled_1"]//div[@class="p-5"]'
        '//i[@class="icon-clock-1"]/preceding-sibling::text()',
        're_date': r'([\w]*\s?\d{1,2}[,]?\s?\d{4})',
        'image': './/div[@id="playerWrap"]/img/@src',
        'performers': '//span[@class="perfImage"]//br'
        '/following-sibling::text()',
        'tags': '//a[@class="tagsRnd"]/text()',
        'duration': '//div[@class="row container_styled_1"]//div[@class="p-5"]'
        '//i[@class="icon-clock-1"]/following-sibling::text()',
        'external_id': r'.*/(.*?)/?$',
        'pagination': '/scenes?Page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        selector = response.selector

        if ('json' in response.headers.get('Content-Type').decode('utf-8')
           and 'html' in response.json()):
            selector = scrapy.Selector(text=response.json()['html'])

        scenes = selector.xpath(
                '//div[@class="scene_title"]//a[contains(@href,"/scene/")]'
                '/@href'
            ).getall()

        for scene in scenes:

            trailer = selector.xpath('//figure//a[@href="' +
                                     str(scene) + '"]//source/@src').get()
            meta = {}
            meta['trailer'] = trailer

            yield scrapy.Request(url=self.format_link(response, str(scene)),
                                 callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)

        if "Gay" not in tags:
            tags.append("Homosexual")

        return tags

    def get_pagin_data(self, response):
        page_data = {}
        page_data['from'] = int(response.xpath(
            '//div[@id="scenesLoadMore"]/@data-from').get())
        page_data['filter'] = response.xpath(
            '//div[@id="scenesLoadMore"]/@data-filter').get()
        page_data['sort'] = response.xpath(
            '//div[@id="scenesLoadMore"]/@data-sort').get()
        page_data['_'] = '1212121'

        return page_data
    
    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0

        if 'pagingData' not in response.meta:
            response.meta['pagingData'] = self.get_pagin_data(response)

        for scene in scenes:
            count += 1
            yield scene

        if count:
            if ('page' in response.meta and
                    response.meta['page'] < self.limit_pages):
                meta = response.meta
                meta['page'] = meta['page'] + 1
                meta['pagingData']['from'] += count

                print('NEXT PAGE: ' + str(meta['page']))

                link = self.format_link(response, '/_ajaxLoadScenes.php?'
                                        + urlencode(meta['pagingData']))
                self.headers['x-requested-with'] = 'XMLHttpRequest'

                yield scrapy.Request(url=link, callback=self.parse, meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)
