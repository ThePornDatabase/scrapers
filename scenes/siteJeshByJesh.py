import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJeshByJeshSpider(BaseSceneScraper):
    name = 'JeshByJesh'
    network = 'Jesh By Jesh'
    parent = 'Jesh By Jesh'
    site = 'Jesh By Jesh'

    start_urls = [
        'https://www.jeshbyjesh.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': r'',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            meta = {}
            image = scene.xpath('./img/@src')
            if image:
                meta['image'] = self.format_link(response, image.get()).replace("1x", "2x")
            else:
                meta['image'] = ''
            meta['date'] = self.search_date(scene, response)
            trailer = scene.xpath('.//source/@src')
            if trailer:
                meta['trailer'] = self.format_link(response, trailer.get())
            else:
                meta['trailer'] = ''
            meta['id'] = scene.xpath('./@class').get()
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and "jeshbyjesh" in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def search_date(self, scene, response):
        date = scene.xpath('.//source/@src')
        if date:
            date = date.get()
            if re.search(r'/(20[12][0-9][01]\d{3})', date):
                return self.parse_date(re.search(r'/(20[12][0-9][01]\d{3})', date).group(1), date_formats=['%Y%m%d']).isoformat()
        return self.parse_date('today').isoformat()

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("SCENE DESCRIPTION:", "").strip().lower()
        description = '. '.join(map(lambda s: s.strip().capitalize(), description.split('. ')))
        return description

    def get_title(self, response):
        title = super().get_title(response)
        title = title.replace("- Jeshbyjesh", "")
        title = title.replace("Jeshbyjesh", "")
        title = title.replace("•", "-")
        return title.strip()

    def get_performers(self, response):
        title = super().get_title(response)
        tags = super().get_tags(response)
        for tag in tags:
            if tag in title:
                return [tag]

        if re.search(r'^(Season)', title.strip()):
            performer = re.search(r'season.*?• ?(\w+ \w+)', title.lower())
            if performer:
                return [string.capwords(performer.group(1).strip())]
        performer = re.search(r'^(\w+ \w+)', title.lower())
        if performer:
            performer = string.capwords(performer.group(1).strip())
            if "Jesh" not in performer:
                return [performer]
        return []

    def get_tags(self, response):
        title = super().get_title(response)
        tags = super().get_tags(response)
        if 'Updates' in tags:
            tags.remove('Updates')
        if 'Photos' in tags:
            tags.remove('Photos')
        if 'Movies' in tags:
            tags.remove('Movies')
        tags2 = tags.copy()
        for tag in tags2:
            if tag in title:
                tags.remove(tag)
            if " Id " in tag:
                tags.remove(tag)
            if "id:" in tag.lower():
                tags.remove(tag)
        return tags
