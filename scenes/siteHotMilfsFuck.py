import re
import scrapy
import string
from cleantext import clean
from tpdb.BaseSceneScraper import BaseSceneScraper


class HotMilfsFuckSpider(BaseSceneScraper):
    name = 'HotMilfsFuck'
    network = "HotMilfsFuck"
    parent = "HotMilfsFuck"
    site = "Hot Milfs Fuck"

    start_urls = [
        'https://www.hotmilfsfuck.com',
    ]

    selector_map = {
        'title': '//section[contains(@id, "scene-info")]//h1/text()',
        'description': '//section[contains(@id, "scene-info")]//p[contains(@class, "descriptionFull")]/text()',
        'date': '//section[contains(@id, "scene-info")]//strong[contains(text(), "Released")]/following-sibling::text()',
        'image': '//script[contains(text(),"video_content")]',
        'performers': '//section[contains(@id, "model-bio")]//h3/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//section[contains(@id, "scene-info")]//strong[contains(text(), "Runtime")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '//script[contains(text(),"video_content")]',
        'external_id': '.*\\/(.*?)\\.html',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):

        scenes = response.xpath(
            '//div[@class="item item-update item-video"]/div[@class="content-div"]/h4/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image_re = re.search('poster=\"(.*.jpg)\"', image).group(1)
            if image_re:
                image = "https://www.hotmilfsfuck.com/" + image_re.strip()
        if not image:
            image = response.xpath('//div[@class="player-window-play"]/following-sibling::img/@src0_1x').get()

        if image:
            if "-1x" in image:
                image = image.replace("-1x", "-3x")
            return self.format_link(response, image.strip())
        return ''

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(
                response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = "https://www.hotmilfsfuck.com/" + \
                    re.search('src=\"(.*.mp4)\"', trailer).group(1).strip()
                return trailer.replace(" ", "%20")
        return ''

    def get_description(self, response):
        description = super().get_description(response)
        description = clean(description, no_emoji=True)
        return description

    def get_performers_data(self, response):
        tags = response.xpath('//ul[@class="tags"]/li/a/text()')
        if tags:
            tags = tags.getall()
        else:
            tags = []

        performers_data = []
        perf_list = response.xpath('//section[contains(@id, "model-bio")]//div[@class="card"]')
        if perf_list:
            for performer in perf_list:
                perf = {}
                perf['name'] = string.capwords(performer.xpath('.//h3/text()').get())
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"

                image = performer.xpath('.//img/@src0_2x')
                if image:
                    image = self.format_link(response, image.get())
                    perf['image'] = image
                    perf['image_blob'] = self.get_image_blob_from_link(image)

                height = performer.xpath('.//strong[contains(text(), "Height")]/following-sibling::text()')
                if height:
                    height = height.get()
                    perf['extra']['height'] = self.conv_height(height)

                measurements = performer.xpath('.//strong[contains(text(), "Measurements")]/following-sibling::text()')
                if measurements:
                    measurements = measurements.get()
                    measurements = re.sub(r'[^A-Z0-9-]+', '', measurements.lower().replace("x", "-").upper())
                    measurements = re.search(r'(\d+\w+?-\d+-\d+)', measurements)
                    if measurements:
                        perf['extra']['measurements'] = measurements.group(1)

                if tags:
                    for tag in tags:
                        if "Ethnicity - " in tag:
                            tag = re.search(r'.*? - (.*)', tag).group(1)
                            perf['extra']['ethnicity'] = string.capwords(tag)
                        if "boobs" in tag.lower() and "natural" in tag.lower():
                            perf['fakeboobs'] = False
                perf['network'] = "HotMilfsFuck"
                perf['site'] = "HotMilfsFuck"
                performers_data.append(perf)
        if tags:
            for tag in tags:
                if "Male - " in tag:
                    tag = re.search(r'.*? - (.*)', tag).group(1)
                    perf = {}
                    perf['name'] = string.capwords(tag)
                    perf['extra'] = {}
                    perf['extra']['gender'] = "Male"
                    perf['network'] = "HotMilfsFuck"
                    perf['site'] = "HotMilfsFuck"
                    performers_data.append(perf)

        return performers_data

    def get_performers(self, response):
        performers = super().get_performers(response)
        tags = response.xpath('//ul[@class="tags"]/li/a/text()')
        if tags:
            tags = tags.getall()
            for tag in tags:
                if "Male - " in tag:
                    tag = re.search(r'.*? - (.*)', tag).group(1)
                    performers.append(string.capwords(tag))
        return performers

    def get_tags(self, response):
        tags_orig = super().get_tags(response)
        tags = []
        for tag in tags_orig:
            if "Male - " not in tag and "Ethnicity - " not in tag:
                if "boobs" not in tag.lower() and "natural" not in tag.lower():
                    tags.append(tag)
        return tags

    def conv_height(self, height):
        if height:
            if "'" in height:
                height = re.sub(r'[^0-9\']', '', height)
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    feet = int(feet) * 12
                else:
                    feet = 0
                inches = re.search(r'\'(\d+)', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                else:
                    inches = 0
                return str(int((feet + inches) * 2.54)) + "cm"
        return None
