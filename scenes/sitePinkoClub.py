import base64
import json
import re

import requests
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePinkoClubSpider(BaseSceneScraper):
    name = 'PinkoClub'
    network = 'Pinko Club'
    parent = 'Pinko Club'
    site = 'Pinko Club'

    start_urls = [
        'https://www.pinkoclub.com',
    ]

    # The site was rebuilt in 2026: the old div.contorno01 grid is gone, replaced
    # by article.card tiles, and the "next" query parameter is ignored in favour
    # of "page".  Scene pages now carry a schema.org VideoObject that holds the
    # title, synopsis, upload date, duration, poster and trailer, so everything
    # but the cast is read out of that.
    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="performer"]/div/strong/text()',
        'tags': '',
        'external_id': r'.*/(\d+.*?)\.php',
        'trailer': '',
        'pagination': '/new-video.php?sort=recenti&page=%s',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article[contains(@class, "card")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_video_object(self, response):
        if 'videoobject' not in response.meta:
            payload = {}
            for blob in response.xpath('//script[@type="application/ld+json"]/text()').getall():
                try:
                    data = json.loads(blob)
                except ValueError:
                    continue
                if isinstance(data, dict) and data.get('@type') == 'VideoObject':
                    payload = data
                    break
            response.meta['videoobject'] = payload
        return response.meta['videoobject']

    def get_description(self, response):
        description = self.get_video_object(response).get('description')
        if description:
            return self.cleanup_description(description.replace("\n", "").replace("\r", "").strip())
        return ''

    def get_date(self, response):
        uploaded = self.get_video_object(response).get('uploadDate')
        if uploaded:
            return self.parse_date(uploaded.split("T")[0], date_formats=['%Y-%m-%d']).isoformat()
        return None

    def get_duration(self, response):
        duration = self.get_video_object(response).get('duration')
        if duration:
            match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            if match and any(match.groups()):
                hours, minutes, seconds = (int(part or 0) for part in match.groups())
                return str(hours * 3600 + minutes * 60 + seconds)
        return None

    def get_trailer(self, response):
        return self.get_video_object(response).get('contentUrl') or ''

    def get_image(self, response):
        image = super().get_image(response)
        if image:
            return image
        return self.get_video_object(response).get('thumbnailUrl') or ''

    def get_tags(self, response):
        return []

    def get_image_blob(self, response):
        # img.pinkocdn.com answers 403 without a site referer.
        image = self.get_image(response)
        if image:
            req = requests.get(image, headers={'Referer': 'https://www.pinkoclub.com/'}, timeout=30)
            if req and req.ok:
                return base64.b64encode(req.content).decode('utf-8')
        return None
