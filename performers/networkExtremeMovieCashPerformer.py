import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'image': '//div[@class="profileimg"]/a/img/@src0_2x',
        'image_blob': True,
        'bio': '//div[@class="aboutmodel"]/p/text()',
        'astrology': '//text()[contains(., "Star Sign:")]/following-sibling::strong[1]/text()',
        'height': '//text()[contains(., "Height:")]/following-sibling::strong[1]/text()',
        'nationality': '//h2[contains(text(), "Country")]/strong/text()',

        'pagination': '/tour/models/%s/latest/',
        'external_id': r'model/(.*)/'
    }

    name = 'ExtremeMovieCashPerformer'
    network = 'Extreme Movie Pass'

    start_urls = [
        'https://www.amateur18.tv',
        'https://www.allthoseboobs.com', #New
        'https://www.allthosegirlfriends.com', #New
        'https://www.allthosegirls.com', #New
        'https://www.allthosemoms.com', #New
        'https://www.analfrench.com',
        'https://www.asianhotbunnies.com',
        'https://www.bangmyboobies.com', #New
        'https://www.bigbreast.tv',
        'https://www.bigmacky.com', #New
        'https://www.bizarix.com',
        'https://www.boundmybitch.com',
        'https://www.bosslesson.com',
        'https://www.brasilextreme.com',
        'https://www.brazilianerotic.com', #New
        'https://www.brazilpartyorgy.com',
        'https://www.bukkakeorgy.com', #New
        'https://www.candidcrush.com',
        'https://www.castingbunnies.com',
        'https://www.chubbyworlds.com', #New
        'https://www.crazybeauties.com',
        'https://www.crazyfetishpass.com',
        'https://www.crazymonstercock.com',
        'https://www.crazymouthmeat.com',
        'https://www.crazyoldmoms.com',
        'https://www.crazypeegirls.com',
        'https://www.crazypregnant.com', #New
        'https://www.crazyspandexgirls.com', #New
        'https://www.cumrotic.com', #New
        'https://www.czechsuperstars.com',
        'https://www.deep-throat.tv', #New
        'https://www.dildopenetrations.com', #New
        'https://www.dirtyclinic.com',
        'https://www.dirtyprivate.com',
        'https://www.dporgasm.com', #New
        'https://www.exgfsexxx.com', #New
        'https://www.extremetranny.com',
        'https://www.fetishtransformation.com', #New
        'https://www.firstanalteens.com',
        'https://www.fistingfiles.com', #New
        'https://www.flexiangels.com', #New
        'https://www.flexidolls.com', #New
        'https://www.flexifetishgirls.com', #New
        'https://www.frenchpickups.com', #New
        'https://www.fuckonstreet.com', #New
        'https://www.fuckthosechicks.com', #New
        'https://www.fuckthosemoms.com', #New
        'https://www.germanpickups.com', #New
        'https://www.germanstreets.com',
        'https://www.glamourinfetish.com', #New
        'https://www.goldwinpass.com', #New
        'https://www.grandpalove.com',
        'https://www.grannyguide.com', #New
        'https://www.herfirstkisses.com',
        'https://www.hotpartysex.com', #New
        'https://www.hotrubberbabes.com', #New
        'https://www.ilikehandjobs.com', #New
        'https://www.indianrealporn.com', #New
        'https://www.juicynudists.com',
        'https://www.kellyinspandex.com',  # Paywalled 2022-08-01
        'https://www.latinlesbea.com',
        'https://www.latinwildparties.com', #New
        'https://www.lederhosengangbang.com', #New
        'https://www.lookiamhairy.com',
        'https://www.lynnhd.com',
        'https://www.milfpower.com', #New
        'https://www.mountainfuckfest.com', #New
        'https://www.mybangvan.com', #New
        'https://www.naughtybi.com',
        'https://www.nylonworlds.com', #New
        'https://www.onlytaboo.com',
        'https://www.onlybreast.com', #New
        'https://www.pervertclips.com', #New
        'https://www.pornonstage.com',
        'https://www.povmovies.com', #New
        'https://www.preggolovers.com', #New
        'https://www.publiccrush.com',
        'https://www.purekisses.com', #New
        'https://www.purepee.com', #New
        'https://www.purolatinas.com',
        'https://www.realgangbangs.com', #New
        'https://www.realitytaboo.com',
        'https://www.realporn.xxx', #New
        'https://www.realteendolls.com', #New
        'https://www.realteenstars.com', #New
        'https://www.rioanal.com',
        'https://www.riobang.com',
        'https://www.safarisex.com', #New
        'https://www.sapphiclovers.com', #New
        'https://www.scandiporn.com', #New
        'https://www.scandalonstage.com', #New
        'https://www.schoolgirllust.com', #New
        'https://www.sexfair.xxx', #New
        'https://www.sexflexvideo.com', #New
        'https://www.sexycuckold.com',
        'https://www.slipperymassage.com', #New
        'https://www.smoke-city.com',
        'https://www.smokingbunnies.com', #New
        'https://www.spandexporn.com', #New
        'https://www.sweetpartychicks.com', #New
        'https://www.thiswife.com', #New
        'https://www.virtualxporn.com', #New
        'https://www.voyeurpapy.com', #New
        'https://www.whoresinpublic.com',
        'https://www.wildgroupsex.com', #New
        'https://www.wildgangbangs.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="modelimage"]/..')
        for performer in performers:
            name = performer.xpath('.//h3/a/text()').get()
            meta['name'] = self.cleanup_title(name)

            performer = performer.xpath('./div[1]/a/@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)
