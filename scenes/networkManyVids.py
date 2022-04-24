"""
Scraper for ManyVids network.
If adding sites, please use the 'Manyvids: <site/performername>' format
This helps keep them together on the site without mixing in what are
usually more or less camgirls into the regular sites
"""
import re
import html
import json
import string
from datetime import datetime
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkManyVidsSpider(BaseSceneScraper):
    name = 'ManyVids'

    start_urls = [
        ['1001216419', 'YouthLust'],
        ['214657', 'Manyvids: Lana Rain'],
        ['423053', 'MySweetApple'],
        ['1001495638', 'Manyvids: Jack and Jill'],
        ['325962', 'Manyvids: Dirty Princess'],
        ['312711', 'Manyvids: Cattie'],
        ['1000286888', 'A Taboo Fantasy'],
        ['694469', 'Adult Candy Store'],
        ['1000159044', 'Fuck Club'],
        ['1000380769', 'IXXVICOM'],
        ['806007', 'Jay Bank Presents'],
        ['1001483477', 'Undercover Sluts'],
        # ~ # ['574529', 'Submissive Teen POV'],  # Seems to have gone away, leaving for reference
        ['1002638751', 'Sloppy Toppy'],
        ['69353', 'Natalia Grey'],
        ['97815', 'Manyvids: Hidori'],
        ['1001123043', 'Manyvids: Paige Steele'],
        ['1001317123', 'Manyvids: Jaybbgirl'],
        ['1001673578', 'Manyvids: FreyaJade'],
        ['304591', 'Manyvids: 420SexTime'],
        ['217682', 'Manyvids: OmankoVivi'],
        ['1000304351', 'Manyvids: Haylee Love'],
        ['1002322838', 'Manyvids: Jewelz Blu'],
        ['1003298627', 'Manyvids: Molly Redwolf'],
        ['1003004427', 'Manyvids: Sweetie Fox'],
        ['32539', 'Manyvids: Cherry Crush'],
        ['35990', 'Manyvids: Charlette Webb'],
        ['91512', 'Manyvids: Alli Leigh'],
        ['65933', 'Manyvids: Little Miss Elle'],
        ['216064', 'Manyvids: Lena Spanks'],
        ['251896', 'Manyvids: Submissive Lexi'],
        ['1004407943', 'Manyvids: Sloansmoans'],
        ['491714', 'Manyvids: ImMeganLive'],
        ['577443', 'Manyvids: Emmas Secret Life'],
        ['375403', 'Manyvids: Natashas Bedroom'],
        ['102036', 'Manyvids: Ashley Alban'],
        ['147843', 'Manyvids: Penny Barber'],
        ['38793', 'Manyvids: Princess Leia'],
        ['1003527333', 'Manyvids: Kathia Nobili'],
        ['1004207044', 'Manyvids: Mrs Mischief'],
        ['1000997612', 'Manyvids: MistressT'],
        ['1005123610', 'Manyvids: Tara Tainton'],
        ['1001836304', 'Manyvids: Siena Rose'],
        ['273124', 'Manyvids: Courtney Scott'],
        ['1000856699', 'Manyvids: Kiittenymph'],
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False'}

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

    def start_requests(self):
        url = "https://www.manyvids.com/Profile/1001216419/YouthLust/Store/Videos/"
        yield scrapy.Request(url,
                             callback=self.get_taglist,
                             headers=self.headers,
                             cookies=self.cookies)

    def get_taglist(self, response):
        meta = response.meta
        meta['mvtoken'] = response.xpath('//html/@data-mvtoken').get()
        meta['headers'] = self.headers
        url = "https://d3e1078hs60k37.cloudfront.net/site_files/json/vid_categories.json"
        yield scrapy.Request(url,
                             callback=self.start_requests2,
                             headers=self.headers,
                             cookies=self.cookies, meta=meta)

    def start_requests2(self, response):
        meta = response.meta
        self.headers['referer'] = 'https://www.manyvids.com/Profile/1003004427/Sweetie-Fox/Store/Videos/'
        taglist = json.loads(response.text)
        meta['taglist'] = taglist

        for link in self.start_urls:
            meta['page'] = self.page
            meta['siteid'] = link[0]
            meta['site'] = link[1]
            yield scrapy.Request(url=self.get_next_page_url(self.page, meta),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response):
        # ~ print(response.text)
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, page, meta):
        offset = str((int(page) - 1) * 30)
        link = f"https://www.manyvids.com/api/model/{meta['siteid']}/videos?category=all&offset={offset}&sort=0&limit=30&mvtoken={meta['mvtoken']}"
        return link

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        data = jsondata['result']['content']['items']
        for jsonentry in data:
            scene = "https://www.manyvids.com" + jsonentry['preview']['path'].replace("\\", "")
            if jsonentry['preview']['videoPreview']:
                meta['trailer'] = jsonentry['preview']['videoPreview'].replace("\\", "").replace(" ", "%20")
            meta['id'] = jsonentry['id']
            meta['title'] = string.capwords(html.unescape(jsonentry['title']))
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
        if "Jewelz Blu" in meta['site']:
            return ['Jewelz Blu']
        if "Molly Redwolf" in meta['site']:
            return ['Molly Redwolf']
        if "Sweetie Fox" in meta['site']:
            return ['Sweetie Fox']
        if "Cherry Crush" in meta['site']:
            return ['Cherry Crush']
        if "Charlette Webb" in meta['site']:
            return ['Charlette Webb']
        if "Alli Leigh" in meta['site']:
            return ['Alli Leigh']
        if "Little Miss Elle" in meta['site']:
            return ['Little Miss Elle']
        if "Lena Spanks" in meta['site']:
            return ['Lena Spanks']
        if "Submissive Lexi" in meta['site']:
            return ['Submissive Lexi']
        if "Ashley Alban" in meta['site']:
            return ['Ashley Alban']
        if "Penny Barber" in meta['site']:
            return ['Penny Barber']
        if "Princess Leia" in meta['site']:
            return ['Princess Leia']
        if "Kathia Nobili" in meta['site']:
            return ['Kathia Nobili']
        if "Mrs Mischief" in meta['site']:
            return ['Mrs Mischief']
        if "MistressT" in meta['site']:
            return ['MistressT']
        if "Tara Tainton" in meta['site']:
            return ['Tara Tainton']
        if "Siena Rose" in meta['site']:
            return ['Siena Rose']
        if "Courtney Scott" in meta['site']:
            return ['Courtney Scott']
        if "Kiittenymph" in meta['site']:
            return ['Lex Kiittenymph']
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
            scenetags = []
            if tags:
                tags = re.search('\"(.*)\"', tags).group(1)
                if tags:
                    tags = tags.split(",")
                    for tag in tags:
                        for alltags in taglist:
                            if alltags['id'] == tag:
                                scenetags.append(alltags['label'])
                                break
            if meta['site'] and "Manyvids" in meta['site']:
                scenetags.append("Manyvids")
            if scenetags:
                return list(map(lambda x: x.strip().title(), scenetags))
        return []

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("[custom video] ", "")
        return description
