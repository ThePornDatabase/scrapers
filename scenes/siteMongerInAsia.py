import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMongerInAsiaSpider(BaseSceneScraper):
    name = 'MongerInAsia'
    network = 'Monger In Asia'
    parent = 'Monger In Asia'
    site = 'Monger In Asia'

    start_urls = [
        'https://mongerinasia.com',
    ]

    # The site left Next.js: there is no buildId in the page any more, so the
    # /_next/data/<buildID>/videos.json feed this scraper walked no longer exists.
    # It now runs the same Elevated X tour as HollyRandall and the others, whose
    # listing card carries the title, cast, date, runtime and still outright.
    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

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

            image = (scene.xpath('.//img/@src0_4x').get() or scene.xpath('.//img/@src0_3x').get()
                     or scene.xpath('.//video/@poster_4x').get() or scene.xpath('.//video/@poster_3x').get())
            if image:
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            trailer = scene.xpath('.//video/source/@src').get() or scene.xpath('.//video/@src').get()
            if trailer:
                item['trailer'] = self.format_link(response, trailer)

            item['site'] = 'Monger In Asia'
            item['parent'] = 'Monger In Asia'
            item['network'] = 'Monger In Asia'

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
