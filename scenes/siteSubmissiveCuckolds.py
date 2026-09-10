import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSubmissiveCuckoldsSpider(BaseSceneScraper):
    name = 'SubmissiveCuckolds'
    network = 'Submissive Cuckolds'
    parent = 'Submissive Cuckolds'
    site = 'Submissive Cuckolds'

    start_urls = [
        'http://submissivecuckolds.com',
    ]

    # The tour was rebuilt: the old nested table cells with div.lastup are gone and
    # the page is now div.item-title / span.update-date / div.item-desc cards, with
    # ?page=N pagination in place of the sta= offset.  There are still no scene
    # pages, so the item is built entirely from the card as before.
    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'/(\d+)\.jpg',
        'trailer': '',
        'pagination': '/cuckold_last_updates_tour.php?page=%s'
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        # the outer cell wraps the whole grid and carries the "Latest updates:"
        # heading in an item-title of its own, so cards are matched on holding the
        # thumbnail as a direct child
        for card in response.xpath('//td[div[contains(@class, "gallery-image-container")]]'):
            image = card.xpath('./div[contains(@class, "gallery-image-container")]//img/@src').get()
            if not image:
                continue

            item = SceneItem()
            item['image'] = image.strip().replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            sceneid = re.search(self.get_selector_map('external_id'), item['image'])
            if not sceneid:
                continue
            item['id'] = sceneid.group(1)

            title = card.xpath('.//div[contains(@class, "item-title")]/strong/text()').get()
            item['title'] = self.cleanup_title(title) if title else ''
            if not item['title']:
                continue
            item['performers'] = [string.capwords(title.strip())]

            scenedate = card.xpath('.//span[contains(@class, "update-date")]/text()').get()
            item['date'] = None
            if scenedate:
                scenedate = re.search(r'(\d{1,2} \w+ \d{4})', scenedate)
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%d %B %Y']).isoformat()

            description = card.xpath('.//div[contains(@class, "item-desc")]/text()').get()
            item['description'] = (self.cleanup_description(description).replace("Pics: ", "").replace("Clips: ", "")
                                   if description else '')

            item['tags'] = ['Female Domination', 'Cuckold']
            item['trailer'] = ''
            item['url'] = response.url
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['type'] = 'Scene'

            item = self.check_item(item, self.days)
            if item:
                yield item
