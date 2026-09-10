import re
import json
import scrapy
from scrapy import Selector
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkJavHDSpider(BaseSceneScraper):
    name = 'JavHD'
    network = 'JavHD'
    parent = 'JavHD'
    site = 'JavHD'

    start_urls = [
        'https://javhd.com',
    ]

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    cookies = {
        'locale': 'en',
    }

    # The scene pages were rebuilt on a new theme: content__title / content__desc /
    # div.content-desc are all gone, which left title and description as None and
    # crashed the pipeline's re.sub on them.  The replacement markup carries the
    # title and categories, and a JSON-LD WebPage block supplies the description,
    # release date and duration -- none of which the old scraper could read.
    selector_map = {
        'title': '//div[@class="video-info__title"]/h1/text()',
        'description': '',
        'date': '',
        'image': '',
        'performers': '//strong[contains(@class, "content-info__title")][contains(text(), "Model")]/following-sibling::a/text()',
        'tags': '//section[contains(@class, "adaptive-page-video__categories")]//a/span/text()',
        'external_id': r'id/(\d+)/',
        'trailer': '',
        'pagination': '/en/japanese-porn-videos/justadded/all/%s?content=all'
    }

    async def start(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        jsondata = response.json()
        # ~ print(jsondata)
        data = jsondata['template']
        data = data.replace("\n", "").replace("\t", "").replace("\r", "").replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        sel = Selector(text=data)
        scenes = sel.xpath('//thumb-component')

        for scene in scenes:
            meta['image'] = scene.xpath('./@url-thumb').get()
            meta['trailer'] = scene.xpath('./@video-preview').get()
            scene = scene.xpath('./@link-content').get()
            meta['id'] = None
            sceneid = re.search(r'id/(\d+)/', scene)
            if sceneid:
                meta['id'] = sceneid.group(1)

            if not meta['id']:
                sceneid = re.search(r'video/(\d+)$', scene)
                if sceneid:
                    meta['id'] = sceneid.group(1)

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies, meta=meta)

    def get_ld_video(self, response):
        """Return the JSON-LD 'video' object.

        The block has a stray trailing brace, so json.loads() rejects the whole
        string; raw_decode reads the valid object and ignores the trailing junk.
        """
        block = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if not block:
            return {}
        try:
            data, _ = json.JSONDecoder().raw_decode(block.strip(), 0)
        except ValueError:
            return {}
        video = data.get('video')
        return video if isinstance(video, dict) else {}

    def get_image(self, response):
        """The listing supplies the thumbnail; JSON-LD carries a larger one.

        The old implementation made a blocking requests.post to /en/player/<id>
        from inside the callback to fetch a smaller (940x530) poster.
        """
        image = response.meta.get('image') or self.get_ld_video(response).get('thumbnailUrl') or ''
        return image.strip()

    def get_trailer(self, response):
        """Use the preview clip the listing carries.

        /en/player/<id> now answers with a placeholder ("black_cap.mp4") join
        prompt rather than a real trailer, so it is no longer worth the blocking
        request the old implementation made.
        """
        trailer = response.meta.get('trailer') or ''
        trailer = trailer.strip()
        return trailer if 'mp4' in trailer else ''

    def get_date(self, response):
        upload = self.get_ld_video(response).get('uploadDate') or self.get_ld_video(response).get('datePublished')
        if upload:
            upload = re.search(r'(\d{4}-\d{2}-\d{2})', upload)
            if upload:
                return upload.group(1)
        return None

    def get_duration(self, response):
        """JSON-LD publishes the runtime as e.g. 'T7M18S' (no leading P)."""
        iso = self.get_ld_video(response).get('duration')
        if iso:
            parts = re.match(r'P?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', iso.strip())
            if parts and any(parts.groups()):
                hours, minutes, seconds = (int(x or 0) for x in parts.groups())
                return str(hours * 3600 + minutes * 60 + seconds)
        return ''

    def get_performers(self, response):
        performers = response.xpath(self.get_selector_map('performers')).getall()
        # Scenes with no credited model list a single "N/A" entry
        return [x.strip() for x in performers if x and x.strip() and x.strip().upper() != 'N/A']

    def get_description(self, response):
        description = self.get_ld_video(response).get('description') or ''
        if not description:
            return ''
        return self.cleanup_description(description.replace("\r\n", " "))
