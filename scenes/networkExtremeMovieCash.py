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
        'https://www.allthoseboobs.com', #New
        'https://www.allthosegirlfriends.com', #New
        'https://www.allthosegirls.com', #New
        'https://www.allthosemoms.com', #New
        'https://www.analfrench.com',
        'https://www.asianhotbunnies.com',
        'https://www.bangmyboobies.com', #New
        'https://www.bigbreast.tv',
        'https://www.bigmacky.com', #New
        'https://www.bizarix.com',
        'https://www.boundmybitch.com',
        'https://www.bosslesson.com',
        'https://www.brasilextreme.com',
        'https://www.brazilianerotic.com', #New
        'https://www.brazilpartyorgy.com',
        'https://www.bukkakeorgy.com', #New
        'https://www.candidcrush.com',
        'https://www.castingbunnies.com',
        'https://www.chubbyworlds.com', #New
        'https://www.crazybeauties.com',
        'https://www.crazyfetishpass.com',
        'https://www.crazymonstercock.com',
        'https://www.crazymouthmeat.com',
        'https://www.crazyoldmoms.com',
        'https://www.crazypeegirls.com',
        'https://www.crazypregnant.com', #New
        'https://www.crazyspandexgirls.com', #New
        'https://www.cumrotic.com', #New
        'https://www.czechsuperstars.com',
        'https://www.deep-throat.tv', #New
        'https://www.dildopenetrations.com', #New
        'https://www.dirtyclinic.com',
        'https://www.dirtyprivate.com',
        'https://www.dporgasm.com', #New
        'https://www.exgfsexxx.com', #New
        'https://www.extremetranny.com',
        'https://www.fetishtransformation.com', #New
        'https://www.firstanalteens.com',
        'https://www.fistingfiles.com', #New
        'https://www.flexiangels.com', #New
        'https://www.flexidolls.com', #New
        'https://www.flexifetishgirls.com', #New
        'https://www.frenchpickups.com', #New
        'https://www.fuckonstreet.com', #New
        'https://www.fuckthosechicks.com', #New
        'https://www.fuckthosemoms.com', #New
        'https://www.germanpickups.com', #New
        'https://www.germanstreets.com',
        'https://www.glamourinfetish.com', #New
        'https://www.goldwinpass.com', #New
        'https://www.grandpalove.com',
        'https://www.grannyguide.com', #New
        'https://www.herfirstkisses.com',
        'https://www.hotpartysex.com', #New
        'https://www.hotrubberbabes.com', #New
        'https://www.ilikehandjobs.com', #New
        'https://www.indianrealporn.com', #New
        'https://www.juicynudists.com',
        'https://www.kellyinspandex.com',  # Paywalled 2022-08-01
        'https://www.latinlesbea.com',
        'https://www.latinwildparties.com', #New
        'https://www.lederhosengangbang.com', #New
        'https://www.lookiamhairy.com',
        'https://www.lynnhd.com',
        'https://www.milfpower.com', #New
        'https://www.mountainfuckfest.com', #New
        'https://www.mybangvan.com', #New
        'https://www.naughtybi.com',
        'https://www.nylonworlds.com', #New
        'https://www.onlytaboo.com',
        'https://www.onlybreast.com', #New
        'https://www.pervertclips.com', #New
        'https://www.pornonstage.com',
        'https://www.povmovies.com', #New
        'https://www.preggolovers.com', #New
        'https://www.publiccrush.com',
        'https://www.purekisses.com', #New
        'https://www.purepee.com', #New
        'https://www.purolatinas.com',

        'https://www.realgangbangs.com', #New
        'https://www.realitytaboo.com',
        'https://www.realporn.xxx', #New
        'https://www.realteendolls.com', #New
        'https://www.realteenstars.com', #New
        'https://www.rioanal.com',
        'https://www.riobang.com',
        'https://www.safarisex.com', #New
        'https://www.sapphiclovers.com', #New
        'https://www.scandiporn.com', #New
        'https://www.scandalonstage.com', #New
        'https://www.schoolgirllust.com', #New
        'https://www.sexfair.xxx', #New
        'https://www.sexflexvideo.com', #New
        'https://www.sexycuckold.com',
        'https://www.slipperymassage.com', #New
        'https://www.smoke-city.com',
        'https://www.smokingbunnies.com', #New
        'https://www.spandexporn.com', #New
        'https://www.sweetpartychicks.com', #New
        'https://www.thiswife.com', #New
        'https://www.virtualxporn.com', #New
        'https://www.voyeurpapy.com', #New
        'https://www.whoresinpublic.com',
        'https://www.wildgroupsex.com', #New
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
        if "crazyfetishpass" in base or "kellyinspandex" in base:
            pagination = "/tour/categories/movies_%s_d.html"
        if "realporn" in base:
            pagination = "/free/categories/movies_%s_d.html"
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "modelfeature")]|//div[@class="product clearfix"]')
        for scene in scenes:
            item = SceneItem()
            if "realgangbangs" in response.url:
                title = scene.xpath('.//div[@class="modeldata"]//a/strong/text()')
            else:
                title = scene.xpath('.//div[@class="modeldata"]//a/text()|.//h3/text()')
            if title:
                item['title'] = string.capwords(title.get().strip())
            else:
                item['title'] = 'No Title Available'
            date = scene.xpath('.//i[contains(@class, "fa-calendar")]/following-sibling::font/text()|.//i[@class="icon-clock"]/following-sibling::b/text()')
            if not date:
                date = scene.xpath('.//i[contains(@class, "fa-calendar")]/following-sibling::text()')
            if not date:
                date = scene.xpath('.//h3/following-sibling::text()[contains(., "Updated")]')
            if date:
                date = date.getall()
                date = "".join(date).replace("\r", "").replace("\n", "").replace("\t", "")
                date = re.search(r'(\d{4}-\d{2}-\d{2})', date)
                if date:
                    item['date'] = date.group(1)
                else:
                    item['date'] = ''
            else:
                item['date'] = ''
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
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = ''
            item['description'] = ''
            item['tags'] = []
            item['network'] = "Extreme Movie Pass"
            item['site'] = match_site(tldextract.extract(response.url).domain)
            item['parent'] = match_site(tldextract.extract(response.url).domain)
            yield self.check_item(item, self.days)
