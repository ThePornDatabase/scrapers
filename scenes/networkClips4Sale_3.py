import re
import string
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClips4Sale_3Spider(BaseSceneScraper):

    sites = [
        ['Clips4Sale', 'Clips4Sale: Ty Bones Bone Zone', 'Clips4Sale: Ty Bones Bone Zone', '136091', 'ty-bones-bone-zone'],
        ['Clips4Sale', 'Clips4Sale: Universal Spanking and Punishments', 'Clips4Sale: Universal Spanking and Punishments', '86173', 'universal-spanking-and-punishments'],
        ['Clips4Sale', 'Clips4Sale: WCA Productions', 'Clips4Sale: WCA Productions', '88054', 'wca-productions'],
        ['Clips4Sale', 'Clips4Sale: WendyWarrior Market', 'Clips4Sale: WendyWarrior Market', '109544', 'wendywarrior-market'],
        ['Clips4Sale', 'Clips4Sale: XXX Multimedia', 'Clips4Sale: XXX Multimedia', '79949', 'xxx-multimedia'],
        ['Clips4Sale', 'Clips4Sale: Yes Ms Talia', 'Clips4Sale: Yes Ms Talia', '133263', 'yes-ms-talia'],
        ['Clips4Sale', 'Clips4Sale: Young Goddess Kim', 'Clips4Sale: Young Goddess Kim', '107054', 'young-goddess-kim'],
        ['Clips4Sale', 'Clips4Sale: Yvette Xtreme', 'Clips4Sale: Yvette Xtreme', '112942', 'yvette-xtreme'],
        ['Clips4Sale', 'Clips4Sale: Cock Ninja Studios', 'Clips4Sale: Cock Ninja Studios', '79893', 'cock-ninja-studios'],
        ['Clips4Sale', 'Cory Chase', 'Corys Super Heroine Adventures', '32589', 'cory-s-super-heroine-adventures'],
        ['Clips4Sale', 'Cruel Anettes Fetish Store', 'Cruel Anettes Fetish Store', '122893', 'cruel-anettes-fetish-store'],
        ['Clips4Sale', 'Cruel Mistresses', 'Cruel Mistresses', '39213', 'cruel-caning-and-whipping-'],
        ['Clips4Sale', 'Cruel Punishments - Severe Femdom', 'Cruel Punishments - Severe Femdom', '20885', 'cruel-punishments---severe-femdom-'],
        ['Clips4Sale', 'Cruel Unusual Femdom', 'Cruel Unusual Femdom', '5751', 'cruel---unusual-femdom'],
        ['Clips4Sale', 'Custom Fetish Cumshots', 'Custom Fetish Cumshots', '104694', 'custom-fetish-cumshots'],
        ['Clips4Sale', 'Dick Sucking Lips And Facials', 'Dick Sucking Lips And Facials', '78419', 'dick-sucking-lips-and-spit'],
        ['Clips4Sale', 'Divine Goddess Amber', 'Divine Goddess Amber', '229077', 'divine-goddess-amber'],
        ['Clips4Sale', 'Eros Handjobs N Blowjobs', 'Eros Handjobs N Blowjobs', '105416', '105416-eros-handjobs-n-blowjobs'],
        ['Clips4Sale', 'Eva de Vil', 'Eva de Vil', '122965', 'eva-de-vil'],
        ['Clips4Sale', 'Family Therapy (Clips4Sale)', 'Family Therapy (Clips4Sale)', '81593', 'family-therapy'],
        ['Clips4Sale', 'Feet of Philly', 'Feet of Philly', '40511', 'feet-of-philly'],
        ['Clips4Sale', 'FemmeLife', 'FemmeLife', '57775', 'codewordsquirrel'],
        ['Clips4Sale', 'Fetish by Daisy Haze', 'Fetish by Daisy Haze', '71770', 'daisys-desires'],
        ['Clips4Sale', 'Fetish Cartel', 'Fetish Cartel', '3044', 'fetish-cartel'],
        ['Clips4Sale', 'Fetish Liza Clips', 'Fetish Liza Clips', '88414', 'fetish-liza-clips'],
        ['Clips4Sale', 'Fifi Foxx Fantasies', 'Fifi Foxx Fantasies', '120643', 'fifi-foxx-fantasies'],
        ['Clips4Sale', 'FM Concepts', 'FM Concepts', '116614', 'fm-concepts-1080p-bondage-store'],
        ['Clips4Sale', 'FM Concepts 1080p Men In Bondage', 'FM Concepts 1080p Men In Bondage', '117240', 'FM-Concepts-1080p-Men-In-Bondage'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Giantess Adventures', '77757', 'ginary-s-giantess-adventures-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Kinky Adventures', '45669', 'ginary-s-kinky-adventures-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Tickle Adventures', '71128', 'ginary-s-tickle-adventures'],
        ['Clips4Sale', 'Girls Controlled', 'Girls Controlled To Be Bad', '10982', 'robo-pimp-girls-trained-to-be-bad'],
        ['Clips4Sale', 'GloveMansion', 'GloveMansion', '78265', 'glove-sex-clips'],
        ['Clips4Sale', 'GodMother The Great Video Store', 'GodMother The Great Video Store', '2519', 'godmother-the-great-video-store'],
        ['Clips4Sale', 'Got Milked Studios', 'Got Milked Studios', '16034', 'black-slave-fantacies-'],
        ['Clips4Sale', 'GwenMedia', 'GwenMedia', '16700', 'gwenmedia-femdom-latex-fetish'],
        ['Clips4Sale', 'Handjob Honeys and Blowjob Babes', 'Handjob Honeys and Blowjob Babes', '162', 'Handjob-Honeys-and-Blowjob-Babes'],
        ['Clips4Sale', 'Hardcore Foot Sex', 'Hardcore Foot Sex', '28231', 'hardcore-foot-sex'],
        ['Clips4Sale', 'Hoby Buchanon Facefucks Chicks', 'Hoby Buchanon Facefucks Chicks', '116032', 'hoby-buchanon-facefucks-chicks'],
        ['Clips4Sale', 'Humiliation from Miss Alika', 'Humiliation from Miss Alika', '147267', 'humiliation-from-miss-alika'],
        ['Clips4Sale', 'J Macs POV', 'J Macs POV', '151671', 'j-macs-pov'],
        ['Clips4Sale', 'Jakes Blows Tugs n Toes', 'Jakes Blows Tugs n Toes', '77551', 'blows-and-toes'],
        ['Clips4Sale', 'Jan Burton', 'Jan Burton', '2853', 'milf-jan-seduces-real-stepson-tom'],
        ['Clips4Sale', 'JBC Videos Pantyhose', 'JBC Videos Pantyhose', '32173', 'jbc-videos-pantyhose'],
        ['Clips4Sale', 'Jerk4PrincessUK', 'Jerk4PrincessUK', '36426', 'jerk4princessuk'],
        ['Clips4Sale', 'Jerky Girls', 'Jerky Girls', '2511', 'jerky-girls'],
        ['Clips4Sale', 'Jerky Sluts', 'Jerky Sluts', '51543', 'jerky-sluts-------'],
        ['Clips4Sale', 'Jerky Wives', 'Jerky Wives', '28671', 'jerky-wives-'],
        ['Clips4Sale', 'K Klixen Productions', 'K Klixen Productions', '7373', 'k-handjob-by-klixen-'],
        ['Clips4Sale', 'Kenny Kong AMWF Porn', 'Kenny Kong AMWF Porn', '105418', 'kenny-kong-amwf-porn'],
        ['Clips4Sale', 'KICK ASS BONDAGE BY ROPEMARKED', 'KICK ASS BONDAGE BY ROPEMARKED', '39599', 'kick-ass-bondage-by-girls-in-a-bind'],
        ['Clips4Sale', 'Cory Chase', 'Kinky Cory', '41549', 'kinki-cory'],
        ['Clips4Sale', 'Kinky Leather Clips', 'Kinky Leather Clips', '83433', 'kinky-leather-clips'],
        ['Clips4Sale', 'Lelu Love - Cum Inside, Lets Play', 'Lelu Love - Cum Inside, Lets Play', '44611', 'lelu-love---cum-inside--let-s-play'],
        ['Clips4Sale', 'Lexis Taboo Diaries', 'Lexis Taboo Diaries', '113974', 'lexis-taboo-diaries'],
        ['Clips4Sale', 'Lucid Dreaming', 'Lucid Dreaming', '145433', 'lucid-dreaming'],
        ['Clips4Sale', 'Mandy Flores', 'Mandy Flores', '33729', 'mandy-flores'],
        ['Clips4Sale', 'Mandy Flores', 'Mandy Flores', '33729', 'mandy-flores'],
        ['Clips4Sale', 'Mandy Marx', 'Mandy Marx', '120911', 'mandy-marx'],
        ['Clips4Sale', 'Mark Rockwell', 'Marks Head Bobbers and Hand Jobbers', '47321', 'marks-head-bobbers-and-hand-jobbers'],
        ['Clips4Sale', 'Meana Wolf (Clips4Sale)', 'Meana Wolf (Clips4Sale)', '81629', 'mean-wolf'],
        ['Clips4Sale', 'Mind Under Master', 'Mind Under Master', '118498', 'mind-under-master'],
        ['Clips4Sale', 'Miss Lilu', 'Miss Lilu', '3010', 'Miss-LiLu'],
        ['Clips4Sale', 'Miss Penny Barber', 'Miss Penny Barber', '18369', 'miss-penny-barber'],
        ['Clips4Sale', 'Mistress - T - Fetish Fuckery', 'Mistress - T - Fetish Fuckery', '23869', 'mistress---t---fetish-fuckery'],
        ['Clips4Sale', 'Cory Chase', 'Mixed Model Wrestling', '32588', 'mixed-model-wrestling'],
        ['Clips4Sale', 'Mouth Stuffed and Tied Up Girls', 'Mouth Stuffed and Tied Up Girls', '4458', 'mouth-stuffed-and-tied-up-girls'],
        ['Clips4Sale', 'Natalie Wonder Clips', 'Natalie Wonder Clips', '79477', 'natalie-wonder-clips'],
        ['Clips4Sale', 'Nathan Blake XXX', 'Nathan Blake XXX', '94243', 'nathan-blake-xxx'],
        ['Clips4Sale', 'Naughty Girls', 'Naughty Girls', '148381', '148381-naughty-girls'],
        ['Clips4Sale', 'Naughty Midwest Girls (Clips4Sale)', 'Naughty Midwest Girls (Clips4Sale)', '3664', 'naughty-midwest-girls-videoclips'],
        ['Clips4Sale', 'Old School Ties By Steve Villa', 'Old School Ties By Steve Villa', '17008', 'tied-up---gagged-by-steve-villa'],
        ['Clips4Sale', 'Pampered Penny', 'Pampered Penny', '11315', 'pampered-penny'],
        ['Clips4Sale', 'Pedi Police', 'Pedi Police', '124175', 'pedi-police'],
        ['Clips4Sale', 'Philly Butt Sluts', 'Philly Butt Sluts', '40522', 'philly-butt-sluts']
    ]

    name = 'Clips4Sale_3'

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
