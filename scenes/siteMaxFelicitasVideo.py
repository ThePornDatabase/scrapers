import re
import datetime
from dateutil.relativedelta import relativedelta
from deep_translator import GoogleTranslator
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMaxFelicitasSpider(BaseSceneScraper):
    name = 'MaxFelicitas'
    network = 'Max Felicitas'
    parent = 'Max Felicitas'
    site = 'Max Felicitas'

    start_urls = [
        'https://maxfelicitasvideo.com',
    ]

    selector_map = {
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)$',
        'pagination': '/video?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-item")]')
        for scene in scenes:

            image = scene.xpath('./div/a/img/@src')
            if image:
                image = image.get()
                meta['image'] = self.format_link(response, image)
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            duration = scene.xpath('.//div[contains(@class, "durata")]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get().strip())

            title = scene.xpath('.//h4/text()')
            if title:
                title = GoogleTranslator(source='it', target='en').translate(title.get().lower())
                meta['title'] = self.cleanup_title(title)

            datetext = scene.xpath('.//div[contains(@class, "video-info")]/text()')
            if datetext:
                datetext = GoogleTranslator(source='it', target='en').translate(datetext.get().lower())
                meta['date'] = self.parse_date(datetext)

            scene = scene.xpath('./div/a/@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        meta = response.meta
        performers = ['Max Felicitas']
        # ~ performer = re.search(r' And (\w+ \w+)', meta['title'])
        # ~ if performer:
            # ~ performers.append(performer.group(1))

        return performers

    def get_tags(self, response):
        return ['European']

    def parse_date(self, datestring):
        today = datetime.datetime.now()
        datestring = datestring.lower()
        intervalcount = re.search(r'(\d+)', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
        if "minute" in datestring:
            date = today - relativedelta(minutes=intervalcount)
        if "hour" in datestring:
            date = today - relativedelta(hours=intervalcount)
        if "day" in datestring:
            date = today - relativedelta(days=intervalcount)
        if "today" in datestring:
            date = today
        if "yesterday" in datestring:
            date = today - relativedelta(days=1)
        if "week" in datestring:
            date = today - relativedelta(weeks=intervalcount)
        if "month" in datestring:
            date = today - relativedelta(months=intervalcount)
        if "year" in datestring:
            date = today - relativedelta(years=intervalcount)

        return date.isoformat()
