import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NewSensationsSpider(BaseSceneScraper):
    name = 'NewSensations'
    network = 'New Sensations'

    start_urls = [
        'https://www.newsensations.com'

        # Sites that are included in scrape, though site names aren't given for scraping
        # Here for reference so we don't double scrape:
        # -------------------------------
        # https://familyxxx.com
        # https://hotwifexxx.com
        # https://parodypass.com
        # https://stretchedoutsnatch.com
        # https://tabutales.com
        # https://talesfromtheedge.com
        # https://thelesbianexperience.com
    ]

    selector_map = {
        'title': '//div[@class="indScene"]/*[self::h1 or self::h2 or self::h3]/text()',
        'description': '//div[@class="description"]/span/following-sibling::h2/text()',
        'date': '//div[@class="sceneDateP"]/span/text()',
        'image': '//span[@id="trailer_thumb"]//img/@src',
        'image_blob': '//span[@id="trailer_thumb"]//img/@src',
        'performers': '//div[@class="sceneTextLink"]//span[@class="tour_update_models"]/a/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': 'tour_ns\\/updates\\/(.+)\\.html',
        'trailer': '',
        'pagination': '/tour_ns/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="captions"]/h4/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_site(self, response):
        if not isinstance(response, str):
            if self.get_selector_map('tags'):
                taglist = self.process_xpath(response, self.get_selector_map('tags')).get()
                taglist = taglist.replace(" ", "")
        else:
            taglist = response

        if "familyxxx" in taglist.lower():
            return "Family XXX"
        if "girlgirlxxx" in taglist.lower():
            return "Girl Girl XXX"
        if "freshouttahighschool" in taglist.lower():
            return "Fresh Outta High School"
        if "heavyhandfuls" in taglist.lower():
            return "Heavy Handfuls"
        if "hotwifexxx" in taglist.lower():
            return "HotWifeXXX"
        if "parody" in taglist.lower():
            return "Parody Pass"
        if "povfantasy" in taglist.lower():
            return "POV Fantasy"
        if "stretchedoutsnatch" in taglist.lower():
            return "Stretched Out Snatch"
        if "tabutales" in taglist.lower():
            return "Tabu Tales"
        if "talesfromtheedge" in taglist.lower():
            return "Tales From the Edge"
        if "theromanceseries" in taglist.lower():
            return "The Romance Series"
        if "thelesbianexperience" in taglist.lower():
            return "The Lesbian Experience"
        if "unlimitedmilfs" in taglist.lower():
            return "Unlimited Milfs"

        return "New Sensations"

    def get_image(self, response):
        image = super().get_image(response)
        if image[-3:] == "%20":
            image = image[:-3]
        return image

    def get_tags(self, response):
        performers = super().get_performers(response)
        site = self.get_site(response).strip().title()

        tags = super().get_tags(response)
        if len(tags) == 1 and "," in tags[0]:
            tags = tags[0].split(',')
            tags = list(map(lambda x: x.strip().title(), tags))
            for performer in performers:
                if performer in tags:
                    tags.remove(performer)
            if "Movies" in tags:
                tags.remove("Movies")
            if "4K" in tags:
                tags.remove("4K")
            if "New Sensations" in tags:
                tags.remove("New Sensations")
            if site in tags:
                tags.remove(site)
            tags2 = tags.copy()
            for tag in tags2:
                if "#" in tag:
                    tags.remove(tag)

        return tags

    def get_id(self, response):
        sceneid = response.xpath('//comment()[contains(.,"data-id")]')
        if sceneid:
            return re.search(r'data-id=\"(\d+)\"', sceneid.get()).group(1)
        return None

    def parse_scene(self, response):
        item = self.init_scene()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)

        if self.check_item(item, self.days):
            item['image'] = self.get_image(response)

            if 'image' not in item or not item['image']:
                item['image'] = None
                item['image_blob'] = None
            else:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if item['image']:
                if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
        else:
            item['image'] = ''
            item['image_blob'] = ''

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = "New Sensations"
        item['parent'] = "New Sensations"

        item['type'] = 'Scene'

        yield self.check_item(item, self.days)
