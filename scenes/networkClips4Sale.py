import re
import tldextract
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
# Yes, this site is a mess.


class SiteBabesInTroubleSpider(BaseSceneScraper):
    name = 'Clips4Sale'

    sites = [
        ['Clips4Sale', 'Primal', 'Primal\'s Custom XXX', '/studio/107990/primals-custom-videos/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Girls Grappling', '/studio/46940/primal-s-girl-s-grappling/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Mental Domination', '/studio/24134/primals-mental-domination/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Handjobs', '/studio/41770/primal-s-handjobs/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Dark Reflections', '/studio/98931/primals-dark-reflections/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Disgraced Superheroines', '/studio/53607/primals-disgraced-superheroines/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Superheroine Shame', '/studio/50111/primal-s-superheroine-shame/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Women Entranced', '/studio/56163/primals-women-entranced/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Taboo Family Relations', '/studio/67653/primals-taboo-family-relations/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Teasing Edging Grinding', '/studio/45057/primal-s-teasing--edging-grinding/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s POV Family Lust', '/studio/48125/primals-pov-family-lust/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Foot Fantasies', '/studio/58943/primal-s-foot-fantasies-/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Savage Tales', '/studio/88150/primals-savage-tales/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Ticklegasm', '/studio/55561/primal-s-ticklegasm/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s MILFs', '/studio/130495/primals-milfs/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Sex Fights', '/studio/46197/primals-sex-fights/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Fantasy POV', '/studio/137897/primals-fantasy-pov/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Bondage Sex POV', '/studio/147745/primals-bondage-sex-pov/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Femme Fatale Nylon Vixens', '/studio/139363/primals-femme-fatale-nylon-vixens/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s BBWs', '/studio/44723/primals-bbws/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Primal', 'Primal\'s Footjobs', '/studio/49351/primal-s-footjobs/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href | //span[@class="thumb_format" and contains(text(),"MKV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Borderland Bound', 'Borderland Bound', '/studio/64171/borderland-bound-/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Kinky Adventures', '/studio/45669/ginary-s-kinky-adventures-/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Giantess Adventures', '/studio/77757/ginary-s-giantess-adventures-/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Tickle Adventures', '/studio/71128/ginary-s-tickle-adventures/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Superbound', 'Superbound', '/studio/8178/superbound/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MOV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Cruel Mistresses', 'Cruel Mistresses', '/studio/39213/cruel-caning-and-whipping-/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"WMV")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'American Mean Girls', 'American Mean Girls', '/studio/32364/american-mean-girl/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4") and not(contains(following-sibling::span/text(),"4K")) and not(contains(following-sibling::span/text(),"480p"))]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Watch Me Audition', 'Watch Me Audition', '/studio/80069/watch-me-audition/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Jerky Girls', 'Jerky Girls', '/studio/2511/jerky-girls/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Mind Under Master', 'Mind Under Master', '/studio/118498/mind-under-master/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Xev Bellringer', 'Xev Bellringer', '/studio/75701/xev-bellringer/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Jerky Wives', 'Jerky Wives', '/studio/28671/jerky-wives-/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Bareback Studios', 'Bareback Studios', '/studio/35625/bare-back-studios/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Mandy Flores', 'Mandy Flores', '/studio/33729/mandy-flores/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'FM Concepts', 'FM Concepts', '/studio/116614/fm-concepts-1080p-bondage-store/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit96/', False, '//span[@class="thumb_format" and contains(text(),"MP4") and not(contains(./following-sibling::span/text(), "4K"))]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Mouth Stuffed and Tied Up Girls', 'Mouth Stuffed and Tied Up Girls', '/studio/4458/mouth-stuffed-and-tied-up-girls/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit96/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Jon Woods', 'American Damsels', '/studio/6571/american-damsels-by-jon-woods/Cat0-AllCategories/Page%s/ClipDate-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Girls Controlled', 'Girls Controlled To Be Bad', '/studio/10982/robo-pimp-girls-trained-to-be-bad/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Mark Rockwell', 'Marks Head Bobbers and Hand Jobbers', '/studio/47321/marks-head-bobbers-and-hand-jobbers/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Aaliyah Taylor', 'Aliyah Taylors Fetish', '/studio/70866/aaliyah-taylor-s-fetish/Cat0-AllCategories/Page%s/ClipDate-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Cock Ninja Studios', 'Cock Ninja Studios', '/studio/79893/cock-ninja-studios/Cat0-AllCategories/Page%s/ClipDate-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Family Therapy (Clips4Sale)', 'Family Therapy (Clips4Sale)', '/studio/81593/family-therapy/Cat0-AllCategories/Page%s/DisplayOrder-asc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Brat Attack', 'Brat Attack', '/studio/83427/brat-attack/Cat0-AllCategories/Page%s/ClipDate-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'BlackCow Video', 'BlackCow Video', '/studio/15814/blackcow-video/Cat0-AllCategories/Page%s/DisplayOrder-asc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Got Milked Studios', 'Got Milked Studios', '/studio/16034/black-slave-fantacies-/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Cory Chase', 'Corys Super Heroine Adventures', '/studio/32589/cory-s-super-heroine-adventures/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Cory Chase', 'Chase Water Babes', '/studio/32587/chase-water-babes/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Cory Chase', 'Kinky Cory', '/studio/41549/kinki-cory/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Cory Chase', 'Mixed Model Wrestling', '/studio/32588/mixed-model-wrestling/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'GwenMedia', 'GwenMedia', '/studio/16700/gwenmedia-femdom-latex-fetish/Cat0-AllCategories/Page%s/DisplayOrder-desc/Limit24/', True, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
        ['Clips4Sale', 'Sinn Sage Dreams', 'Sinn Sage Dreams', '/studio/96823/sinn-sage-dreams/Cat0-AllCategories/Page%s/ClipDate-desc/Limit24/', False, '//span[@class="thumb_format" and contains(text(),"MP4")]/../following-sibling::div/div/a[1]/@href'],
    ]

    url = 'https://www.clips4sale.com'

    selector_map = {
        'title': '//h3[@class="[ text-white mt-3-0 mb-1-0 text-2-4 ]"]/text()',
        'description': '//div[@class="individualClipDescription"]/p/text()',
        'date': '//span[contains(text(),"Added")]/span/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//span[@class="relatedCatLinks"]/span/a/text()',
        'external_id': r'studio\/.*\/(\d+)\/',
        'trailer': '',
        'pagination': '/studio/37354/babes-in-trouble/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/'
    }

    def start_requests(self):
        link = self.url
        meta = {}
        for site in self.sites:
            meta['network'] = site[0]
            meta['parent'] = site[1]
            meta['site'] = site[2]
            meta['pagination'] = site[3]
            meta['get_performers'] = site[4]
            meta['search_string'] = site[5]
            meta['page'] = self.page

            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['pagination']),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        url = self.format_url(base, pagination % page)
        return url

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath(meta['search_string']).getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene) and "smaller-file" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        extern_id = search.group(1)
        if extern_id:
            extern_id = extern_id.lower().replace("-wmv", "")
        return extern_id.strip()

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            if re.search(r'^\w+ \w+ - (.*)', title):
                title = re.search(r'^\w+ \w+ - (.*)', title).group(1)
            title = title.lower()
            title = title.replace("enhanced hd quality", "")
            title = title.replace("wmv", "")
            title = title.replace("(full hd)", "")
            title = title.replace("full hd", "")
            title = title.replace("(full)", "")
            title = title.replace(" hd", "")
            title = title.replace("smaller file", "")
            title = title.replace("wmv", "")
            title = title.replace(" xxx", "")
            title = title.replace(" mp4", "")
            title = title.replace("mp4 ", "")
            title = title.replace("(mp4)", "")
            title = title.replace("(.mp4)", "")
            title = title.replace("(hd)", "")
            title = title.replace("(1080)", "")
            title = title.replace("(1080hd)", "")
            title = title.replace("(1080 )", "")
            title = title.replace(" 1080", "")
            title = title.replace("(4k)", "")
            title = title.replace(" 4k", "")
            title = title.replace("(hd-)", "")
            title = title.replace("hd-", "")
            title = title.replace("(hd-4k)", "")
            title = title.replace(" optimum", "")
            title = title.replace("1080p Version", "")
            title = title.replace("1080p", "")
            title = title.replace("720p", "")
            title = title.replace("()", "")
            title = title.replace("( )", "")
            title = title.replace("mf~", "")
            # ~ title = title.replace(" - ", "")
            if re.match(r'.*\(.*? discounted\)', title):
                title = re.sub(r'(.*)\(.*? discounted\)(.*)', r'\1 \2', title)
            if re.match(r'.*\(.*? remastered\)', title):
                title = re.sub(r'(.*)\(.*? remastered\)(.*)', r'\1 \2', title)
            if re.match(r'.*\(remastered .*?\)', title):
                title = re.sub(r'(.*)\(remastered .*?\)(.*)', r'\1 \2', title)
            if re.match(r'.*\(remastered .*?\)', title):
                title = re.sub(r'(.*)\(remastered .*?\)(.*)', r'\1 \2', title)
            title = title.replace("(remastered)", "")
            title = title.strip()
            if title[-2:] == " -":
                title = title[:-2]
            return self.cleanup_title(title)
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                if 'Bondage By Jon Woods' in tags:
                    tags.remove('Bondage By Jon Woods')
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_performers(self, response):
        meta = response.meta
        if meta['get_performers']:
            performers = []
            title = self.process_xpath(
                response, self.get_selector_map('title')).get()
            if title:
                if re.match(r'^\w+ \w+ in .*', title.lower()):
                    title = re.sub(r'^(\w+ \w+) in (.*)', r'\1 - \2', title.lower())

                if re.match(r'^\w+ \w+ - .*', title):
                    performers = re.search(r'^(\w+ \w+) - .*', title).group(1)
                    performers = [performers]

                if re.match(r'^\w+ \w+ & \w+ \w+ - .*', title):
                    performers = re.search(r'^(\w+ \w+ & \w+ \w+) - .*', title).group(1)
                    performers = performers.split("&")

                if re.match(r'^\w+ \w+ and \w+ \w+ - .*', title.lower()):
                    title = title.lower()
                    performers = re.search(r'^(\w+ \w+ and \w+ \w+) - .*', title).group(1)
                    performers = performers.split("and")

                if re.match(r'^\w+ \w+ & \w+ \w+ in .*', title):
                    performers = re.search(r'^(\w+ \w+ & \w+ \w+) in .*', title).group(1)
                    performers = performers.split("&")

                if re.match(r'^\w+ \w+ and \w+ \w+ in .*', title.lower()):
                    title = title.lower()
                    performers = re.search(r'^(\w+ \w+ and \w+ \w+) in .*', title).group(1)
                    performers = performers.split("and")

            if performers:
                performers = list(map(lambda x: x.strip().title(), performers))
                if "Wonder Woman" in performers:
                    performers.remove("Wonder Woman")
                if "Birthday Gift" in performers:
                    performers.remove("Birthday Gift")
                if "Omega Girl" in performers:
                    performers.remove("Omega Girl")
                if "Mixed Boxing" in performers:
                    performers.remove("Mixed Boxing")
                if "Exchange Student" in performers:
                    performers.remove("Exchange Student")
                if "Finishing School" in performers:
                    performers.remove("Finishing School")
                if "Humiliation Match" in performers:
                    performers.remove("Humiliation Match")
                if "Just Friends" in performers:
                    performers.remove("Just Friends")
                if "Full Video" in performers:
                    performers.remove("Full Video")
                if "First Facial" in performers:
                    performers.remove("First Facial")
                if "Master Trainer" in performers:
                    performers.remove("Master Trainer")
                if "Master Coach" in performers:
                    performers.remove("Master Coach")
                if "Mixed Match" in performers:
                    performers.remove("Mixed Match")
                if "Scissorhold Domination" in performers:
                    performers.remove("Scissorhold Domination")
                if "Scissorhold Supremacy" in performers:
                    performers.remove("Scissorhold Supremacy")
                if "The Headmaster" in performers:
                    performers.remove("The Headmaster")
                if "The Inquiry" in performers:
                    performers.remove("The Inquiry")
                if "The Tutor" in performers:
                    performers.remove("The Tutor")
                if "Witch Hunter" in performers:
                    performers.remove("Witch Hunter")
                performers2 = performers.copy()
                for performer in performers2:
                    if "Vampire" in performer:
                        performers.remove(performer)
                if "" in performers:
                    performers.remove("")

                return performers

        if meta['site'] == "Mandy Flores":
            return ['Mandy Flores']

        if meta['site'] == "Sinn Sage Dreams":
            return ['Sinn Sage']

        return []

    def get_description(self, response):
        desc_rows = self.process_xpath(response, self.get_selector_map('description')).getall()
        if desc_rows:
            description = ''
            for desc in desc_rows:
                if "screen size" not in desc.lower() and "for mp4" not in desc.lower() and "for wmv" not in desc.lower() and "if you like this video" not in desc.lower():
                    if "this format is" not in desc:
                        if not re.search(r'(\d{3,4}\*\d{3,4})', desc):
                            description = description + " " + desc.strip()
            return self.cleanup_description(description)
        return ''

    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
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
