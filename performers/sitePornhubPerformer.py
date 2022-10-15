import re
import json
import string

from os.path import exists
from scrapy_splash import SplashRequest
from tpdb.helpers.http import Http
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePornhubPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@itemprop="name"]/text()|//div[@class="name"]/h1/text()',
        'image': '//img[@id="getAvatar"]/@src',
        'bio': '//div[@itemprop="description"]/text()|//section[contains(@class, "aboutMeSection")]/div[@class="title"]/following-sibling::div/text()|//div[contains(@class,"text longBio")]/text()',
        'gender': '//span[@itemprop="gender"]/text()',
        'astrology': '//span[contains(text(), "Star Sign")]/following-sibling::span/text()|//span[contains(text(), "Star Sign")]/following-sibling::text()',
        'ethnicity': '//span[contains(text(), "Ethnicity")]/following-sibling::span/text()|//span[contains(text(), "Ethnicity")]/following-sibling::text()',
        'birthplace': '//span[contains(text(), "Birth Place")]/following-sibling::span/text()|//span[contains(text(), "Birth Place")]/following-sibling::text()|//span[contains(text(), "Birthplace")]/following-sibling::span/text()|//span[contains(text(), "Birthplace")]/following-sibling::text()',
        'nationality': '//span[contains(text(), "City and Country")]/following-sibling::span/text()|//span[contains(text(), "City and Country")]/following-sibling::text()|//span[contains(text(), "City and Country")]/following-sibling::span/text()|//span[contains(text(), "City and Country")]/following-sibling::text()',
        'haircolor': '//span[contains(text(), "Hair Color")]/following-sibling::span/text()|//span[contains(text(), "Hair Color")]/following-sibling::text()',
        'eyecolor': '//span[contains(text(), "Eye Color")]/following-sibling::span/text()|//span[contains(text(), "Eye Color")]/following-sibling::text()',
        'piercings': '//span[contains(text(), "Piercings")]/following-sibling::span/text()|//span[contains(text(), "Piercings")]/following-sibling::text()',
        'tattoos': '//span[contains(text(), "Tattoos")]/following-sibling::span/text()|//span[contains(text(), "Tattoos")]/following-sibling::text()',
        'measurements': '//span[contains(text(), "Measurements")]/following-sibling::span/text()|//span[contains(text(), "Measurements")]/following-sibling::text()',
        'fakeboobs': '//span[contains(text(), "Fake Boobs")]/following-sibling::span/text()|//span[contains(text(), "Fake Boobs")]/following-sibling::text()',
        'height': '//span[contains(text(), "Height")]/following-sibling::span/text()|//span[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//span[contains(text(), "Weight")]/following-sibling::span/text()|//span[contains(text(), "Weight")]/following-sibling::text()',
        'birthday': '//span[contains(text(), "Born")]/following-sibling::span/text()|//span[contains(text(), "Born")]/following-sibling::text()',
        'pagination': '/tour/models/%s/name/?g=',
        'external_id': r'models/(.+).html$'
    }

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
            'scrapy_splash.SplashCookiesMiddleware': 250,
            'scrapy_splash.SplashMiddleware': 251,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        'SPLASH_URL': 'http://192.168.1.151:8050/',
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
        'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage'
    }

    name = 'PornhubPerformer'
    network = "Pornhub"
    parent = "Pornhub"

    def start_requests(self):
        newjsondata = []
        # ~ headers = {'Content-Type': 'application/json'}
        index = "https://www.pornhub.com/webmasters/stars_detailed"
        print('Retrieving new index list...')
        req = Http.get(index, headers=self.headers, cookies=self.cookies)
        jsondata = json.loads(req.text)
        jsondata = jsondata['stars']
        print('Retrieving current index list...')
        oldindex = self.open_current_index()
        print(f"JSONData Length: {len(jsondata)}")
        for star in jsondata:
            found_star = False
            starid = re.search(r'pornstar=(.*)$', star['star']['star_url'].lower().strip())
            if starid:
                starid = starid.group(1)
            else:
                print(f"No ID Found for: {star['star']['star_name']}")

            for oldstar in oldindex:
                oldstarid = re.search(r'pornstar=(.*)$', oldstar['star']['star_url'].lower().strip())
                if oldstarid:
                    oldstarid = oldstarid.group(1)
                else:
                    print(f"No ID Found for: {oldstar['star']['star_name']}")
                if starid == oldstarid:
                    oldindex.remove(oldstar)
                    found_star = True
                    break

            if not found_star:
                newjsondata.append(star)

        print(f"New JSONData Length: {len(newjsondata)}")

        for performer in newjsondata:
            meta = {}
            meta['name'] = string.capwords(performer['star']['star_name'])
            meta['gender'] = string.capwords(performer['star']['gender'])
            matches = ['m2f', 'f2m', 'non-binary', 'other']
            if any(x in meta['gender'].lower() for x in matches):
                meta['gender'] = 'Trans'
            if meta['gender'].lower() == 'same sex couple (female)':
                meta['gender'] = 'Female'
            if meta['gender'].lower() == 'same sex couple (male)':
                meta['gender'] = 'Male'
            if meta['gender'].lower() == 'couple' or meta['gender'].lower() == 'unknown':
                meta['gender'] = None

            meta['image'] = performer['star']['star_thumb']
            meta['json'] = performer
            yield SplashRequest(performer['star']['star_url'], self.parse_performer, endpoint='render.html', meta=meta)

    def open_current_index(self):
        index = []
        if exists('pornhub_performer.json'):
            with open('pornhub_performer.json', encoding="utf-8") as json_file:
                for jsonrow in json_file:
                    row = json.loads(jsonrow)
                    index.append(row)
        return index

    def write_to_index_file(self, jsondata):
        with open('pornhub_performer.json', 'a', encoding="utf-8") as outfile:
            json.dump(jsondata, outfile)
            outfile.write('\n')
            outfile.close()

    def get_fakeboobs(self, response):
        if 'fakeboobs' in self.selector_map:
            fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).getall()
            fakeboobs = "".join(fakeboobs).strip()
            if fakeboobs:
                return fakeboobs.strip()
        return ''

    def get_eyecolor(self, response):
        if 'eyecolor' in self.selector_map:
            eyecolor = self.process_xpath(response, self.get_selector_map('eyecolor')).getall()
            eyecolor = "".join(eyecolor).strip()
            if eyecolor:
                return eyecolor.strip()

        return ''

    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).getall()
            haircolor = "".join(haircolor).strip()
            if haircolor:
                return haircolor.strip()

        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).getall()
            height = "".join(height).strip()
            if height:
                if re.search(r'(\d+ cm)', height.lower()):
                    height = re.search(r'(\d+ cm)', height.lower()).group(1)
                    height = height.replace(" ", "")
                return height.strip()

        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).getall()
            weight = "".join(weight).strip()
            if weight:
                if re.search(r'(\d+ kg)', weight.lower()):
                    weight = re.search(r'(\d+ kg)', weight.lower()).group(1)
                    weight = weight.replace(" ", "")
                return weight.strip()

        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).getall()
            measurements = "".join(measurements).strip()
            if measurements:
                return measurements.strip()

        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).getall()
            measurements = "".join(measurements).strip()
            if measurements:
                if re.search(r'^(\d{2,3}\w+)[-\.:]', measurements):
                    cupsize = re.search(r'^(\d{2,3}\w+)[-\.:]', measurements).group(1)
                    return cupsize.strip().upper()
        return ''

    def get_tattoos(self, response):
        if 'tattoos' in self.selector_map:
            tattoos = self.process_xpath(response, self.get_selector_map('tattoos')).getall()
            tattoos = "".join(tattoos).strip()
            if tattoos:
                return tattoos.strip()

        return ''

    def get_piercings(self, response):
        if 'piercings' in self.selector_map:
            piercings = self.process_xpath(response, self.get_selector_map('piercings')).getall()
            piercings = "".join(piercings).strip()
            if piercings:
                return piercings.strip()

        return ''

    def get_astrology(self, response):
        if 'astrology' in self.selector_map:
            astrology = self.process_xpath(response, self.get_selector_map('astrology')).getall()
            astrology = "".join(astrology).strip()
            if astrology:
                return astrology.strip()

        return ''

    def get_birthplace(self, response):
        if 'birthplace' in self.selector_map:
            birthplace = self.process_xpath(response, self.get_selector_map('birthplace')).getall()
            birthplace = "".join(birthplace).strip()
            if birthplace:
                return birthplace.strip()

        return ''

    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).getall()
            ethnicity = "".join(ethnicity).strip()
            if ethnicity:
                return ethnicity.strip()

        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).getall()
            birthday = "".join(birthday).strip()
            if birthday:
                if re.search(r'(\d{4}-\d{2}-\d{2})', birthday):
                    birthday = re.search(r'(\d{4}-\d{2}-\d{2})', birthday).group(1)
                return self.parse_date(birthday).isoformat()

        return ''

    def get_nationality(self, response):
        if 'nationality' in self.selector_map:
            nationality = self.process_xpath(response, self.get_selector_map('nationality')).getall()
            nationality = "".join(nationality).strip()
            if nationality:
                return nationality.strip()

        return ''

    def parse_performer(self, response):
        meta = response.meta
        item = PerformerItem()

        item['name'] = response.meta['name']
        if "male.jpg" not in response.meta['image'].lower():
            item['image'] = response.meta['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = None
            item['image_blob'] = None

        item['bio'] = self.get_bio(response).replace("\n", "  ")
        item['gender'] = response.meta['gender']
        item['birthday'] = self.get_birthday(response)
        item['astrology'] = self.get_astrology(response)
        item['birthplace'] = self.get_birthplace(response)
        item['ethnicity'] = self.get_ethnicity(response)
        item['nationality'] = self.get_nationality(response)
        item['eyecolor'] = self.get_eyecolor(response)
        item['haircolor'] = self.get_haircolor(response)
        item['height'] = self.get_height(response)
        item['weight'] = self.get_weight(response)
        item['measurements'] = self.get_measurements(response)
        item['tattoos'] = self.get_tattoos(response)
        item['piercings'] = self.get_piercings(response)
        item['cupsize'] = self.get_cupsize(response)
        item['fakeboobs'] = self.get_fakeboobs(response)
        item['url'] = self.get_url(response)
        item['network'] = "Pornhub"

        if self.debug:
            print(item)
        else:
            self.write_to_index_file(meta['json'])
            yield item
