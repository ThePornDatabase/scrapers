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
        ['Clips4Sale', 'Clips4Sale: Fox Smoulder Fetish Clips', 'Clips4Sale: Fox Smoulder Fetish Clips', '82595', 'fox-smoulder-fetish-clips'],        
        ['Clips4Sale', 'Clips4Sale: Mistress Lunatika', 'Clips4Sale: Mistress Lunatika', '320813', 'mistress-lunatika'],
        ['Clips4Sale', 'Clips4Sale: Mistress Boo', 'Clips4Sale: Mistress Boo', '258831', 'mistress-boo'],
        ['Clips4Sale', 'Clips4Sale: Fuck n Fetish', 'Clips4Sale: Fuck n Fetish', '80227', 'fucknfetish'],
        ['Clips4Sale', 'Clips4Sale: Roped Prose Productions', 'Clips4Sale: Roped Prose Productions', '68947', 'roped-prose-productions'],
        ['Clips4Sale', 'Clips4Sale: alaskalovesfetish', 'Clips4Sale: alaskalovesfetish', '422417', 'alaskalovesfetish'],
        ['Clips4Sale', 'Clips4Sale: Rough Ink', 'Clips4Sale: Rough Ink', '509769', 'rough-ink'],
        ['Clips4Sale', 'Clips4Sale: Mistress Nina Morovic', 'Clips4Sale: Mistress Nina Morovic', '244083', 'mistress-nina-morovic'],
        ['Clips4Sale', 'Clips4Sale: Miss Kirsch', 'Clips4Sale: Miss Kirsch', '303959', 'miss-kirsch'],
        ['Clips4Sale', 'Clips4Sale: Mistress Youko', 'Clips4Sale: Mistress Youko', '196595', 'mistress-youko'],
        ['Clips4Sale', 'Clips4Sale: ASX', 'Clips4Sale: ASX', '326621', 'asx'],
        ['Clips4Sale', 'Clips4Sale: slave m', 'Clips4Sale: slave m', '13628', 'slave-m'],
        ['Clips4Sale', 'Clips4Sale: MissErinia', 'Clips4Sale: MissErinia', '354757', 'misserinia'],
        ['Clips4Sale', 'Clips4Sale: SQ Bossy Delilah', 'Clips4Sale: SQ Bossy Delilah', '16207', 'sq-bossy-delilah'],
        ['Clips4Sale', 'Clips4Sale: The KinkyBoy', 'Clips4Sale: The KinkyBoy', '317141', 'the-kinkyboy'],
        ['Clips4Sale', 'Clips4Sale: Show Some Restraint', 'Clips4Sale: Show Some Restraint', '177461', 'show-some-restraint'],
        ['Clips4Sale', 'Clips4Sale: Domiiscz store', 'Clips4Sale: Domiiscz store', '246527', 'domiiscz-store'],
        ['Clips4Sale', 'Clips4Sale: Cybill Troy Femdom Antisex League', 'Clips4Sale: Cybill Troy Femdom Antisex League', '40408', 'cybill-troy-femdom-antisex-league'], 
        ['Clips4Sale', 'Clips4Sale: Mistress Brighid', 'Clips4Sale: Mistress Brighid', '328745', 'mistress-brighid'], 
        ['Clips4Sale', 'Clips4Sale: Strafkamer', 'Clips4Sale: Strafkamer', '97459', 'strafkamer'], 
        ['Clips4Sale', 'Clips4Sale: Mistress Celene', 'Clips4Sale: Mistress Celene', '200277', 'mistress-celene'], 
        ['Clips4Sale', 'Clips4Sale: Mistress Vixen', 'Clips4Sale: Mistress Vixen', '27428', 'mistress-vixen'], 
        ['Clips4Sale', 'Clips4Sale: Domina Diably', 'Clips4Sale: Domina Diably', '433653', 'domina-diably'], 
        ['Clips4Sale', 'Clips4Sale: Mistress Lotusx', 'Clips4Sale: Mistress Lotusx', '262799', 'mistress-lotusx'], 
        ['Clips4Sale', 'Clips4Sale: Goddess Charlie Cake', 'Clips4Sale: Goddess Charlie Cake', '241107', 'goddess-charlie-cake'],
        ['Clips4Sale', 'Clips4Sale: Miss Flora', 'Clips4Sale: Miss Flora', '248503', 'miss-flora'], 
        ['Clips4Sale', 'Clips4Sale: Mistress Amarena', 'Clips4Sale: Mistress Amarena', '223973', 'mistress-amarena'], 
        ['Clips4Sale', 'Clips4Sale: Lillithid', 'Clips4Sale: Lillithid', '346861', 'lillithid'], 
        ['Clips4Sale', 'Clips4Sale: Hecate Reigns', 'Clips4Sale: Hecate Reigns', '186311', 'hecate-reigns'], 
        ['Clips4Sale', 'Clips4Sale: Mistress April', 'Clips4Sale: Mistress April', '401793', 'mistress-april'], 
        ['Clips4Sale', 'Clips4Sale: Jessica Sol', 'Clips4Sale: Jessica Sol', '460943', 'jessica-sol'], 
        ['Clips4Sale', 'Clips4Sale: Mistress Tirza Nl', 'Clips4Sale: Mistress Tirza Nl', '204569', 'mistress-tirza-nl'], 
        ['Clips4Sale', 'Clips4Sale: Sophiamayy', 'Clips4Sale: Sophiamayy', '232295', 'sophiamayy'], 
        ['Clips4Sale', 'Clips4Sale: Anouschka Femme Fatale', 'Clips4Sale: Anouschka Femme Fatale', '139051', 'anouschka-femme-fatale'], 
        ['Clips4Sale', 'Clips4Sale: Squishysaxs Sadistic Queens', 'Clips4Sale: Squishysaxs Sadistic Queens', '125293', 'squishysaxs-sadistic-queens'], 
        ['Clips4Sale', 'Clips4Sale: Predicamentbondage', 'Clips4Sale: Predicamentbondage', '296897', 'predicamentbondage'], 
        ['Clips4Sale', 'Clips4Sale: Quioyja', 'Clips4Sale: Quioyja', '301623', 'quioyja'], 
        ['Clips4Sale', 'Clips4Sale: Peggingonly', 'Clips4Sale: Peggingonly', '218729', 'peggingonly'], 
        ['Clips4Sale', 'Clips4Sale: Hotvaleria S Fetish Clip Store', 'Clips4Sale: Hotvaleria S Fetish Clip Store', '47227', 'hotvaleria-s-fetish-clip-store'], 
        ['Clips4Sale', 'Clips4Sale: Mistress Raven Uk Dominatrix', 'Clips4Sale: Mistress Raven Uk Dominatrix', '111366', 'mistress-raven-uk-dominatrix'], 
        ['Clips4Sale', 'Clips4Sale: Demoness J', 'Clips4Sale: Demoness J', '170097', 'demoness-j'],        
        ['Clips4Sale', 'Clips4Sale: Fetish Lady - Blowjobs & Handjobs', 'Clips4Sale: Fetish Lady - Blowjobs & Handjobs', '11578', 'fetish-lady---blowjobs---handjobs'],
        ['Clips4Sale', 'Clips4Sale: Bound And Milked', 'Clips4Sale: Bound And Milked', '12683', 'bound-and-milked'], 
        ['Clips4Sale', 'Clips4Sale: Laxfanat Latex Pierced Public Girl', 'Clips4Sale: Laxfanat Latex Pierced Public Girl', '48871', 'laxfanat-latex-pierced-public-girl'], 
        ['Clips4Sale', 'Clips4Sale: Lustful Orchid', 'Clips4Sale: Lustful Orchid', '168825', 'lustful-orchid'],
        # ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: ', '', ''],
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
            "dame-olgas-fetish-clips": "Dame Olga",
            "darling-kiyomi": "Darling Kiyomi",
            "divine-goddess-amber": "Divine Goddess Amber",
            "domiiscz-store": "Samantha Boobs",
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
            "mistress-nina-morovic": "Mistress Nina Morovic",
            "mistress-youko": "Mistress Youko",
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
