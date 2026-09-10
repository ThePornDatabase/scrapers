import re

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteGangbangMediaGermanySpider(BaseSceneScraper):
    name = 'GangbangMediaGermany'
    network = 'GangbangMediaGermany'
    parent = 'GangbangMediaGermany'
    site = 'GangbangMediaGermany'

    start_urls = [
        'https://p-p-p.tv',
    ]

    # /en/video/list is a 404 now; the listing is /en/videos/list?page=N and the
    # cards are div.card-video-thumb rather than div[id*=video].  The scene pages
    # are still nothing but a join wall, so as before the item is built entirely
    # from the card.
    selector_map = {
        'title': './/div[contains(@class, "card-footer")]//strong/text()',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'/video/([^/?]+)',
        'pagination': '/en/videos/list?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for link in response.xpath('//a[contains(@href, "/video/")][.//div[contains(@class, "card-video-thumb")]]'):
            href = link.attrib.get('href') or ''
            if not re.search(self.get_selector_map('external_id'), href):
                continue

            item = SceneItem()
            item['title'] = self.cleanup_title(super().get_title(link) or '')
            if not item['title']:
                continue

            item['url'] = self.format_link(response, href)
            # the card anchor carries the site's own numeric id
            item['id'] = (link.attrib.get('data-thumb-videoid-value')
                          or re.search(self.get_selector_map('external_id'), href).group(1))
            item['description'] = ''

            image = link.xpath('.//img/@src').get()
            if image:
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = None

            # the footer pills are runtime, then the release as an English relative
            # phrase ("15 hours ago"), then the view count
            pills = [re.sub(r'\s+', ' ', x).strip()
                     for x in link.xpath('.//div[contains(@class, "card-footer")]//span//text()').getall()
                     if x.strip()]

            runtime = next((re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})$', p) for p in pills
                            if re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})$', p)), None)
            if runtime:
                hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
                item['duration'] = str(hours * 3600 + minutes * 60 + seconds)

            scenedate = next((p for p in pills if 'ago' in p or p.lower() in ('today', 'yesterday')), None)
            if scenedate:
                item['date'] = self.parse_date(scenedate).strftime('%Y-%m-%d')

            item['trailer'] = ''
            item['tags'] = ['European', 'Gangbang']
            item['performers'] = []
            item['network'] = self.network
            item['parent'] = self.parent
            item['site'] = self.site
            item['type'] = 'Scene'

            item = self.check_item(item, self.days)
            if item:
                yield item
