import re
import string
import requests
import scrapy
import json
import unidecode
import html
import codecs
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class JavJAVTrailersSpider(BaseSceneScraper):
    name = 'JAVTrailers'

    start_urls = [
        'https://javtrailers.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 2,
        # ~ 'CONCURRENT_REQUESTS': 4,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        # ~ 'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        # ~ 'CONCURRENT_REQUESTS_PER_IP': 4,
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        if self.limit_pages == 1:
            self.limit_pages = 10

        if self.days == 20:
            self.days = 99999

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card-container"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        item = SceneItem()
        item = self.prep_item(item)

        jsondata = response.xpath('//script[contains(text(), "__NUXT__")]/text()')
        if jsondata:
            jsondata = jsondata.get()
            jsondata = re.search(r'(video:.*?),popunder', jsondata)
            if jsondata:
                jsondata = jsondata.group(1)

        contentid = False
        sceneid = response.xpath('//span[contains(text(), "DVD ID:")]/following-sibling::text()[1]')
        if not sceneid:
            sceneid = response.xpath('//span[contains(text(), "Content ID:")]/following-sibling::text()[1]')
            print(f"    * Using Content_ID for: {sceneid.get().strip().upper()}")
            contentid = True
        if sceneid:
            item['id'] = sceneid.get().strip().upper()


        r18 = self.get_r18(item['id'])
        # ~ if contentid:
            # ~ print(r18)
        # ~ if item['id'] == 'HOWS-002':
        # ~ print(r18)
        r18image = False

        if r18:
            if r18['title']:
                item['title'] = string.capwords(self.uncensor(r18['title']))
            else:
                title = response.xpath('//h1[@class="lead"]/text()').get()
                if "[" in title and "]" in title:
                    title = re.sub(r'\[.*?\]', '', title)
                item['title'] = string.capwords(title)

            if r18['label'] and "name" in r18['label']:
                item['site'] = string.capwords(r18['label']['name'].replace(".", ""))
            else:
                site = response.xpath('//span[contains(text(), "Studio:")]/following-sibling::*/text()').getall()
                site = list(map(lambda x: string.capwords(x.strip()), site))
                if site:
                    site = list(filter(None, site))
                    item['site'] = string.capwords(site[0].replace(".", ""))

            if r18['maker'] and "name" in r18['maker']:
                item['parent'] = string.capwords(r18['maker']['name'].replace(".", ""))
            else:
                parent = response.xpath('//span[contains(text(), "Studio:")]/following-sibling::*/text()').getall()
                parent = list(map(lambda x: string.capwords(x.strip()), parent))
                if parent:
                    parent = list(filter(None, parent))
                    item['parent'] = string.capwords(parent[0].replace(".", ""))

            if item['parent'] and not item['site']:
                item['site'] = item['parent']
            if item['site'] and not item['parent']:
                item['parent'] = item['site']
            item['date'] = r18['release_date']

            r18image = False
            if r18['images']['jacket_image']['large'] and "http" in r18['images']['jacket_image']['large']:
                r18image = r18['images']['jacket_image']['large']
            elif r18['images']['jacket_image']['large2'] and "http" in r18['images']['jacket_image']['large2']:
                r18image = r18['images']['jacket_image']['large2']

            if r18['actresses']:
                for performer in r18['actresses']:
                    item['performers'].append(string.capwords(performer['name']))
            if not item['performers']:
                item['performers'] = response.xpath('//span[contains(text(), "Cast(s):")]/following-sibling::a/text()').getall()

            if r18['sample']:
                if r18['sample']['high']:
                    item['trailer'] = r18['sample']['high']

            if r18['categories']:
                for tag in r18['categories']:
                    item['tags'].append(string.capwords(tag['name']))

            if r18['director']:
                item['director'] = r18['director']

            if r18['runtime_minutes']:
                item['duration'] = str(int(r18['runtime_minutes']) * 60)

            item['url'] = f"https://r18.dev/videos/vod/movies/detail/-/id={r18['content_id']}/"
            item['network'] = 'R18'
        else:
            title = response.xpath('//h1[@class="lead"]/text()').get()
            if "[" in title and "]" in title:
                title = re.sub(r'\[.*?\]', '', title)
            item['title'] = string.capwords(title)

            if "director" in jsondata:
                director = string.capwords(re.search(r'director:.*?[\'\"](.*?)[\'\"]', jsondata).group(1))
            else:
                director = response.xpath('//span[contains(text(), "Director:")]/following-sibling::text()')
                if director:
                    director = string.capwords(director.get())

            scenedate = response.xpath('//span[contains(text(), "Release Date:")]/following-sibling::text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%d %b %Y']).strftime('%Y-%m-%d')

            if "casts" in jsondata:
                performers = re.search(r'casts:(.*?)\]', jsondata).group(1)
                item['performers'] = re.findall(r'name.*?[\'\"](.*?)[\'\"]', performers)
            else:
                item['performers'] = response.xpath('//span[contains(text(), "Cast(s):")]/following-sibling::a/text()').getall()

            duration = response.xpath('//span[contains(text(), "Duration:")]/following-sibling::text()')
            if duration:
                duration = re.search(r'(\d+)', duration.get())
                if duration:
                    item['duration'] = str(int(duration.group(1)) * 60)

            site = response.xpath('//span[contains(text(), "Studio:")]/following-sibling::*/text()').getall()
            site = list(map(lambda x: string.capwords(x.strip()), site))
            if site:
                site = list(filter(None, site))
                item['site'] = string.capwords(site[0].replace(".", ""))

            parent = response.xpath('//span[contains(text(), "Studio:")]/following-sibling::*/text()').getall()
            parent = list(map(lambda x: string.capwords(x.strip()), parent))
            if parent:
                parent = list(filter(None, parent))
                item['parent'] = string.capwords(parent[0].replace(".", ""))

            item['network'] = 'R18'

            item['url'] = f"https://r18.dev/videos/vod/movies/detail/-/id={re.sub('[^a-z0-9]', '', item['id'].lower())}"

        # ### Tasks for both sources

        if not item['parent'] or "---" in item['parent']:
            item['parent'] = item['site']

        if not item['site'] or "---" in item['site']:
            item['site'] = item['parent']

        # Strip the ID from the title, then re-add it in uppercase and without embellishments
        title = re.search(fr"{item['id']}(?:-\w+)? (.*)", item['title'].upper())
        if title:
            title = title.group(1)
            item['title'] = f"{item['id']}: {string.capwords(title)}"
        else:
            item['title'] = f"{item['id']}: {string.capwords(item['title'])}"

        # Get the Front and Back images from site, using R18 image if not available
        if "image" in jsondata:
            image = re.search(r'image.*?[\'\"](.*?)[\'\"]', jsondata)
            if image:
                image = unidecode.unidecode(html.unescape(image.group(1)))
        if not item['image'] and r18image:
            item['image'] = r18image

        item['image'] = item['image'].strip()
        if not item['image']:
            image = response.xpath('//meta[@property="og:image"]/@content')
            if image:
                item['image'] = image.get()

        # Get the blobs
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        # Add site tags to existing tags pulled from R18 if available

        if "categories" in jsondata:
            tags = re.search(r'categories:(.*?)\]', jsondata).group(1)
            tags = re.findall(r'name.*?[\'\"](.*?)[\'\"]', tags)
        else:
            tags = response.xpath('//span[contains(text(), "Categories:")]/following-sibling::*/text()').getall()

        if tags:
            tags = list(map(lambda x: codecs.decode(unidecode.unidecode(html.unescape(string.capwords(x.strip()))), 'unicode-escape'), tags))
            tags = list(filter(None, tags))
            for tag in tags:
                item['tags'].append(string.capwords(tag))

        matches = ['Actress Best', 'Exclusive', 'Featured', 'Foreign Imports', 'Hi-def', 'High-quality', 'Hours', 'Sample']
        for tag in item['tags']:
            for match in matches:
                if match.lower() in tag.lower():
                    item['tags'].remove(tag)

        item['performers_data'] = []
        if len(item['performers']):
            for place, performer in enumerate(item['performers']):
                hiragana = re.compile('[\u3040-\u309F]')
                performer = hiragana.sub('', performer)
                katakana = re.compile('[\u30A0-\u30FF]')
                performer = katakana.sub('', performer)
                CJK = re.compile('[\u4300-\u9faf]')
                performer = CJK.sub('', performer)

                performer = performer.replace("\n", "").replace("\n", "").replace("\n", "").strip()

                if performer != item['performers'][place]:
                    item['performers'][place] = performer

                if re.search(r'(\d{3})', performer):
                    item['performers'].remove(performer)
                elif re.search(r'[a-z0-9]{20,26}', performer.lower()):
                    item['performers'].remove(performer)
                else:
                    perf = {}
                    perf['name'] = performer
                    perf['extra'] = {}
                    perf['extra']['gender'] = "Female"
                    perf['network'] = item['network']
                    perf['site'] = item['network']
                    item['performers_data'].append(perf)

        # General purpose removal of any additonal tokens for image url
        if item['image']:
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['type'] = 'JAV'

        # ~ if contentid:
            # ~ print(item)
        if ("duration" not in item or not item['duration'] or int(item['duration']) > 3900) and item['site'] and item['title']:
            yield self.check_item(item, self.days)

    def get_r18(self, javid):
        javid = javid.replace("-", "").lower().strip()
        link = f"https://r18.dev/videos/vod/movies/detail/-/dvd_id={javid}/json"
        req = requests.get(link)
        if req:
            content = json.loads(req.content)
        else:
            content = False
        return content

    def uncensor(self, title):
        title = title.replace("A*****t", "Assault")
        title = title.replace("A****p", "Asleep")
        title = title.replace("A***e", "Abuse")
        title = title.replace("A****d", "Abused")
        title = title.replace("B***d", "Blood")
        title = title.replace("B**d", "Bled")
        title = title.replace("C***d", "Child")
        title = title.replace("C*ck", "Cock")
        title = title.replace("D******e", "Disgrace")
        title = title.replace("D***king", "Drinking")
        title = title.replace("D***k", "Drunk")
        title = title.replace("D**g", "Drug")
        title = title.replace("D*****d", "Drugged")
        title = title.replace("F*****g", "Forcing")
        title = title.replace("F***e", "Force")
        title = title.replace("G*******g", "Gangbang")
        title = title.replace("G******g", "Gangbang")
        title = title.replace("H*********n", "Humiliation")
        title = title.replace("H*******e", "Hypnotize")
        title = title.replace("H********d", "Hypnotized")
        title = title.replace("H*******m", "Hypnotism")
        title = title.replace("H**t", "Hurt")
        title = title.replace("I****t", "Incest")
        title = title.replace("K****p", "Kidnap")
        title = title.replace("K****r", "Killer")
        title = title.replace("K**l", "Kill")
        title = title.replace("K*d", "Kid")
        title = title.replace("L****a", "Lolita")
        title = title.replace("M************n", "Mother And Son")
        title = title.replace("M****t", "Molest")
        title = title.replace("P********t", "Passed Out")
        title = title.replace("P****h", "Punish")
        title = title.replace("R****g", "Raping")
        title = title.replace("R**e", "Rape")
        title = title.replace("R***d", "Raped")
        title = title.replace("RStepB****************r", "Stepbrother and Sister")
        title = title.replace("S*********l", "School Girl")
        title = title.replace("S**********s", "School Girls")
        title = title.replace("S********l", "Schoolgirl")
        title = title.replace("S*********s", "Schoolgirls")
        title = title.replace("S******g", "Sleeping")
        title = title.replace("S*****t", "Student")
        title = title.replace("S***e", "Slave")
        title = title.replace("S**t", "Scat")
        title = title.replace("S*******y", "Scatology")
        title = title.replace("Sch**l", "School")
        title = title.replace("StepM************n", "Stepmother and Son")
        title = title.replace("T******e", "Tentacle")
        title = title.replace("T*****e", "Torture")
        title = title.replace("U*********s", "Unconscious")
        title = title.replace("V*****e", "Violate")
        title = title.replace("V*******n", "Violation")
        title = title.replace("V*****t", "Violent")
        title = title.replace("Y********l", "Young Girl")
        title = title.replace("A*****t", "Assault")
        title = title.replace("a*****t", "assault")
        title = title.replace("a****p", "asleep")
        title = title.replace("a***e", "abuse")
        title = title.replace("a****d", "abused")
        title = title.replace("b***d", "blood")
        title = title.replace("b**d", "bled")
        title = title.replace("c***d", "child")
        title = title.replace("c*ck", "cock")
        title = title.replace("d******e", "disgrace")
        title = title.replace("d***king", "drinking")
        title = title.replace("d***k", "drunk")
        title = title.replace("d**g", "drug")
        title = title.replace("d*****d", "drugged")
        title = title.replace("f*****g", "forcing")
        title = title.replace("f***e", "force")
        title = title.replace("g*******g", "gangbang")
        title = title.replace("g******g", "gangbang")
        title = title.replace("h*********n", "humiliation")
        title = title.replace("h*******e", "hypnotize")
        title = title.replace("h********d", "hypnotized")
        title = title.replace("h*******m", "hypnotism")
        title = title.replace("h**t", "hurt")
        title = title.replace("i****t", "incest")
        title = title.replace("k****p", "kidnap")
        title = title.replace("k****r", "killer")
        title = title.replace("k**l", "kill")
        title = title.replace("k*d", "kid")
        title = title.replace("l****a", "lolita")
        title = title.replace("m************n", "mother and son")
        title = title.replace("m****t", "molest")
        title = title.replace("p********t", "passed out")
        title = title.replace("p****h", "punish")
        title = title.replace("r****g", "raping")
        title = title.replace("r**e", "rape")
        title = title.replace("r***d", "raped")
        title = title.replace("rstepb****************r", "stepbrother and sister")
        title = title.replace("s*********l", "school girl")
        title = title.replace("s********l", "schoolgirl")
        title = title.replace("s**********s", "school girls")
        title = title.replace("s*********s", "schoolgirls")
        title = title.replace("s******g", "sleeping")
        title = title.replace("s*****t", "student")
        title = title.replace("s***e", "slave")
        title = title.replace("s**t", "scat")
        title = title.replace("s*******y", "scatology")
        title = title.replace("sch**l", "school")
        title = title.replace("stepm************n", "stepmother and son")
        title = title.replace("t******e", "tentacle")
        title = title.replace("t*****e", "torture")
        title = title.replace("u*********s", "unconscious")
        title = title.replace("v*****e", "violate")
        title = title.replace("v*******n", "violation")
        title = title.replace("v*****t", "violent")
        title = title.replace("y********l", "young girl")

        return title

    def prep_item(self, item):
        item['title'] = ''
        item['date'] = ''
        item['description'] = ''
        item['image'] = ''
        item['image_blob'] = ''
        item['tags'] = []
        item['performers'] = []
        item['trailer'] = ''
        item['type'] = 'JAV'
        item['director'] = ''
        item['site'] = ''
        item['parent'] = ''
        item['network'] = ''

        return item

    def json_validate(self, input_str):
        founds = re.findall(r"{(?:[^{}]*{[^{]*})*[^{}]*}", input_str)
        valid_jsons = []
        for x in founds:
            try:
                valid_jsons.append(json.loads(x))
            except json.JSONDecodeError:
                continue

        return valid_jsons
