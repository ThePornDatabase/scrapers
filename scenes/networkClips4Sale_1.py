import re
import string
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClips4Sale_1Spider(BaseSceneScraper):

    sites = [
        ['Clips4Sale', 'Aaliyah Taylors Fetish', 'Aaliyah Taylors Fetish', '70866', 'aaliyah-taylor-s-fetish'],
        ['Clips4Sale', 'Addie Juniper Fetish Clips', 'Addie Juniper Fetish Clips', '4502', 'addie-juniper-fetish-clips'],
        ['Clips4Sale', 'Alex Mack Clip Store', 'Alex Mack Clip Store', '143621', 'alex-mack-clip-store'],
        ['Clips4Sale', 'Alexis Playground', 'Alexis Playground', '33899', 'milf-alexis-rain-s-playground'],
        ['Clips4Sale', 'Aaliyah Taylor', 'Aliyah Taylors Fetish', '70866', 'aaliyah-taylor-s-fetish'],
        ['Clips4Sale', 'Jon Woods', 'American Damsels', '6571', 'american-damsels-by-jon-woods'],
        ['Clips4Sale', 'American Mean Girls', 'American Mean Girls', '32364', 'american-mean-girl'],
        ['Clips4Sale', 'Andrea Rosus Kinky Explorations', 'Andrea Rosus Kinky Explorations', '75279', 'andrea-rosu-s-kinky-explorations'],
        ['Clips4Sale', 'Angel the Dreamgirl', 'Angel the Dreamgirl', '68591', 'angel-the-dreamgirl'],
        ['Clips4Sale', 'Angel The Dreamgirl', 'Angel The Dreamgirl', '68591', 'angel-the-dreamgirl'],
        ['Clips4Sale', 'AngryHJs', 'AngryHJs', '137383', 'angryhjs'],
        ['Clips4Sale', 'Ashley Fires Fetish Clips', 'Ashley Fires Fetish Clips', '5177', 'ashley-fires-fetish-clips'],
        ['Clips4Sale', 'Asian Gypsy Snow', 'Asian Gypsy Snow', '74789', 'feet-4-dinner'],
        ['Clips4Sale', 'AstroDomina', 'AstroDomina', '56587', 'astrodomina'],
        ['Clips4Sale', 'Bareback Studios', 'Bareback Studios', '35625', 'bare-back-studios'],
        ['Clips4Sale', 'Bareback Studios', 'Bareback Studios', '35625', 'bare-back-studios'],
        ['Clips4Sale', 'Barely Legal Foot Jobs', 'Barely Legal Foot Jobs', '40521', 'barely-legal-foot-jobs'],
        ['Clips4Sale', 'BlackCow Video', 'BlackCow Video', '15814', 'blackcow-video'],
        ['Clips4Sale', 'Borderland Bound', 'Borderland Bound', '64171', 'borderland-bound-'],
        ['Clips4Sale', 'Brat Attack', 'Brat Attack', '83427', 'brat-attack'],
        ['Clips4Sale', 'Bratty Bunny', 'Bratty Bunny', '35587', 'Bratty-Bunny'],
        ['Clips4Sale', 'Bratty Foot Girls', 'Bratty Foot Girls', '40537', 'bratty-foot-girls'],
        ['Clips4Sale', 'BrokeAmateurs Clips Store', 'BrokeAmateurs Clips Store', '15842', 'brokeamateurs-clips-store'],
        ['Clips4Sale', 'Cory Chase', 'Chase Water Babes', '32587', 'chase-water-babes'],
        ['Clips4Sale', 'Clips4Sale: Alicia Silvers 1111 Customs', 'Clips4Sale: Alicia Silvers 1111 Customs', '151073', 'alicia-silvers-1111-customs'],
        ['Clips4Sale', 'Clips4Sale: Alluras Addictions', 'Clips4Sale: Alluras Addictions', '57829', 'allura-s-addictions'],
        ['Clips4Sale', 'Clips4Sale: Alysa Nylon', 'Clips4Sale: Alysa Nylon', '270421', 'alysa-nylon'],
        ['Clips4Sale', 'Clips4Sale: Ama Rios Playground', 'Clips4Sale: Ama Rios Playground', '153417', 'ama-rios-playground'],
        ['Clips4Sale', 'Clips4Sale: AnikaFall', 'Clips4Sale: AnikaFall', '123317', 'anikafall'],
        ['Clips4Sale', 'Clips4Sale: Annabelle Rogers', 'Clips4Sale: Annabelle Rogers', '140743', 'annabelle-rogers-taboo'],
        ['Clips4Sale', 'Clips4Sale: Ashley Albans Fetish Fun', 'Clips4Sale: Ashley Albans Fetish Fun', '71774', 'ashley-alban-s-fetish-fun'],
        ['Clips4Sale', 'Clips4Sale: Asiana Starr Bondage', 'Clips4Sale: Asiana Starr Bondage', '52109', 'asiana-starr-bondage'],
        ['Clips4Sale', 'Clips4Sale: BBW Casey', 'Clips4Sale: BBW Casey', '138831', 'bbw-casey'],
        ['Clips4Sale', 'Clips4Sale: BBW CHLOE', 'Clips4Sale: BBW CHLOE', '134447', 'bbw-chloe'],
        ['Clips4Sale', 'Clips4Sale: BBW Feedee Bonnies clips', 'Clips4Sale: BBW Feedee Bonnies clips', '72633', 'bbw-feedee-bonnie-s-clips'],
        ['Clips4Sale', 'Clips4Sale: BBWLayla', 'Clips4Sale: BBWLayla', '181173', 'bbwlayla'],
        ['Clips4Sale', 'Clips4Sale: Bella Bates', 'Clips4Sale: Bella Bates', '187465', 'bella-bates'],
        ['Clips4Sale', 'Clips4Sale: Bettie Bondage', 'Clips4Sale: Bettie Bondage', '27897', 'bettie-bondage'],
        ['Clips4Sale', 'Clips4Sale: Bitch World Femdom', 'Clips4Sale: Bitch World Femdom', '66613', 'bitch-world-femdom'],
        ['Clips4Sale', 'Clips4Sale: BlowRayne', 'Clips4Sale: BlowRayne', '175947', 'blowrayne'],
        ['Clips4Sale', 'Clips4Sale: Bondage Junkies', 'Clips4Sale: Bondage Junkies', '47664', 'bondagejunkies-clips'],
        ['Clips4Sale', 'Clips4Sale: Bondage Land', 'Clips4Sale: Bondage Land', '221869', 'TeamJacky'],
        ['Clips4Sale', 'Clips4Sale: BondageTea', 'Clips4Sale: BondageTea', '187753', '187753-bondagetea'],
        ['Clips4Sale', 'Clips4Sale: Bossy Girls', 'Clips4Sale: Bossy Girls', '107974', 'bossy-girls'],
        ['Clips4Sale', 'Clips4Sale: Bound To Be GAGGED', 'Clips4Sale: Bound To Be GAGGED', '170465', 'bound-to-be-gagged'],
        ['Clips4Sale', 'Clips4Sale: Bound to Orgasm', 'Clips4Sale: Bound to Orgasm', '122831', 'bound-to-orgasm'],
        ['Clips4Sale', 'Clips4Sale: Bound2Burst', 'Clips4Sale: Bound2Burst', '8916', 'bound2burst-female-desperation'],
        ['Clips4Sale', 'Clips4Sale: Brat Princess 2', 'Clips4Sale: Brat Princess 2', '21233', 'brat-princess-2'],
        ['Clips4Sale', 'Clips4Sale: Bratty Foot Girls', 'Clips4Sale: Bratty Foot Girls', '40537', 'bratty-foot-girls'],
        ['Clips4Sale', 'Clips4Sale: Brianna and Jae Fat Fetish Clips', 'Clips4Sale: Brianna and Jae Fat Fetish Clips', '111076', 'brianna-and-jae-fat-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: Calisas Bondage Diaries', 'Clips4Sale: Calisas Bondage Diaries', '182907', 'calisas-bondage-diaries'],
        ['Clips4Sale', 'Clips4Sale: CapturedCurves', 'Clips4Sale: CapturedCurves', '226795', 'capturedcurves'],
        ['Clips4Sale', 'Clips4Sale: Chaos Clips', 'Clips4Sale: Chaos Clips', '53471', 'chaos-clips'],
        ['Clips4Sale', 'Clips4Sale: Chronicles of Mlle Fanchette', 'Clips4Sale: Chronicles of Mlle Fanchette', '56793', 'chronicles-of-mlle-fanchette-'],
        ['Clips4Sale', 'Clips4Sale: CinematicKink', 'Clips4Sale: CinematicKink', '215717', 'cinematickink'],
        ['Clips4Sale', 'Clips4Sale: Club Steffi', 'Clips4Sale: Club Steffi', '32047', 'club-steffi'],
        ['Clips4Sale', 'Clips4Sale: Club Stiletto FemDom', 'Clips4Sale: Club Stiletto FemDom', '896', 'club-stiletto-femdom'],
        ['Clips4Sale', 'Clips4Sale: CreamPuff', 'Clips4Sale: CreamPuff', '104420', 'creampuff'],
        ['Clips4Sale', 'Clips4Sale: Crystal Knight', 'Clips4Sale: Crystal Knight', '96651', 'crystal-knight'],
        ['Clips4Sale', 'Clips4Sale: Daddys Dirty Girls', 'Clips4Sale: Daddys Dirty Girls', '54583', 'daddys-dirty-girls'],
        ['Clips4Sale', 'Clips4Sale: Dahlia Fallon', 'Clips4Sale: Dahlia Fallon', '95649', 'dahlia-fallon'],
        ['Clips4Sale', 'Clips4Sale: Darling Kiyomi', 'Clips4Sale: Darling Kiyomi', '189285', 'darling-kiyomi'],
        ['Clips4Sale', 'Clips4Sale: DestinyBBW AND FRIENDS FETISH CLIPS', 'Clips4Sale: DestinyBBW AND FRIENDS FETISH CLIPS', '5986', 'destinybbw-and-friends-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: Diary of a growing girl', 'Clips4Sale: Diary of a growing girl', '81419', 'big-cutie-margot'],
        ['Clips4Sale', 'Clips4Sale: Entrancement', 'Clips4Sale: Entrancement', '12956', 'entrancement'],
        ['Clips4Sale', 'Clips4Sale: Evans Feet', 'Clips4Sale: Evans Feet', '229967', 'evansfeet'],
        ['Clips4Sale', 'Clips4Sale: Femdom Delilah', 'Clips4Sale: Femdom Delilah', '254391', 'femdom-delilah'],
        ['Clips4Sale', 'Clips4Sale: Fetishmindsproductions', 'Clips4Sale: Fetishmindsproductions', '118228', 'fetishmindsproductions'],
        ['Clips4Sale', 'Clips4Sale: Filthy Fuckers', 'Clips4Sale: Filthy Fuckers', '142821', 'filthy-fuckers'],
        ['Clips4Sale', 'Clips4Sale: FLEX-RX', 'Clips4Sale: FLEX-RX', '66443', 'flex-rx'],
        ['Clips4Sale', 'Clips4Sale: Foot Tongue Mouth and Vore', 'Clips4Sale: Foot Tongue Mouth and Vore', '119032', 'foot-tongue-mouth-and-vore'],
        ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: Foxxx Studios', '81539', 'princess-sasha-foxxx-'],
        ['Clips4Sale', 'Clips4Sale: God Slavena', 'Clips4Sale: God Slavena', '155741', 'god-slavena'],
        ['Clips4Sale', 'Clips4Sale: Goddess Alessa', 'Clips4Sale: Goddess Alessa', '178303', 'goddess-alessa'],
        ['Clips4Sale', 'Clips4Sale: Goddess LaVey', 'Clips4Sale: Goddess LaVey', '119180', 'goddess-lavey']
    ]

    name = 'Clips4Sale_1'

    url = 'https://www.clips4sale.com'

    selector_map = {
        'external_id': r'studio\/.*\/(\d+)\/',
        'pagination': ''
    }

    async def start(self):
        link = self.url
        meta = {}
        for site in self.sites:
            meta['network'] = site[0]
            meta['parent'] = site[1]
            meta['storedsite'] = site[2]
            meta['store'] = site[3]
            meta['storename'] = site[4]
            meta['page'] = self.page

            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['store'], meta['storename']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['store'], meta['storename']), callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, store, storename):
        # ~ url = f"https://www.clips4sale.com/studio/{store}/{storename}/Cat0-AllCategories/Page{str(page)}/C4SSort-added_at/Limit24/?onlyClips=true&_data=routes%2Fstudio.$id_.$studioSlug.$"
        # ~ url = f"https://www.clips4sale.com/en/studio/v/Cat0-AllCategories/Page{str(page)}/C4SSort-added_at/Limit24/?onlyClips=true&_data=routes%2F($lang).studio.$id_.$studioSlug.$"
        url = f"https://www.clips4sale.com/en/studio/{store}/{storename}/Cat0-AllCategories/Page{str(page)}/C4SSort-added_at/Limit24?onlyClips=true&storeSimilarClips=false&_data=routes%2F%28%24lang%29.studio.%24id_.%24studioSlug.%24"
        return url

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['clips']
        for scene in jsondata:
            # ~ print(scene)
            # ~ print()
            # ~ print()
            item = self.init_scene()
            if scene['title']:
                item['title'] = self.cleanup_title(scene['title'])
                item['id'] = scene['clipId']
                if item['id'] == "17694316":
                    item['title'] = "Buzzed"
                if "description" in scene and scene['description']:
                    item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description']))
                else:
                    item['description'] = ''
                item['image'] = self.format_link(response, scene['previewLink']).replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                if scene['cdn_preview_link']:
                    item['trailer'] = self.format_link(response, scene['cdn_preview_link']).replace(" ", "%20")
                else:
                    item['trailer'] = ""
                scene_date = self.parse_date(scene['dateDisplay'], date_formats=['%m/%d/%y %h:%m %p']).strftime('%Y-%m-%d')
                item['date'] = ""
                if scene_date:
                    item['date'] = scene_date
                item['url'] = f"https://www.clips4sale.com{scene['link']}"
                item['tags'] = []
                if "related_category_links" in scene and scene['related_category_links']:
                    for tag in scene['related_category_links']:
                        if "category" in tag:
                            item['tags'].append(tag['category'])
                        if "clean_name" in tag:
                            item['tags'].append(string.capwords(tag['clean_name']))
                if "keyword_links" in scene and scene['keyword_links']:
                    for tag in scene['keyword_links']:
                        if "keyword" in tag:
                            item['tags'].append(string.capwords(tag['keyword']))
                if scene['duration']:
                    item['duration'] = str(int(scene['duration']) * 60)
                item['site'] = self.get_site(response, scene)
                item['parent'] = self.get_parent(response)
                item['network'] = self.get_network(response)
                if "performers" in scene and scene['performers'] and len(scene['performers']):
                    for performer in scene['performers']:
                        item['performers'].append(string.capwords(performer['stage_name']))
                else:
                    item['performers'] = self.get_performers(response)

                yield self.check_item(item, self.days)

    def get_site(self, response, scene):
        meta = self.copy_meta(response)
        if "Missa X" in meta['storedsite']:
            title = re.sub(r'[^a-z0-9]+', '', scene['title'].lower())
            if "allherluv" in title:
                return "Clips4Sale: All Her Luv"
            if "missax" in title:
                return "Clips4Sale: Missa X"
            if "apovstory" in title:
                return "Clips4Sale: A POV Story"

        if meta['storedsite']:
            return meta['storedsite']
        return tldextract.extract(response.url).domain

    def get_parent(self, response):
        meta = self.copy_meta(response)
        if meta['parent']:
            return meta['parent']
        return tldextract.extract(response.url).domain

    def get_network(self, response):
        meta = self.copy_meta(response)
        if meta['network']:
            return meta['network']
        return tldextract.extract(response.url).domain

    def get_performers(self, response):
        url = response.url.lower()

        patterns = {
            "addie-juniper": "Addie Juniper",
            "alexa-creed": "Alexa Creed",
            "alysa-nylon": "Alysa Nylon",
            "ama-rios-playground": "Ama Rio",
            "andrea-rosu-s": "Andrea Rosu",
            "anikafall": "Anika Fall",
            "annabelle-rogers": "Annabelle Rogers",
            "asiana-starr-bondage": "Asiana Starr",
            "astrodomina": "AstroDomina",
            "bella-bates": "Bella Bates",
            "bettie-bondage": "Bettie Bondage",
            "chronicles-of-mlle-fanchette": "Mlle Fanchette",
            "crystal-knight": "Crystal Knight",
            "dahlia-fallon": "Dahlia Fallon",
            "daisys-desires": "Daisy Haze",
            "darling-kiyomi": "Darling Kiyomi",
            "divine-goddess-amber": "Divine Goddess Amber",
            "evansfeet": "Lis Evans",
            "goddess-alessa": "Goddess Alessa",
            "goddess-lavey": "Harley LaVey",
            "goddess-maisha": "Goddess Maisha",
            "helena-price": "Helena Price",
            "jenna-hoskins-bondage": "Jenna Hoskins",
            "lady-angelika": "Lady Angelika",
            "lilith-last-witch": "Lilith Last Witch",
            "little-puck-perversions": "Little Puck",
            "lovehershoes": "Lis Evans",
            "manda-marx": "Mandy Marx",
            "marisol-price": "Marisol Price",
            "mean-wolf": "Meana Wolf",
            "milf-jan-seduces": "Jan Burton",
            "milaamorabondage": "Mila Amora",
            "miss-ruby-greys-clips": "Miss Ruby Grey",
            "mistress-courtneys-fetish-lair": "Mistress Courtney",
            "mistress-euryale": "Elis Euryale",
            "mistress-jessica-starling": "Jessica Starling",
            "mistress-nikita-femdom": "Mistress Nikita",
            "natalie-wonder": "Natalie Wonder",
            "princess-camryn": "Princess Camryn",
            "princess-sasha-foxxx": "Sasha Foxxx",
            "sara-saint": "Sara Saint",
            "scarlettbelle-s-fetish-clips": "Scarlette Belle",
            "slave247story": "SlaveQ",
            "stella-liberty": "Stella Liberty",
            "superior-lana-blade": "Lana Blade",
            "sylvie-labrae": "Sylvie Labrae",
            "tamystarly-cbt": "Tamy Starly",
            "tammie-madison": "Tammie Madison",
            "tatti-roana": "Tatti Roana",
            "tgirloneguy": "Kendall Penny",
            "yes-ms-talia": "Talia Tate",
            "young-goddess-kim": "Young Goddess Kim",
            "yvette-xtreme": "Yvette Costeau",
        }

        # Return the first matching performer
        for key, performer in patterns.items():
            if key in url:
                return [performer]

        return []
