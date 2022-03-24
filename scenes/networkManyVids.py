"""
Scraper for ManyVids network.
"""
import re
import json
from datetime import datetime
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkManyVidsSpider(BaseSceneScraper):
    name = 'ManyVids'

    start_urls = [
        ['https://www.manyvids.com', '/api/model/1001216419/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'YouthLust'],
        ['https://www.manyvids.com', '/api/model/214657/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Lana Rain'],
        ['https://www.manyvids.com', '/api/model/423053/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'MySweetApple'],
        ['https://www.manyvids.com', '/api/model/1001495638/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Jack and Jill'],
        ['https://www.manyvids.com', '/api/model/325962/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Dirty Princess'],
        ['https://www.manyvids.com', '/api/model/312711/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Cattie'],
        ['https://www.manyvids.com', '/api/model/1000286888/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'A Taboo Fantasy'],
        ['https://www.manyvids.com', '/api/model/694469/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Adult Candy Store'],
        ['https://www.manyvids.com', '/api/model/1000159044/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Fuck Club'],
        ['https://www.manyvids.com', '/api/model/1000380769/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'IXXVICOM'],
        ['https://www.manyvids.com', '/api/model/806007/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Jay Bank Presents'],
        ['https://www.manyvids.com', '/api/model/1001483477/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Undercover Sluts'],
        # ['https://www.manyvids.com', '/api/model/574529/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Submissive Teen POV'],  # Seems to have gone away, leaving for reference
        ['https://www.manyvids.com', '/api/model/1002638751/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Sloppy Toppy'],
        ['https://www.manyvids.com', '/api/model/69353/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Natalia Grey'],
        ['https://www.manyvids.com', '/api/model/97815/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Hidori'],
        ['https://www.manyvids.com', '/api/model/1001123043/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Paige Steele'],
        ['https://www.manyvids.com', '/api/model/1001317123/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Jaybbgirl'],
        ['https://www.manyvids.com', '/api/model/1001673578/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: FreyaJade'],
        ['https://www.manyvids.com', '/api/model/304591/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: 420SexTime'],
        ['https://www.manyvids.com', '/api/model/217682/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: OmankoVivi'],
        ['https://www.manyvids.com', '/api/model/1000304351/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=6199def482315613508608', 'Manyvids: Haylee Love'],
    ]

    selector_map = {
        'title': '',
        'description': '//div[contains(@class, "desc-text")]/text()',
        'date': '//div[@class="mb-1"]/span[1]/span[2]|//div[@class="mb-1"]/span[2]/text()',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '',
        'tags': '//script[contains(text(),"tagListApp")]/text()',
        'external_id': '',
        'trailer': '',
        'pagination': ''
    }

    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    cookies = {
        'PHPSESSID': '1i3dnqaq575hvn72antt9ugmm2jf3l0t7m81bve1'
    }

    def start_requests(self):
        url = "https://www.manyvids.com/Profile/1001216419/YouthLust/Store/Videos/"
        yield scrapy.Request(url,
                             callback=self.get_taglist,
                             headers=self.headers,
                             cookies=self.cookies)

    def get_taglist(self, response):
        meta = response.meta
        url = "https://d3e1078hs60k37.cloudfront.net/site_files/json/vid_categories.json"
        yield scrapy.Request(url,
                             callback=self.start_requests2,
                             headers=self.headers,
                             cookies=self.cookies, meta=meta)

    def start_requests2(self, response):
        meta = response.meta
        taglist = json.loads(response.text)
        meta['taglist'] = taglist

        for link in self.start_urls:
            meta['page'] = self.page
            meta['pagination'] = link[1]
            meta['site'] = link[2]
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        offset = str((int(page) - 1) * 30)
        return self.format_url(base, pagination % offset)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        data = jsondata['result']['content']['items']
        for jsonentry in data:
            scene = "https://www.manyvids.com" + jsonentry['preview']['path'].replace("\\", "")
            if jsonentry['preview']['videoPreview']:
                meta['trailer'] = jsonentry['preview']['videoPreview'].replace("\\", "").replace(" ", "%20")
            meta['id'] = jsonentry['id']
            meta['title'] = jsonentry['title']
            if scene and meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        meta = response.meta
        videostring = response.xpath('//meta[@property="og:video"]/@content')
        if videostring:
            videostring = videostring.get()
            datestring = re.search(r'_(\d{10,13})\.', videostring)
            if datestring:
                datestring = datestring.group(1)
                if len(datestring) > 10:
                    datestring = int(datestring) / 1000
                date = datetime.utcfromtimestamp(int(datestring)).isoformat()
                return date
        else:
            imagestring = response.xpath('//meta[@name="twitter:image"]/@content').get()
            if imagestring:
                imagestring = re.search(r'.*_([0-9a-zA-Z]{10,20}).jpg', imagestring)
                if imagestring:
                    imagestring = imagestring.group(1)
                    imagestringhex = imagestring[:8]
                    if imagestringhex and "386D43BC" <= imagestringhex <= "83AA7EBC":
                        imagedate = int(imagestringhex, 16)
                        date = datetime.utcfromtimestamp(imagedate).isoformat()
                        return date
                    if imagestring and 946684860 <= int(imagestring) <= 2208988860:
                        date = datetime.utcfromtimestamp(int(imagestring)).isoformat()
                        return date

        # If no valid image string available to pull date from
        # print(f'Guessing date for: {response.url}')
        page = int(meta['page'])
        date = response.xpath('//div[@class="mb-1"]/span[@class="d-none"]/span[2]/text()')
        if date:
            date = date.get()
            date = re.search(r'(\w{3} \d{1,2})', date)
            if date:
                date = date.group(1)
        if not date:
            date = response.xpath('//div[@class="mb-1"]/span[2]/text()')
            if date:
                date = date.get()
                date = re.search(r'(\w{3} \d{1,2})', date)
                if date:
                    date = date.group(1)
        if date:
            date = date.strip()
            if re.search(r'([a-zA-Z]{3} \d{1,2})', date):
                date = re.search(r'([a-zA-Z]{3} \d{1,2})', date).group(1)
                date = date.split(" ")
                monthstring = datetime.strptime(date[0], '%b')
                month = str(monthstring.month)
                if len(month) == 1:
                    month = "0" + month
                if len(date[1]) == 1:
                    day = "0" + date[1]
                else:
                    day = date[1]

                today = datetime.now().strftime('%m%d')
                year = datetime.now().strftime('%Y')
                scenedate = str(month) + str(day)

                sceneid = re.search(r'Video\/(\d+)\/', response.url).group(1)
                if sceneid:
                    sceneid = int(sceneid)
                    if sceneid > 2462280:
                        scenedate = scenedate + "2021"
                    if 1657000 <= sceneid <= 2462279:
                        scenedate = scenedate + "2020"
                    if 1014000 <= sceneid <= 1656999:
                        scenedate = scenedate + "2019"
                    if 600000 <= sceneid <= 1013999:
                        scenedate = scenedate + "2018"
                    if sceneid < 599999:
                        scenedate = scenedate + "2017"
                else:
                    if page in range(1, 5):
                        if scenedate <= today:
                            scenedate = scenedate + year
                        else:
                            scenedate = scenedate + str(int(year) - 1)

                    if page in range(6, 7):
                        if scenedate <= today:
                            scenedate = scenedate + str(int(year) - 1)
                        else:
                            scenedate = scenedate + str(int(year) - 2)

                    if page == 8:
                        if scenedate <= today:
                            scenedate = scenedate + str(int(year) - 2)
                        else:
                            scenedate = scenedate + str(int(year) - 3)

                    if page == 9:
                        if scenedate <= today:
                            scenedate = scenedate + str(int(year) - 3)
                        else:
                            scenedate = scenedate + str(int(year) - 4)

                    if page == 10:
                        if scenedate <= today:
                            scenedate = scenedate + str(int(year) - 4)
                        else:
                            scenedate = scenedate + str(int(year) - 5)

                    if page > 10:
                        if scenedate <= today:
                            scenedate = scenedate + str(int(year) - 5)
                        else:
                            scenedate = scenedate + str(int(year) - 6)

            if len(scenedate) > 2:
                try:
                    return dateparser.parse(scenedate, date_formats=['%m%d%Y']).isoformat()
                except Exception:
                    return dateparser.parse('today').isoformat()
        return dateparser.parse('today').isoformat()

    def get_performers(self, response):
        meta = response.meta
        if meta['site'] == "Lana Rain":
            return ['Lana Rain']
        if meta['site'] == "Natalia Grey":
            return ['Natalia Grey']
        if meta['site'] == "Cattie":
            return ['Cattie Candescent']
        if "Hidori" in meta['site']:
            return ['Hidori']
        if "Jaybbgirl" in meta['site']:
            return ['Jaybbgirl']
        if "FreyaJade" in meta['site']:
            return ['Freya Jade']
        if "420SexTime" in meta['site']:
            return ['Asteria']
        if "OmankoVivi" in meta['site']:
            return ['Omanko Vivi']
        if "Haylee Love" in meta['site']:
            return ['Haylee Love']
        if "Paige Steele" in meta['site']:
            return ['Paige Steele']
        return []

    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return "Manyvids"

    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            if "Manyvids" in meta['site']:
                return "Manyvids"
            return meta['site']
        return "Manyvids"

    def get_network(self, response):
        return "Manyvids"

    def get_tags(self, response):
        meta = response.meta
        taglist = meta['taglist']
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags')).get()
            if tags:
                tags = re.search('\"(.*)\"', tags).group(1)
                if tags:
                    tags = tags.split(",")
                    scenetags = []
                    for tag in tags:
                        for alltags in taglist:
                            if alltags['id'] == tag:
                                scenetags.append(alltags['label'])
                                break
            if meta['site'] and "ManyVids" in meta['site']:
                scenetags.append("ManyVids")
            if scenetags:
                return list(map(lambda x: x.strip().title(), scenetags))
        return []

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("[custom video] ", "")
        return description
