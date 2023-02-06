import re
import json
import html
import unidecode
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLittleCapriceJSONSpider(BaseSceneScraper):
    name = 'LittleCapriceJSON'
    network = 'Little Caprice Dreams'

    start_urls = [
        'https://www.littlecaprice-dreams.com'
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': "//article/div[@class='entry-content']//div[contains(@class,'et_section_regular')]//div[contains(@class,'et_pb_row_1-4_3-4')]//div[contains(@class,'et_pb_column_3_4')]//div[contains(@class,'et_pb_text')]/text()",
        'performers': '//div[contains(@class, "et_pb_text_align_left")]/ul/li[contains(., "Models")]/a/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '',
        'external_id': 'project/([a-z0-9-_]+)/?',
        'trailer': '',
        'pagination': 'https://www.littlecaprice-dreams.com/wp-json/wp/v2/project?per_page=10&page=%s'
    }

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # ~ 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
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
        tagdata = [{"id": 204728, "name": ".AWARD"}, {"id": 193215, "name": "afghanistan"}, {"id": 190901, "name": "american"}, {"id": 3029, "name": "anal"}, {"id": 207665, "name": "anal creampie"}, {"id": 206748, "name": "anal fingering"}, {"id": 206749, "name": "anal fisting"}, {"id": 207663, "name": "anal gaping"}, {"id": 207224, "name": "arabic"}, {"id": 190895, "name": "asian"}, {"id": 190877, "name": "australian"}, {"id": 190846, "name": "ball sucking"}, {"id": 207222, "name": "BehindTheScenes"}, {"id": 207669, "name": "belarus"}, {"id": 190869, "name": "big ass"}, {"id": 190847, "name": "big dick"}, {"id": 183692, "name": "big tits"}, {"id": 190867, "name": "black hair"}, {"id": 190902, "name": "blindfold"}, {"id": 207681, "name": "blond"}, {"id": 190831, "name": "blonde"}, {"id": 4007, "name": "blowjob"}, {"id": 190907, "name": "brazilian"}, {"id": 190837, "name": "brunette"}, {"id": 193225, "name": "butt plug"}, {"id": 190842, "name": "canadian"}, {"id": 207214, "name": "casting"}, {"id": 207038, "name": "chilenin"}, {"id": 207671, "name": "cock grinding"}, {"id": 190898, "name": "colombian"}, {"id": 143755, "name": "comedy"}, {"id": 193204, "name": "costume"}, {"id": 1214, "name": "couple sex"}, {"id": 190844, "name": "cowgirl"}, {"id": 24315, "name": "creampie"}, {"id": 193220, "name": "cuckold"}, {"id": 193240, "name": "cuckquean"}, {"id": 207677, "name": "cum eating"}, {"id": 190876, "name": "cum in mouth"}, {"id": 207683, "name": "cum on feets"}, {"id": 207670, "name": "cum on tits"}, {"id": 190891, "name": "cum swapping"}, {"id": 190838, "name": "czech"}, {"id": 190832, "name": "deep throat"}, {"id": 190839, "name": "dildo"}, {"id": 2388, "name": "dirty talk"}, {"id": 207685, "name": "doggy"}, {"id": 190843, "name": "doggy style"}, {"id": 207225, "name": "double blowjob"}, {"id": 179178, "name": "DP"}, {"id": 190882, "name": "ebony"}, {"id": 207221, "name": "EroticReport"}, {"id": 190860, "name": "face sitting"}, {"id": 190841, "name": "facial"}, {"id": 207682, "name": "feder games"}, {"id": 193139, "name": "femdom"}, {"id": 1215, "name": "fetish"}, {"id": 190874, "name": "ffm"}, {"id": 207603, "name": "fingering"}, {"id": 193119, "name": "food"}, {"id": 3197, "name": "foot fetish"}, {"id": 190893, "name": "foot job"}, {"id": 3518, "name": "foursome"}, {"id": 193123, "name": "french"}, {"id": 190887, "name": "german"}, {"id": 190872, "name": "girl on girl"}, {"id": 1212, "name": "group sex"}, {"id": 190863, "name": "hairy pussy"}, {"id": 190900, "name": "hand job"}, {"id": 190864, "name": "high heels"}, {"id": 207678, "name": "hitchhiking"}, {"id": 190885, "name": "hungarian"}, {"id": 190883, "name": "indonesian"}, {"id": 4023, "name": "interracial"}, {"id": 190866, "name": "italian"}, {"id": 190852, "name": "kinky"}, {"id": 190856, "name": "kissing"}, {"id": 190871, "name": "landing strip"}, {"id": 2375, "name": "latex"}, {"id": 206932, "name": "latino"}, {"id": 193116, "name": "latvian"}, {"id": 207672, "name": "leggings"}, {"id": 1216, "name": "lesbian"}, {"id": 190848, "name": "lingerie"}, {"id": 183763, "name": "livesex show"}, {"id": 3282, "name": "lowlight"}, {"id": 1211, "name": "masturbation"}, {"id": 190829, "name": "missionary"}, {"id": 193115, "name": "mmf"}, {"id": 207679, "name": "moldova"}, {"id": 190827, "name": "monkey"}, {"id": 190833, "name": "natural tits"}, {"id": 190904, "name": "netherlands"}, {"id": 193211, "name": "nylons"}, {"id": 179188, "name": "oil"}, {"id": 193242, "name": "oral sex"}, {"id": 207017, "name": "orgie"}, {"id": 207660, "name": "pantiehose"}, {"id": 207680, "name": "peruvian"}, {"id": 24178, "name": "pissing"}, {"id": 193122, "name": "polish"}, {"id": 183769, "name": "POV"}, {"id": 190868, "name": "prone bone"}, {"id": 207684, "name": "public"}, {"id": 185446, "name": "public sex"}, {"id": 190886, "name": "puffy nipples"}, {"id": 190834, "name": "pussy licking"}, {"id": 190875, "name": "pussy to mouth"}, {"id": 190896, "name": "raw"}, {"id": 190894, "name": "redhead"}, {"id": 190845, "name": "reverse cowgirl"}, {"id": 190849, "name": "riding"}, {"id": 193126, "name": "rimming"}, {"id": 190870, "name": "russian"}, {"id": 190873, "name": "serbian"}, {"id": 207212, "name": "sexlesson"}, {"id": 190835, "name": "shaved"}, {"id": 190861, "name": "sixty nine"}, {"id": 207184, "name": "slapping"}, {"id": 193202, "name": "sloppy blowjob"}, {"id": 190857, "name": "small tits"}, {"id": 193222, "name": "smoking"}, {"id": 183664, "name": "soft erotic"}, {"id": 131823, "name": "solo"}, {"id": 190897, "name": "spanish"}, {"id": 190865, "name": "spanking"}, {"id": 193463, "name": "spitting"}, {"id": 190855, "name": "spooning"}, {"id": 24246, "name": "squirting"}, {"id": 190892, "name": "standing doggy"}, {"id": 205886, "name": "stepbrother"}, {"id": 190677, "name": "strapOn"}, {"id": 190853, "name": "submissive"}, {"id": 183771, "name": "swingers"}, {"id": 190851, "name": "tattoo"}, {"id": 3517, "name": "threesome"}, {"id": 190854, "name": "tied"}, {"id": 190905, "name": "titty fuck"}, {"id": 207018, "name": "two cock blowjob"}, {"id": 190881, "name": "ukrainian"}, {"id": 206939, "name": "uruguayer"}, {"id": 207687, "name": "v"}, {"id": 190888, "name": "venezuelan"}, {"id": 190858, "name": "vibrator"}, {"id": 177677, "name": "Virtual Reality"}, {"id": 179189, "name": "water"}]

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.get_scenes, meta={'page': self.page, 'tagdata': tagdata, "playwright": True}, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        responsedata = re.sub(r'<[^<]+?>', '', response.text)
        meta = response.meta
        jsondata = json.loads(responsedata)
        for scene in jsondata:
            item = SceneItem()
            image_url = scene['_links']['wp:featuredmedia'][0]['href']
            item['id'] = str(scene['slug'])
            item['date'] = scene['date']
            item['title'] = self.clean_text(scene['title']['rendered'])
            item['trailer'] = None
            item['description'] = self.clean_text(scene['excerpt']['rendered'])
            if 'vc_raw_html' in item['description']:
                item['description'] = ''
            item['performers'] = []
            item['tags'] = []
            for projecttag in scene['project_tag']:
                for tag in meta['tagdata']:
                    if str(tag['id']) == str(projecttag):
                        item['tags'].append(tag['name'])
            item['site'] = 'Little Caprice Dreams'
            item['parent'] = 'Little Caprice Dreams'
            item['network'] = 'Little Caprice Dreams'
            item['url'] = scene['link']

            meta['item'] = item
            yield scrapy.Request(image_url, callback=self.get_image_link, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image_link(self, response):
        responsedata = re.sub(r'<[^<]+?>', '', response.text)
        item = response.meta['item']
        jsondata = json.loads(responsedata)

        item['image'] = jsondata['guid']['rendered']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        yield self.check_item(item, self.days)

    def clean_text(self, text):
        text = unidecode.unidecode(text)
        text = html.unescape(text).strip()
        text = unidecode.unidecode(text)
        text = re.sub(r'<[^<]+?>', '', text)
        return text
