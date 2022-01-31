import re
import string
import json
from datetime import date, timedelta
import tldextract
from chompjs import chompjs
from extruct.jsonld import JsonLdExtractor
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        '1000facials': "1000 Facials",
        '21sextreme': "21Sextreme",
        '21naturals': "21Naturals",
        'activeduty': "Active Duty",
        'allblackx': "All BlackX",
        'allgirlmassage': "All Girl Massage",
        'analacrobats': "Anal Acrobats",
        'bearback': "Bear Back",
        'bigfatcreampie': "Big Fat Creampie",
        'bigtoyxxx': "Big Toy XXX",
        'blowbanged': "Blowbanged",
        'blowpass': "Blowpass",
        'bondagelegend': "Bondage Legend",
        'boyzparty': "Boyz Party",
        'bskow': "BSkow",
        'burningangel': "Burning Angel",
        'bushybushy': "Bushy Bushy",
        'buttman': "Butt-Man",
        'christophclarkonline': "Christoph Clark Online",
        'circlejerkboys': "Circlejerk Boys",
        'cockvirgins': "Cock Virgins",
        'cumshotoasis': "Cumshot Oasis",
        'currycreampie': "Curry Creampie",
        'darkx': "DarkX",
        'devilsgangbangs': "Devils Gangbangs",
        'devilstgirls': "Devils TGirls",
        'dpfanatics': "DPFanatics",
        'dylanlucas': "Dylan Lucas",
        'eroticax': "EroticaX",
        'extrabigdicks': "Extra Big Dicks",
        'falconstudios': "Falcon Studios",
        'famedigital': "Fame Digital",
        'fantasymassage': "Fantasy Massage",
        'familycreep': "Family Creep",
        'footsiebabes': "Footsie Babes",
        'gapingangels': "Gaping Angels",
        'girlfriendsfilms': "Girlfriends Films",
        'girlsandstuds': "Girls and Studs",
        'girlstryanal': "Girls Try Anal",
        'grannyghetto': "Granny Ghetto",
        'hairyundies': "Hairy Undies",
        'hardx': "HardX",
        'highperformancemen': "High Performance Men",
        'hothouse': "Hothouse",
        'immorallive': "Immoral Live",
        'jakemalone': "Jake Malone",
        'jaysinxxx': "Jay Sinxxx",
        'joeysilvera': "Joey Silvera",
        'jonnidarkkoxxx': "Jonni Darkkoxxx",
        'lesbianfactor': "Lesbian Factor",
        'lesbianx': "LesbianX",
        'lewood': "Lewood",
        'lexingtonsteele': "Lexington Steele",
        'maledigital': "Male Digital",
        'maskurbate': "Maskurbate",
        'massage-parlo': "Massage Parlor",
        'menover30': "Men Over 30",
        'milkingtable': "Milking Table",
        'myxxxpass.com': "My XXX Pass",
        'mommyblowsbest': "Mommy Blows Best",
        'mommysgirl': "Mommys Girl",
        'nachovidalhardcore': "Nacho Vidal Hardcore",
        'nudefightclub': "Nude Fightclub",
        'nurumassage': "Nuru Massage",
        'nurunetwork': "Nuru Network",
        'onlyteenblowjobs': "Only Teen Blowjobs",
        'outofthefamily': "Out of the Family",
        'pantypops': "Panty Pops",
        'pridestudios': "Pride Studios",
        'prettydirty': "Pretty Dirty",
        'povblowjobs': "POV Blowjobs",
        'povmassage': "POV Massage",
        'povthis': "POV This",
        'ragingstallion': "Raging Stallion",
        'roccosiffredi': "Rocco Siffredi",
        'seemyflixxx': "SeeMyFlixxx",
        'soapymassage': "Soapy Massage",
        'squirtalicious': "Squirtalicious",
        'squirtingorgies': "Squirting Orgies",
        'strapattackers': "Strap Attackers",
        'sunlustxxx': "Sun Lust XXX",
        'throated': "Throated",
        'tittycreampies': "Titty Creampies",
        'transsexualroadtrip': "Transsexual Roadtrip",
        'tealconrad': "Teal Conrad",
        'trickyspa': "Tricky Spa",
        'tsfactor': "TS Factor",
        'xempire': "XEmpire",
    }
    return match.get(argument.lower(), argument)


class GammaEnterprisesSpider(BaseSceneScraper):
    name = 'GammaEnterprises'
    network = 'GammaEnterprises'

    start_urls = [

        ##############################
        # Network Sites
        ##############################
        # 'https://www.21sextreme.com',  Moved to Adult Time API
        # 'https://www.lustygrandmas.com',
        # 'https://www.teachmefisting.com',
        # 'https://www.trannyfrombrazil.com',


        'https://www.blowpass.com',
        # 'https://www.1000facials.com',
        # 'https://www.immorallive.com',
        # 'https://www.mommyblowsbest.com',
        # 'https://www.onlyteenblowjobs.com',
        # 'https://www.throated.com',


        'https://www.famedigital.com',
        # 'https://www.devilsfilm.com',
        # 'https://www.ebonycafe.com',
        # 'https://www.givemeteens.com',
        # 'https://www.lickalicka.com',
        # 'https://www.lowartfilms.com',
        # 'https://www.motherfuckerxxx.com',
        # 'https://www.peternorth.com',
        # 'https://www.roccosiffredi.com',
        # 'https://www.silverstonedvd.com',
        # 'https://www.silviasaint.com',
        # 'https://www.webmature.com',
        # 'https://www.whiteghetto.com',

        # 'https://www.fantasymassage.com',  Moved to Adult Time API
        # 'https://www.allgirlmassage.com',
        # 'https://www.nurumassage.com',

        'https://www.xempire.com',
        # 'https://www.allblackx.com/',
        # 'https://www.darkx.com/',
        # 'https://www.eroticaX.com/',
        # 'https://www.hardx.com/',
        # 'https://www.lesbianx.com/',

        'https://www.pridestudios.com',
        # 'https://www.familycreep.com',
        # 'https://www.circlejerkboys.com',
        # 'https://www.cockvirgins.com',
        # 'https://www.bearbacks.com',
        # 'https://www.boyzparty.com',
        # 'https://www.dylanlucas.com',
        # 'https://www.extrabigdicks.com',
        # 'https://www.highperformancemen.com',
        # 'https://www.menover30.com',


        ##############################
        # Standalone Sites
        ##############################
        # 'https://www.21naturals.com', Moved to AdultTime API
        'https://www.activeduty.com',
        'https://www.analacrobats.com',
        'https://www.bigfatcreampie.com',
        'https://www.bskow.com',
        'https://www.burningangel.com',
        'https://www.bushybushy.com',
        'https://www.buttman.com',
        'https://www.christophclarkonline.com/',
        'https://www.cumshotoasis.com',
        'https://www.currycreampie.com',
        'https://www.dpfanatics.com',
        'https://www.falconstudios.com',
        'https://www.footsiebabes.com',
        'https://www.gapingangels.com',
        'https://www.girlfriendsfilms.com',
        'https://www.girlsandstuds.com',
        'https://www.girlstryanal.com',
        'https://www.grannyghetto.com',
        'https://www.hothouse.com',
        'https://www.immorallive.com',  # Originally part of Blowpass, moved out of group
        'https://www.jakemalone.com',
        'https://www.jaysinxxx.com',
        'https://www.joeysilvera.com',
        'https://www.jonnidarkkoxxx.com',
        'https://www.lewood.com',
        'http://www.lexingtonsteele.com',
        'https://www.maledigital.com',
        'https://www.maskurbate.com',
        'https://www.milkingtable.com',
        # 'https://www.mommysgirl.com', Part of Adulttime API now
        'https://www.nachovidalhardcore.com',
        'https://www.nudefightclub.com',
        'https://www.pantypops.com',
        'https://www.povblowjobs.com',
        'https://www.povthis.com',
        'https://www.prettydirty.com',
        'https://www.ragingstallion.com',
        'http://www.seemyflixxx.com',
        'https://www.soapymassage.com',
        'https://www.squirtingorgies.com',
        'https://www.strapattackers.com',
        'https://www.tittycreampies.com',
        'https://www.transsexualroadtrip.com',
        'https://www.trickyspa.com',
        'https://www.tsfactor.com',


        #  API or Comments
        # 'https://www.adulttime.com' -> No videos listed on site
        # 'https://www.bisexdigital.com' -> page links go to signup page
        # 'https://www.grandpasfuckteens.com' -> page links go to signup page
        # 'https://www.lust.com' -> page links go to signup page
        # 'https://www.squirtinglesbian.com' -> page links go to signup page
        # 'https://www.girlcore.com' -> Part of AdultTime API
        # 'https://www.puretaboo.com' -> Part of AdultTime API
        # 'https://www.shapeofbeauty.com' -> Part of AdultTime API
        # 'https://www.transexualangel.com' -> Part of AdultTime API (Previously "www.sheplayswithhercock.com"
        # 'https://www.cockchokingsluts.com',
        # 'https://www.johnleslie.com',

        #  Moved to AdultTime API
        # 'https://www.devilsgangbangs.com',
        # 'https://www.devilstgirls.com',
        # 'https://www.hairyundies.com',
        # 'https://www.lesbianfactor.com',
        # 'https://www.outofthefamily.com',
        # 'https://www.squirtalicious.com',

        # To do in another scraper, too different
        # 'https://www.ashleyfires.com'
        # 'http://christophsbignaturaltits.net/'
        # 'https://www.devilsfilmparodies.com/'
        # 'https://www.devonlee.com/'
        # 'https://www.dylanryder.com/'
        # 'https://www.jocksstudios.com/'
        # 'https://www.lanesisters.com/'
        # 'https://www.iconmale.com/'
        # 'https://www.menofmontreal.com/'
        # 'https://www.myteenoasis.com/'
        # 'https://www.openlife.com/'
        # 'https://www.sunnyleone.com/'
        # 'https://www.tsplayground.com/'
        # 'https://www.vivid.com/'
    ]

    selector_map = {
        'title': '//h1[@class="sceneTitle"]/text() | //h3[@class="sceneTitle"]/text() | //h1[@class="seo_h1"]/text() | //h1[@class="title"]/text() | //h3[@class="dvdTitle"]/text() | //h1[@class="dynamicContent"]/text()',
        'description': "//meta[@itemprop='description']/@content | //*[@class='p-desc']/text()",
        'date': '//div[@class="tlcSpecs"]/span[@class="tlcSpecsDate"]/span[@class="tlcDetailsValue"]/text() | //*[@class="updatedDate"]/text()',
        'image': '//meta[@name="twitter:image"]/@content | //video/@poster | //meta[@property="og:image"]/@content | //div[@class="module-content"]//img[contains(@src,"/previews/")]/@src',
        'performers': '//div[@class="sceneCol sceneColActors"]//a/text() | //p[@class="starringLinks"]//a/text() | //div[@class="sceneCol actors"]//a/text() | //div[@class="actors sceneCol"]//a/text() | //div[@class="sceneCol sceneActors"]//a/text() | //div[@class="pornstarName"]/text() | //a[@class="pornstarName"]/text() | //div[@id="slick_DVDInfoActorCarousel"]//a/text() | //div[@id="slick_sceneInfoPlayerActorCarousel"]//a/text() | //div[@id="slick_sceneInfoActorCarousel"]//a/text()',
        'tags': '//div[@class="sceneCol sceneColCategories"]/a/text()',
        'external_id': '(\\d+)/?$',
        'trailer': '',
    }

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            totalpages = re.search(r'\"nbPages\":(\d+)', response.text)
            if totalpages:
                totalpages = int(totalpages.group(1))
            else:
                totalpages = 99999

            if "analacrobats" in response.url:
                totalpages = 99999

            if 'page' in response.meta and response.meta['page'] < self.limit_pages and response.meta['page'] <= totalpages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                url = self.get_next_page_url(response.url, meta['page'])
                print('NEXT PAGE: ' + str(meta['page']) + "     (" + url + ")")
                yield scrapy.Request(url,
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        selectors = [
            "//div[@class='content']/ul[@class='sceneList']/li[contains(@class,'scene')]//a[contains(@class,'imgLink')]/@href",
            "//ul[@class='sceneList']/li[contains(@class,'sceneItem')]//a[contains(@class,'imgLink')]/@href",
            "//div[@class='tlcAllContentHolder']//div[@class='tlcContent']//div[contains(@class, 'tlcContent')]//div[contains(@class, 'tlcItem')]/a[not(contains(@href,'/pornstar/'))][1]/@href",
            "//div[@class='sceneContainer']/a/@href",
        ]

        if "fantasymassage" in response.url:
            scenes = response.xpath(
                "//div[@class='tlcAllContentHolder']//div[@class='tlcContent']//div[contains(@class, 'tlcContent')]//div[contains(@class, 'tlcItem')]")
        elif "blowpass" in response.url or "xempire" in response.url or "pridestudios" in response.url:
            scenes = response.xpath(
                '//h3[@class="sceneTitle"]')
        else:
            scenes = response.xpath(' | '.join(selectors)).getall()

        for scene in scenes:
            if "fantasymassage" in response.url:
                site = scene.xpath(
                    './/div[@class="tlcSourceSite"]/span/a/text()').get().strip()
                scene = scene.xpath('./a[1]/@href').get().strip()
            elif "blowpass" in response.url or "xempire" in response.url or "pridestudios" in response.url:
                site = scene.xpath(
                    './following-sibling::p[@class="fromSite"]/a/strong/text()').get().strip()
                scene = scene.xpath('./a[1]/@href').get().strip()

            if "fantasymassage" in response.url or "blowpass" in response.url or "xempire" in response.url or "pridestudios" in response.url and site:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': site.lower().replace(".com", "")})
            else:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = response.xpath(
            '//script[contains(text(),"picPreview")]').get()
        if image:
            image = re.search(
                'picPreview\":\"(.*?)\",',
                image).group(1).strip()
            image = image.replace('\\', '')

        if not image:
            image = self.process_xpath(
                response, self.get_selector_map('image')).get()

        if re.search(r'jpg\?', image):
            image = re.search(r'(.*jpg)\?', image).group(1)

        if image is not None:
            if "transform" in image:
                image_xpath = response.xpath('//meta[@name="twitter:image"]/@content').get()
                if image_xpath:
                    image = image_xpath.strip()
                else:
                    image = image.replace("https://transform.gammacdn.com/", "https://images02-openlife.gammacdn.com/")
            return self.format_link(response, image)

    def parse_scene(self, response):
        data = response.css('script:contains("dataLayer =")::text').get()
        data2 = response.xpath("//script[contains(text(), 'ScenePlayerId = \"player\"')] | //script[contains(text(), 'ScenePlayerId = \"scenePlayer\"')] | //script[contains(text(), 'sceneReleaseDate')]").get()
        data3 = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if data3:
            data3 = json.loads(data3)
            data3 = data3[0]
        else:
            data3 = []

        if len(chompjs.parse_js_object(data)):
            json_data = chompjs.parse_js_object(data)[0]

            jslde = JsonLdExtractor().extract(response.text)
            jsonlde = {}
            for obj in jslde:
                jsonlde.update(obj)

            item = SceneItem()

            if 'name' in jsonlde:
                item['title'] = jsonlde['name']
            elif 'sceneDetails' in json_data and 'sceneTitle' in json_data['sceneDetails']:
                item['title'] = json_data['sceneDetails']['sceneTitle']
            else:
                item['title'] = self.get_title(response)

            if item['title']:
                if ", scene #01" in item['title'].lower():
                    item['title'] = item['title'].replace(", Scene #01", "").replace(", scene #01", "")

            if 'sceneDetails' in json_data and 'sceneDescription' in json_data['sceneDetails']:
                item['description'] = json_data['sceneDetails']['sceneDescription']
            elif 'description' in jsonlde:
                item['description'] = jsonlde['description']
            else:
                item['description'] = self.get_description(response)

            if 'site' in response.meta:
                item['site'] = response.meta['site']
            elif 'productionCompany' in data3:
                item['site'] = data3['productionCompany']['name']
            elif 'siteName_pretty' in json_data:
                item['site'] = json_data['siteName_pretty']
            elif 'siteName' in json_data:
                item['site'] = json_data['siteName']

            if item['site']:
                item['site'] = match_site(item['site'])

            if not item['site']:
                item['site'] = self.get_site(response)

            if 'date' in response.meta:
                item['date'] = response.meta['date']
            elif 'dateCreated' in jsonlde and 'nudefightclub' not in response.url and '0000-00-00' not in jsonlde['dateCreated']:
                item['date'] = self.parse_date(jsonlde['dateCreated'], date_formats=['%Y-%m-%d']).isoformat()
            elif 'datePublished' in jsonlde and 'nudefightclub' not in response.url and '0000-00-00' not in jsonlde['datePublished']:
                item['date'] = self.parse_date(jsonlde['datePublished'], date_formats=['%Y-%m-%d']).isoformat()
            elif 'nudefightclub' in response.url:
                date1 = response.xpath(
                    '//div[@class="updatedDate"]/b/following-sibling::text()').get()
                item['date'] = self.parse_date(date1.strip()).isoformat()
            else:
                item['date'] = self.get_date(response)

            if not item['date']:
                item['date'] = self.get_date(response)

            if data2:
                date2 = re.search(r'sceneReleaseDate\":\"(\d{4}-\d{2}-\d{2})', data2)
                if date2:
                    date2 = date2.group(1)
                    date2 = self.parse_date(date2.strip(), date_formats=['%Y-%m-%d']).isoformat()
                    if item['date'] and date2 > item['date']:
                        item['date'] = date2

            if 'image' in response.meta:
                item['image'] = response.meta['image']
            else:
                item['image'] = self.get_image(response)

            item['image_blob'] = None

            if 'performers' in response.meta:
                item['performers'] = response.meta['performers']
            elif 'actor' in jsonlde:
                item['performers'] = list(
                    map(lambda x: x['name'].strip(), jsonlde['actor']))
            else:
                item['performers'] = self.get_performers(response)

            if 'tags' in response.meta:
                item['tags'] = response.meta['tags']
            elif 'keywords' in jsonlde:
                item['tags'] = jsonlde['keywords'].split(',')
            else:
                item['tags'] = self.get_tags(response)

            if item['tags']:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))

            if 'id' in response.meta:
                item['id'] = response.meta['id']
            else:
                item['id'] = self.get_id(response)

            if 'trailer' in response.meta:
                item['trailer'] = response.meta['trailer']
            else:
                item['trailer'] = self.get_trailer(response)

            item['url'] = self.get_url(response)

            if hasattr(self, 'network'):
                item['network'] = self.network
            else:
                item['network'] = self.get_network(response)

            if hasattr(self, 'parent'):
                item['parent'] = self.parent
            else:
                item['parent'] = self.get_parent(response)

            if item['title']:
                item['title'] = self.cleanup_title(item['title'])

            if item['description']:
                item['description'] = self.cleanup_description(item['description'])

            if item['id'] and item['title']:
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item

        else:
            super().parse_scene(response)

    def get_next_page_url(self, base, page):
        selector = '/en/videos/AllCategories/0/%s'

        if '21naturals' in base:
            selector = '/en/videos/%s'

        if '21sextreme' in base:
            selector = '/en/videos/updates/%s/categoryName/0/Pornstar/0'

        if 'activeduty' in base:
            selector = '/en/videos/latest/All-categories/0/All-soldiers/0/%s'

        if 'allgirlmassage' in base:
            selector = '/en/videos/page/%s'

        if 'analacrobats' in base:
            selector = '/en/videos/updates/%s/All/0/Pornstar/0'

        if 'blowpass' in base:
            selector = '/en/videos/blowpass/latest/All-Categories/0/All-Pornstars/0/%s'

        if 'bskow' in base or 'lexingtonsteele' in base:
            selector = '/en/videos/updates/%s/All/0/Pornstar/0'

        matches = ['bushybushy', 'bigfatcreampie', 'christophclarkonline', 'cumshotoasis',
                   'currycreampie', 'famedigital', 'gapingangels', 'grannyghetto', 'hairyundies',
                   'jakemalone', 'joeysilvera', 'nachovidalhardcore', 'povblowjobs', 'povthis',
                   'squirtalicious', 'strapattackers', 'transsexualroadtrip']
        if any(x in base for x in matches):
            selector = '/en/All/scenes/0/latest/%s'

        if 'buttman' in base or 'devilsgangbangs' in base or 'lewood' in base or 'tittycreampies' in base:
            selector = '/en/scenes/All/0/%s'

        if 'devilsfilm' in base:
            selector = '/en/scenes/AllCategories/0/%s'

        if 'devilstgirls' in base:
            selector = '/en/videos/updates/%s/All/0/Actor/0'

        if 'dpfanatics' in base:
            selector = '/en/videos/All-Categories/0/All-Pornstars/0/latest/%s'

        if 'falconstudios' in base:
            selector = '/en/videos/latest/All+Categories/0/All+Models/0/All+Dvds/0/Falcon+Studios//%s'

        if 'fantasymassage' in base:
            selector = '/en/videos/AllCategories/0/Actor/0/updates/%s'

        if 'footsiebabes' in base or 'nudefightclub' in base:
            selector = '/en/videos/All-Categories/0/All-Pornstars/0/latest/%s'

        if 'girlfriendsfilms' in base:
            selector = '/en/videos/all-series/0/all-categories/0/all-pornstars/0/latest/%s'

        if 'girlsandstuds' in base:
            selector = '/en/allfilms/latest/%s'

        if 'hothouse' in base:
            selector = '/en/videos/latest/All-Studios/0/All-categories/0/All-stars/0/All-movies/0/%s'

        if 'immorallive' in base:
            selector = '/en/videos/All-Categories/0/All-Pornstars/0/All/0/%s'

        if 'jaysinxxx' in base or 'jonnidarkkoxxx' in base or 'pantypops' in base:
            selector = '/en/scenes/All/0/latest/%s'

        if 'lesbianfactor' in base:
            selector = '/en/All/scenes/latest/%s'

        if 'maledigital' in base:
            selector = '/en/videos/latest/All-Studios/0/All-Categories/0/%s'

        if 'maskurbate' in base:
            selector = '/en/videos/latest/All+Categories/0/All+Models/0/%s'

        if 'milkingtable' in base or 'soapymassage' in base or 'trickyspa' in base:
            selector = '/en/videos/updates/0/All/0/Actor/%s'

        if 'mommysgirl' in base or 'girlstryanal' in base or 'webyoung' in base:
            selector = '/en/videos/updates/All-Categories/0/All-Pornstars/0/%s'

        if 'onlyteenblow' in base or 'mommyblowsbest' in base:
            selector = '/en/scenes/updates/0/Category/0/Actor/%s'

        if 'outofthefamily' in base:
            selector = '/en/videos/latest/All-Categories/0/All-Pornstars/0/All-Dvds/0/%s'

        if 'peternorth' in base:
            selector = '/en/videos/All-Categories/0/All-Pornstars/0/All-Dvds/0/latest/%s'

        if 'prettydirty' in base:
            selector = '/en/videos/updates/%s/Category/0/Pornstar/0'

        if 'pridestudios' in base:
            selector = '/en/videos/pridestudios/latest/All+Categories/0/All+Models/0/%s'

        if 'ragingstallion' in base:
            selector = '/en/scenes/All+Studios/0/%s'

        if 'roccosiffredi' in base or 'burningangel' in base:
            selector = '/en/videos/latest/%s'

        if 'squirtingorgies' in base:
            selector = '/en/latest/%s#main'

        if 'seemyflixxx' in base:
            selector = '/en/videos/All-Categories/0/All-Pornstars/0/0/All-Dvds/%s'

        if 'tsfactor' in base:
            selector = '/en/videos/updates/%s/All/0/Pornstar/0'

        if 'xempire' in base:
            selector = '/en/videos/xempire/latest/%s'

        returnurl = selector % page
        return self.format_url(base, returnurl)

    def get_site(self, response):

        if 'site' in response.meta:
            return response.meta['site']

        if response.xpath('//a[@href="/en"]/@title'):
            return response.xpath('//a[@href="/en"]/@title').get().strip()

        if response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()'):
            return response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()').get().strip().split('.')[0]

        if response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()'):
            return response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()').get().strip().split('.')[0]

        if response.xpath('//meta[@name="twitter:domain"]'):
            return response.xpath(
                '//meta[@name="twitter:domain"]/@content').get().replace('www.', '').split('.')[0]

        if response.xpath(
                '//div[@class="siteLink"]//a/text() | //div[@id="videoInfoTop"]//a/text()'):
            return response.xpath(
                '//div[@class="siteLink"]//a/text() | //div[@id="videoInfoTop"]//a/text()').get().strip()

        if response.css('span.siteNameSpan') is not None:
            return response.css('span.siteNameSpan::text').get()

        return tldextract.extract(response.url).domain

    def get_date(self, response):
        matches = [
            'christophclarkonline',
            'gapingangels',
            'jakemalone',
            'joeysilvera',
            'lewood',
            'nachovidalhardcore',
            'povblowjobs',
            'tittycreampies']
        if any(x in response.url for x in matches):
            date = response.xpath(
                '//script[contains(text(),"sceneReleaseDate")]').get()
            date = re.search(
                'sceneReleaseDate\":\"(\\d{4}-\\d{2}-\\d{2})',
                date).group(1)
        else:
            date = self.process_xpath(response, self.get_selector_map('date')).getall()
            if len(date) > 1:
                for daterow in date:
                    datetemp = ""
                    daterow.replace('Released:', '').replace('Added:', '').rstrip().strip()
                    if re.match('(\\d{4}-\\d{2}-\\d{2})', daterow):
                        datetemp = re.search('(\\d{4}-\\d{2}-\\d{2})', daterow).group(1).strip()
                    elif re.match('(\\d{2}-\\d{2}-\\d{4})', daterow):
                        datetemp = re.search('(\\d{2}-\\d{2}-\\d{4})', daterow).group(1).strip()
                    if not datetemp:
                        date = datetemp.strip()

        matches = ['21sextreme']
        if not date or any(x in response.url for x in matches):
            date = response.xpath(
                '//script[contains(text(),"sceneReleaseDate")]').getall()
            if len(date) > 1:
                for daterow in date:
                    datetemp = re.search('sceneReleaseDate\":\"(\\d{4}-\\d{2}-\\d{2})', daterow)
                    if datetemp:
                        datetemp = datetemp.group(1)
                        if datetemp:
                            date = datetemp.strip()

        if not date:
            date = response.xpath(
                '//div[@class="updatedDate"]/b/following-sibling::text()').get()

        if not date:
            date = response.xpath('//div[@class="updatedDate"]/b/following-sibling::text()').get()

        return self.parse_date(date.strip(), date_formats=['%m-%d-%Y', '%Y-%m-%d']).isoformat()

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get().strip()

        return title

    def get_performers(self, response):
        matches = [
            'christophclarkonline',
            'gapingangels',
            'jakemalone',
            'joeysilvera',
            'lewood',
            'povblowjobs']
        if any(x in response.url for x in matches):
            performer = response.xpath(
                '//meta[@name="description"]/@content').get()
            if "starring" in performer.lower():
                performer = re.search(
                    'starring\\ (.*?)\\ in', performer).group(1)
                if "," in performer:
                    performers = performer.split(",")
                else:
                    performers = [performer]
            performers = list(map(str.strip, performers))
        elif 'nachovidalhardcore' in response.url:
            return []
        else:
            performers = self.process_xpath(
                response, self.get_selector_map('performers')).getall()
        if performers:
            performers = list(map(str.strip, performers))
            return list(map(lambda x: x.strip(), performers))
        return []

    def get_tags(self, response):
        matches = [
            'christophclarkonline',
            'gapingangels',
            'jakemalone',
            'joeysilvera',
            'lewood',
            'povblowjobs']
        if any(x in response.url for x in matches):
            tag = response.xpath('//meta[@name="description"]/@content').get()
            if "starring" in tag.lower():
                if " last updated " in tag:
                    tag = re.search(
                        '\\ in\\ (.*?)\\ last\\ updated',
                        tag.lower()).group(1)
                else:
                    tag = re.search('\\ in\\ (.*?)\\ updated', tag).group(1)
                if tag:
                    if "," in tag:
                        tags = tag.split(",")
                    else:
                        tags = [tag]

        elif 'nachovidalhardcore' in response.url:
            return []
        else:
            if self.get_selector_map('tags'):
                tags = self.process_xpath(
                    response, self.get_selector_map('tags')).getall()
        if tags:
            tags = list(map(str.strip, tags))
            if "Newest" in tags:
                tags.remove("Newest")
            if "newest" in tags:
                tags.remove("newest")
            return list(map(lambda x: x.strip(), tags))
        return []

    def get_id(self, response):
        if "lexingtonsteele" in response.url:
            search = re.search(
                '\\/video\\/(\\d*)\\/',
                response.url,
                re.IGNORECASE)
        else:
            search = re.search(self.get_selector_map(
                'external_id'), response.url, re.IGNORECASE)
        return search.group(1)

    def get_parent(self, response):

        tld = tldextract.extract(response.url).domain
        parent = match_site(tld)

        if "girlstryanal" in response.url or "webyoung" in response.url:
            return "Girlsway"

        if "mommysgirl" in response.url:
            return "Adult Time"

        return parent
