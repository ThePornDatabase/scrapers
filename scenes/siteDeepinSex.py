import re
import scrapy
from scrapy.utils.project import get_project_settings
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDeepInSexSpider(BaseSceneScraper):
    name = 'DeepInSex'
    network = 'Deep In Sex'
    parent = 'Deep In Sex'
    site = 'Deep In Sex'

    start_url = 'https://www.deepinsex.com'

    # /3d-videos/ and /2d-videos/ both 404 now; the site consolidated onto a single
    # /new listing, paginated as /new/page/N.  The VR/2D split is no longer a URL
    # distinction, so the VR tag comes from the card's own passthrough/VR badge.
    paginations = [
        '/new',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': ''
    }

    async def start(self):
        settings = get_project_settings()

        meta = {}
        meta['page'] = self.page
        if 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        for link in self.paginations:
            page = int(self.page)
            url = self.start_url + link + ('' if page == 1 else '/page/%d' % page)
            yield scrapy.Request(url, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        # div.card.video became article.card-video; the card links straight to the
        # scene slug at the site root (no /video/ path) and carries the title in a
        # title attribute, plus a preview clip in data-preview.
        for scene in response.xpath('//article[contains(@class, "card-video")]'):
            link = scene.xpath('.//a[contains(@class, "d-block")]/@href').get()
            if not link:
                continue

            item = SceneItem()
            item['url'] = self.format_link(response, link)
            sceneid = re.search(r'/([^/]+?)/?$', item['url'])
            if not sceneid:
                continue
            item['id'] = sceneid.group(1)

            title = (scene.xpath('.//a[contains(@class, "d-block")]/@title').get()
                     or scene.xpath('.//h3//text()').get() or '')
            if not title.strip():
                continue
            item['title'] = self.cleanup_title(title)

            item['description'] = ''
            item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('.//picture//img/@src').get() or scene.xpath('.//img/@src').get()
            item['image'] = self.format_link(response, image) if image else ''
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

            trailer = scene.xpath('.//div[contains(@class, "thumb")]/@data-preview').get()
            item['trailer'] = self.format_link(response, trailer) if trailer else ''

            item['performers'] = [x.strip() for x in
                                  scene.xpath('.//a[contains(@href, "/pornstar")]//text()').getall()
                                  if x and x.strip()]

            # the VR badge replaces the old 3d-videos/2d-videos URL split
            item['tags'] = ['VR'] if scene.xpath('.//a[contains(@href, "vr-passthrough")]') else []

            item['site'] = "Deep In Sex"
            item['parent'] = "Deep In Sex"
            item['network'] = "Deep In Sex"

            yield item
