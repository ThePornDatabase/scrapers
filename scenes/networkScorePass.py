import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
import tldextract


def match_site(argument):
    match = {
        '18eighteen': "18Eighteen",
        '40somethingmag': "40Somethingmag",
        '50plusmilfs': "50Plus MILFs",
        '60plusmilfs': "60Plus MILFs",
        'ashleysageellison': "Ashley Sage Ellison",
        'autumn-jade': "Autumn-Jade",
        'bigboobbundle': "Big Boob Bundle",
        'bigboobspov': "Big Boobs POV",
        'bigtitangelawhite': "Big Tit Angela White",
        'bigtithitomi': "Big Tit Hitomi",
        'bigtithooker': "Big Tit Hooker",
        'bigtitterrynova': "Big Tit Terry Nova",
        'bigtitvenera': "Big Tit Venera",
        'bonedathome': "Boned At Home",
        'bootyliciousmag': "Bootyliciousmag",
        'bustyangelique': "Busty Angelique",
        'bustyarianna': "Busty Arianna",
        'bustydustystash': "Busty Dusty Stash",
        'bustyinescudna': "Busty Ines Cudna",
        'bustykellykay': "Busty Kelly Kay",
        'bustykerrymarie': "Busty Kerry Marie",
        'bustymerilyn': "Busty Merilyn",
        'bustyoldsluts': "Busty Old Sluts",
        'chloesworld': "Chloes World",
        'christymarks': "Christy Marks",
        'codivorexxx': "Codi Vore XXX",
        'creampieforgranny': "Creampie For Granny",
        'daylenerio': "Daylene Rio",
        'desiraesworld': "Desiraes World",
        'evanottyvideos': "Eva Notty Videos",
        'feedherfuckher': "Feed Her, Fuck Her",
        'flatandfuckedmilfs': "Flat And Fucked MILFs",
        'grannygetsafacial': "Granny Gets a Facial",
        'grannylovesbbc': "Granny Loves BBC",
        'grannylovesyoungcock': "Granny Loves Young Cock",
        'homealonemilfs': "Home Alone MILFs",
        'ibonedyourmom': "I Boned Your Mom",
        'joanabliss': "Joana Bliss",
        'leannecrowvideos': "Leanne Crow Videos",
        'legsex': "Leg Sex",
        'linseysworld': "Linseys World",
        'megatitsminka': "Megatits Minka",
        'mickybells': "Micky Bells",
        'milfbundle': "MILF Bundle",
        'milfthreesomes': "MILF Threesomes",
        'milftugs': "MILF Tugs",
        'nataliefiore': "Natalie Fiore",
        'naughtyfootjobs': "Naughty Footjobs",
        'naughtymag': "Naughtymag",
        'naughtytugs': "Naughty Tugs",
        'nicolepeters': "Nicole Peters",
        'oldhornymilfs': "Old Horny MILFs",
        'pickinguppussy': "Picking Up Pussy",
        'pornmegaload': "PornMegaLoad",
        'sarennasworld': "Sarennas World",
        'scoreland': "Scoreland",
        'scorevideos': "Score Videos",
        'sharizelvideos': "Sharizel Videos",
        'silversluts': "Silver Sluts",
        'stacyvandenbergboobs': "Stacy Vandenberg Boobs",
        'tawny-peaks': "Tawny-Peaks",
        'tiffany-towers': "Tiffany-Towers",
        'titsandtugs': "Tits And Tugs",
        'tnatryouts': "TnA Tryouts",
        'valoryirene': "Valory Irene",
        'xlgirls': "XL Girls",
        'yourmomlovesanal': "Your Mom Loves Anal",
        'yourmomsgotbigtits': "Your Moms Got Big Tits",
        'yourwifemymeat': "Your Wife, My Meat",
    }
    return match.get(argument, argument)


def match_page_scenepath(argument):
    match = {
        'bigboobspov': "/big-boob-videos/?page=%s",
        'bigtithooker': "/big-boob-videos/?page=%s",
        'bonedathome': "/amateur-videos/?page=%s",
        'feedherfuckher': "/bbw-videos/?page=%s",
        'milfbundle': "/milf-scenes/?page=%s",
        'naughtyfootjobs': "/foot-job-videos/?page=%s",
        'naughtytugs': "/hand-job-videos/?page=%s",
        'pickinguppussy': "/xxx-teen-videos/?page=%s",
        'pornmegaload': "/hd-porn-scenes/?page=%s",
        'titsandtugs': "/big-boob-videos/?page=%s",
        'tnatryouts': "/xxx-teen-videos/?page=%s",
    }
    return match.get(argument, '/videos/?page=%s')


class ScorePassSpider(BaseSceneScraper):
    name = 'ScorePass'
    network = 'ScorePass'

    start_urls = [
        'https://www.bigboobspov.com',
        'https://www.bigtithooker.com',
        'https://www.bonedathome.com',
        'https://www.chloesworld.com',
        'https://www.christymarks.com',
        'https://www.feedherfuckher.com',
        'https://www.linseysworld.com',
        'https://www.naughtyfootjobs.com',
        'https://www.naughtytugs.com',
        'https://www.pickinguppussy.com',
        'https://www.titsandtugs.com',
        'https://www.tnatryouts.com',


        # -----------------------------------
        # Index Sites Below
        # -----------------------------------


        'https://www.bigboobbundle.com',
        # -----------------------------------
        # 'https://www.ashleysageellison.com',
        # 'https://www.autumn-jade.com',
        # 'https://www.bigtitangelawhite.com',
        # 'https://www.bigtithitomi.com',
        # 'https://www.bigtitterrynova.com',
        # 'https://www.bigtitvenera.com',
        # 'https://www.bustyangelique.com',
        # 'https://www.bustyarianna.com',
        # 'https://www.bustydustystash.com',
        # 'https://www.bustyinescudna.com',
        # 'https://www.bustykellykay.com',
        # 'https://www.bustykerrymarie.com',
        # 'https://www.bustymerilyn.com',
        # 'https://www.codivorexxx.com',
        # 'https://www.daylenerio.com',
        # 'https://www.desiraesworld.com',
        # 'https://www.evanottyvideos.com',
        # 'https://www.joanabliss.com',
        # 'https://www.leannecrowvideos.com',
        # 'https://www.megatitsminka.com',
        # 'https://www.mickybells.com',
        # 'https://www.nataliefiore.com',
        # 'https://www.nicolepeters.com',
        # 'https://www.sarennasworld.com',
        # 'https://www.sharizelvideos.com',
        # 'https://www.stacyvandenbergboobs.com',
        # 'https://www.tawny-peaks.com',
        # 'https://www.tiffany-towers.com',
        # 'https://www.valoryirene

        'https://www.milfbundle.com',
        # -----------------------------------
        # 'https://www.bustyoldsluts.com',
        # 'https://www.creampieforgranny.com',
        # 'https://www.flatandfuckedmilfs.com',
        # 'https://www.grannygetsafacial.com',
        # 'https://www.grannylovesbbc.com',
        # 'https://www.grannylovesyoungcock.com',
        # 'https://www.homealonemilfs.com',
        # 'https://www.ibonedyourmom.com',
        # 'https://www.milfthreesomes.com',
        # 'https://www.milftugs.com',
        # 'https://www.oldhornymilfs.com',
        # 'https://www.silversluts.com',
        # 'https://www.yourmomlovesanal.com',
        # 'https://www.yourmomsgotbigtits.com',
        # 'https://www.yourwifemymeat.com',

        'https://www.pornmegaload.com',
        # -----------------------------------
        # 'https://www.18eighteen.com',
        # 'https://www.40somethingmag.com',
        # 'https://www.50plusmilfs.com',
        # 'https://www.60plusmilfs.com',
        # 'https://www.bigtithooker.com',
        # 'https://www.bootyliciousmag.com',
        # 'https://www.legsex.com',
        # 'https://www.mickybells.com',
        # 'https://www.naughtymag.com',
        # 'https://www.pornmegaload.com',
        # 'https://www.scoreland.com',
        # 'https://www.scorevideos.com',
        # 'https://www.xlgirls.com'
    ]

    selector_map = {
        'title': "#videos_page-page h1::text",
        'description': "//meta[@itemprop='description']/@content | //*[@class='p-desc']/text()",
        'date': "//div[contains(@class, 'stat')]//span[contains(text(),'Date')]/following-sibling::span/text()",
        'image': '//meta[@property="og:image"]/@content',
        'performers': "//div[contains(@class, 'stat')]//span[contains(text(),'Featuring')]/following-sibling::span//text()",
        'tags': "//a[contains(@href,'videos-tag')]/text()",
        'external_id': r'/(\d+)',
        'trailer': '//div[@class="pos-rel"]//video/source/@src',
        'pagination': 'xxx-teen-videos/?page=%s'
    }

    def get_scenes(self, response):
        if "pornmegaload" in response.url:
            scenes = response.xpath('//div[@class="info h-100 p-2 p-md-4"]')
        elif "tnatryouts" in response.url:
            scenes = response.xpath('//div[@class="box group"]/div[@class="info"]/a/@href')
        elif "titsandtugs" in response.url or "bigboobspov" in response.url or "bigtithooker" in response.url:
            scenes = response.xpath('//div[@class="box group"]/div[@class="cell"]/div/a/@href')
        elif "bonedathome" in response.url or "feedherfuckher" in response.url or "naughtytugs" in response.url or "pickinguppussy" in response.url:
            scenes = response.xpath('//div[@class="box group"]/div[@class="info"]/a/@href')
        elif "naughtyfootjobs" in response.url:
            scenes = response.xpath('//div[@class="box group"]/div[@class="item-img row"]/a/@href')
        else:
            scenes = response.css(".video").css('a').xpath("@href")
        for scene in scenes:
            if "pornmegaload" in response.url:
                site = scene.xpath('./div[@class="site"]/img/@alt').get()
                if site:
                    site = site.strip()
                    site = match_site(site)
                scene = scene.xpath('./div/div[contains(@class,"i-title")]/a/@href').get()
            else:
                scene = scene.get()

            if re.match(r'.*/\?nats=', scene):
                scene = re.search(r'(.*)/\?nats=', scene).group(1)
            if "step=signup" not in scene and "join." not in scene:
                if "pornmegaload" in response.url and site:
                    yield scrapy.Request(url=scene, callback=self.parse_scene, meta={'site': site})
                else:
                    yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        parsed_uri = tldextract.extract(base)
        scene_path = match_page_scenepath(parsed_uri.domain)
        return self.format_url(base, scene_path % page)

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if not title:
            title = response.xpath('//h2[@class="subtitle"]/text()').get()
        if not title:
            title = response.xpath('//h2[@class="title"]/span/text()').get()
        if not title:
            title = response.xpath('//main/div/section/div[@class="row"]/div/h1/text()').get()  # Milfbundle

        if "christymarks" in response.url or "linseysworld" in response.url:
            sitetitle = response.xpath('//h1[@class="m-title row"]/text()').get()
            if sitetitle:
                if "»" in sitetitle:
                    sitetitle = re.search(r'»\s+?(.*)', sitetitle).group(1)
                title = sitetitle.strip()

        if not title:
            title = response.xpath('//meta[@property="og:title"]/@content').get()
        if not title:
            title = response.xpath('//meta[@name="twitter:title"]/@content').get()

        if title.startswith(" - "):
            title = title[3:]

        if title:
            return self.cleanup_title(title)
        return ''

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if not date:
            date = response.xpath('//div[@class="desc row"]/following-sibling::div[@class="date"][1]/text()').get()
        if not date:
            date = response.xpath('//div[contains(@class, "stat")]//span[contains(text(),"Date")]/following-sibling::text()').get()
        if date:
            return self.parse_date(date.strip()).isoformat()
        return self.parse_date('today').isoformat()

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if not trailer:
                trailer = response.xpath('//div[@class="vt-mssg"]/a/@href').get()
            if trailer:
                if trailer.startswith("//"):
                    trailer = "https:" + trailer
                return trailer.strip()
        return ''

    def get_performers(self, response):
        if "bigboobspov" in response.url:
            performerlist = response.xpath('//div[@class="stat"]/span[contains(text(),"Featuring")]/following-sibling::text()').get()
            if performerlist:
                if " and " in performerlist:
                    performers = performerlist.split(" and ")
                else:
                    performers = [performerlist.strip()]
        else:
            performers = self.process_xpath(
                response, self.get_selector_map('performers')).getall()
        if not performers:
            performers = response.xpath('//span[contains(text(),"Featuring")]/following-sibling::a/text()').getall()
        if performers:
            performers = list(map(lambda x: x.replace(",", "").strip(), performers))
            performers = [x for x in performers if x != 'and' and x != '']
            return performers
        if "linseysworld" in response.url:
            return ['Linsey McKenzie']
        if "chloesworld" in response.url:
            return ['Chloe Vevrier']
        if "christymarks" in response.url:
            return ['Christy Marks']
        return []

    def get_site(self, response):
        site = ""
        if "milfbundle" in response.url or "bigboobbundle" in response.url:
            canonlink = response.xpath('//link[@rel="canonical"]/@href').get()
            if not canonlink:
                canonlink = response.xpath('//meta[@property="og:url"]/@content').get()
            if canonlink:
                canondomain = tldextract.extract(canonlink).domain
                if canondomain:
                    site = canondomain.strip()
        subsite = response.xpath('//div[@class="mb-3"]/a[contains(@href,"videos-category")]/text()').get()
        if subsite:
            site = subsite.strip()

        if not site:
            site = tldextract.extract(response.url).domain

        site = match_site(site)
        return site

    def get_description(self, response):
        if 'description' not in self.get_selector_map():
            return ''

        description = self.process_xpath(
            response, self.get_selector_map('description'))
        if description:
            if len(description) > 1:
                description = description.getall()
                description = " ".join(description)
            else:
                description = description.get()

        description2 = response.xpath('//div[@class="desc frame"]/text()').get()
        if description2:
            description2 = description2.strip()
            if len(description2) > len(description):
                description = description2

        if description is not None:
            return self.cleanup_description(description)
        return ""

    def get_parent(self, response):
        parent = tldextract.extract(response.url).domain
        parent = match_site(parent)
        return parent
