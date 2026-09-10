import re
import string
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClips4Sale_2Spider(BaseSceneScraper):

    sites = [
        ['Clips4Sale', 'Clips4Sale: Goddess Maisha', 'Clips4Sale: Goddess Maisha', '243771', 'goddess-maisha'],
        ['Clips4Sale', 'Clips4Sale: Hardcore Tickling', 'Clips4Sale: Hardcore Tickling', '22851', 'hardcore-tickling-'],
        ['Clips4Sale', 'Clips4Sale: Helena Price Cock Quest', 'Clips4Sale: Helena Price Cock Quest', '127111', 'helena-price-cock-quest'],
        ['Clips4Sale', 'Clips4Sale: Helena Price Taboo', 'Clips4Sale: Helena Price Taboo', '127013', 'helena-price-taboo'],
        ['Clips4Sale', 'Clips4Sale: Hot Milf and Taboo Fetishes', 'Clips4Sale: Hot Milf and Taboo Fetishes', '14439', 'hot-milf-and-taboo-fetishes'],
        ['Clips4Sale', 'Clips4Sale: HUGE n HOT', 'Clips4Sale: HUGE n HOT', '4541', 'huge-n-hot'],
        ['Clips4Sale', 'Clips4Sale: Jae and Luna - THE BBW ROOMMATES', 'Clips4Sale: Jae and Luna - THE BBW ROOMMATES', '18529', 'jae-and-luna---the-bbw-roommates-'],
        ['Clips4Sale', 'Clips4Sale: Jae SSBBW', 'Clips4Sale: Jae SSBBW', '16339', 'jae-ssbbw'],
        ['Clips4Sale', 'Clips4Sale: Jenna Hoskins Bondage', 'Clips4Sale: Jenna Hoskins Bondage', '242941', 'jenna-hoskins-bondage'],
        ['Clips4Sale', 'Clips4Sale: KathiaNobiliGirls', 'Clips4Sale: KathiaNobiliGirls', '76113', 'kathianobiligirls'],
        ['Clips4Sale', 'Clips4Sale: Kendra James Fetish Experience', 'Clips4Sale: Kendra James Fetish Experience', '11330', 'kendra-james-fetish-exxxpierence'],
        ['Clips4Sale', 'Clips4Sale: Kenny Kong AMWF Porn', 'Clips4Sale: Kenny Kong AMWF Porn', '105418', 'kenny-kong-amwf-porn'],
        ['Clips4Sale', 'Clips4Sale: Kyras BBW Fetish Depot', 'Clips4Sale: Kyras BBW Fetish Depot', '111606', 'kyrakane-clip-store'],
        ['Clips4Sale', 'Clips4Sale: Lady Angelika', 'Clips4Sale: Lady Angelika', '56387', 'lady-angelika'],
        ['Clips4Sale', 'Clips4Sale: Lady Fyre Femdom', 'Clips4Sale: Lady Fyre Femdom', '60555', 'lady-fyre-femdom'],
        ['Clips4Sale', 'Clips4Sale: Lady X', 'Clips4Sale: Lady X', '2582', 'lady-x'],
        ['Clips4Sale', 'Clips4Sale: Latina Bondage', 'Clips4Sale: Latina Bondage', '194487', 'latina-bondage'],
        ['Clips4Sale', 'Clips4Sale: Layla Bondage Addiction', 'Clips4Sale: Layla Bondage Addiction', '142109', 'layla-bondage-addiction'],
        ['Clips4Sale', 'Clips4Sale: LBC Fetish', 'Clips4Sale: LBC Fetish', '69727', 'lbc-fetish'],
        ['Clips4Sale', 'Clips4Sale: Little Puck Perversions', 'Clips4Sale: Little Puck Perversions', '112222', 'little-puck-perversions'],
        ['Clips4Sale', 'Clips4Sale: loveadipose', 'Clips4Sale: loveadipose', '147757', 'loveadipose'],
        ['Clips4Sale', 'Clips4Sale: LoveHerShoes', 'Clips4Sale: LoveHerShoes', '298841', 'lovehershoes'],
        ['Clips4Sale', 'Clips4Sale: Luna Love SSBBW', 'Clips4Sale: Luna Love SSBBW', '16922', 'luna-love-ssbbw'],
        ['Clips4Sale', 'Clips4Sale: Madame Brooks Sinister Latex Studio', 'Clips4Sale: Madame Brooks Sinister Latex Studio', '153193', 'madame-brooks-sinister-latex-studio'],
        ['Clips4Sale', 'Clips4Sale: Marisol Price', 'Clips4Sale: Marisol Price', '199605', 'marisol-price'],
        ['Clips4Sale', 'Clips4Sale: Mastubation Encouragement Scenarios', 'Clips4Sale: Mastubation Encouragement Scenarios', '29481', 'mastubation-encouragement-scenarios'],
        ['Clips4Sale', 'Clips4Sale: Maternal Seductions', 'Clips4Sale: Maternal Seductions', '32590', 'maternal-seductions'],
        ['Clips4Sale', 'Clips4Sale: MilaAmoraBondage', 'Clips4Sale: MilaAmoraBondage', '220829', 'milaamorabondage'],
        ['Clips4Sale', 'Clips4Sale: Miss Melissa', 'Clips4Sale: Miss Melissa', '58397', 'spoiled-princess-mel'],
        ['Clips4Sale', 'Clips4Sale: Miss Ruby Greys Clips', 'Clips4Sale: Miss Ruby Greys Clips', '164277', 'miss-ruby-greys-clips'],
        ['Clips4Sale', 'Clips4Sale: Missa X', 'Clips4Sale: Missa X', '51941', 'missa'],
        ['Clips4Sale', 'Clips4Sale: Mistress Courtneys Fetish Lair', 'Clips4Sale: Mistress Courtneys Fetish Lair', '97973', 'mistress-courtneys-fetish-lair'],
        ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: Mistress Elis Euryale', '152249', 'mistress-euryale'],
        ['Clips4Sale', 'Clips4Sale: Mistress Iside', 'Clips4Sale: Mistress Iside', '96981', 'mistress-iside---femdom'],
        ['Clips4Sale', 'Clips4Sale: Mistress Jessica Starling', 'Clips4Sale: Mistress Jessica Starling', '146727', 'mistress-jessica-starling'],
        ['Clips4Sale', 'Clips4Sale: Mistress Lilith Last Witch', 'Clips4Sale: Mistress Lilith Last Witch', '214733', 'mistress-lilith-last-witch'],
        ['Clips4Sale', 'Clips4Sale: Mistress Nikita FemDom Videos', 'Clips4Sale: Mistress Nikita FemDom Videos', '57215', 'mistress-nikita-femdom-videos'],
        ['Clips4Sale', 'Clips4Sale: Nasty Family', 'Clips4Sale: Nasty Family', '82539', 'nasty-family'],
        ['Clips4Sale', 'Clips4Sale: Natashas Bedroom', 'Clips4Sale: Natashas Bedroom', '72779', 'natasha-s-palace'],
        ['Clips4Sale', 'Clips4Sale: Olivia Jaide Kink', 'Clips4Sale: Olivia Jaide Kink', '68859', 'sweetie-slut--zecora-belle'],
        ['Clips4Sale', 'Clips4Sale: Russian girls in fetish', 'Clips4Sale: Russian girls in fetish', '98785', 'russian-girls-in-fetish'],
        ['Clips4Sale', 'Clips4Sale: Sara Saint', 'Clips4Sale: Sara Saint', '162999', 'sara-saint'],
        ['Clips4Sale', 'Clips4Sale: ScarlettBelles Fetish Clips', 'Clips4Sale: ScarlettBelles Fetish Clips', '70634', 'scarlettbelle-s-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: Shibari Kalahari', 'Clips4Sale: Shibari Kalahari', '221255', 'shibari-kalahari'],
        ['Clips4Sale', 'Clips4Sale: Shiny Cock Films', 'Clips4Sale: Shiny Cock Films', '128845', 'shiny-cock-films'],
        ['Clips4Sale', 'Clips4Sale: Shiny leather heaven', 'Clips4Sale: Shiny leather heaven', '139143', 'shiny-leather-heaven'],
        ['Clips4Sale', 'Clips4Sale: Shoelovers', 'Clips4Sale: Shoelovers', '216831', 'shoelovers'],
        ['Clips4Sale', 'Clips4Sale: slave247story', 'Clips4Sale: slave247story', '223337', 'slave247story'],
        ['Clips4Sale', 'Clips4Sale: SofiaStudios', 'Clips4Sale: SofiaStudios', '173843', 'sofiastudios'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Briannas Fat Fetish Clips', 'Clips4Sale: SSBBW Briannas Fat Fetish Clips', '69525', 'ssbbw-brianna-s-fat-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: Ssbbw Bubbly Booty', 'Clips4Sale: Ssbbw Bubbly Booty', '130003', 'ssbbw-bubbly-booty'],
        ['Clips4Sale', 'Clips4Sale: SSBBW CaitiDee', 'Clips4Sale: SSBBW CaitiDee', '43781', 'ssbbw-caitidee'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Foxy Roxxie', 'Clips4Sale: SSBBW Foxy Roxxie', '18516', 'ssbbw-foxy-roxxie'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Juicy Jackie', 'Clips4Sale: SSBBW Juicy Jackie', '135731', 'ssbbw-juicy-jackie'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Pinup BODacious Kellie Kay', 'Clips4Sale: SSBBW Pinup BODacious Kellie Kay', '21475', 'ssbbw-pinup-bodacious-kellie-kay-'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Reenaye Starr', 'Clips4Sale: SSBBW Reenaye Starr', '14925', 'ssbbw-reenaye-starr'],
        ['Clips4Sale', 'Clips4Sale: SSBBWLEIGHTON', 'Clips4Sale: SSBBWLEIGHTON', '118282', 'ssbbwleighton'],
        ['Clips4Sale', 'Clips4Sale: Stella Liberty', 'Clips4Sale: Stella Liberty', '101957', 'stella-liberty'],
        ['Clips4Sale', 'Clips4Sale: Summer Marshmallow', 'Clips4Sale: Summer Marshmallow', '119504', 'summer-marshmallow'],
        ['Clips4Sale', 'Clips4Sale: Superior Lana Blade', 'Clips4Sale: Superior Lana Blade', '229937', 'superior-lana-blade'],
        ['Clips4Sale', 'Clips4Sale: Sweet Adeline', 'Clips4Sale: Sweet Adeline', '68633', 'sweet-adeline-s-clip-store'],
        ['Clips4Sale', 'Clips4Sale: Sylvie Labrae', 'Clips4Sale: Sylvie Labrae', '337583', 'sylvie-labrae'],
        ['Clips4Sale', 'Clips4Sale: TABOO', 'Clips4Sale: TABOO', '58471', 'taboo'],
        ['Clips4Sale', 'Clips4Sale: TABOO CHAOS', 'Clips4Sale: TABOO CHAOS', '73105', 'taboo-chaos'],
        ['Clips4Sale', 'Clips4Sale: Taboo Diaries', 'Clips4Sale: Taboo Diaries', '56891', 'taboo-diaries'],
        ['Clips4Sale', 'Clips4Sale: TamyStarly CBT and Bootjobs', 'Clips4Sale: TamyStarly CBT and Bootjobs', '209723', 'tamystarly-cbt-and-bootjobs'],
        ['Clips4Sale', 'Clips4Sale: Tatti Roana Bondage', 'Clips4Sale: Tatti Roana Bondage', '254031', 'tatti-roana-bondage'],
        ['Clips4Sale', 'Clips4Sale: TaylorMadeClips', 'Clips4Sale: TaylorMadeClips', '2119', 'taylormadeclips'],
        ['Clips4Sale', 'Clips4Sale: Ted Michaels Damsels', 'Clips4Sale: Ted Michaels Damsels', '38048', 'ted-michaels-damsels'],
        ['Clips4Sale', 'Clips4Sale: TgirlOneGuy', 'Clips4Sale: TgirlOneGuy', '120767', 'tgirloneguy'],
        ['Clips4Sale', 'Clips4Sale: That Kinky Girl', 'Clips4Sale: That Kinky Girl', '45475', 'that-kinky-girl'],
        ['Clips4Sale', 'Clips4Sale: The BigBootyBeautyXXL Emporium', 'Clips4Sale: The BigBootyBeautyXXL Emporium', '65243', 'the-bigbootybeautyxxl-emporium'],
        ['Clips4Sale', 'Clips4Sale: This Boys Dream', 'Clips4Sale: This Boys Dream', '52799', 'this-boy-s-dream'],
        ['Clips4Sale', 'Clips4Sale: TIEDNCUFFED', 'Clips4Sale: TIEDNCUFFED', '40704', 'tiedncuffed'],
        ['Clips4Sale', 'Clips4Sale: TILLYTOWN', 'Clips4Sale: TILLYTOWN', '121155', 'tillytown']
    ]

    name = 'Clips4Sale_2'

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
