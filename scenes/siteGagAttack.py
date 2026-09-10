import re
import html
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGagAttackSpider(BaseSceneScraper):
    name = 'GagAttack'
    network = 'GagAttack'
    parent = 'GagAttack'
    site = 'GagAttack'

    cookies = [{"name": "cwarn", "value": "true"}, {"name": "warn", "value": "true"}]

    start_urls = [
        'https://gagattack.org',
    ]

    # The site moved off its Elevated X tour: the listing is /updates (the old
    # /categories/movies_N_d.html is gone) and scenes live at /updates/<slug>.  The
    # scene page carries the title, synopsis, still, cast and tags, but no date --
    # that only exists on the listing card, along with the runtime.
    selector_map = {
        'title': '//h1//text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//a[contains(@href, "/models/")]/text()',
        'tags': '//a[contains(@href, "/tags/")]/text()',
        'trailer': '',
        'external_id': r'/updates/(.+?)/?$',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "videoBlock")]'):
            link = card.xpath('.//h3/a/@href').get() or card.xpath('.//div[@class="videoPic"]/a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue
            meta = {}
            for entry in [x.strip() for x in card.xpath('.//ul[contains(@class, "contentInfo")]/li//text()').getall() if x.strip()]:
                scenedate = re.search(r'(\w{3} \d{1,2}, \d{4})', entry)
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%b %d, %Y'])
                    if scenedate:
                        meta['date'] = scenedate.strftime('%Y-%m-%d')
                runtime = re.search(r'^(\d{1,2}:\d{2}(?::\d{2})?)$', entry)
                if runtime:
                    meta['duration'] = self.duration_to_seconds(runtime.group(1))
            performers = [x.strip() for x in card.xpath('.//div[@class="modelName"]/a/text()').getall() if x and x.strip()]
            if performers:
                meta['performers'] = performers
            image = card.xpath('.//div[@class="videoPic"]//img/@src').get()
            if image and image.strip():
                meta['image'] = self.format_link(response, image.strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        """og:description ships as escaped HTML paragraphs."""
        import html as _html
        text = response.xpath(self.get_selector_map('description')).get() or ''
        text = re.sub(r'<[^>]+>', ' ', _html.unescape(text))
        return self.cleanup_description(re.sub(r'\s+', ' ', text))
