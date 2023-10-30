import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteClips4SaleSpider(BaseSceneScraper):
    name = 'Clips4Sale'

    sites = [
        ['Clips4Sale', 'Primal', 'Primal\'s Custom XXX', '107990', 'primals-custom-videos'],
        ['Clips4Sale', 'Primal', 'Primal\'s Girls Grappling', '46940', 'primal-s-girl-s-grappling'],
        ['Clips4Sale', 'Primal', 'Primal\'s Mental Domination', '24134', 'primals-mental-domination'],
        ['Clips4Sale', 'Primal', 'Primal\'s Handjobs', '41770', 'primal-s-handjobs'],
        ['Clips4Sale', 'Primal', 'Primal\'s Dark Reflections', '98931', 'primals-dark-reflections'],
        ['Clips4Sale', 'Primal', 'Primal\'s Disgraced Superheroines', '53607', 'primals-disgraced-superheroines'],
        ['Clips4Sale', 'Primal', 'Primal\'s Superheroine Shame', '50111', 'primal-s-superheroine-shame'],
        ['Clips4Sale', 'Primal', 'Primal\'s Women Entranced', '56163', 'primals-women-entranced'],
        ['Clips4Sale', 'Primal', 'Primal\'s Taboo Family Relations', '67653', 'primals-taboo-family-relations'],
        ['Clips4Sale', 'Primal', 'Primal\'s Teasing Edging Grinding', '45057', 'primal-s-teasing--edging-grinding'],
        ['Clips4Sale', 'Primal', 'Primal\'s POV Family Lust', '48125', 'primals-pov-family-lust'],
        ['Clips4Sale', 'Primal', 'Primal\'s Foot Fantasies', '58943', 'primal-s-foot-fantasies-'],
        ['Clips4Sale', 'Primal', 'Primal\'s Savage Tales', '88150', 'primals-savage-tales'],
        ['Clips4Sale', 'Primal', 'Primal\'s Ticklegasm', '55561', 'primal-s-ticklegasm'],
        ['Clips4Sale', 'Primal', 'Primal\'s MILFs', '130495', 'primals-milfs'],
        ['Clips4Sale', 'Primal', 'Primal\'s Sex Fights', '46197', 'primals-sex-fights'],
        ['Clips4Sale', 'Primal', 'Primal\'s Fantasy POV', '137897', 'primals-fantasy-pov'],
        ['Clips4Sale', 'Primal', 'Primal\'s Bondage Sex POV', '147745', 'primals-bondage-sex-pov'],
        ['Clips4Sale', 'Primal', 'Primal\'s Femme Fatale Nylon Vixens', '139363', 'primals-femme-fatale-nylon-vixens'],
        ['Clips4Sale', 'Primal', 'Primal\'s BBWs', '44723', 'primals-bbws'],
        ['Clips4Sale', 'Primal', 'Primal\'s Footjobs', '49351', 'primal-s-footjobs'],
        ['Clips4Sale', 'Borderland Bound', 'Borderland Bound', '64171', 'borderland-bound-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Kinky Adventures', '45669', 'ginary-s-kinky-adventures-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Giantess Adventures', '77757', 'ginary-s-giantess-adventures-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Tickle Adventures', '71128', 'ginary-s-tickle-adventures'],
        ['Clips4Sale', 'Superbound', 'Superbound', '8178', 'superbound'],
        ['Clips4Sale', 'Cruel Mistresses', 'Cruel Mistresses', '39213', 'cruel-caning-and-whipping-'],
        ['Clips4Sale', 'American Mean Girls', 'American Mean Girls', '32364', 'american-mean-girl'],
        ['Clips4Sale', 'Watch Me Audition', 'Watch Me Audition', '80069', 'watch-me-audition'],
        ['Clips4Sale', 'Jerky Girls', 'Jerky Girls', '2511', 'jerky-girls'],
        ['Clips4Sale', 'Mind Under Master', 'Mind Under Master', '118498', 'mind-under-master'],
        ['Clips4Sale', 'Xev Bellringer', 'Xev Bellringer', '75701', 'xev-bellringer'],
        ['Clips4Sale', 'Jerky Wives', 'Jerky Wives', '28671', 'jerky-wives-'],
        ['Clips4Sale', 'Bareback Studios', 'Bareback Studios', '35625', 'bare-back-studios'],
        ['Clips4Sale', 'Bareback Studios', 'Bareback Studios', '35625', 'bare-back-studios'],
        ['Clips4Sale', 'Mandy Flores', 'Mandy Flores', '33729', 'mandy-flores'],
        ['Clips4Sale', 'FM Concepts', 'FM Concepts', '116614', 'fm-concepts-1080p-bondage-store'],
        ['Clips4Sale', 'Mouth Stuffed and Tied Up Girls', 'Mouth Stuffed and Tied Up Girls', '4458', 'mouth-stuffed-and-tied-up-girls'],
        ['Clips4Sale', 'Jon Woods', 'American Damsels', '6571', 'american-damsels-by-jon-woods'],
        ['Clips4Sale', 'Girls Controlled', 'Girls Controlled To Be Bad', '10982', 'robo-pimp-girls-trained-to-be-bad'],
        ['Clips4Sale', 'Mark Rockwell', 'Marks Head Bobbers and Hand Jobbers', '47321', 'marks-head-bobbers-and-hand-jobbers'],
        ['Clips4Sale', 'Aaliyah Taylor', 'Aliyah Taylors Fetish', '70866', 'aaliyah-taylor-s-fetish'],
        ['Clips4Sale', 'Family Therapy (Clips4Sale)', 'Family Therapy (Clips4Sale)', '81593', 'family-therapy'],
        ['Clips4Sale', 'Brat Attack', 'Brat Attack', '83427', 'brat-attack'],
        ['Clips4Sale', 'BlackCow Video', 'BlackCow Video', '15814', 'blackcow-video'],
        ['Clips4Sale', 'Got Milked Studios', 'Got Milked Studios', '16034', 'black-slave-fantacies-'],
        ['Clips4Sale', 'Cory Chase', 'Corys Super Heroine Adventures', '32589', 'cory-s-super-heroine-adventures'],
        ['Clips4Sale', 'Cory Chase', 'Chase Water Babes', '32587', 'chase-water-babes'],
        ['Clips4Sale', 'Cory Chase', 'Kinky Cory', '41549', 'kinki-cory'],
        ['Clips4Sale', 'Cory Chase', 'Mixed Model Wrestling', '32588', 'mixed-model-wrestling'],
        ['Clips4Sale', 'GwenMedia', 'GwenMedia', '16700', 'gwenmedia-femdom-latex-fetish'],
        ['Clips4Sale', 'Sinn Sage Dreams', 'Sinn Sage Dreams', '96823', 'sinn-sage-dreams'],
        ['Clips4Sale', 'Aaliyah Taylors Fetish', 'Aaliyah Taylors Fetish', '70866', 'aaliyah-taylor-s-fetish'],
        ['Clips4Sale', 'Ashley Fires Fetish Clips', 'Ashley Fires Fetish Clips', '5177', 'ashley-fires-fetish-clips'],
        ['All Her Luv', 'Missa X', 'Missa X', '51941', 'missa'],
        ['Clips4Sale', 'Cock Ninja Studios', 'Cock Ninja Studios', '79893', 'cock-ninja-studios'],
        ['Clips4Sale', 'Pampered Penny', 'Pampered Penny', '11315', 'pampered-penny'],
        ['Clips4Sale', 'Miss Penny Barber', 'Miss Penny Barber', '18369', 'miss-penny-barber'],
        ['Clips4Sale', 'VMVideo', 'VMVideo', '174737', 'vince-may-video'],
        ['Clips4Sale', 'Angel the Dreamgirl', 'Angel the Dreamgirl', '68591', 'angel-the-dreamgirl'],
        ['Clips4Sale', 'K Klixen Productions', 'K Klixen Productions', '7373', 'k-handjob-by-klixen-'],
        ['Clips4Sale', 'Dick Sucking Lips And Facials', 'Dick Sucking Lips And Facials', '78419', 'dick-sucking-lips-and-spit'],
        ['Clips4Sale', 'Feet of Philly', 'Feet of Philly', '40511', 'feet-of-philly'],
        ['Clips4Sale', 'Cruel Unusual Femdom', 'Cruel Unusual Femdom', '5751', 'cruel---unusual-femdom'],
        ['Clips4Sale', 'Ruthless Vixens Femdom', 'Ruthless Vixens Femdom', '9085', 'ruthless-vixens-femdom'],
        ['Clips4Sale', 'XXXTREMECOMIXXX', 'XXXTREMECOMIXXX', '56081', 'xxxtremecomixxx'],
        ['Clips4Sale', 'Robomeats', 'Robomeats', '50885', 'robomeats'],
        ['Clips4Sale', 'The Tabooddhist', 'The Tabooddhist', '62135', 'dan-s-porn-and-taboo'],
        ['Clips4Sale', 'Bondage Junkies', 'Bondage Junkies', '47664', 'bondagejunkies-clips'],
        ['Clips4Sale', 'KICK ASS BONDAGE BY ROPEMARKED', 'KICK ASS BONDAGE BY ROPEMARKED', '39599', 'kick-ass-bondage-by-girls-in-a-bind'],
        ['Clips4Sale', 'Fetish Cartel', 'Fetish Cartel', '3044', 'fetish-cartel'],
        ['Clips4Sale', 'Philly Butt Sluts', 'Philly Butt Sluts', '40522', 'philly-butt-sluts'],
        ['Clips4Sale', 'Pedi Police', 'Pedi Police', '124175', 'pedi-police'],
        ['Clips4Sale', 'Barely Legal Foot Jobs', 'Barely Legal Foot Jobs', '40521', 'barely-legal-foot-jobs'],
        ['Clips4Sale', 'SilverCherrys Handjobs With a Twist', 'SilverCherrys Handjobs With a Twist', '79', 'silvercherrys-handjobs-with-a-twist'],
        ['Clips4Sale', 'Eros Handjobs N Blowjobs', 'Eros Handjobs N Blowjobs', '105416', '105416-eros-handjobs-n-blowjobs'],
        ['Clips4Sale', 'Lexis Taboo Diaries', 'Lexis Taboo Diaries', '113974', 'lexis-taboo-diaries'],
        ['Clips4Sale', 'TABOO', 'TABOO', '58471', 'taboo'],
        ['Clips4Sale', 'Old School Ties By Steve Villa', 'Old School Ties By Steve Villa', '17008', 'tied-up---gagged-by-steve-villa'],
        ['Clips4Sale', 'Hardcore Foot Sex', 'Hardcore Foot Sex', '28231', 'hardcore-foot-sex'],
        ['Clips4Sale', 'FM Concepts 1080p Men In Bondage', 'FM Concepts 1080p Men In Bondage', '117240', 'FM-Concepts-1080p-Men-In-Bondage'],
        ['Clips4Sale', 'Addie Juniper Fetish Clips', 'Addie Juniper Fetish Clips', '4502', 'addie-juniper-fetish-clips'],
        ['Clips4Sale', 'Play With Amai', 'Play With Amai', '47204', 'play-with-amai'],
        ['Clips4Sale', 'Fetish by Daisy Haze', 'Fetish by Daisy Haze', '71770', 'daisys-desires'],
        ['Clips4Sale', 'Jerk4PrincessUK', 'Jerk4PrincessUK', '36426', 'jerk4princessuk'],
    ]

    url = 'https://www.clips4sale.com'

    selector_map = {
        'external_id': r'studio\/.*\/(\d+)\/',
        'pagination': ''
    }

    def start_requests(self):
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
        url = f"https://www.clips4sale.com/studio/{store}/{storename}/Cat0-AllCategories/Page{str(page)}/C4SSort-added_at/Limit24/?onlyClips=true&_data=routes%2Fstudio.$id_.$studioSlug.$"
        return url

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['clips']
        for scene in jsondata:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['id'] = scene['clipId']
            item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description']))
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
                    item['tags'].append(tag['category'])
            if scene['duration']:
                item['duration'] = str(int(scene['duration']) * 60)
            item['site'] = self.get_site(response)
            item['parent'] = self.get_parent(response)
            item['network'] = self.get_network(response)
            item['performers'] = self.get_performers(response)

            yield self.check_item(item, self.days)

    def get_site(self, response):
        meta = response.meta
        if "Missa X" in meta['storedsite']:
            title = self.process_xpath(response, self.get_selector_map('title')).get()
            if "allherluv" in title.lower():
                return "All Her Luv"
            if "missax" in title.lower():
                return "Missa X"
            if "apovstory" in title.lower():
                return "A POV Story"

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
        if "daisys-desires" in response.url:
            return ['Daisy Haze']
        if "addie-juniper" in response.url:
            return ['Addie Juniper']
        return []
