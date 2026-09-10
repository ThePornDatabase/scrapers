import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteHungarianHoneysSpider(BaseSceneScraper):
    name = 'HungarianHoneys'
    network = 'Hungarian Honeys'
    parent = 'Hungarian Honeys'
    site = 'Hungarian Honeys'

    start_urls = [
        'https://www.hungarianhoneys.com',
    ]

    cookies ={"name": "warn", "value": "true"}

    selector_map = {
        'title': '//article/section/div/div/div[@class="title-block"]/h2[@class="section-title"]/text()',
        'description': '//h3[contains(text(), "Description")]/following-sibling::text()',
        'date': '//h3[contains(text(), "Video")]/following-sibling::div[1]//strong[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[contains(@class, "player-window-play")]/following-sibling::img/@src0_1x',
        'performers': '//div[contains(@class, "models-list")]/ul/li/a/span/text()',
        'tags': '//h3[contains(text(), "Tags:")]/following-sibling::ul/li/a/text()',
        'duration': '//h3[contains(text(), "Video")]/following-sibling::div[1]//strong[contains(text(), "Runtime")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'RETRY_HTTP_CODES': [502, 503, 504, 522, 524, 408, 429],
    }

    async def start(self):
        # The listing serves a full page but answers with HTTP 500, which the
        # HttpErrorMiddleware drops by default -- hence a crawl that made one
        # request and stopped.  Accept it explicitly, and stop the retry middleware
        # burning three attempts on every one of them.
        meta = {}
        meta['page'] = self.page
        meta['handle_httpstatus_list'] = [500]
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        # div.videothumb is gone; each card is a div.item-update carrying its link,
        # title, still, runtime and release date.
        for card in response.xpath('//div[contains(@class, "item-update")]'):
            link = card.xpath('.//div[@class="content-div"]//a/@href').get() or card.xpath('.//a/@href').get()
            if not link:
                continue
            # the scene pages answer 500 intermittently too, while still serving
            # the full document, so carry the allowance through
            meta = dict(response.meta)
            meta['handle_httpstatus_list'] = [500]

            sceneid = card.xpath('.//img[contains(@id, "set-target")]/@id').get()
            sceneid = re.search(r'(\d+)', sceneid) if sceneid else None
            if sceneid:
                meta['id'] = sceneid.group(1)

            title = card.xpath('.//div[@class="content-div"]//h4/a/text()').get()
            if title:
                meta['title'] = self.cleanup_title(re.sub(r'\s+Video$', '', title.strip()))

            info = ' '.join(x.strip() for x in card.xpath('.//div[contains(@class, "more-info-div")]//text()').getall() if x.strip())
            scenedate = re.search(r'(\w{3,9} \d{1,2}, \d{4})', info)
            if scenedate:
                scenedate = self.parse_date(scenedate.group(1), date_formats=['%b %d, %Y', '%B %d, %Y'])
                if scenedate:
                    meta['date'] = scenedate.strftime('%Y-%m-%d')
            runtime = re.search(r'((?:\d{1,2}:)?\d{1,2}:\d{2})', info)
            if runtime:
                meta['duration'] = self.duration_to_seconds(runtime.group(1))

            image = card.xpath('.//img/@src0_1x').get() or card.xpath('.//img/@src').get()
            if image and image.strip():
                meta['image'] = self.format_link(response, image.strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)
