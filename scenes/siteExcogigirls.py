import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteExcogigirlsSpider(BaseSceneScraper):
    name = 'Excogigirls'
    network = 'Excogigirls'
    parent = 'Excogigirls'
    site = 'Excogigirls'

    start_urls = [
        'https://excogigirls.com',
    ]

    selector_map = {
        'title': '//section[@id="scene-info"]//h1/text()',
        'date': '//i[@class="fa fa-calendar"]/following-sibling::text()[contains(., ",")]',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="player-thumb"]//img/@src0_1x',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//strong[contains(text(), "Runtime")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-video")]//h4/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            if "1st" not in tag.lower():
                tags2.append(tag)
        return tags2

    def get_description(self, response):
        desc_node = response.xpath('//p[contains(@class, "descriptionFull")]')[0]
        description_parts = []

        for node in desc_node.root:
            # Stop if we hit a <strong> tag
            if getattr(node, 'tag', None) == 'strong':
                break

            # Skip spans
            if getattr(node, 'tag', None) == 'span':
                continue

            # If it's a text node
            if isinstance(node, str):
                text = node.strip()
                if text:
                    description_parts.append(text)

            # If it's an element (e.g., <br>, <em>, etc.)
            elif hasattr(node, 'text') and node.text:
                description_parts.append(node.text.strip())

            # Also include tail text (text after inline tags)
            if hasattr(node, 'tail') and node.tail:
                tail_text = node.tail.strip()
                if tail_text:
                    description_parts.append(tail_text)

        description = ' '.join(description_parts).strip()
        return description

    def get_performers(self, response):
        perf_list = []
        performers = response.xpath('//div[@class="card__model-bio"]')
        for performer in performers:
            perf_name = performer.xpath('./h3/text()').get()
            perf_name = perf_name.lower()
            perf_url = performer.xpath('.//a/@href').get()
            perf_url_name = re.search(r'.*/(.*?)\.htm', perf_url)
            if perf_url_name:
                perf_url_name = perf_url_name.group(1)
                perf_url_name = perf_url_name.lower()
                perf_url_name = re.sub(r'[^a-z]+', ' ', perf_url_name)
                perf_url_name = perf_url_name.strip()

                if perf_name in perf_url_name:
                    if len(perf_url_name) > len(perf_name):
                        perf_name = string.capwords(perf_url_name)
                        perf_list.append(perf_name)
        return perf_list

    def get_performers_data(self, response):
        performers_data = []
        performers = response.xpath('//div[@class="card__model-bio"]')
        if len(performers):
            for performer in performers:
                perf = {}
                perf_name = performer.xpath('./h3/text()').get()
                perf_name = perf_name.lower()
                perf_url = performer.xpath('.//a/@href').get()
                perf_url_name = re.search(r'.*/(.*?)\.htm', perf_url)
                if perf_url_name:
                    perf_url_name = perf_url_name.group(1)
                    perf_url_name = perf_url_name.lower()
                    perf_url_name = re.sub(r'[^a-z]+', ' ', perf_url_name)
                    perf_url_name = perf_url_name.strip()

                    if perf_name in perf_url_name:
                        if len(perf_url_name) > len(perf_name):
                            perf_name = perf_url_name

                perf['name'] = string.capwords(perf_name)

                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Excogigirls"
                perf['site'] = "Excogigirls"

                image = performer.xpath('./preceding-sibling::img[1]/@src0_3x')
                if image:
                    image = image.get()
                    image = self.format_link(response, image)
                    if "content" in image:
                        perf['image'] = image
                        perf['image_blob'] = self.get_image_blob_from_link(image)

                height = performer.xpath('.//strong[contains(text(), "Height:")]/following-sibling::text()')
                if height:
                    height = height.get()
                    height = re.sub(r'[^0-9\'\"]', '', height)
                    if re.search(r'(\d+)\'', height):
                        perf['extra']['height'] = self.convert_height(height)

                measurements = performer.xpath('.//strong[contains(text(), "Measurements:")]/following-sibling::text()')
                if measurements:
                    measurements = measurements.get()
                    measurements = re.sub(r'[^0-9a-z]+', '', measurements.lower())
                    measurements = measurements.replace("x", "-")
                    perf['extra']['measurements'] = self.convert_measurements(measurements)

                performers_data.append(perf)
        return performers_data

    def convert_measurements(self, measurements):
        measurements = re.search(r'(\d+\w+).*?(\d+).*?(\d+)', measurements)
        if measurements:
            measurements = f"{measurements.group(1)}-{measurements.group(2)}-{measurements.group(3)}"
            return measurements.upper()
        return None

    def convert_height(self, height):
        feet, inches = map(int, height.replace(" ", "").strip().replace('"', '').split("'"))
        cm = (feet * 30.48) + (inches * 2.54)
        if cm:
            return str(int(cm)) + "cm"
        return None

    def get_image(self, response):
        image = super().get_image(response)
        if "-1x" in image:
            image = image.replace("-1x", "-3x")
        return image
