import re
import string
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClips4Sale_4Spider(BaseSceneScraper):

    sites = [
        ['Clips4Sale', 'Play With Amai', 'Play With Amai', '47204', 'play-with-amai'],
        ['Clips4Sale', 'POV Central', 'POV Central', '15933', 'pov-central'],
        ['Clips4Sale', 'Princess Camryn', 'Princess Camryn', '117722', 'princess-camryn'],
        ['Clips4Sale', 'Princess Camryn', 'Princess Camryn', '117722', 'princess-camryn'],
        ['Clips4Sale', 'Queens of Kink', 'Queens of Kink', '74545', 'queens-of-kink'],
        ['Clips4Sale', 'Robomeats', 'Robomeats', '50885', 'robomeats'],
        ['Clips4Sale', 'Ruthless Vixens Femdom', 'Ruthless Vixens Femdom', '9085', 'ruthless-vixens-femdom'],
        ['Clips4Sale', 'SilverCherrys Handjobs With a Twist', 'SilverCherrys Handjobs With a Twist', '79', 'silvercherrys-handjobs-with-a-twist'],
        ['Clips4Sale', 'Sinn Sage Dreams', 'Sinn Sage Dreams', '96823', 'sinn-sage-dreams'],
        ['Clips4Sale', 'Superbound', 'Superbound', '8178', 'superbound'],
        ['Clips4Sale', 'Tammie Madison', 'Tammie Madison', '95015', 'tammie-madison'],
        ['Clips4Sale', 'The Tabooddhist', 'The Tabooddhist', '62135', 'dan-s-porn-and-taboo'],
        ['Clips4Sale', 'VMVideo', 'VMVideo', '174737', 'vince-may-video'],
        ['Clips4Sale', 'Watch Me Audition', 'Watch Me Audition', '80069', 'watch-me-audition'],
        ['Clips4Sale', 'Women on Top - of men', 'Women on Top - of men', '7740', 'women-on-top---of-men'],
        ['Clips4Sale', 'Xev Bellringer', 'Xev Bellringer', '75701', 'xev-bellringer'],
        ['Clips4Sale', 'XXXTREMECOMIXXX', 'XXXTREMECOMIXXX', '56081', 'xxxtremecomixxx'],
        ['Clips4Sale', 'Clips4Sale: Alba Loves Bondage', 'Clips4Sale: Alba Loves Bondage', '168959', 'alba-loves-bondage'],
        ['Clips4Sale', 'Clips4Sale: Foot Fetish by Rootdawg25', 'Clips4Sale: Foot Fetish by Rootdawg25', '13249', 'rootdawg25'],
        ['Clips4Sale', 'Clips4Sale: Alexa Creed', 'Clips4Sale: Alexa Creed', '203653', 'alexa-creed'],
        ['Clips4Sale', 'Clips4Sale: Gagged Fantasy', 'Clips4Sale: Gagged Fantasy', '116240', 'gagged-fantasy'],
        ['Clips4Sale', 'Clips4Sale: Feisty Entertainment', 'Clips4Sale: Feisty Entertainment', '40069', 'feisty-entertainment'],
        ['Clips4Sale', 'Clips4Sale: Kink Haven', 'Clips4Sale: Kink Haven', '249321', 'kink-haven'],
        ['Clips4Sale', 'Clips4Sale: Miss Lin', 'Clips4Sale: Miss Lin', '385583', 'miss-lin'],
        ['Clips4Sale', 'Clips4Sale: Skull Candy Bri Bondage', 'Clips4Sale: Skull Candy Bri Bondage', '158575', 'Skull_Candy_Bri_Bondage'],
        ['Clips4Sale', 'Clips4Sale: WHCS Food Crush by Chinese Goddess', 'Clips4Sale: WHCS Food Crush by Chinese Goddess', '114006', 'whcs-food-crush-by-chinese-goddess'],
        ['Clips4Sale', 'Clips4Sale: UKCuteGirl', 'Clips4Sale: UKCuteGirl', '126755', 'ukcutegirl'],
        ['Clips4Sale', 'Clips4Sale: MissKsiaBB', 'Clips4Sale: MissKsiaBB', '235199', 'missksiabb'],
        ['Clips4Sale', 'Clips4Sale: Dame Olgas Fetish Clips', 'Clips4Sale: Dame Olgas Fetish Clips', '98797', 'dame-olgas-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: Diamondly Bound', 'Clips4Sale: Diamondly Bound', '136777', 'diamondly-bound'],
        ['Clips4Sale', 'Clips4Sale: Cali Logans Bondage Boutique', 'Clips4Sale: Cali Logans Bondage Boutique', '93317', 'cali-logans-bondage-boutique'],
        ['Clips4Sale', 'Clips4Sale: Bondage Agency', 'Clips4Sale: Bondage Agency', '171829', 'bondageagency'],
        ['Clips4Sale', 'Clips4Sale: Mistress Damazonia', 'Clips4Sale: Mistress Damazonia', '143325', 'mistress-damazonia'],
        ['Clips4Sale', 'Clips4Sale: Parannanza', 'Clips4Sale: Parannanza', '182611', 'parannanza'],
        ['Clips4Sale', 'Clips4Sale: Bedroom Bondage by Lorelei', 'Clips4Sale: Bedroom Bondage by Lorelei', '412', 'bedroom-bondage-by-lorelei'],
        ['Clips4Sale', 'Clips4Sale: AlterEgoRey', 'Clips4Sale: AlterEgoRey', '294495', 'alteregorey'],
        ['Clips4Sale', 'Clips4Sale: FrenchBondage', 'Clips4Sale: FrenchBondage', '322429', 'frenchbondage'],
        ['Clips4Sale', 'Clips4Sale: Muffled Screams', 'Clips4Sale: Muffled Screams', '126155', 'muffled-screams'],
        ['Clips4Sale', 'Clips4Sale: RECatadas Studio', 'Clips4Sale: RECatadas Studio', '135157', 'recatadas-studio'],
        ['Clips4Sale', 'Clips4Sale: Keye Bondage Images', 'Clips4Sale: Keye Bondage Images', '22502', 'keye-bondage-images'],
        ['Clips4Sale', 'Clips4Sale: Adult Stories', 'Clips4Sale: Adult Stories', '231415', 'adult-stories'],
        ['Clips4Sale', 'Clips4Sale: Calista Vixen', 'Clips4Sale: Calista Vixen', '227107', 'calista-vixen'],
        ['Clips4Sale', 'Clips4Sale: Empress Empire', 'Clips4Sale: Empress Empire', '9911', 'empress-empire'],
        ['Clips4Sale', 'Clips4Sale: Realfetishwifey', 'Clips4Sale: realfetishwifey', '373473', 'realfetishwifey'],
        ['Clips4Sale', 'Clips4Sale: Jayne Doe', 'Clips4Sale: Jayne Doe', '148787', 'jayne-doe'],
        ['Clips4Sale', 'Clips4Sale: Bound by Choice', 'Clips4Sale: Bound by Choice', '23733', 'bound-by-choice'],
        ['Clips4Sale', 'Clips4Sale: Tied Tales', 'Clips4Sale: Tied Tales', '111172', 'tied-tales'],
        ['Clips4Sale', 'Clips4Sale: PsychoSJ Bondage Store', 'Clips4Sale: PsychoSJ Bondage Store', '405135', 'psychosj-bondage-store'],
        ['Clips4Sale', 'Clips4Sale: Tony Houston Bondage Paranoia', 'Clips4Sale: Tony Houston Bondage Paranoia', '47002', 'tony-houston-bondage-paranoia'],
        ['Clips4Sale', 'Clips4Sale: Amateur Boxxx', 'Clips4Sale: Amateur Boxxx', '140969', 'amateur-boxxx'],
        ['Clips4Sale', 'Clips4Sale: Portia Everly', 'Clips4Sale: Portia Everly', '235967', 'Portia-Everly'],
        ['Clips4Sale', 'Clips4Sale: KingDom Of Infinity', 'Clips4Sale: KingDom Of Infinity', '292343', 'kingdom-of-infinity'],
        ['Clips4Sale', 'Clips4Sale: FJ Squirts', 'Clips4Sale: FJ Squirts', '304649', 'fj-squirts'],
        ['Clips4Sale', 'Fox Smoulder Fetish Clips', 'Fox Smoulder Fetish Clips', '82595', 'fox-smoulder-fetish-clips'],
        # ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: ', '', ''],
        # ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: ', '', ''],
    ]

    name = 'Clips4Sale_4'

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
                meta = response.meta
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
        meta = response.meta
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
        meta = response.meta
        if meta['parent']:
            return meta['parent']
        return tldextract.extract(response.url).domain

    def get_network(self, response):
        meta = response.meta
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
            "dame-olgas-fetish-clips": "Dame Olga",
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
            "missksiabb": "MissKsiaBB",
            "mistress-courtneys-fetish-lair": "Mistress Courtney",
            "mistress-euryale": "Elis Euryale",
            "mistress-jessica-starling": "Jessica Starling",
            "mistress-nikita-femdom": "Mistress Nikita",
            "natalie-wonder": "Natalie Wonder",
            "parannanza": "Parannanza",
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
