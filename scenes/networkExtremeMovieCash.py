import string
import re
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'amateur18': "Amateur 18 TV",
        'analfrench': "Anal French",
        'asianhotbunnies': "Asian Hot Bunnies",
        'bigbreast': "Big Breast TV",
        'bizarix': "Bizarix",
        'boundmybitch': "Bound My Bitch",
        'bosslesson': "Boss Lesson",
        'brasilextreme': "Brasil Extreme",
        'brazilpartyorgy': "Brazil Party Orgy",
        'candidcrush': "Candid Crush",
        'castingbunnies': "Casting Bunnies",
        'crazybeauties': "Crazy Beauties",
        'crazyfetishpass': "Crazy Fetish Pass",
        'crazymonstercock': "Crazy Monster Cock",
        'crazymouthmeat': "Crazy Mouth Meat",
        'crazyoldmoms': "Crazy Old Moms",
        'crazypeegirls': "Crazy Pee Girls",
        'czechsuperstars': "Czech Superstars",
        'dirtyclinic': "Dirty Clinic",
        'dirtyprivate': "Dirty Private",
        'extremetranny': "Extreme Tranny",
        'firstanalteens': "First Anal Teens",
        'germanstreets': "German Streets",
        'grandpalove': "Grandpa Love",
        'herfirstkisses': "Her First Kisses",
        'hotrubberbabes': "Hot Rubber Babes",
        'juicynudists': "Juicy Nudists",
        'kellyinspandex': "Kelly in Spandex",
        'latinlesbea': "Latin Lesbea",
        'lookiamhairy': "Look I Am Hairy",
        'lynnhd': "LynnHD",
        'naughtybi': "Naughty Bi",
        'onlytaboo': "Only Taboo",
        'pornonstage': "Porn on Stage",
        'publiccrush': "Public Crush",
        'purolatinas': "Puro Latinas",
        'realitytaboo': "Reality Taboo",
        'rioanal': "Rio Anal",
        'riobang': "Rio Bang",
        'sexycuckold': "Sexy Cuckold",
        'smoke-city': "Smoke City",
        'whoresinpublic': "Whores in Public",
        'wildgangbangs': "Wild Gangbangs",
    }
    return match.get(argument, argument)


class NetworkExtremeMovieCashSpider(BaseSceneScraper):
    name = 'ExtremeMovieCash'

    start_urls = [
        'https://www.amateur18.tv',
        'https://www.analfrench.com',
        'https://www.asianhotbunnies.com',
        'https://www.bigbreast.tv',
        'https://www.bizarix.com',
        'https://www.boundmybitch.com',
        'https://www.bosslesson.com',
        'https://www.brasilextreme.com',
        'https://www.brazilpartyorgy.com',
        'https://www.candidcrush.com',
        'https://www.castingbunnies.com',
        'https://www.crazybeauties.com',
        'https://www.crazyfetishpass.com',
        'https://www.crazymonstercock.com',
        'https://www.crazymouthmeat.com',
        'https://www.crazyoldmoms.com',
        'https://www.crazypeegirls.com',
        'https://www.czechsuperstars.com',
        'https://www.dirtyclinic.com',
        'https://www.dirtyprivate.com',
        'https://www.extremetranny.com',
        'https://www.firstanalteens.com',
        'https://www.germanstreets.com',
        'https://www.grandpalove.com',
        'https://www.herfirstkisses.com',
        'https://www.hotrubberbabes.com',
        'https://www.juicynudists.com',
        'https://www.kellyinspandex.com',
        'https://www.latinlesbea.com',
        'https://www.lookiamhairy.com',
        'https://www.lynnhd.com',
        'https://www.naughtybi.com',
        'https://www.onlytaboo.com',
        'https://www.pornonstage.com',
        'https://www.publiccrush.com',
        'https://www.purolatinas.com',
        'https://www.realitytaboo.com',
        'https://www.rioanal.com',
        'https://www.riobang.com',
        'https://www.sexycuckold.com',
        'https://www.smoke-city.com',
        'https://www.whoresinpublic.com',
        'https://www.wildgangbangs.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_next_page_url(self, base, page):
        pagination = '/tour/categories/movies/%s/latest/'
        if "crazyfetishpass" in base:
            pagination = "/tour/categories/movies_%s_d.html"
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "modelfeature")]|//div[@class="product clearfix"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = string.capwords(scene.xpath('.//div[@class="modeldata"]//a/text()|.//h3/text()').get().strip())
            date = scene.xpath('.//i[contains(@class, "fa-calendar")]/following-sibling::font/text()|.//i[@class="icon-clock"]/following-sibling::b/text()')
            if not date:
                date = scene.xpath('.//i[contains(@class, "fa-calendar")]/following-sibling::text()')
            if date:
                date = date.get()
                if "Updated" in date:
                    date = date.replace("Updated", "").strip()
                item['date'] = self.parse_date(date).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            external_id = scene.xpath('.//img[contains(@id, "set-target")]/@id')
            if external_id:
                external_id = external_id.get().replace("set-target-", "").strip()
            else:
                external_id = scene.xpath('./div[@class="product-image"]/a/img/@src').get()
            external_id = re.search(r'(\d*)-', external_id).group(1)
            item['id'] = external_id
            item['url'] = response.url
            performers = scene.xpath('.//span[@class="update_models"]/a/text()|.//a[contains(@href, "/models")]/text()')
            if performers:
                item['performers'] = scene.xpath('.//span[@class="update_models"]/a/text()|.//a[contains(@href, "/models")]/text()').getall()
            else:
                item['performers'] = []
            item['image'] = self.format_link(response, scene.xpath('.//img[contains(@id, "set-target")]/@src0_3x|.//img[contains(@id, "set-target")]/@src0_2x|.//img[contains(@id, "set-target")]/@src0_1x|./div[@class="product-image"]/a/img/@src').get())
            item['image_blob'] = None
            item['trailer'] = None
            item['description'] = None
            item['tags'] = []
            item['network'] = "Extreme Movie Cash"
            item['site'] = match_site(tldextract.extract(response.url).domain)
            item['parent'] = match_site(tldextract.extract(response.url).domain)
            yield item
