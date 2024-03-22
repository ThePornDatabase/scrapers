import re
import string
import requests
import scrapy
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class JavSEXTBSpider(BaseSceneScraper):
    name = 'JAVSEXTBPlaywright'

    start_url = 'https://sextb.net'

    paginations = [
        '/censored/pg-%s',
        '/uncensored/pg-%s',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'JAV',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': False,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "tray-item")]/a[1]/@href').getall()
        for scene in scenes:
            meta['id'] = re.search(r'.*/(.*?)$', scene).group(1)
            if re.search(r'(\w+-\w+)-\w+', meta['id']):
                meta['id'] = re.search(r'(\w+-\w+)-\w+', meta['id']).group(1)
            if meta['id'] and "ppv" not in meta['id'].lower():
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta = response.meta
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()
        item = self.prep_item(item)

        item['id'] = meta['id'].upper()

        r18 = self.get_r18(item['id'])
        if r18:
            if r18['title']:
                item['title'] = string.capwords(self.uncensor(r18['title']))
            else:
                title = response.xpath('//h1[@class="film-info-title"]/strong/text()[1]').get()
                if "[" in title and "]" in title:
                    title = re.sub(r'\[.*?\]', '', title)
                item['title'] = string.capwords(title)

            if r18['label'] and "name" in r18['label']:
                item['site'] = string.capwords(r18['label']['name'].replace(".", ""))
            if r18['maker'] and "name" in r18['maker']:
                item['parent'] = string.capwords(r18['maker']['name'].replace(".", ""))
            item['date'] = r18['release_date']

            r18image = False
            if r18['images']['jacket_image']['large'] and "http" in r18['images']['jacket_image']['large']:
                r18image = r18['images']['jacket_image']['large']
            elif r18['images']['jacket_image']['large2'] and "http" in r18['images']['jacket_image']['large2']:
                r18image = r18['images']['jacket_image']['large2']

            if r18['actresses']:
                for performer in r18['actresses']:
                    item['performers'].append(string.capwords(performer['name']))

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
            title = response.xpath('//h1[@class="film-info-title"]/strong/text()[1]').get()
            if "[" in title and "]" in title:
                title = re.sub(r'\[.*?\]', '', title)
            item['title'] = string.capwords(title)

            director = response.xpath('//i[@class="fa fa-user" and contains(./following-sibling::text(), "Director")]/following-sibling::a//text()|//i[@class="fa fa-user"]/following-sibling::strong/text()')
            if director:
                item['director'] = string.capwords(director.get())

            scenedate = response.xpath('//div[@class="description"]/i[@class="fa fa-calendar"]/following-sibling::strong/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            item['performers'] = response.xpath('//i[@class="fa fa-users" and contains(./following-sibling::text(), "Cast")]/following-sibling::a/strong/text()').getall()

            duration = response.xpath('//i[@class="fa fa-clock" and contains(./following-sibling::text(), "Runtime")]/following-sibling::strong/text()')
            if duration:
                duration = re.search(r'(\d+)', duration.get())
                if duration:
                    item['duration'] = str(int(duration.group(1)) * 60)

            site = response.xpath('//i[@class="fa fa-tag" and contains(./following-sibling::text(), "Label")]/following-sibling::a/strong/text()').getall()
            site = list(map(lambda x: string.capwords(x.strip()), site))
            if site:
                site = list(filter(None, site))
                item['site'] = string.capwords(site[0].replace(".", ""))

            parent = response.xpath('//i[@class="fa fa-camera" and contains(./following-sibling::text(), "Studio")]/following-sibling::a/strong/text()').getall()
            parent = list(map(lambda x: string.capwords(x.strip()), parent))
            if parent:
                parent = list(filter(None, parent))
                item['parent'] = string.capwords(parent[0].replace(".", ""))

            if not item['parent'] or "---" in item['parent']:
                item['parent'] = item['site']

            item['network'] = 'R18'

            item['url'] = f"https://r18.dev/videos/vod/movies/detail/-/id={re.sub('[^a-z0-9]', '', item['id'].lower())}"

        # ### Tasks for both sources

        # Strip the ID from the title, then re-add it in uppercase and without embellishments
        title = re.search(fr"{item['id']}(?:-\w+)? (.*)", item['title'].upper())
        if title:
            title = title.group(1)
            item['title'] = f"{item['id']}: {string.capwords(title)}"
        else:
            item['title'] = f"{item['id']}: {string.capwords(item['title'])}"

        # Verify we have both Site and Parent
        if item['parent'] and not item['site']:
            item['site'] = item['parent']
        if item['site'] and not item['parent']:
            item['parent'] = item['site']

        # Get the Front and Back images from site, using R18 image if not available
        item['image'] = response.xpath('//img[@class="cover"]/@src|//div[@id="trailer"]/video/@poster').get()
        if not item['image'] and r18image:
            item['image'] = r18image

        # Get the blobs
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        # Add site tags to existing tags pulled from R18 if available
        tags = response.xpath('//i[@class="fa fa-list" and contains(./following-sibling::text(), "Genre")]/following-sibling::a/strong/text()').getall()
        tags = list(map(lambda x: string.capwords(x.strip()), tags))
        tags = list(filter(None, tags))
        if tags:
            for tag in tags:
                item['tags'].append(string.capwords(tag))

        # General purpose removal of any additonal tokens for image url
        if item['image']:
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['type'] = 'JAV'

        if not item['duration'] or int(item['duration']) > 4200:
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
        title = title.replace("B***d", "Blood")
        title = title.replace("B**d", "Bled")
        title = title.replace("C***d", "Child")
        title = title.replace("C*ck", "Cock")
        title = title.replace("D******e", "Disgrace")
        title = title.replace("D***king", "Drinking")
        title = title.replace("D***k", "Drunk")
        title = title.replace("D**g", "Drug")
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
        title = title.replace("V*****t", "Violent")
        title = title.replace("Y********l", "Young Girl")
        title = title.replace("A*****t", "Assault")
        title = title.replace("a*****t", "assault")
        title = title.replace("a****p", "asleep")
        title = title.replace("a***e", "abuse")
        title = title.replace("b***d", "blood")
        title = title.replace("b**d", "bled")
        title = title.replace("c***d", "child")
        title = title.replace("c*ck", "cock")
        title = title.replace("d******e", "disgrace")
        title = title.replace("d***king", "drinking")
        title = title.replace("d***k", "drunk")
        title = title.replace("d**g", "drug")
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
