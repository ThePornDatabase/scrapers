import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKillergramFullScrapeSpider(BaseSceneScraper):
    name = 'KillergramFullScrape'
    network = 'Killergram'

    url = 'https://killergram.com'
    paginations = [
            ['anal+rehab', 'Anal Rehab', ['Anal']],
            # ~ ['get+shafted', 'Baby Loves the Shaft', ['BBC']],
            # ~ ['bitch+funkers', 'Bitch Funkers', []],
            # ~ ['booty+packers', 'Booty Back Packers', ['Big Ass']],
            # ~ ['brown+sugar', 'Brown Sugar Rush', []],
            # ~ ['burlesque+xxx', 'Burlesque XXX', []],
            # ~ ['college+babes', 'College Babes Exposed', ['College']],
            # ~ ['cream+my+cunt', 'Cream My Cunt', ['Creampie']],
            # ~ ['office+antics', 'Cum Into My Office', ['Office']],
            # ~ ['cum+party+sluts', 'Cum Party Sluts', []],
            # ~ ['fetish+sex+clinic', 'Fetish Sex Clinic', ['Medical', 'Nurse']],
            # ~ ['girly+riders', 'Girly Riders', []],
            # ~ ['gloryhole+girls', 'Gloryhole Gaggers', ['Gloryhole', 'Blowjob', 'Gagging']],
            # ~ ['chain+smokers', 'Hardcore Chain Smokers', ['Smoking']],
            # ~ ['lets+get+slippy', 'Lets Get Slippy', ['Shower', 'Bathroom']],
            # ~ ['nylon+cum+sluts', 'Nylon Cum Sluts', ['Pantyhose']],
            # ~ ['dogging+missions', 'On a Dogging Mission', ['Outdoors']],
            # ~ ['pornostatic', 'Pornostatic', []],
            # ~ ['rock+chicks', 'Rock Chicks', []],
            # ~ ['ru+4+hire', 'RU 4 Hire', ['Car Sex', 'Car', 'Taxi']],
            # ~ ['club+babes', 'Sexy Club Babes', ['Nightclub']],
            # ~ ['space+hoppers', 'Space Hoppers and Lolly Poppers', ['Schoolgirl', 'Food']],
            # ~ ['tattooed+sluts', 'Tattooed Fuck Sluts', ['Tattoos']],
            # ~ ['the+handy+man', 'The Handy Man', ['Blue Collar Worker']],
            # ~ ['the+lady+pimp', 'The Lady Pimp', []],
            # ~ ['kinky+couples', 'UK Reality Swingers', ['Amateur', 'Swingers']],
            # ~ ['porn+stars+utd', 'UK Soccer Babes', ['Sports']],
            # ~ ['street+walkers', 'UK Street Walkers', ['Prostitution']],
            # ~ ['hard-fi+sex', 'Urban Perversions', ['Fetish']],
            # ~ ['voyeur+cams', 'Voyeur Cam Sluts', ['Webcam']],
            # ~ ['wife+sluts', 'Wife Slut Adventures', ['MILF', 'Wife']],
            # ~ ['wishes+cum+true', 'Wishes Cum True', ['Fantasy']],
            # ~ ['killergram%20cuts', 'Killergram Cuts', []],
            # ~ ['killergram%20platinum', 'Killergram Platinum', []],
    ]

    selector_map = {
        'description': '//table[contains(@class, "episodetext")]/tr[5]/td/text()',
        'date': '//table[contains(@class, "episodetext")]//span[contains(text(), "ublished")]/following-sibling::text()',
        'date_formats': ['%d %B %Y'],
        'image': '//table//td/img[contains(@name, "episode_001")]/@src',
        'performers': '//table[contains(@class, "episodetext")]//a[contains(@href, "model")]/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'id=(\d+)',
    }

    def start_requests(self):
        for pagination in self.paginations:
            url=self.get_next_page_url(self.url, self.page, pagination[0])
            print(url)
            yield scrapy.Request(url,
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': pagination[0], 'site': pagination[1], 'parent': 'Killergram', 'network': 'Killergram', 'tags': pagination[2]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = response.meta
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        page = str(((page - 1) * 15) + 1)
        return f"https://killergram.com/episodes.asp?page=episodes&ct=site&site={pagination}&p={page}"

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@id, "episodes")]/table//a[contains(@href, "id=")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = response.xpath('//table//td/img[contains(@name, "episode_001")]/@src')
        if title:
            title = title.get()
            model = re.search(r'models/(.*?)/', title).group(1)
            title = re.search(r'models/.*?/(.*?)/', title).group(1)
            title = title.replace(model, "").replace("_", " ").replace("-", " ").strip()
            return self.cleanup_title(title)
        return ''

    def get_duration(self, response):
        duration = response.xpath('//table[contains(@class, "episodetext")]//span[contains(text(), "uration")]/following-sibling::text()')
        if duration:
            duration = re.search(r'(\d+) min', duration.get()).group(1)
            duration = str(int(duration) * 60)
            return duration
        return None

    def get_description(self, response):
        description = response.xpath(self.get_selector_map('description'))
        if description:
            description = " ".join(description.getall())
            return description.strip()
        return ''
