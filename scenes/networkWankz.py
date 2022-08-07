import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkWankzSpider(BaseSceneScraper):
    name = 'Wankz'
    network = "Wankz"

    url = 'https://www.wankz.com'

    start_urls = [
        'https://www.wankz.com',
        # ~ --------- Added for search compatibility
        # ~ 'https://www.360solos.com',
        # ~ 'https://www.4kdesire.com',
        # ~ 'https://www.allinterracial.com',
        # ~ 'https://www.bangamidget.com',
        # ~ 'https://www.bangmystepmom.com',
        # ~ 'https://www.bigtitslikebigdicks.com',
        # ~ 'https://www.blackfeetbootystreet.com',
        # ~ 'https://www.blowpatrol.com',
        # ~ 'https://www.bootystudio.com',
        # ~ 'https://www.borntoswing.com',
        # ~ 'https://www.brotherundercover.com',
        # ~ 'https://www.bubblymassage',
        # ~ 'https://www.cameltoehos.com',
        # ~ 'https://www.cfnmexposed.com',
        # ~ 'https://www.chickslovetoys.com',
        # ~ 'https://www.cougarsexclub.com',
        # ~ 'https://www.cumcoveredglasses.com',
        # ~ 'https://www.eastblocamateurs.com',
        # ~ 'https://www.ebonyinternal.com',
        # ~ 'https://www.escorttrick.com',
        # ~ 'https://www.exploited18.com',
        # ~ 'https://www.foodbangers.com',
        # ~ 'https://www.fuckingrobots.com',
        # ~ 'https://www.fuckthewhorehard.com',
        # ~ 'https://www.handjobharry.com',
        # ~ 'https://www.iameighteen.com',
        # ~ 'https://www.ilikeemwhite.com',
        # ~ 'https://www.lesbiansexcity.com',
        # ~ 'https://www.lesbiansistas.com',
        # ~ 'https://www.lesbotrick.com',
        # ~ 'https://www.makethemgag.com',
        # ~ 'https://www.matrixmodels.com',
        # ~ 'https://www.milfsearch.com',
        # ~ 'https://www.milfsexposed.com',
        # ~ 'https://www.mommyneedsmoney.com',
        # ~ 'https://www.mymilfboss.com',
        # ~ 'https://www.notsoinnocentteens.com',
        # ~ 'https://www.over40hardcore.com',
        # ~ 'https://www.pornstartryouts.com',
        # ~ 'https://www.rapvideoauditions.com',
        # ~ 'https://www.realblowjobauditions.com',
        # ~ 'https://www.realteenskissing.com',
        # ~ 'https://www.roundjuicybutts.com',
        # ~ 'https://www.sapphicsecrets.com',
        # ~ 'https://www.schoolgirlinternal.com',
        # ~ 'https://www.servicewhores.com',
        # ~ 'https://www.sexforgrades.com',
        # ~ 'https://www.sexycougars.com',
        # ~ 'https://www.spoiledslut.com',
        # ~ 'https://www.swallowforcash.com',
        # ~ 'https://www.teengirls.com',
        # ~ 'https://www.tightholesbigpoles.com',
        # ~ 'https://www.wankmywood.com',
        # ~ 'https://www.wanks3d.com',
        # ~ 'https://www.wankztv.com',
        # ~ 'https://www.whaletailn.com',
        # ~ 'https://www.wildmassage.com',
        # ~ 'https://www.xxxatwork.com',
        # ~ 'https://www.youngdirtylesbians.com',
        # ~ 'https://www.youngslutshardcore.com',
    ]

    paginations = [
        '/sites/teen-girls?p=%s',
        '/videos?p=%s#',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': "//div[@class='views']/span/text()",
        're_date': r'Added (\d{1,2} \w+,? \d{4})',
        'date_formats': ['%d %B %Y', '%d %B, %Y'],
        'image': '//a[@class="noplayer"]/img/@src',
        'performers': '//div[@class="models-wrapper actors"]/a/span/text()',
        'tags': "//a[@class='cat']/text()",
        'external_id': '-(\\d+)$',
        'trailer': '',
        'pagination': '/videos?p=%s#'
    }

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': pagination},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
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
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[@class='title-wrapper']/a/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[@class="inner"]/div/p/a[@class="sitelogom"]/img/@alt').get().strip()
        return site
