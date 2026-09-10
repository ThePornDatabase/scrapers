import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTransEroticaSpider(BaseSceneScraper):
    name = 'TransErotica'
    site = 'TransErotica'
    parent = 'TransErotica'
    network = 'TransErotica'

    start_urls = [
        'https://tour.transerotica.com',
    ]

    # The tour was rebuilt onto the shared Grooby template, so div.updateItem,
    # h1.title_bar, div.updateDetails and the meta keywords tag list are all gone.
    # Cards are div.sexyvideo_outer and the scene pages use the same
    # trailerpage_info / set_tags markup as networkGrooby.
    selector_map = {
        'title': '//div[@class="trailerpage_info"]/p[contains(@class, "trailertitle")]/text()|//div[@class="trailer_toptitle_left"]//text()',
        'description': '//div[@class="trailerpage_info"]/p[not(contains(@class, "trailertitle"))]/text()|//div[@class="trailer_videoinfo"]/p[not(./b)]/text()',
        'image': '//div[@class="trailerdata"]/div[contains(@class, "trailerposter")]/img/@src0_2x|//div[@class="videohere"]/img[contains(@src,".jpg")]/@src',
        'performers': '//div[@class="trailerpage_info"]//a[contains(@href, "/models/")]/text()|//div[@class="trailer_videoinfo"]//a[contains(@href, "/models/")]/text()',
        'tags': './/div[@class="set_tags"]/ul/li/a/text()',
        'trailer': '//div[@class="trailerdata"]/div[contains(@class, "trailermp4")]/text()',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "sexyvideo_outer")]'):
            meta = dict(response.meta)

            # the runtime and the release date only exist on the card
            scenedate = card.xpath('.//i[contains(@class, "fa-calendar")]/following-sibling::text()').get()
            if scenedate:
                scenedate = scenedate.lower().replace("added", "").strip()
                meta['date'] = self.parse_date(scenedate, date_formats=['%d %b %Y']).isoformat()

            runtime = card.xpath('.//div[@class="video_stats"]//text()').getall()
            runtime = re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})', ' '.join(runtime))
            if runtime:
                hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
                meta['duration'] = str(hours * 3600 + minutes * 60 + seconds)

            title = card.xpath('.//h4/a/text()').get()
            if title:
                meta['title'] = self.cleanup_title(title)

            scene = card.xpath('.//h4/a/@href|.//div[@class="videohere"]/a/@href').get()
            if scene and scene.startswith("//"):
                scene = "https:" + scene
            if scene and re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     meta=meta, headers=self.headers, cookies=self.cookies)

    def get_duration(self, response):
        return response.meta.get('duration')

    def get_trailer(self, response):
        """Scenes without a preview publish the literal string 'no_trailer'."""
        trailer = (super().get_trailer(response) or '').strip()
        if not trailer or 'no_trailer' in trailer:
            return ''
        return trailer

    def get_tags(self, response):
        tags = [string.capwords(x.strip()) for x in
                response.xpath(self.get_selector_map('tags')).getall() if x.strip()]
        if "Trans" not in tags:
            tags.append("Trans")
        return tags
