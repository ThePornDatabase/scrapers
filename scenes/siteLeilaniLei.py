import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLeilaniLeiSpider(BaseSceneScraper):
    name = 'LeilaniLei'
    network = 'Leilani Lei'
    parent = 'Leilani Lei'
    site = 'Leilani Lei'

    start_urls = [
        'https://leilanilei.elxcomplete.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    # The Elevated X tour was restyled: div.updateItem became div.latestUpdateB, the
    # cast moved from span.tour_update_models into p.link_light, and the date and
    # runtime are now list items in ul.videoInfo rather than a span.  The set id is
    # on the card itself as data-setid, so it no longer has to be dug out of an
    # image id attribute.
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

            item['url'] = self.format_link(response, scene.xpath('.//div[@class="videoPic"]/a/@href').get() or '')

            performers = scene.xpath('.//p[contains(@class, "link_light")]/a/text()').getall()
            item['performers'] = [x.strip() for x in performers if x and x.strip()]

            info = [x.strip() for x in scene.xpath('.//ul[contains(@class, "videoInfo")]/li//text()').getall() if x.strip()]
            for entry in info:
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

            item['site'] = 'Leilani Lei'
            item['parent'] = 'Leilani Lei'
            item['network'] = 'Leilani Lei'

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
