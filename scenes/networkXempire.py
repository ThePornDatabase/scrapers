import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

class XEmpireSpider(BaseSceneScraper):
    name = 'XEmpire'
    network = "XEmpire"

    start_urls = [
        'https://www.xempire.com'
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//meta[@name="twitter:description"]/@content',
        'date': "//div[@class='updatedDate']/b/following-sibling::text()",
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="sceneCol sceneColActors"]/a/text()',
        'tags': "//div[@class='sceneCol sceneColCategories']/a/text()",
        'external_id': '\\/xempire\\/.*\\/(\d+)',
        'trailer': '//meta[@name="twitter:player"]/@content',
        'pagination': '/en/videos/xempire/latest/%s#'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//div[@class='sceneContainer']/a/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
                
    def get_site(self, response):
        site = response.xpath('//meta[@name="twitter:domain"]/@content').get().strip()
        site = re.search('(.*)\.com', site).group(1)
        return site

    def get_trailer(self, response):
        trailer = re.search('\'Stream-HD-720p\'.*file=\"(.*?)\"\ size', response.text).group(1)
        trailer = "https://trailers-openlife.gammacdn.com" + trailer
        return trailer

# ~ // --------  Site Definition: Wankz  ---------------------
# ~ $definition['wankz']['quickname'] = "wankz";
# ~ $definition['wankz']['site'] = "https://www.wankz.com";
# ~ $definition['wankz']['addSite'] = TRUE;
# ~ $definition['wankz']['studio'] = "Wankz";
# ~ $definition['wankz']['initialUrl'] = "/videos";
# ~ $definition['wankz']['xpathOverall'] = '//div[@class="row scenes-list"]/div[@class="scene"]';
# ~ $definition['wankz']['xpathMediapage'] = 'div[@class="inner"]/div[@class="main-meta"]/div[@class="title-wrapper"]/a/@href';
# ~ $definition['wankz']['xpathNextpage'] = '//a[@class="next"]/@href';

# ~ $definition['wankz']['xpathTitle'] = '//title';
# ~ $definition['wankz']['xpathDate'] = '//div[@class="views"]/span';
# ~ $definition['wankz']['regexDate'] = '/Added\ (.*)/';
# ~ $definition['wankz']['dateOnIndex'] = FALSE;
# ~ $definition['wankz']['xpathSite'] = '//a[@class="sitelogom"]/following-sibling::a';
# ~ $definition['wankz']['xpathSceneid'] = '//div[@class="player-wrapper"]/@data-rmc';
# ~ $definition['wankz']['xpathGenres'] = '//span[contains(text(),"Categories")]/following-sibling::a';
# ~ $definition['wankz']['xpathModelsname'] = '//a[@class="model"]/span';

# ~ $definition['wankz']['xpathBackground'] = '//a[@class="noplayer"]/img/@src';
# ~ $definition['wankz']['xpathPlot'] = '//meta[@name="description"]/@content';
# ~ // =================================================================
