import json

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBigLatinAnalSpider(BaseSceneScraper):
    name = 'BigLatinAnal'
    network = 'Big Latin Anal'
    parent = 'Big Latin Anal'
    site = 'Big Latin Anal'

    # home/home.html renders nothing server-side -- section.modelo never appears
    # in the served HTML, which is why the old selectors matched nothing and the
    # page looked like a bare "coming soon" countdown. assets/js/pages/home.js
    # fetches the catalogue from the site's own JSON API and draws it in, so the
    # API is read directly.
    #
    # The front end appends a clientUuid for its like/view tracking; it is not
    # required to read the listing, so none is sent. limit is capped high enough
    # to take the whole catalogue in one request (43 videos at the time of
    # writing), and pagination is still honoured if it ever outgrows that.
    start_urls = [
        'https://www.biglatinanal.com',
    ]

    api_url = 'https://www.biglatinanal.com/api/videos?page=%s&limit=%d'
    # Every image lives in the site's R2 bucket; see assets/js/utils/cdn.js.
    image_base = 'https://cdn.biglatinanal.com/biglatinanal/gallery/'
    tour_url = 'https://www.biglatinanal.com/home/home.html'
    per_page = 50

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        yield scrapy.Request(self.api_url % (self.page, self.per_page),
                             callback=self.parse, meta={'page': self.page},
                             headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        try:
            payload = json.loads(response.text)
        except ValueError:
            print("*** BigLatinAnal: /api/videos did not return JSON")
            return

        count = 0
        for video in payload.get('data') or []:
            item = self.build_item(video)
            if item:
                count += 1
                yield self.check_item(item, self.days)

        pagination = payload.get('pagination') or {}
        meta = self.copy_meta(response)
        if count and pagination.get('hasNext') and meta['page'] < self.limit_pages:
            meta = dict(meta)
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(self.api_url % (meta['page'], self.per_page),
                                 callback=self.parse, meta=meta,
                                 headers=self.headers, dont_filter=True)

    def build_item(self, video):
        title = (video.get('title') or '').strip()
        if not title or not video.get('id'):
            return None

        item = self.init_scene()
        item['title'] = self.cleanup_title(title)
        item['id'] = str(video['id'])
        # The catalogue is one page with no per-scene route, so every scene
        # points at the tour.
        item['url'] = self.tour_url
        item['date'] = self.get_date(video)
        item['duration'] = self.get_duration(video)

        gallery = ((video.get('media') or {}).get('gallery')) or []
        item['image'] = (self.image_base + gallery[0]) if gallery else ''
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else ''

        item['performers'] = [model.strip() for model in video.get('models') or [] if model and model.strip()]
        # The API carries no synopsis or tags.
        item['description'] = ''
        item['tags'] = []
        item['trailer'] = ''
        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        item['type'] = 'Scene'
        return item

    def get_date(self, video):
        # Dates read dd/mm/yyyy: across the catalogue the first field reaches 29
        # while the second never passes 12, so it is day-first, not month-first.
        scenedate = video.get('date')
        if scenedate:
            parsed = self.parse_date(scenedate.strip(), date_formats=['%d/%m/%Y'])
            if parsed:
                return parsed.isoformat()
        return ''

    @staticmethod
    def get_duration(video):
        # "14:07.00" is mm:ss with a fractional-seconds tail.
        runtime = (video.get('time') or '').split('.')[0]
        parts = [p for p in runtime.split(':') if p.isdigit()]
        if len(parts) == 2:
            return str(int(parts[0]) * 60 + int(parts[1]))
        if len(parts) == 3:
            return str(int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]))
        return None
