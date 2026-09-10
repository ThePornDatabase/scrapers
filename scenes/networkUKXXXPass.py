import re
from urllib.parse import urlparse
from datetime import date, timedelta
import string
import tldextract
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'ukpornparty': "UK Porn Party",
        'splatbukkake': "Splat Bukkake",
        'sexyukpornstars': "Sexy UK Pornstars",
        'realasianexposed': "Real Asian Exposed",
    }
    return match.get(argument, argument)


class NetworkUKXXXPassSpider(BaseSceneScraper):
    name = 'UKXXXPass'
    network = 'UK XXX Pass'

    start_urls = [
        'https://ukpornparty.xxx',
        'https://sexyukpornstars.xxx',
        'https://splatbukkake.xxx',
    ]

    # The Elevated X tour is gone: /models/models_N_d.html and div.model no longer
    # exist, and the scene page is now a Livewire app with no og: tags, no JSON-LD
    # and no addressable title.  The listing card carries the title, cast, release
    # date and still, so the item is built there instead.
    selector_map = {
        'external_id': r'/movie/(\d+)/',
        'pagination': '/movies?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "movieItem")]'):
            link = card.xpath('.//div[contains(@class, "title")]//a/@href').get()
            if not link:
                continue
            sceneid = re.search(self.get_selector_map('external_id'), link)
            if not sceneid:
                continue

            item = SceneItem()
            item['id'] = sceneid.group(1)
            item['url'] = self.format_link(response, link)

            title = card.xpath('.//div[contains(@class, "title")]//a/text()').get()
            if not title or not title.strip():
                continue
            item['title'] = self.cleanup_title(title)
            item['description'] = ''

            # the card's date reads DD.MM.YYYY
            item['date'] = None
            for text in card.xpath('.//div[contains(@class, "text-xs")]//text()').getall():
                scenedate = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%d.%m.%Y'])
                    if scenedate:
                        item['date'] = scenedate.isoformat()
                    break

            item['performers'] = [x.strip() for x in
                                  card.xpath('.//div[contains(@class, "actors")]//a/text()').getall()
                                  if x and x.strip()]
            item['tags'] = []
            item['trailer'] = ''

            image = card.xpath('.//img/@src').get()
            item['image'] = self.format_link(response, image) if image else ''
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

            site = match_site(tldextract.extract(response.url).domain)
            item['site'] = site
            item['parent'] = site
            item['network'] = 'UK XXX Pass'

            yield self.check_item(item, self.days)
