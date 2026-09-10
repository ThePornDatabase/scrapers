import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSheReactsSpider(BaseSceneScraper):
    name = 'SheReacts'
    network = 'TugPass'
    parent = 'She Reacts'
    site = 'She Reacts'

    start_urls = [
        'https://www.shereacts.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        # /videos/N.php redirects to the Tailwind rebuild at /videos?page=N
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        # div.update-box is gone: the listing is a Tailwind rebuild whose cards are
        # flex rows holding an h2 link to /video/<id>, the still, a "Published ..."
        # line and the cast.  Scoping on the h2 link avoids matching the sort bar,
        # which shares the same flex classes.
        for scene in response.xpath('//div[contains(@class, "flex flex-col")][.//h2/a[contains(@href, "/video/")]]'):
            link = scene.xpath('.//h2/a/@href').get()
            if not link:
                continue
            if '?nats' in link:
                link = re.search(r'(.*?)\?nats', link).group(1)

            item = SceneItem()
            item['url'] = self.format_link(response, link)
            sceneid = re.search(r'/video/(\d+)', item['url'])
            if not sceneid:
                continue
            item['id'] = sceneid.group(1)

            title = scene.xpath('.//h2/a/text()').get()
            if not title or not title.strip():
                continue
            item['title'] = self.cleanup_title(title)

            item['description'] = ''

            published = ' '.join(scene.xpath('.//p[contains(text(), "Published")]//text()').getall())
            scenedate = re.search(r'(\w{3,9} \d{1,2}, \d{4})', published)
            item['date'] = None
            if scenedate:
                scenedate = self.parse_date(scenedate.group(1), date_formats=['%b %d, %Y', '%B %d, %Y'])
                if scenedate:
                    item['date'] = scenedate.isoformat()

            item['duration'] = None
            image = scene.xpath('.//img/@src').get()
            item['image'] = self.format_link(response, image) if image else ''
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

            item['tags'] = ['Reaction Video']
            item['performers'] = [x.strip() for x in
                                  scene.xpath('.//a[contains(@href, "/models/")]/text()').getall()
                                  if x and x.strip()]
            item['trailer'] = None
            item['site'] = "She Reacts"
            item['parent'] = "She Reacts"
            item['network'] = "TugPass"

            yield self.check_item(item, self.days)
