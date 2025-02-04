import os
import re
import datetime
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class InTheCrackIPSpider(BaseSceneScraper):
    name = 'InTheCrackIP'
    network = 'In The Crack'
    parent = 'In The Crack'
    site = 'In The Crack'

    start_urls = [
        'https://72.52.135.91',
    ]

    selector_map = {
        'title': '//section[@class="modelCollectionHeader"]/h2/span/text()',
        'description': '//div[@class="ClipDetail"]//p/text()',
        'date': '',
        'image': '//style[contains(text(),"background-image")]/text()',
        'image_blob': '//style[contains(text(),"background-image")]/text()',
        'performers': '//section[@class="modelCollectionHeader"]/h2/span/text()',
        'tags': '',
        'external_id': r'/(\d*)$',
        'trailer': '',  # Videos listed in code require login
        'pagination': '/Collections/Date/%s'
    }

    def get_next_page_url(self, base, page):
        year = datetime.datetime.now().year + 1
        year = str(year - page)
        url = self.format_url(
            base, self.get_selector_map('pagination') % year)
        return url

    def get_scenes(self, response):
        scenes = response.xpath('//ul[@class="collectionGridLayout"]/li/a[contains(@href,"Collection")]')
        # ~ print(response.text)
        for scene in scenes:
            # ~ print(scene.xpath('//*').getall())
            scenedate = scene.xpath('./span[2]/text()').get()
            # ~ print(f"Scenedate: {scenedate}")
            if scenedate:
                scenedate = scenedate.strip()
            else:
                scenedate = dateparser.parse('today').isoformat()
            scene = scene.xpath('./@href').get()
            url = "https://72.52.135.91" + scene
            yield scrapy.Request(url, callback=self.parse_scene, meta={'date': scenedate})

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            return title.replace("  ", " ").strip()
        return ''

    def get_description(self, response):
        description = ''
        desc_sections = response.xpath('//div[@class="ClipDetail"]')
        if desc_sections:
            for desc_section in desc_sections:
                desc_title = desc_section.xpath('./div/h4/text()').get()
                desc_description = desc_section.xpath('./div/p/text()').get()
                if desc_title and desc_description:
                    description = description + desc_title.strip() + os.linesep + desc_description + os.linesep
                    description = description.replace("\r\n", "\n")

        return description

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if "url" in image:
            image = re.search(r'url\(\'(.*)\'\)', image).group(1)
            if image:
                image = 'https://72.52.135.91' + image.strip()
            else:
                image = None

        if image:
            return self.format_link(response, image)
        return None

    def get_performers(self, response):
        performers = []
        performer_text = self.process_xpath(
            response, self.get_selector_map('performers')).get()
        if performer_text:
            performer_text = re.search(r'^\d+\s+?(.*)', performer_text).group(1)
            if performer_text:
                performers = performer_text.strip().split("&")

        if performers:
            return list(map(lambda x: x.strip(), performers))
        return []

    def parse_scene(self, response):
        item = SceneItem()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if hasattr(self, 'site'):
            item['site'] = self.site
        elif 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None

        if 'image_blob' in response.meta:
            item['image_blob'] = response.meta['image_blob']
        else:
            item['image_blob'] = self.get_image_blob(response)

        if ('image_blob' not in item or not item['image_blob']) and item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if 'image_blob' not in item:
            item['image_blob'] = None

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

        if 'markers' in response.meta:
            item['markers'] = response.meta['markers']
        else:
            item['markers'] = self.get_markers(response)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        # ~ tempid = re.search(r'(\d+)', item['title'])
        # ~ if tempid:
            # ~ tempid = int(tempid.group(1))
            # ~ if tempid > 1821 and tempid < 1843:
                # ~ item['id'] = item['id'] + "-1"

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        if 'duration' in response.meta:
            item['duration'] = response.meta['duration']
        else:
            item['duration'] = self.get_duration(response)

        if 'url' in response.meta:
            item['url'] = response.meta['url']
        else:
            item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        elif 'network' in response.meta:
            item['network'] = response.meta['network']
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        elif 'parent' in response.meta:
            item['parent'] = response.meta['parent']
        else:
            item['parent'] = self.get_parent(response)

        # Movie Items

        if 'store' in response.meta:
            item['store'] = response.meta['store']
        else:
            item['store'] = self.get_store(response)

        if 'director' in response.meta:
            item['director'] = response.meta['director']
        else:
            item['director'] = self.get_director(response)

        if 'format' in response.meta:
            item['format'] = response.meta['format']
        else:
            item['format'] = self.get_format(response)

        if 'back' in response.meta:
            item['back'] = response.meta['back']
        else:
            item['back'] = self.get_back_image(response)

        if 'back' not in item or not item['back']:
            item['back'] = None
            item['back_blob'] = None
        else:
            if 'back_blob' in response.meta:
                item['back_blob'] = response.meta['back_blob']
            else:
                item['back_blob'] = self.get_image_back_blob(response)

            if ('back_blob' not in item or not item['back_blob']) and item['back']:
                item['back_blob'] = self.get_image_from_link(item['back'])

        if 'back_blob' not in item:
            item['back_blob'] = None

        if 'sku' in response.meta:
            item['sku'] = response.meta['sku']
        else:
            item['sku'] = self.get_sku(response)

        if hasattr(self, 'type'):
            item['type'] = self.type
        elif 'type' in response.meta:
            item['type'] = response.meta['type']
        elif 'type' in self.get_selector_map():
            item['type'] = self.get_selector_map('type')
        else:
            item['type'] = 'Scene'

        item['url'] = item['url'].replace("72.52.135.91", "www.inthecrack.com")
        item['image'] = item['image'].replace("72.52.135.91", "www.inthecrack.com")

        yield self.check_item(item, self.days)
