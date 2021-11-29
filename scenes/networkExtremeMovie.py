import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkExtremeMoviePassSpider(BaseSceneScraper):
    name = 'ExtremeMoviePass'
    network = 'Extreme Movie Pass'

    start_urls = [
        'https://www.extrememoviepass.com/',
    ]

    matches = {
        'ab4you': 'Anabelle 4 You',
        'atb': 'All Those Boobs',
        'atg': 'All Those Girls',
        'atgf': 'All Those Girlfriends',
        'atm': 'All Those Moms',
        'be': 'Brazilian Erotic',
        'bea4you': 'Bea 4 You',
        'biz': 'Young Bondage Teens',
        'bm': 'Big Macky',
        'bmb': 'Bang My Boobs',
        'buo': 'Bukkake Orgy',
        'cp': 'Crazy Pregnant',
        'cpg': 'Crazy Pee Girls',
        'cr': 'CumRotic',
        'csg': 'Crazy Spandex Girls',
        'cw': 'Chubby Worlds',
        'dp': 'Dildo Penetrations',
        'dpo': 'DPOrgasm',
        'dt': 'Deep-Throat TV',
        'emily4you': 'Emily 4 You',
        'exgfs': 'EXGF Sexxx',
        'fd': 'FlexiDolls',
        'ff': 'Fisting Files',
        'ffg': 'Flexi Fetish Girls',
        'fos': 'Fuck on Street',
        'fp': 'French Pickups',
        'ft': 'Fetish Transformation',
        'ftc': 'Fuck Those Chicks',
        'ftm': 'Fuck Those Moms',
        'gg': 'Granny Guide',
        'gif': 'Glamour in Fetish',
        'gp': 'German Pickups',
        'gwp': 'Goldwin Pass',
        'hps': 'Hot Party Sex',
        'hrb': 'Hot Rubber Babes',
        'ilhj': 'I Like Handjobs',
        'ilikehj': 'I Like Handjobs',
        'irp': 'Indian Real Porn',
        'linda4you': 'Linda 4 You',
        'lwp': 'Latin Wild Parties',
        'mff': 'Mountain Fuck Fest',
        'mp': 'MILF Power',
        'nw': 'Nylon Worlds',
        'ob': 'Only Breast',
        'ot': 'Only Taboo',
        'pc': 'Pervert Clips',
        'pk': 'Pure Kisses',
        'pls': 'Preggo Lovers',
        'pp': 'Pure Pee',
        'rgb': 'Real Gangbangs',
        'rp': 'Real Porn',
        'rtd': 'Real Teen Dolls',
        'safarisex': 'Safari Sex',
        'scandi2': 'ScandiPorn',
        'sf': 'Sex Fair',
        'sfv': 'Sex Flex Video',
        'sgl': 'School Girl Lust',
        'sl': 'Sapphic Lovers',
        'sm': 'Slippery Massage',
        'sos': 'Scandal on Stage',
        'sp': 'ScandiPorn',
        'spc': 'Sweet Party Chicks',
        'spp': 'Spandex Porn',
        'twlav': 'This Wife',
        'vpv': 'Voyeur Papy',
        'wgs': 'Wild Group Sex',
    }

    selector_map = {
        'title': '//h2/a/text()',
        'description': '',
        'date': '//li[contains(text(),"Published")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//video/@poster',
        'performers': '//section[@id="content"]//center/a[contains(@href,"/models/")]/text()',
        'tags': '//li[contains(text(),"Tags")]/a/text()',
        'external_id': r'.*/(.*?)\.html',
        'trailer': '',
        'pagination': '/t7/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="product-desc"]/div[@class="product-title"]/a[contains(@href,"/scenes/")]/@href').getall()
        for scene in scenes:
            if scene[0] == '.':
                scene = scene[1:]
            scene = "https://www.extrememoviepass.com/t7" + scene
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        search = super().get_id(response)
        if search:
            search = search.replace("_vids", "").lower()
        return search

    def get_site(self, response):
        extern_id = re.search(r'.*/(.*)\.html', response.url)
        site = ''
        if extern_id:
            extern_id = extern_id.group(1)
            extern_id = extern_id.lower()
            for match in self.matches:
                if extern_id.startswith(match):
                    site = self.matches[match]
            if site:
                return site

            if "flexidolls" in extern_id:
                return "FlexiDolls"

            if "mbv" in extern_id:
                return "My Bang Van"

        return "Extreme Movie Pass"

    def get_parent(self, response):
        extern_id = re.search(r'.*/(.*)\.html', response.url)
        site = ''
        if extern_id:
            extern_id = extern_id.group(1)
            extern_id = extern_id.lower()
            for match in self.matches:
                if extern_id.startswith(match):
                    site = self.matches[match]
            if site:
                return site

            if "flexidolls" in extern_id:
                return "FlexiDolls"

            if "mbv" in extern_id:
                return "My Bang Van"

            if "ilikehand" in extern_id:
                return "I Like Handjobs"

        return "Extreme Movie Pass"
