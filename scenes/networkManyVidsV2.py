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
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkManyVidsV2Spider(BaseSceneScraper):
    name = 'ManyVidsV2'

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
        ['1004388117', 'Manyvids: ForbiddenFruitsFilms'],
        ['1004388132', 'Manyvids: Jodi West'],
        ['320527', 'Manyvids: Diane Andrews'],
        ['97815', 'Manyvids: Midori Rose'],
        ['1000324638', 'Manyvids: Blissed XXX'],
        ['1004131603', 'Manyvids: Chris And Mari'],
        ['1000829435', 'Manyvids: RhiannonRyder1995'],
        ['1001194277', 'Manyvids: Legendarylootz'],
        ['1002393375', 'Manyvids: Natasha Nixx'],
        ['208703', 'Manyvids: Tatum Christine'],
        ['150576', 'Manyvids: xxxCaligulaxxx'],
        ['1004057036', 'Manyvids: Amber Hallibell'],
        ['1000691111', 'Manyvids: Purple Bitch'],
        ['1003667583', 'Manyvids: Im Heather Harmon'],
        ['590705', 'Manyvids: Bettie Bondage'],
        ['1002042328', 'Manyvids: Jade Vow'],
        ['518153', 'Manyvids: Naughty Midwest Girls'],
        ['1002715079', 'Manyvids: Alice Bong'],
        ['1002319155', 'Manyvids: Sola Zola'],
        ['1002133241', 'Manyvids: Reislin'],
        ['1000107977', 'Manyvids: Chad Alva'],
        ['1000228944', 'Manyvids: Heather Vahn'],
        ['1002812736', 'Manyvids: Tommy Wood'],
        ['1000657719', 'Manyvids: Dawns Place'],
        ['1004225528', 'Manyvids: MyLittleSwallow'],
        ['1000933793', 'Manyvids: Sukisukigirl'],
        ['1005546662', 'Manyvids: Andregotbars'],
        ['1003828607', 'Manyvids: Brandibabes']
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False'}

    selector_map = {
        'title': '',
        'description': '//div[contains(@class, "desc-text")]/text()',
        'date': '//div[@class="mb-1"]/span[1]/span[2]|//div[@class="mb-1"]/span[2]/text()',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '',
        'tags': '//script[contains(text(),"tagListApp")]/text()',
        'duration': '//div[@class="video-details"]//i[contains(@class, "mv-icon-video-length")]/following-sibling::text()[contains(., "min")]',
        're_duration': r'(\d{1,2}\:.*?) min',
        'external_id': '',
        'trailer': '',
        'pagination': ''
    }

    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    def start_requests(self):
        url = "https://www.manyvids.com/Profile/1001216419/YouthLust/Store/Videos/"
        yield scrapy.Request(url, callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        meta['mvtoken'] = response.xpath('//html/@data-mvtoken').get()
        self.headers['referer'] = 'https://www.manyvids.com/Profile/1003004427/Sweetie-Fox/Store/Videos/'

        for link in self.start_urls:
            meta['page'] = self.page
            meta['siteid'] = link[0]
            meta['site'] = link[1]
            yield scrapy.Request(url=self.get_next_page_url(self.page, meta), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, page, meta):
        offset = str((int(page) - 1) * 30)
        link = f"https://www.manyvids.com/api/model/{meta['siteid']}/videos?category=all&offset={offset}&sort=0&limit=30&mvtoken={meta['mvtoken']}"
        return link

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        data = jsondata['result']['content']['items']
        for jsonentry in data:
            meta['id'] = jsonentry['id']
            meta['title'] = string.capwords(html.unescape(jsonentry['title']))
            scenelink = f"https://video-player-bff.estore.kiwi.manyvids.com/videos/{meta['id']}"
            if meta['id']:
                yield scrapy.Request(scenelink, callback=self.parse_scene, meta=meta)

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
        if "Brandibabes" in meta['site']:
            return ['Brandi Babes']
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
        if "RhiannonRyder1995" in meta['site']:
            return ['Rhiannon Ryder']
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
        if "Tatum Christine" in meta['site']:
            return ['Tatum Christine']
        if "Ashley Alban" in meta['site']:
            return ['Ashley Alban']
        if "Natasha Nixx" in meta['site']:
            return ['Natasha Nixx']
        if "Legendary" in meta['site']:
            return ['Legendarylootz']
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
        if "Jade Vow" in meta['site']:
            return ['Jade Vow']
        if "Bettie Bondage" in meta['site']:
            return ['Bettie Bondage']
        if "Heather Harmon" in meta['site']:
            return ['Heather Harmon']
        if "xxxCaligulaxxx" in meta['site']:
            return ['xxxCaligulaxxx']
        if "ForbiddenFruitsFilms" in meta['site']:
            return ['Jodi West']
        if "Jodi West" in meta['site']:
            return ['Jodi West']
        if "Purple Bitch" in meta['site']:
            return ['Purple Bitch']
        if "Alice Bong" in meta['site']:
            return ['Alice Bong']
        if "Amber Hallibell" in meta['site']:
            return ['Amber Hallibell']
        if "Diane Andrews" in meta['site']:
            return ['Diane Andrews']
        if "Midori Rose" in meta['site']:
            return ['Midori Rose']
        if "Sola Zola" in meta['site']:
            return ['Sola Zola']
        if "Reislin" in meta['site']:
            return ['Reislin']
        if "Chad Alva" in meta['site']:
            return ['Chad Alva']
        if "Heather Vahn" in meta['site']:
            return ['Heather Vahn']
        if "Sukisuki" in meta['site']:
            return ['Sukisukigirl']
        if "Andregotbars" in meta['site']:
            return ['Andregotbars']
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

    def parse_scene(self, response):
        item = SceneItem()
        meta = response.meta
        jsondata = json.loads(response.text)
        item['title'] = meta['title']
        item['id'] = meta['id']
        if 'description' in jsondata:
            item['description'] = jsondata['description']
        else:
            item['description'] = ""
        if "tags" in jsondata:
            item['tags'] = jsondata['tags']
        else:
            item['tags'] = []
        item['image'] = jsondata['screenshot'].replace(" ", "%20")
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['date'] = jsondata['launchDate']
        item['trailer'] = None
        item['type'] = 'Scene'
        item['network'] = "Manyvids"
        item['performers'] = self.get_performers(response)
        item['site'] = self.get_site(response)
        item['parent'] = self.get_parent(response)
        item['url'] = "https://www.manyvids.com" + jsondata['url']
        if "videoDuration" in jsondata:
            duration = re.search(r'(\d{1,2}:\d{1,2}:?\d{1,2}?)', jsondata['videoDuration'])
            item['duration'] = self.duration_to_seconds(duration.group(1))
        else:
            item['duration'] = ""
        yield self.check_item(item, self.days)
