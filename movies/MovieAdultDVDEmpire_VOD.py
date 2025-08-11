import re
import json
import html
import string
import os.path
from datetime import date, datetime, timedelta
from pathlib import Path
import unidecode
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieAdultDVDEmpireSpider(BaseSceneScraper):
    name = 'MovieAdultDVDEmpire_VOD'
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
        # ~ 'pagination': '/new-addition-porn-videos.html?page=%s&media=14'
        'pagination': '/new-release-porn-videos.html?page=%s&unlimited=0&media=14'
    }

    def get_scenes(self, response):
        movies = response.xpath('//div[@class="product-card"]/div/a/@href').getall()
        for movie in movies:
            movie = movie.strip()
            if re.search(self.get_selector_map('external_id'), movie):
                yield scrapy.Request(url=self.format_link(response, movie), callback=self.parse_movie)

    def get_title(self, response):
        jsondata = response.xpath('//script[contains(text(), "uploadDate")][1]/text()')
        title = None
        if jsondata:
            jsondata = jsondata.get()
            title = self.check_json(jsondata, 'name')
        if not title:
            title = response.xpath('//meta[@name="og:title"]/@content')
            if title:
                title = title.get()
                title = re.search(r'(.*?)\|', title)
                if title:
                    title = title.group(1)
                    title = re.sub(r'\(\d{4}\)', '', title).strip()
        title = unidecode.unidecode(html.unescape(string.capwords(title).strip()))
        return self.clean_text(title)

    def get_studio(self, response):
        jsondata = response.xpath('//script[contains(text(), "uploadDate")][1]/text()')
        studio = None
        if jsondata:
            jsondata = jsondata.get()
            studio = self.check_json(jsondata, 'productionCompany', 'name')
        if not studio:
            studio = super().get_studio(response)
        studio = unidecode.unidecode(html.unescape(string.capwords(studio).strip()))
        return studio.strip()

    def get_description(self, response):
        jsondata = response.xpath('//script[contains(text(), "uploadDate")][1]/text()')
        description = None
        if jsondata:
            jsondata = jsondata.get()
            description = self.check_json(jsondata, 'description')
        if not description:
            description = response.xpath('//h4[contains(@class,"synopsis")]/p/text()|//h4[contains(@class,"synopsis")]/following-sibling::p/text()')
            if description:
                description = description.getall()
                description = " ".join(description).replace("  ", " ").strip()
        if description:
            description = self.clean_text(description)
            description = unidecode.unidecode(html.unescape(string.capwords(description).strip()))
        else:
            description = ""
        return description

    def get_tags(self, response):
        tags = []
        tags = response.xpath('//meta[@property="og:video:tag"]/@content')
        if tags:
            tags = tags.getall()
        if not tags:
            tags = self.process_xpath(response, self.get_selector_map('tags')).getall()
        if tags:
            return list(map(lambda x: string.capwords(x.strip()), tags))
        return []

    def get_performers(self, response):
        performers = []
        performers = response.xpath('//meta[@property="og:video:actor"]/@content')
        if performers:
            performers = performers.getall()
        if not performers:
            performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
        if performers:
            return list(map(lambda x: string.capwords(x.strip()), performers))
        return []

    def get_date(self, response):
        scenedate = None
        scenedate = response.xpath('//meta[@property="og:video:release_date"]/@content')
        if scenedate:
            scenedate = scenedate.get().strip()
        if not scenedate:
            scenedate = self.process_xpath(response, self.get_selector_map('date'))
            if scenedate:
                scenedate = scenedate.get()
                scenedate.replace('Released:', '').replace('Added:', '').strip()
            else:
                scenedate = response.xpath('//li/small[contains(text(),"Production")]/following-sibling::text()').get()
                if scenedate:
                    scenedate = scenedate + "-01-01"
        if not scenedate:
            return datetime.now().isoformat()

        return dateparser.parse(scenedate).isoformat()

    def get_duration(self, response):
        length = None
        length = response.xpath('//meta[@property="og:video:duration"]/@content')
        if length:
            length = length.get()
            if length:
                if not int(length):
                    length = None
        if not length:
            length = super().get_duration(response)
            if length:
                length = length.lower()
                if "hr" in length and "min" in length:
                    if re.search(r'(\d{1,2}).+?hr.+?(\d{1,2}).+?min', length):
                        length = re.search(r'(\d{1,2}).+?hr.+?(\d{1,2}).+?min', length)
                        hour = int(length.group(1))
                        minute = int(length.group(2))
                    length = str((hour * 3600) + (minute * 60))
        return length

    def get_format(self, response):
        movieformat = self.process_xpath(response, self.get_selector_map('format'))
        if movieformat:
            movieformat = list(map(lambda x: string.capwords(x.strip()), movieformat.getall()))
            movieformat.sort()
            movieformat = " / ".join(movieformat)
            return movieformat

        return "Video on Demand"

    def clean_tags(self, tags):
        cleanlist = [
            'movie',
            'vod exclusive',
            '4k',
            'hd',
            'feature',
            '4k ultra hd',
        ]
        newlist = []
        for word in tags:
            if word.lower() not in cleanlist:
                newlist.append(word)
        return newlist

    def get_image(self, response):
        front = super().get_image(response)
        if not front or ".com/" not in front:
            front = response.xpath('//meta[@property="og:image"]/@content')
            if front:
                front = front.get()
        if not front or ".com/" not in front:
            front = response.xpath('//a[contains(@href, "h.jpg") and not(contains(@href, "bh.jpg"))]/@href')
            if front:
                front = front.get()
        if isinstance(front, list):
            front = front[0]
        if front in response.url:
            print(f"Invalid front image returned for: {response.url}")
            return ""
        if front:
            return self.format_link(response, front)
        return None

    def get_back_image(self, response):
        back = super().get_back_image(response)
        if not back or back in response.url:
            back = response.xpath('//a[contains(@href, "bh.jpg")]/@href')
            if back:
                back = back.get()
        if isinstance(back, list) and back:
            back = back[0]

        if not isinstance(back, str) or back in response.url:
            print(f"Invalid back image returned for: {response.url}")
            return ""
        if back:
            return self.format_link(response, back)
        return None

    def parse_movie(self, response):
        item = SceneItem()
        num_scenes = response.xpath('//h3/a[contains(@label, "Scene Title")]')
        if len(num_scenes) > 1 or not len(num_scenes):
            item['title'] = self.clean_text(self.get_title(response))
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

            matches = ['bangbros', 'jeffsmodels', 'private', 'dorcel', 'bluebirdfilms', 'privateblack', 'dorcelclub', 'evilangel', 'wicked', 'zerotolerance', 'zerotolerancefilms', 'zerotoleranceent', 'burningangel', 'burningangelentertainment']
            if item['title'] and item['site'] and not any(x in re.sub(r'[^a-zA-Z0-9]', '', item['site']).lower().replace(" ", "") for x in matches):
                year = re.search(r'(\d{4})-\d{2}-\d{2}', item['date']).group(1)
                teststring = item['title'] + year + item['site']
                teststring = re.sub(r'[^A-Za-z0-9#]+', '', teststring).lower()
                # ~ with open('adedupelist.txt', 'a', encoding="utf-8") as file1:
                    # ~ file1.write(teststring + "\n")

                # limit_date is to keep it from pulling movies within the past two days from ADE, just in case they're on the actual studio sites
                limit_date = date.today() - timedelta(2)
                limit_date = limit_date.strftime('%Y-%m-%d')

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
            else:
                print(f"Skipping {item['title']} Due to blocked Studio: {item['site']}")
        # ~ else:
            # ~ urltitle = re.search(r'.*/(.*?)$', response.url).group(1)
            # ~ print(f"Skipping Due to Low Scene Count: {len(num_scenes)} {urltitle} :: ({response.url})")

    def check_json(self, jsondata, arg1, arg2=None):
        try:
            jsondata = json.loads(jsondata)
        except:
            jsondata = None
        if jsondata:
            if arg2:
                result = jsondata[arg1][arg2]
            else:
                result = jsondata[arg1]
            return result
        return None

    def clean_text(self, textstring):
        if textstring is not None:
            textstring = textstring.strip()
            textstring = unidecode.unidecode(textstring)
            textstring = html.unescape(textstring)
            textstring = re.sub('<[^<]+?>', '', textstring)
        return textstring
