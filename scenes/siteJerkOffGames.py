import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJerkOffGamesSpider(BaseSceneScraper):
    name = 'TheJerkOffGames'

    start_urls = [
        'https://www.thejerkoffmembers.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    # The Elevated X tour was restyled: div.updateItem / div.item-thumb became
    # div.latestUpdateB, the cast moved into p.link_light, and the release date and
    # runtime are now list items in ul.videoInfo.  The scene pages carry no
    # description or tags any more, and the card already holds the title, cast,
    # date, runtime, still and set id -- so the item is built straight from the
    # listing instead of spending a request per scene on a page with less on it.

    def get_scenes(self, response):
        for scene in response.xpath('//div[contains(@class, "latestUpdateB") and not(contains(@class, "info"))]'):
            item = self.init_scene()

            item['id'] = scene.xpath('./@data-setid').get()
            if not item['id']:
                sceneid = scene.xpath('.//img[contains(@id, "target")]/@id').get()
                sceneid = re.search(r'(\d+)', sceneid) if sceneid else None
                item['id'] = sceneid.group(1) if sceneid else None

            title = scene.xpath('.//h4/a/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)

            # XBrats nests the link inside div.hover_update_info, so match a descendant
            link = scene.xpath('.//div[@class="videoPic"]//a/@href').get()
            if link:
                item['url'] = self.format_link(response, link)

            performers = scene.xpath('.//p[contains(@class, "link_light")]/a/text()').getall()
            item['performers'] = [x.strip() for x in performers if x and x.strip()]

            for entry in [x.strip() for x in scene.xpath('.//ul[contains(@class, "videoInfo")]/li//text()').getall() if x.strip()]:
                scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', entry)
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y'])
                    if scenedate:
                        item['date'] = scenedate.strftime('%Y-%m-%d')
                runtime = re.search(r'(\d+)\s*min', entry)
                if runtime:
                    item['duration'] = str(int(runtime.group(1)) * 60)

            # Some of these tours render the card as a <video> with poster_Nx
            # attributes rather than an <img> with src0_Nx.
            image = (scene.xpath('.//img/@src0_4x').get() or scene.xpath('.//img/@src0_3x').get()
                     or scene.xpath('.//video/@poster_4x').get() or scene.xpath('.//video/@poster_3x').get())
            if image:
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            trailer = scene.xpath('.//video/source/@src').get() or scene.xpath('.//video/@src').get()
            if trailer:
                item['trailer'] = self.format_link(response, trailer)

            item['site'] = 'TheJerkOffGames'
            item['parent'] = 'TheJerkOffGames'
            item['network'] = 'TheJerkOffGames'

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
