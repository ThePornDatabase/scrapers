import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteStaxusSpider(BaseSceneScraper):
    name = 'Staxus'
    network = 'Staxus'
    parent = 'Staxus'
    site = 'Staxus'

    start_urls = [
        'https://staxus.com',
    ]

    # The tour was rebuilt.  li.item is gone, and the scene page is now a 5.6MB
    # document whose itemprop markup mixes the scene's own cast with every related
    # scene's, so it is no longer a reliable source.  The listing card, by contrast,
    # carries the title, cast, release date, set id, still and hover trailer, all
    # correctly scoped -- so the item is built from the listing instead.
    selector_map = {
        'external_id': r'id=(\d+)',
        'pagination': '/trial/category.php?id=50&page=%s&s=d&',
        'type': 'Scene'
    }

    def get_scenes(self, response):
        for scene in response.xpath('//div[@class="update_details"]'):
            item = self.init_scene()

            item['id'] = scene.xpath('./@data-setid').get()
            link = scene.xpath('.//a[contains(@class, "title_bar_movie")]/@href').get()
            if not link or not item['id']:
                continue
            item['url'] = self.format_link(response, link)

            title = scene.xpath('.//a[contains(@class, "title_bar_movie")]//span[@itemprop="name"]/text()').get()
            if not title:
                continue
            item['title'] = self.cleanup_title(title)

            item['performers'] = [x.strip().strip(',') for x in
                                  scene.xpath('.//span[@class="update_models"]//span[@itemprop="name"]/text()').getall()
                                  if x and x.strip().strip(',')]

            for text in scene.xpath('.//div[contains(@class, "details")]/span/text()').getall():
                scenedate = re.search(r'(\d{1,2} \w{3} \d{4})', text)
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%d %b %Y'])
                    if scenedate:
                        item['date'] = scenedate.strftime('%Y-%m-%d')
                    break

            # the still is a CSS background on the thumbnail anchor
            style = scene.xpath('.//a[contains(@style, "background-image")]/@style').get() or ''
            image = re.search(r'background-image:\s*url\(([^)]+)\)', style)
            if image:
                item['image'] = self.format_link(response, image.group(1).strip('\'"'))
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            trailer = scene.xpath('.//a[@data-video]/@data-video').get()
            if trailer:
                item['trailer'] = trailer.strip()

            item['site'] = 'Staxus'
            item['parent'] = 'Staxus'
            item['network'] = 'Staxus'

            yield self.check_item(item, self.days)
