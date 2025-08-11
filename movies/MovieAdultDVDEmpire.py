import re
import html
import string
from PIL import Image
import base64
from io import BytesIO
from requests import get
import os.path
from datetime import date, datetime, timedelta
from pathlib import Path
import unidecode
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieAdultDVDEmpireSpider(BaseSceneScraper):
    name = 'MovieAdultDVDEmpire'
    store = "Adult DVD Empire"

    start_urls = [
        'https://www.adultdvdempire.com'
    ]

    cookies = [{"name":"ageConfirmed","value":"true"},{"name":"defaults","value":"{}"}]
    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False'}

    selector_map = {
        'title': '//div[contains(@class,"title-rating-section")]/div/h1/text()',
        'description': '//h4[contains(@class,"synopsis")]/p/text()',
        'date': '//li/small[contains(text(),"Released")]/following-sibling::text()',
        'image': '//a[@id="front-cover"]/img/@src',
        'back': '//a[@id="back-cover"]/@href',
        'performers': '//strong[contains(text(),"Starring")]/following-sibling::a/div//text()|//strong[contains(text(),"Starring")]/following-sibling::a//text()',
        'tags': '//strong[contains(text(),"Categories")]/following-sibling::a/text()',
        'external_id': r'/(\d+)/',
        'studio': '//li/small[contains(text(), "Studio:")]/following-sibling::a/text()',
        'director': '//a[@label="Director"]/text()',
        'format': '//div[contains(@class, "pricing")]/h2/text()[1]',
        'duration': '//li/small[contains(text(), "Length:")]/following-sibling::text()',
        'sku': '//li/small[contains(text(), "SKU:")]/following-sibling::text()',
        'pagination': '/new-release-porn-movies.html?page=%s',
        # ~ 'pagination': '/85941/studio/combat-zone-porn-movies.html?page=%s&media=2',
    }

    def get_scenes(self, response):
        movies = response.xpath('//div[@class="product-card"]/div/a/@href').getall()
        for movie in movies:
            movie = movie.strip()
            if re.search(self.get_selector_map('external_id'), movie):
                yield scrapy.Request(url=self.format_link(response, movie), callback=self.parse_movie)

    def get_description(self, response):
        description = response.xpath('//h4[contains(@class,"synopsis")]/p/text()|//h4[contains(@class,"synopsis")]/following-sibling::p/text()')
        if description:
            description = description.getall()
            description = " ".join(description).replace("  ", " ").strip()
            return description
        return ""

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return self.clean_tags(list(map(lambda x: x.strip().title(), tags)))
        return []

    def get_date(self, response):
        dvddate = self.process_xpath(response, self.get_selector_map('date')).get()
        if dvddate:
            dvddate.replace('Released:', '').replace('Added:', '').strip()
        else:
            dvddate = response.xpath('//li/small[contains(text(),"Production")]/following-sibling::text()').get()
            if dvddate:
                dvddate = dvddate + "-01-01"
            if not dvddate:
                return datetime.now().strftime('%Y-%m-%d')

        return dateparser.parse(dvddate.strip()).strftime('%Y-%m-%d')

    def get_duration(self, response):
        length = super().get_duration(response)
        if length:
            length = length.lower()
            if "hr" in length and "min" in length:
                if re.search(r'(\d{1,2}).+?hr.+?(\d{1,2}).+?min', length):
                    length = re.search(r'(\d{1,2}).+?hr.+?(\d{1,2}).+?min', length)
                    hour = int(length.group(1))
                    minute = int(length.group(2))
                    length = str((hour * 3600) + (minute * 60))
            elif "min" in length:
                if re.search(r'(\d{1,2}).+?min', length):
                    length = re.search(r'(\d{1,2}).+?min', length)
                    minute = int(length.group(1))
                    length = str((minute * 60))
            else:
                length = None
        return length

    def get_format(self, response):
        if 'format' in self.get_selector_map():
            if self.get_selector_map('format'):
                movieformat = self.process_xpath(response, self.get_selector_map('format'))
                if movieformat:
                    movieformat = list(map(lambda x: string.capwords(x.strip()), movieformat.getall()))
                    movieformat.sort()
                    movieformat = " / ".join(movieformat)
                    return movieformat

        return "Dvd"

    def clean_tags(self, tags):
        cleanlist = [
            'movie',
            'vod exclusive',
            '4k',
            'hd',
            'feature',
            '4k ultra hd',
            'boxed sets',
        ]
        newlist = []
        for word in tags:
            if word.lower() not in cleanlist:
                newlist.append(word)
        return newlist

    def parse_movie(self, response):
        item = SceneItem()

        item['title'] = self.clean_text(self.get_title(response))
        item['title'] = re.sub(r'\(.*?dvd.*?\)|\(.*?blu-ray.*?\)|\(.*?combo.*?\)', '', item['title'], flags=re.IGNORECASE)
        item['description'] = self.clean_text(self.get_description(response))
        item['store'] = "Adult DVD Empire"
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['back'] = self.get_back_image(response)
        item['back_blob'] = self.get_image_blob_from_link(item['back'])
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['network'] = self.get_studio(response)
        item['site'] = self.get_studio(response)
        item['parent'] = self.get_studio(response)
        item['director'] = self.get_director(response)
        item['format'] = self.get_format(response)
        item['duration'] = self.get_duration(response)
        item['sku'] = self.get_sku(response)
        item['type'] = 'Movie'

        item['url'] = self.get_url(response)

        if self.days > 27375:
            filter_date = '0000-00-00'
        else:
            days = self.days
            filter_date = date.today() - timedelta(days)
            filter_date = filter_date.strftime('%Y-%m-%d')

        # limit_date is to keep it from pulling movies within the past two days from ADE, just in case they're on the actual studio sites
        limit_date = date.today() - timedelta(2)
        limit_date = limit_date.strftime('%Y-%m-%d')

        matches = ['bangbros', 'jeffsmodels', 'private', 'dorcel', 'bluebirdfilms', 'privateblack', 'dorcelclub', 'evilangel', 'wicked', 'zerotolerance', 'zerotolerancefilms', 'zerotoleranceent', 'burningangel', 'burningangelentertainment']
        if item['title'] and item['site'] and not any(x in re.sub(r'[^a-zA-Z0-9]', '', item['site']).lower().replace(" ", "") for x in matches):
            year = re.search(r'(\d{4})-\d{2}-\d{2}', item['date']).group(1)
            teststring = item['title'] + year + item['site']
            teststring = re.sub(r'[^A-Za-z0-9#]+', '', teststring).lower()

            if self.debug:
                if not item['date'] > filter_date and item['date'] < limit_date:
                    item['filtered'] = 'movie filtered due to date restraint'
                print(item)
            else:
                if filter_date and filter_date != "0000-00-00":
                    if item['date'] >= filter_date and item['date'] <= limit_date:
                        yield item
                    else:
                        print(f"Movie Filtered Due to Date: {item['title']}   [{item['date']}]   (Limit: {limit_date})  (Filter Date: {filter_date})")
                else:
                    if item['date'] < limit_date:
                        yield item
                    else:
                        print(f"Too new to submit: {item['title']}   [{item['date']}]   (Limit: {limit_date})")

    def clean_text(self, textstring):
        if textstring is not None:
            textstring = textstring.strip()
            textstring = unidecode.unidecode(textstring)
            textstring = html.unescape(textstring)
            textstring = re.sub('<[^<]+?>', '', textstring)
        return textstring

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            print(f"Invalid image returned for: {response.url}")
            return ""
        return image

    def get_back_image(self, response):
        if 'back' in self.get_selector_map():
            image = self.get_element(response, 'back', 're_back')
            if isinstance(image, list):
                image = image[0]
            if image in response.url:
                print(f"Invalid back image returned for: {response.url}")
                return ""
            return self.format_link(response, image)
        return ''
