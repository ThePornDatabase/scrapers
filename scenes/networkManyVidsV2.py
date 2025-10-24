"""
Scraper for ManyVids network.
If adding sites, please use the 'Manyvids: <site/performername>' format
This helps keep them together on the site without mixing in what are
usually more or less camgirls into the regular sites
"""
import re
import html
import json
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkManyVidsV2Spider(BaseSceneScraper):

    start_urls = [
        # ['Submissive Teen POV', False, '574529'],  # Seems to have gone away, leaving for reference
        ['A Taboo Fantasy', False, '1000286888'],
        ['Adult Candy Store', False, '694469'],
        ['BJ World', False, '1005948542'],
        ['Fuck Club', False, '1000159044'],
        ['IXXVICOM', False, '1000380769'],
        ['Jay Bank Presents', False, '806007'],
        ['Manyvids: 2 Drops Studio', False, '1003987502'],
        ['Manyvids: 420SexTime', False, '304591'],
        ['Manyvids: Aaliyah Yasin', True, '1007066939'],
        ['Manyvids: Aathenatheslut', False, '1002632830'],
        ['Manyvids: Aderes Quin', True, '1003312288'],
        ['Manyvids: Adult Candy Store', False, '694469'],  # Rework this, Dupes!
        ['Manyvids: Aery Tiefling', True, '1004557133'],
        ['Manyvids: Aiko Moe', True, '565287'],
        ['Manyvids: AimeeWavesXXX', True, '1004357188'],
        ['Manyvids: Alex Saint', True, '1002225814'],
        ['Manyvids: Alexa Pearl', True, '1000945715'],
        ['Manyvids: AlexBreeCooper', True, '1005544720'],
        ['Manyvids: Alexxxis89', True, '1002515519'],
        ['Manyvids: Alice Bong', True, '1002715079'],
        ['Manyvids: Alice Red', True, '1007208921'],
        ['Manyvids: Alice Stoner', True, '1005082413'],
        ['Manyvids: AliceNZ', False, '493690'],
        ['Manyvids: Alissa Foxy', True, '1005955692'],
        ['Manyvids: Alix Lynx', True, '30313'],
        ['Manyvids: Alli Leigh', True, '91512'],
        ['Manyvids: AlyXXperience', True, '76699'],
        ['Manyvids: AmandaToy', True, '1001529074'],
        ['Manyvids: Amarna Miller', True, '419612'],
        ['Manyvids: Amber Hallibell', True, '1004057036'],
        ['Manyvids: Andre Stone', True, '1005621092'],
        ['Manyvids: Andregotbars', True, '1005546662'],
        ['Manyvids: Andylynn Payne', True, '1002706590'],
        ['Manyvids: Angel Wicky', True, '1002218259'],
        ['Manyvids: Angelphub', True, '1004855103'],
        ['Manyvids: Angie Lynx', True, '1002061427'],
        ['Manyvids: Angie Noir', True, '34'],
        ['Manyvids: Anna Bell Peaks', True, '152830'],
        ['Manyvids: Antonio Mallorca', True, '1000358477'],
        ['Manyvids: Anya Olsen', True, '1002868639'],
        ['Manyvids: Arabelle Raphael', True, '353960'],
        ['Manyvids: ArgenDana', True, '1000732526'],
        ['Manyvids: Ashe Maree', True, '666099'],
        ['Manyvids: Ashley Alban', True, '102036'],
        ['Manyvids: AsiaXXXTour', False, '1004942285'],
        ['Manyvids: ASMRMaddy', True, '1004334654'],
        ['Manyvids: Athena Blaze', True, '4043'],
        ['Manyvids: Aurora Angel', True, '1004044394'],
        ['Manyvids: AuroraXoxo', True, '494106'],
        ['Manyvids: Azure Sky Films', False, '1001644775'],
        ['Manyvids: Babesafreak', True, '1004577792'],
        ['Manyvids: Babygirlhazel', True, '796862'],
        ['Manyvids: BadDragonSlayer', True, '1002931153'],
        ['Manyvids: BaileyLove6969', False, '1000594124'],
        ['Manyvids: Bambii Mercedes', True, '1000333268'],
        ['Manyvids: BangedProductionsXXX', False, '1001618574'],
        ['Manyvids: Baxters Blowies', False, '1004417786'],
        ['Manyvids: Bea York', True, '1000611142'],
        ['Manyvids: Bella Bates', True, '1004323423'],
        ['Manyvids: Bettie Bondage', True, '590705'],
        ['Manyvids: Billy Boston', True, '1001072949'],
        ['Manyvids: BlackpantherXXX', True, '1001027504'],
        ['Manyvids: Blake Blossom', True, '1003638619'],
        ['Manyvids: Blazed Brat', True, '1002996067'],
        ['Manyvids: Blissed XXX', False, '1000324638'],
        ['Manyvids: Blondelashes19', True, '1001067347'],
        ['Manyvids: BlowbyBlowAccts', False, '419500'],
        ['Manyvids: Bluberrydreams', True, '1004835717'],
        ['Manyvids: Blue Dream', True, '752777'],
        ['Manyvids: Boba_Bitch', True, '1003445334'],
        ['Manyvids: Brad Newman XXX', True, '1001824648'],
        ['Manyvids: Brandibabes', False, '1003828607'],
        ['Manyvids: Brazilian Girl', True, '1003088114'],
        ['Manyvids: Brea Rose', True, '1000024307'],
        ['Manyvids: Brett TylerXXX', False, '1004700026'],
        ['Manyvids: Britney Amber', True, '1003387859'],
        ['Manyvids: Brittanythingoz', True, '1006754881'],
        ['Manyvids: Brooke Dillinger', True, '376796'],
        ['Manyvids: Brooklyn Springvalley', True, '1001853938'],
        ['Manyvids: BuniBun', True, '49000'],
        ['Manyvids: CallMeBabyBlue', True, '1004603307'],
        ['Manyvids: Carmita Bonita', True, '30655'],
        ['Manyvids: Carol Cox', True, '130540'],
        ['Manyvids: Casey Calvert', True, '1003999309'],
        ['Manyvids: Cassie Clarke', True, '1001062063'],
        ['Manyvids: Cassie0pia', True, '1000447514'],
        ['Manyvids: Catching Gold Diggers', False, '1002481658'],
        ['Manyvids: Cattie', False, '312711'],
        ['Manyvids: Ceres Clouds', True, '1002771463'],
        ['Manyvids: Chad Alva', True, '1000107977'],
        ['Manyvids: Chad Diamond', True, '577547'],
        ['Manyvids: Chanel Santini', True, '1000344210'],
        ['Manyvids: Chantal Owens', True, '1002667100'],
        ['Manyvids: Charlette Webb', True, '35990'],
        ['Manyvids: Cherry Crush', True, '32539'],
        ['Manyvids: Cherry Fae', False, '110767'],
        ['Manyvids: Chezza Luna', True, '177172'],
        ['Manyvids: Chris And Mari', False, '1004131603'],
        ['Manyvids: Ciren Verde', True, '1002613557'],
        ['Manyvids: Cmbprod', True, '1003696960'],
        ['Manyvids: Codi Vore', True, '574802'],
        ['Manyvids: Courtney Scott', True, '273124'],
        ['Manyvids: CrazyBella', True, '327770'],
        ['Manyvids: CreamBerryFairy', True, '1002527905'],
        ['Manyvids: CuckoldingMILF', False, '1002431767'],
        ['Manyvids: CumSlutJenna', True, '1006212286'],
        ['Manyvids: CutieElly', False, '1002778789'],
        ['Manyvids: Daddys Rozay', True, '1002023399'],
        ['Manyvids: Daisy Haze', True, '261301'],
        ['Manyvids: Daniela Agudelo', True, '1007087745'],
        ['Manyvids: Danielle Maye', True, '175486'],
        ['Manyvids: Danny Blaq Videos', False, '1005150544'],
        ['Manyvids: DarkBerry101', True, '1005336509'],
        ['Manyvids: Darya Jane', True, '1001356544'],
        ['Manyvids: Dawns Place', False, '1000657719'],
        ['Manyvids: Delphoxi', True, '375644'],
        ['Manyvids: Denali Dink Lu', True, '202192'],
        ['Manyvids: Desiree Dulce', True, '1000078988'],
        ['Manyvids: Desiree Woods', True, '1004061955'],
        ['Manyvids: Destination Kat', True, '426738'],
        ['Manyvids: Destiny Diaz', True, '109770'],
        ['Manyvids: Diane Andrews', True, '320527'],
        ['Manyvids: Diane Chrystall', True, '1000621105'],
        ['Manyvids: Dinkybum', False, '1001648874'],
        ['Manyvids: Dirty Princess', False, '325962'],
        ['Manyvids: DirtyGardenGirl', False, '510633'],
        ['Manyvids: DoggVisionXL', False, '1000198417'],
        ['Manyvids: Dolli Doll', True, '1000962160'],
        ['Manyvids: Dolly Mattel', True, '1000250991'],
        ['Manyvids: Domino Faye', True, '100072'],
        ['Manyvids: Doschers Production', False, '1004463898'],
        ['Manyvids: Dotadasp', False, '1005469404'],
        ['Manyvids: Dr. K In LA', False, '1003399990'],
        ['Manyvids: EastCoastXXX', False, '1000457016'],
        ['Manyvids: eliskye', True, '223595'],
        ['Manyvids: Ellie Skyes', True, '1004933109'],
        ['Manyvids: Elunaxc', False, '379389'],
        ['Manyvids: Emilia Song', True, '487827'],
        ['Manyvids: Emily Grey', True, '312043'],
        ['Manyvids: Emmas Secret Life', False, '577443'],
        ['Manyvids: Erica Cherry', True, '1002519245'],
        ['Manyvids: Eva Long', True, '1002576385'],
        ['Manyvids: Evie Rees', True, '1000468027'],
        ['Manyvids: Facial King Pro', False, '1001204864'],
        ['Manyvids: Fay Valentine', True, '1001627467'],
        ['Manyvids: Felicia Vox', True, '321754'],
        ['Manyvids: Fell On Productions', False, '456897'],
        ['Manyvids: FFeZine', False, '1000045578'],
        ['Manyvids: Fiery Redhead', False, '527041'],
        ['Manyvids: Fiona Dagger', True, '759730'],
        ['Manyvids: Fishnet Housepet', True, '222290'],
        ['Manyvids: FitSid', False, '1002419479'],
        ['Manyvids: Florida Milf', True, '1003205269'],
        ['Manyvids: Forbidden Perversions', False, '599647'],
        ['Manyvids: ForbiddenFruitsFilms', False, '1004388117'],
        ['Manyvids: Freya Fields', True, '1001935270'],
        ['Manyvids: FreyaJade', False, '1001673578'],
        ['Manyvids: Funaussiecouple', False, '1003446430'],
        ['Manyvids: Funsizedcumslut', True, '1007113302'],
        ['Manyvids: Gala MV', True, '830429'],
        ['Manyvids: Gia OhMy', True, '1003519826'],
        ['Manyvids: Gin Lustig', True, '1006293001'],
        ['Manyvids: Ginger Banks', True, '37055'],
        ['Manyvids: GirlOnTop880', True, '1004830774'],
        ['Manyvids: Goddess Tangent', False, '427284'],
        ['Manyvids: Godmother The Great', True, '228889'],
        ['Manyvids: Gogofukmexxx', False, '1002219117'],
        ['Manyvids: Golden Lace', True, '1002587264'],
        ['Manyvids: Goldie Blair', True, '380752'],
        ['Manyvids: Haley420', True, '427284'],
        ['Manyvids: Halfwin', True, '1003125256'],
        ['Manyvids: HannahJames710', False, '1000105196'],
        ['Manyvids: Hannibal Damage', False, '1002514329'],
        ['Manyvids: Haunter Hexx', True, '196439'],
        ['Manyvids: Haylee Love', True, '1000304351'],
        ['Manyvids: HayleeX', True, '203233'],
        ['Manyvids: Hazel Lush', True, '1002921386'],
        ['Manyvids: Hazel Simone', True, '1002202911'],
        ['Manyvids: Heather Vahn', True, '1000228944'],
        ['Manyvids: Heatherbby', True, '88086'],
        ['Manyvids: Hello Alice', True, '1005562667'],
        ['Manyvids: Hidori', True, '97815'],
        ['Manyvids: Holland of Chicago', True, '1003631211'],
        ['Manyvids: Hope Penetration', True, '1004890226'],
        ['Manyvids: Hornnstudio', False, '1003146686'],
        ['Manyvids: Horny Lily', True, '1000862654'],
        ['Manyvids: Hottalicia1', False, '1000447453'],
        ['Manyvids: HouseholdFantasy', False, '1007157741'],
        ['Manyvids: HugeBoobsErin', True, '1001183502'],
        ['Manyvids: Icy Winters', True, '697815'],
        ['Manyvids: Im Heather Harmon', False, '1003667583'],
        ['Manyvids: ImMeganLive', True, '491714'],
        ['Manyvids: IndiscreetHotAndFit', True, '1005093292'],
        ['Manyvids: InkedMonster', True, '1001576946'],
        ['Manyvids: ItsReeseRobins', False, '1005302009'],
        ['Manyvids: Ivy Starshine', True, '362540'],
        ['Manyvids: Izzy Rosse', True, '1005964496'],
        ['Manyvids: Jack and Jill', False, '1001495638'],
        ['Manyvids: Jack Blaque', True, '536056'],
        ['Manyvids: Jack Ripher', True, '1001692458'],
        ['Manyvids: Jackie Synn', True, '194026'],
        ['Manyvids: Jada Kai', True, '1000722201'],
        ['Manyvids: Jade Vow', True, '1002042328'],
        ['Manyvids: JadedJuneBug', True, '1007315738'],
        ['Manyvids: Jane Cane', True, '1000718761'],
        ['Manyvids: Jane Judge', True, '1000197274'],
        ['Manyvids: Jasper Nyx', True, '1003787164'],
        ['Manyvids: Jaybbgirl', True, '1001317123'],
        ['Manyvids: JaySmoothXXX', False, '525062'],
        ['Manyvids: Jenna Creed', True, '1001071635'],
        ['Manyvids: Jenni Knight', True, '1000534648'],
        ['Manyvids: Jeri Lynn', True, '13343'],
        ['Manyvids: Jewelz Blu', True, '1002322838'],
        ['Manyvids: Jill Kassidy', True, '1001466952'],
        ['Manyvids: Jodi West', True, '1004388132'],
        ['Manyvids: JohnnyGotBlown', False, '1006247385'],
        ['Manyvids: Joshua Lewis', True, '1004083778'],
        ['Manyvids: Julie Snow', True, '1000053441'],
        ['Manyvids: Just Bondage Sex', False, '341832'],
        ['Manyvids: KalicoKats', False, '1005848363'],
        ['Manyvids: Kalina Ryu', True, '815701'],
        ['Manyvids: Karabella', False, '1000456360'],
        ['Manyvids: KarmannAndJosie', False, '1006611324'],
        ['Manyvids: Kate Kuray', True, '1002855322'],
        ['Manyvids: Kathia Nobili', True, '1003527333'],
        ['Manyvids: Kati3kat', True, '354103'],
        ['Manyvids: Katie Cummings', True, '1000489998'],
        ['Manyvids: Katilingus', False, '1005141746'],
        ['Manyvids: Katy_Ann_XO', False, '1002032691'],
        ['Manyvids: Kayle Oralglory', True, '1003232260'],
        ['Manyvids: KCupQueen', True, '1002249501'],
        ['Manyvids: Keri Berry', True, '486227'],
        ['Manyvids: Kiittenymph', False, '1000856699'],
        ['Manyvids: Kiki Cali', True, '1001238534'],
        ['Manyvids: KimberleyJx', True, '1001389615'],
        ['Manyvids: Kimberly Kane', True, '539280'],
        ['Manyvids: Kimi The Milf Mommy', True, '1002484950'],
        ['Manyvids: KinkDevice', False, '528213'],
        ['Manyvids: Kitsune_foreplay', True, '1003162974'],
        ['Manyvids: Kitty Darlingg', True, '491411'],
        ['Manyvids: Knightfetish', False, '1000666199'],
        ['Manyvids: Korina Kova', True, '1000151926'],
        ['Manyvids: KorpseKitten', True, '1000416688'],
        ['Manyvids: Krissy Lynn', True, '65682'],
        ['Manyvids: Kristen Wylde', True, '1002217501'],
        ['Manyvids: Ksu Colt', True, '1001211849'],
        ['Manyvids: Kyutty', True, '1002643188'],
        ['Manyvids: LaceyinLaLaLand', False, '1002200110'],
        ['Manyvids: Lain Arbor', True, '1002265267'],
        ['Manyvids: lalunalewd', True, '1001996011'],
        ['Manyvids: Lana Rain', True, '214657'],
        ['Manyvids: Lani Lust', True, '1001830287'],
        ['Manyvids: Lanie Love', True, '54610'],
        ['Manyvids: Lara Loxley', True, '513312'],
        ['Manyvids: Laura King', True, '1003025690'],
        ['Manyvids: Lauryn Mae', True, '1005161332'],
        ['Manyvids: Lea Childs', True, '465703'],
        ['Manyvids: Leah Meow', True, '1002460913'],
        ['Manyvids: Leena Mae', True, '1001513306'],
        ['Manyvids: Legendarylootz', True, '1001194277'],
        ['Manyvids: Leina Sex', True, '1000278547'],
        ['Manyvids: Lena Paul', True, '541454'],
        ['Manyvids: Lena Spanks', True, '216064'],
        ['Manyvids: Lewdest Bunnie', True, '1005049819'],
        ['Manyvids: Lexa Lite', True, '1002827259'],
        ['Manyvids: Lexi Lore', True, '1001311376'],
        ['Manyvids: Lexxxi Luxe', True, '826394'],
        ['Manyvids: Lia Lennice', True, '1003079099'],
        ['Manyvids: Lilcanadiangirl', True, '683542'],
        ['Manyvids: Lilijunex', True, '1006854117'],
        ['Manyvids: Lilith Petite', True, '1000322028'],
        ['Manyvids: Lily DeMure', True, '1001103504'],
        ['Manyvids: LilyGaia', False, '301576'],
        ['Manyvids: Lissie Belle', True, '549738'],
        ['Manyvids: Little Miss Elle', True, '65933'],
        ['Manyvids: Little Puck', True, '419692'],
        ['Manyvids: LittleBunnyB', True, '1003962281'],
        ['Manyvids: Littleredheadlisa', True, '1003426440'],
        ['Manyvids: LittleSubGirl', True, '358347'],
        ['Manyvids: Lola Rose', True, '1001106526'],
        ['Manyvids: Lola Tessa', True, '1001749834'],
        ['Manyvids: LongHairLuna', True, '1004473027'],
        ['Manyvids: Loollypop24', True, '388869'],
        ['Manyvids: Loren Aprile', True, '1004728288'],
        ['Manyvids: Loretta Rose', True, '556632'],
        ['Manyvids: Lourdes Noir', True, '1001422207'],
        ['Manyvids: Lovely Lilith', True, '105450'],
        ['Manyvids: Lucy Hyde', True, '1001152130'],
        ['Manyvids: Luke Cooper', True, '1003079493'],
        ['Manyvids: Lulu Blue x', True, '590554'],
        ['Manyvids: Luna Roulette', True, '1002865441'],
        ['Manyvids: Lusciousx Luci', True, '1004732742'],
        ['Manyvids: Lydiagh0st', True, '1002402449'],
        ['Manyvids: Made In Canarias', True, '1000567799'],
        ['Manyvids: Madison Volt', True, '1002671662'],
        ['Manyvids: Maggie Rose xo', True, '1004575017'],
        ['Manyvids: Makayla Divine', True, '257117'],
        ['Manyvids: Mama Fiona', True, '1002612831'],
        ['Manyvids: Mandy Lohr', True, '297983'],
        ['Manyvids: Marcelin Abadir', True, '1002345908'],
        ['Manyvids: Marica Hase', True, '1000297683'],
        ['Manyvids: MaryVincXXX', False, '1003915918'],
        ['Manyvids: Mathema Kitten', True, '1002619397'],
        ['Manyvids: Mazee The Goat', True, '1002835239'],
        ['Manyvids: Melody Radford', True, '1002621425'],
        ['Manyvids: MelodyFluffington', True, '1004951413'],
        ['Manyvids: Mia Jocelyn', True, '1001682538'],
        ['Manyvids: Mila Swift', True, '1000233506'],
        ['Manyvids: MILF Katie', True, '1001106384'],
        ['Manyvids: Mindi Mink', True, '498847'],
        ['Manyvids: Miss Ellie', True, '1000833600'],
        ['Manyvids: Miss Lith Domina', True, '1002157606'],
        ['Manyvids: Miss Malorie Switch', True, '1003548829'],
        ['Manyvids: Miss Something', True, '1003843130'],
        ['Manyvids: MissEllieMouse', True, '1004033350'],
        ['Manyvids: MissHowl', True, '1000161593'],
        ['Manyvids: MissPrincessKay', True, '1001213579'],
        ['Manyvids: MissReinaT', True, '355416'],
        ['Manyvids: Missvioletstarr', True, '454320'],
        ['Manyvids: Mistress Rola', True, '1003520896'],
        ['Manyvids: MistressT', True, '1000997612'],
        ['Manyvids: Mohawk Molly', True, '329268'],
        ['Manyvids: Molly Darling', True, '1002604886'],
        ['Manyvids: Molly Redwolf', True, '1003298627'],
        ['Manyvids: Mona Wales', True, '345718'],
        ['Manyvids: MonsterMales', False, '209009'],
        ['Manyvids: Mr Adventure', False, '1006795494'],
        ['Manyvids: MrCooperXXX', False, '1000512688'],
        ['Manyvids: Mrs Betty Darling', True, '1005741190'],
        ['Manyvids: Mrs Mischief', True, '1004207044'],
        ['Manyvids: Ms Mysty', True, '1003127950'],
        ['Manyvids: Ms Price', False, '1001474586'],
        ['Manyvids: My Secret Life POV', False, '1005434394'],
        ['Manyvids: Mylene', True, '620931'],
        ['Manyvids: MyLittleSwallow', True, '1004225528'],
        ['Manyvids: Mymindbreaks', False, '1002745086'],
        ['Manyvids: Nalabrooksxxx', False, '1005934130'],
        ['Manyvids: Natalia Grey', True, '69353'],
        ['Manyvids: Natalie Mars', True, '1000035308'],
        ['Manyvids: Natalie Wonder', True, '1001768929'],
        ['Manyvids: Natasha Nice', True, '1000592171'],
        ['Manyvids: Natasha Nixx', True, '1002393375'],
        ['Manyvids: Natashas Bedroom', False, '375403'],
        ['Manyvids: Naughty Midwest Girls', False, '518153'],
        ['Manyvids: NaughtyBoyPOV', False, '454725'],
        ['Manyvids: Nicole Belle', True, '1000182655'],
        ['Manyvids: Nicole Doshi', True, '1002698505'],
        ['Manyvids: Nicole Nabors', True, '1002818112'],
        ['Manyvids: Nicole Riley', True, '30108'],
        ['Manyvids: Nicolebun', True, '1003188552'],
        ['Manyvids: Nikki Hugs', True, '1003352035'],
        ['Manyvids: Nikkiandleigh', False, '1000199434'],
        ['Manyvids: Nina Crowne', True, '196659'],
        ['Manyvids: Nova Patra', True, '407165'],
        ['Manyvids: Numi R', True, '1000071471'],
        ['Manyvids: Nyxi Leon', True, '1000696554'],
        ['Manyvids: Octokuro', True, '1003906145'],
        ['Manyvids: ohaiNaomi', True, '115565'],
        ['Manyvids: OhItsEmmaRose', False, '1003513574'],
        ['Manyvids: Olive Glass', True, '1005338874'],
        ['Manyvids: Olive Wood', True, '124871'],
        ['Manyvids: Olivia Robin', True, '1003562970'],
        ['Manyvids: OmankoVivi', False, '217682'],
        ['Manyvids: Ondrea Lee', True, '1000452244'],
        ['Manyvids: OnlyOneRhonda', True, '1002756755'],
        ['Manyvids: oopepperoo', True, '83782'],
        ['Manyvids: Oralsonly', False, '1002463312'],
        ['Manyvids: OUSweetheart', False, '106308'],
        ['Manyvids: Owen Gray', True, '184119'],
        ['Manyvids: Paige Steele', True, '1001123043'],
        ['Manyvids: Peachy Skye', True, '1002980475'],
        ['Manyvids: Peachypoppy', True, '1004271325'],
        ['Manyvids: Pearl Sage', True, '1001978110'],
        ['Manyvids: Penny Barber', True, '147843'],
        ['Manyvids: Penny Loren', True, '1003964373'],
        ['Manyvids: Pepperanncan', False, '1004243978'],
        ['Manyvids: Petite Nymphet', True, '1000213623'],
        ['Manyvids: Phatassedangel69', True, '1003179211'],
        ['Manyvids: Pierbi', True, '1003981229'],
        ['Manyvids: Pink Drip', True, '1002498762'],
        ['Manyvids: Playfulsolesandtoes', False, '1003888651'],
        ['Manyvids: PocketRocketMimi', False, '1005551091'],
        ['Manyvids: Poppy', True, '1000351267'],
        ['Manyvids: Princess Berpl', True, '215156'],
        ['Manyvids: Princess Leia', True, '38793'],
        ['Manyvids: Princess SpunkMuffin', True, '2178'],
        ['Manyvids: Puertorockxxx20', False, '1004190164'],
        ['Manyvids: PuppyGirlfriend', True, '1003012316'],
        ['Manyvids: Purple Bitch', True, '1000691111'],
        ['Manyvids: PurpleHailStorm', False, '1001941212'],
        ['Manyvids: Rachel Rivers', True, '1002522994'],
        ['Manyvids: Rae Knight', True, '528941'],
        ['Manyvids: Rainbowslut', True, '1001147312'],
        ['Manyvids: Raquel Roper', True, '380172'],
        ['Manyvids: RavenAlternative', True, '1004995688'],
        ['Manyvids: Rayray Sugarbutt', True, '1003235455'],
        ['Manyvids: Reagan Foxx', True, '167615'],
        ['Manyvids: Rebel Rhyder', True, '1002507133'],
        ['Manyvids: Reislin', True, '1002133241'],
        ['Manyvids: Reya Reign', True, '1000038417'],
        ['Manyvids: Rhea Sweet', True, '1000532441'],
        ['Manyvids: RhiannonRyder1995', False, '1000829435'],
        ['Manyvids: Riley Jacobs', True, '1002621197'],
        ['Manyvids: Robin Mae', True, '159708'],
        ['Manyvids: Rocky Emerson', True, '1000919840'],
        ['Manyvids: Rookie Stray', True, '1002499478'],
        ['Manyvids: Rosella Extrem', True, '1000095372'],
        ['Manyvids: Roxy Cox', True, '1000040846'],
        ['Manyvids: Ryland BabyLove', True, '559827'],
        ['Manyvids: Sabina Steele', True, '1004045902'],
        ['Manyvids: SaintVirginPro', False, '1005258725'],
        ['Manyvids: Sally Dangelo', True, '522512'],
        ['Manyvids: Samantha Rone', True, '547430'],
        ['Manyvids: Sammi Starfish', True, '1002592624'],
        ['Manyvids: Sammie Cee', True, '12694'],
        ['Manyvids: Sasha V', True, '782826'],
        ['Manyvids: Sashalikescats', False, '1004550238'],
        ['Manyvids: Scarlet Chase', True, '1003854828'],
        ['Manyvids: Scarlet Ellie', True, '1002529193'],
        ['Manyvids: ScarletteD_xo', False, '1004774961'],
        ['Manyvids: Selena Ryan', True, '1003640378'],
        ['Manyvids: Senorita Satan', False, '1002214325'],
        ['Manyvids: Sexy Aymee', True, '361688'],
        ['Manyvids: Sheena Shaw', True, '479557'],
        ['Manyvids: Shina Ryen', True, '1000039650'],
        ['Manyvids: Shiri Allwood', True, '1000135912'],
        ['Manyvids: Sia Siberia', True, '1001301396'],
        ['Manyvids: Siena Rose', True, '1001836304'],
        ['Manyvids: Siri Dahl', True, '1809'],
        ['Manyvids: Sissy Joyce', True, '1000133567'],
        ['Manyvids: Sloansmoans', True, '1004407943'],
        ['Manyvids: Slut Me Out Now', False, '1004385584'],
        ['Manyvids: Smiles of Sally', False, '1001368680'],
        ['Manyvids: Smithmyth123', False, '1004691906'],
        ['Manyvids: Smolbabsie', True, '1002794183'],
        ['Manyvids: Sofie Skye', True, '1003904073'],
        ['Manyvids: Sola Zola', True, '1002319155'],
        ['Manyvids: Soleil Succubus', True, '430494'],
        ['Manyvids: Sonya Vibe', True, '1003672212'],
        ['Manyvids: Sophia Wolfe', True, '1003445498'],
        ['Manyvids: Sophie Ladder', True, '1001417413'],
        ['Manyvids: Starryfawnn', True, '1005896761'],
        ['Manyvids: Stirling Cooper', True, '1000635912'],
        ['Manyvids: Submissive Lexi', True, '251896'],
        ['Manyvids: Sugary_Kitty', True, '1005790100'],
        ['Manyvids: Sukisukigirl', True, '1000933793'],
        ['Manyvids: Summer Fox', True, '1003834874'],
        ['Manyvids: Sweet Bunny', True, '1002468421'],
        ['Manyvids: Sweetalienbunny', True, '1003132653'],
        ['Manyvids: Sweetie Fox', True, '1003004427'],
        ['Manyvids: Swineys ProAm', False, '1000512833'],
        ['Manyvids: Sybil Raw', True, '1004472635'],
        ['Manyvids: Sydney Harwin', True, '1001213004'],
        ['Manyvids: Taboo Saga', False, '1002555505'],
        ['Manyvids: Tara Tainton', True, '1005123610'],
        ['Manyvids: Tatum Christine', True, '208703'],
        ['Manyvids: Tdot Produxxxion', False, '1003577926'],
        ['Manyvids: TentacleBimbo', True, '1005797593'],
        ['Manyvids: Texas MILF POV', False, '1003881589'],
        ['Manyvids: ThaiGyaru', True, '1007502059'],
        ['Manyvids: ThaiNymph', True, '1005503479'],
        ['Manyvids: ThaiSprite', True, '1006075221'],
        ['Manyvids: The Forest Dame', True, '1003781256'],
        ['Manyvids: The MANDINGO Club', False, '1002768577'],
        ['Manyvids: The Queen Lanie', True, '1000675514'],
        ['Manyvids: The TS Slayer', True, '1003918598'],
        ['Manyvids: TheFleshMechanic', False, '1006773354'],
        ['Manyvids: TheGorillaGrip', True, '1004893370'],
        ['Manyvids: TheLedaLotharia', False, '1002735612'],
        ['Manyvids: TheLunaLain', False, '1000129127'],
        ['Manyvids: TheSophieJames', False, '1004485402'],
        ['Manyvids: THEYLOVEFLAXK', False, '1002980236'],
        ['Manyvids: ThisIsFuckingFun', False, '1002856023'],
        ['Manyvids: Tigger Rosey', True, '716969'],
        ['Manyvids: Tindra Frost', True, '1000557912'],
        ['Manyvids: Tommy Wood', True, '1002812736'],
        ['Manyvids: Tori Easton', True, '1004225310'],
        ['Manyvids: TracyFem', True, '1001951761'],
        ['Manyvids: Trisha Moon', True, '1005854378'],
        ['Manyvids: Tweetney', True, '1000764908'],
        ['Manyvids: Valerica Steele', True, '1003823837'],
        ['Manyvids: Vanessa Veracruz', True, '1001516727'],
        ['Manyvids: Vanniall', True, '1002371854'],
        ['Manyvids: VenusAngelic', True, '1004017225'],
        ['Manyvids: Vera1995', False, '286187'],
        ['Manyvids: Veruca James', True, '673872'],
        ['Manyvids: Vina Sky', True, '1003572193'],
        ['Manyvids: Vince May Video', False, '1003424183'],
        ['Manyvids: Violet Myers', True, '1002190635'],
        ['Manyvids: Virgo Peridot', True, '176608'],
        ['Manyvids: Vitaduplez', True, '1003468856'],
        ['Manyvids: Vixenxmoon', True, '1001075493'],
        ['Manyvids: Wagabang', False, '1006541429'],
        ['Manyvids: WCA Productions', False, '602138'],
        ['Manyvids: Winterxxdoll', False, '1004591966'],
        ['Manyvids: xxxCaligulaxxx', True, '150576'],
        ['Manyvids: xxxmultimediacom', False, '1001803967'],
        ['Manyvids: Yogabella', True, '1001244409'],
        ['Manyvids: Youngandadorbs', True, '1000964738'],
        ['Manyvids: Yourboyfcisco', False, '1002986872'],
        ['Manyvids: YourLittleAngel', False, '1001186725'],
        ['Manyvids: Zac Wild', True, '1002955920'],
        ['Manyvids: Zaria Stone', True, '1003771650'],
        ['Manyvids: Zirael Rem', True, '1002067521'],
        ['Manyvids: _Mandala_', False, '1001282023'],
        ['MySweetApple', False, '423053'],
        ['Natalia Grey', False, '69353'],
        ['Sloppy Toppy', False, '1002638751'],
        ['Undercover Sluts', False, '1001483477'],
        ['YouthLust', False, '1001216419'],
        ['Manyvids: Helly Rite', True, '1002625980'],
        ['Manyvids: Samantha Flair', True, '1001379073'],
        ['Manyvids: DrKInLA', True, '1003399990'],
        ['Manyvids: JazminTorresBBW', True, '1001552380'],
        ['Manyvids: juicyxjaden', True, '1004101467'],
        ['Manyvids: KatesKurves', True, '1001897961'],
        ['Manyvids: LilyLoveles', True, '1002028291'],
        ['Manyvids: Melonie Kares', True, '1003030823'],
        ['Manyvids: MissGothBooty', True, '33842'],
        ['Manyvids: MZ NORMA STITZ', True, '1001723300'],
        ['Manyvids: Nixlynka', True, '1002349390'],
        ['Manyvids: QueenRhaena', True, '1004676688'],
        ['Manyvids: Rebeca Cross', True, '1004469370'],
        ['Manyvids: Rem Sequence', True, '1001345701'],
        ['Manyvids: Rice Bunny', True, '410732'],
        ['Manyvids: Shemeatress', True, '1000243328'],
        ['Manyvids: SugarSweetmeatBBW', True, '1003902752'],
        ['Manyvids: SuzyQ44ks', True, '1001155424'],
        ['Manyvids: SweetheartMiaBBW', True, '1001145696'],
        ['Manyvids: xPrincessAura', True, '1001967166'],
        ['Manyvids: AriaNicoleXXX', True, '1006336627'],
        ['Manyvids: Ayumi Anime', True, '1000907145'],
        ['Manyvids: Bubblebumbutt', True, '1001007459'],
        ['Manyvids: QueenieSteph', True, '1006752181'],
        ['Manyvids: Kimswallows', True, '1001125267'],
        ['Manyvids: PinkMaggit', True, '418469'],
        ['Manyvids: Layndare', True, '1002480074'],
        ['Manyvids: Ninadoll', True, '113109'],
        ['Manyvids: Lolliepopxxx', True, '1004243105'],
        ['Manyvids: Ema Lee', True, '1004698572'],
        ['Manyvids: Evelin Stone', True, '1000691850'],
        ['Manyvids: Throat GOAT', True, '1003432123'],
        ['Manyvids: Mikaela_tx', True, '1007908784'],
        ['Manyvids: Alyssia Vera', True, '1005246426'],
        ['Manyvids: Hotwife Heidi Haze', True, '1006555513'],
        ['Manyvids: DireDesires', False, '1003430946'],
        ['Manyvids: Hailey Rose', True, '1005765177'],
        ['Manyvids: Max Fills', True, '1006435546'],
        ['Manyvids: DickHerDownDaily', True, '1002541551'],
        ['Manyvids: Alex Mack', True, '1002787813'],
        ['Manyvids: Jessica Starling', True, '1000109566'],
        ['Manyvids: Theangelyoungs', False, '1004142584'],
        ['Manyvids: Thorri and Jax', False, '1004382198'],
        ['Manyvids: Ninacola', True, '1004836982'],
        ['Manyvids: Chris Marxxx', True, '1003245114'],
        ['Manyvids: Lucy Mochi', True, '1004503279'],
        ['Manyvids: Ruth Lee', True, '1002380360'],
        ['Manyvids: Sammm Next Door', True, '1005661691'],
        ['Manyvids: Cassie Bender', True, '1004671475'],
        ['Manyvids: Denise Anders', True, '1007127347'],
        ['Manyvids: Miss Lexa', True, '1001853993'],
        ['Manyvids: MadBros', False, '1007147288'],
        ['Manyvids: The Little Red', True, '1007787775'],
        ['Manyvids: Hayley Davies', True, '1007327920'],
        ['Manyvids: Allie Asia', True, '1004512140'],
        ['Manyvids: Kathryn Mae', True, '1000864948'],
        ['Manyvids: LeoLulu', True, '1000585143'],
        ['Manyvids: Lilyiskawaii', True, '1003844153'],
        ['Manyvids: pokemonfit', True, '1004995873'],
        ['Manyvids: sura_raya', True, '1004897680'],
        ['Manyvids: Nick Winter', True, '1005220898'],
        ['Manyvids: Onlyping', True, '1006754211'],
        ['Manyvids: Rocket Powers', True, '1006739926'],
        ['Manyvids: Katy Fit', True, '1007576103'],
        ['Manyvids: Ariel Anderssen', True, '454058'],
        ['Manyvids: Alex Bishop', True, '561134'],
        ['Manyvids: Christian Clay', True, '1004471534'],
        ['Manyvids: Flightlifexxx', True, '1006349004'],
        ['Manyvids: Girthmasterr', True, '1006311658'],
        ['Manyvids: Jakknife', True, '1006789072'],
        ['Manyvids: Videoxxx', True, '254265'],
        ['Manyvids: Misscjmiles', False, '1003570213'],
        ['Manyvids: Azumi Zeitline', True, '1003971662'],
        ['Manyvids: Thaliagomex', True, '1004028605'],
        ['Manyvids: Maxine_Milf', True, '1006016940'],
        ['Manyvids: Freakytuk', True, '1006881757'],
        ['Manyvids: aranacoyotebbw', True, '1005058948'],
        ['Manyvids: TabithaXXX', True, '1004115587'],
        ['Manyvids: Sp00pybeans', True, '1007723999'],
        ['Manyvids: Jia lulu', True, '1007367342'],
        ['Manyvids: Themotionoftheocean1', True, '1002935965'],
        ['Manyvids: Funsizedasian', True, '1001182120'],
        ['Manyvids: Daring Kiara', True, '1005971382'],
        ['Manyvids: Foreign Affairs XXX', False, '1006609881'],
        ['Manyvids: Reya Sunshine', True, '721966'],
        ['Manyvids: Littleponywife', True, '1006368600'],
        ['Manyvids: Max Sinbros', True, '1006281405'],
        ['Manyvids: Tyler Saber', True, '1006739002'],
        ['Manyvids: Lora Cross', True, '1002502469'],
        ['Manyvids: FirstclassJD', True, '1004263958'],
        ['Manyvids: Luiza Marcato', True, '1004862068'],
        ['Manyvids: Freckledred', True, '426998'],
        ['Manyvids: Debauchery Desired', True, '1006704082'],
        ['Manyvids: Nikita Belle', True, '1002437812'],
        ['Manyvids: ButteryBubbleButt', True, '428331'],
        ['Manyvids: Kali Roses', True, '580406'],
        ['Manyvids: TgirlOneGuy', False, '1001105501'],
        ['Manyvids: John Legendary', True, '1005086754'],
        ['Manyvids: JayToy', True, '1002541986'],
        ['Manyvids: Exoticasian', True, '1003473493'],
        ['Manyvids: Mila Mae XO', True, '1005016492'],
        ['Manyvids: The Cupcake SinClair', True, '1003958034'],
        ['Manyvids: JessieHH', True, '1008264323'],
        ['Manyvids: Lora Cross', True, '1002502469'],
        ['Manyvids: Angela Salvagno', True, '308967'],
        ['Manyvids: Jolie Lyon', True, '1001506737'],
        ['Manyvids: FeistyBlackBeauty', True, '1007728603'],
        ['Manyvids: Juliette Crimson', True, '1005821442'],
        ['Manyvids: BirdyLovesIt', True, '246789'],
        ['Manyvids: Harley Rose', True, '326561'],
        ['Manyvids: Ezra', True, '1000376982'],
        ['Manyvids: Isiah Maxwell', True, '1001687261'],
        ['Manyvids: Janet Mason', True, '1005452249'],
        ['Manyvids: Mandy Madison', True, '1003321586'],
        ['Manyvids: Ellie Idol', True, '354029'],
        ['Manyvids: Pure Pleasure', True, '1005394759'],
        ['Manyvids: Cosmic Broccoli', True, '1003335972'],
        ['Manyvids: Casey Kisses', True, '1000310737'],
        ['Manyvids: Lore Shane', True, '1001880948'],
        ['Manyvids: Maggie Landrin', True, '1002621924'],
        ['Manyvids: Lucy Alexandra', True, '1001339090'],
        ['Manyvids: Kinky Kristi', True, '507555'],
        ['Manyvids: Aria Allure', True, '1001620152'],
        ['Manyvids: Mandy Mitchell', True, '760384'],
        ['Manyvids: Kendra Sinclaire', True, '768875'],
        ['Manyvids: Julie Prim', True, '1000877561'],
        ['Manyvids: Sashade Sade', True, '1000138542'],
        ['Manyvids: Karmen Karma', True, '261541'],
        ['Manyvids: Skylar Quinn', True, '610013'],
        ['Manyvids: Lindsey Leigh', True, '481862'],
        ['Manyvids: Charlie Z', True, '36719'],
        ['Manyvids: Massimo Films', False, '1003761827'],
        ['Manyvids: Caylin', True, '114968'],
        ['Manyvids: InsideTatum', True, '1008353358'],
        ['Manyvids: Molly Stewart', True, '17808'],
        ['Manyvids: Stacy Valentine X', True, '1006966255'],
        ['Manyvids: Yasmina Khan', True, '1006840318'],
        ['Manyvids: Leila Cherry', True, '1002076838'],
        ['Manyvids: Ashley Aoki', True, '1001127010'],
        ['Manyvids: April Bunny', True, '1008342676'],
        ['Manyvids: HuneyBaked', True, '1003427367'],
        ['Manyvids: Petite Nymphet', True, '1000213623'],
        ['Manyvids: Zara Sutra', True, '374487'],
        ['Manyvids: Jasmine Teaa', True, '1001524782'],
        ['Manyvids: Indian BabeXX69XX', True, '1001903948'],
        ['Manyvids: kissystudio', False, '1005662608'],
        ['Manyvids: nokithai', True, '1006200966'],
        ['Manyvids: Japanstraycat', True, '1007451603'],
        ['Manyvids: Nymph_Candy', True, '1005541669'],
        ['Manyvids: Reel_Plans', False, '1007141447'],
        ['Manyvids: Finnys Playhouse', False, '1002809912'],
        ['Manyvids: Erin Moore', True, '1004957418'],
        ['Manyvids: Elle Brooke', True, '1007008684'],
        ['Manyvids: Emma Paige', True, '1006543449'],
        ['Manyvids: Daphanezz', True, '1006227545'],
        ['Manyvids: Lorena Brink', True, '1000055009'],
        ['Manyvids: Natasha_4_love', True, '1003022080'],
        ['Manyvids: Clarissa Brightstar', True, '1002333590'],
        ['Manyvids: Olivia Jay', True, '1003730153'],
        ['Manyvids: Nicole Kitt', True, '1004219823'],
        ['Manyvids: TeenyNene', True, '1006626235'],
        ['Manyvids: Softbby123', True, '1002459499'],
        ['Manyvids: ravenswallowz', True, '1008009861'],
        ['Manyvids: Babykittyp', True, '1006603670'],
        ['Manyvids: Asia Drake', True, '1002663330'],
        ['Manyvids: Vina Moon', True, '1003983984'],
        ['Manyvids: Xoxolane', True, '1005604015'],
        ['Manyvids: Trixxxie Rose', True, '1003927600'],
        ['Manyvids: mechanicalhymen', True, '1003867159'],
        ['Manyvids: Ember Snow', True, '1000518974'],
        ['Manyvids: Gianna Dior', True, '1003784874'],
        ['Manyvids: ThaiTease', True, '1008515508'],
        ['Manyvids: ThaiSpark', True, '1008570174'],
        ['Manyvids: ThaiMinx', True, '1006494534'],
        ['Manyvids: Luci Power', True, '1002527111'],
        ['Manyvids: bbybimbogamer', True, '1007319325'],
        ['Manyvids: Elly Clutch', True, '1006760641'],
        ['Manyvids: Alexis Tae', True, '1002428437'],
        ['Manyvids: Tony Rope UK', False, '1005853482'],
        ['Manyvids: xxNaughtyGirlxx', True, '1001631391'],
        ['Manyvids: Ella Kojira', True, '1003119513'],
        ['Manyvids: Sloane Sabbath', True, '1004407943'],
        ['Manyvids: SweetVickie', True, '1004875734'],
        ['Manyvids: ShotPOV', False, '1004525496'],
        ['Manyvids: Kisankanna', True, '1006193093'],
        ['Manyvids: Panamero 088', True, '1008261778'],
        ['Manyvids: Danika Mori', True, '1001100824'],
        ['Manyvids: TheStartOfUs', False, '1004374197'],
        ['Manyvids: UnfriendlyBlckHottie', True, '1002248211'],
        ['Manyvids: August Skye', True, '1004206736'],
        ['Manyvids: DaBBLWhisperer', True, '1008119301'],
        ['Manyvids: Lily Fox', True, '1006055071'],
        ['Manyvids: MissMiserlou', True, '1002488290'],
        ['Manyvids: xxbebegrrlxx', True, '1002245098'],
        ['Manyvids: Paypeaches', True, '173770'],
        ['Manyvids: Tattooed Temptress', True, '1002436250'],
        ['Manyvids: Katerina Piglet', True, '1002155472'],
        ['Manyvids: Kimberly X', True, '1002334075'],
        ['Manyvids: Miss Alika White', True, '1002975678'],
        ['Manyvids: Gypsy Page', True, '1001650513'],
        ['Manyvids: Alice Skary', True, '1001895402'],
        ['Manyvids: LATEXnCHILL', True, '1004021302'],
        ['Manyvids: Sugary Little', True, '1001801942'],
        ['Manyvids: Faye Taylor', True, '267758'],
        ['Manyvids: peachypoppy', True, '1004271325'],
        ['Manyvids: PureLatex', True, '1004399213'],
        ['Manyvids: Trixie Miss Rebecca', True, '1000698132'],
        ['Manyvids: Wendy Warrior', True, '761263'],
        ['Manyvids: An Li', True, '1001756028'],
        ['Manyvids: Cristal Kinky', True, '1003781419'],
        ['Manyvids: Gwen Adora', True, '1001118385'],
        ['Manyvids: Sugarbooty CB', True, '10314'],
        ['Manyvids: Long Toe Sally', True, '1001734618'],
        ['Manyvids: Adrienne Luxe', True, '1006113987'],
        ['Manyvids: TheFacialParty', False, '1004994721'],
        ['Manyvids: LittleMouchette', True, '1006811545'],
        ['Manyvids: hayleyxyz', True, '1004098334'],
        ['Manyvids: NatashaTy9', True, '1001777859'],
        ['Manyvids: KnottyNatasha', True, '1006330421'],
        ['Manyvids: icanbeurnuocmami', True, '1004549717'],
        ['Manyvids: Ellie Idol', True, '354029'],
        ['Manyvids: Mandy Madison', True, '1003321586'],
        ['Manyvids: Anastangel', True, '1007679603'],
        ['Manyvids: JohnnyLovexxx', True, '1002514420'],
        ['Manyvids: Monte Cristo XV', True, '1002514963'],
        ['Manyvids: Jameshardon007', True, '1005403401'],
        ['Manyvids: Maasai Warrior BBC', True, '1006713480'],
        ['Manyvids: Jayinne', True, '1003837091'],
        ['Manyvids: Johnny Sins', True, '1000255726'],
        ['Manyvids: iamannawilde', True, '1007454708'],
        ['Manyvids: HulkandIsa', True, '1006335580'],
        ['Manyvids: thedakotalyn', True, '1005244027'],
        ['Manyvids: NikkiMagic', True, '1002937596'],
        ['Manyvids: Liz Raw', True, '1002632960'],
        ['Manyvids: Fiona Sprouts', True, '1002953146'],
        ['Manyvids: Madiiitay', True, '1004382358'],
        ['Manyvids: CrushedVelvetX', True, '1003352933'],
        ['Manyvids: Elle Marz', True, '1004416590'],
        ['Manyvids: Petite Professor XXX', True, '1006171419'],
        ['Manyvids: Cooldehla1', True, '1003557054'],
        ['Manyvids: Melissa Stratton', True, '1005154748'],
        ['Manyvids: fmnclub', False, '1007048754'],
        ['Manyvids: Creamy_Spot', True, '1002782907'],
        ['Manyvids: TruKait', True, '1002963530'],
        ['Manyvids: Yessy D Waifu', True, '1007827546'],
        ['Manyvids: MyAsianGF', False, '1008083027'],
        ['Manyvids: BBC Worldwide', True, '1003626645'],
        ['Manyvids: Balenci Bby', True, '1006527632'],
        ['Manyvids: Lisa the Succubrat', True, '1001433106'],
        ['Manyvids: Peachy Riya', True, '1002335610'],
        ['Manyvids: Faye Lockwood', True, '1003925936'],
        ['Manyvids: Cockteau Twink', True, '1002125840'],
        ['Manyvids: Queen Zara Sutra', False, '1005512279'],
        ['Manyvids: Steffy Moreno', True, '1001960967'],
        ['Manyvids: NaughtyBonnie69', True, '1007210480'],
        ['Manyvids: Danny Luckee', False, '1006315784'],
        ['Manyvids: AudreyReid', True, '1008673774'],
        ['Manyvids: ZIAxBITE', True, '1001721841'],
        ['Manyvids: Sweetlilhotwife', True, '1008036477'],
        ['Manyvids: lenapolanski', True, '1008201765'],
        ['Manyvids: VanessaArizonaxxx', True, '1007497076'],
        ['Manyvids: shamelessxx', True, '1003209511'],
        ['Manyvids: Sage_Roux', True, '1005023663'],
        ['Manyvids: miaipanema', True, '1005001845'],
        ['Manyvids: DirtyDanii_69', True, '1005002465'],
        ['Manyvids: Rogita26', True, '1005404372'],
        ['Manyvids: TyroneLovePOV', True, '1005380780'],
        ['Manyvids: April_Maxima', True, '1004780609'],
        ['Manyvids: The Thai Godess', True, '1006654354'],
        ['Manyvids: Asianbbcluvr', True, '1005194704'],
        ['Manyvids: Tiny Miu', True, '1006531494'],
        ['Manyvids: alaiarose', True, '1004810253'],
        ['Manyvids: Loupanxxx', True, '1003128949'],
        ['Manyvids: ArinaFox', True, '1005789601'],
        ['Manyvids: TeddyTarantino', True, '1007033675'],
        ['Manyvids: Mmmickeyy', True, '1003093106'],
        ['Manyvids: Backdoorgf', True, '1007261232'],
        ['Manyvids: Yui Peachpie', True, '1006316998'],
        ['Manyvids: Abi Angel', True, '1007893362'],
        ['Manyvids: Bosslady808', True, '1007877241'],
        ['Manyvids: JMacsPOV', False, '1003290494'],
        ['Manyvids: Venusss Fetish', True, '1004752147'],
        ['Manyvids: FootTongueMouthVore', True, '1001924467'],
        ['Manyvids: RedEviee', True, '1008491888'],
        ['Manyvids: Naomi Foxxx', True, '1005164499'],
        ['Manyvids: Indian Sneha', True, '1005941597'],
        ['Manyvids: darkflameangel', True, '1004741655'],
        ['Manyvids: Pepper Kat', True, '1006003794'],
        ['Manyvids: Ittybittycherry', True, '1007813826'],
        ['Manyvids: WetZemu', True, '1002818162'],
        ['Manyvids: BlowRayne', True, '1004052738'],
        ['Manyvids: Frosty Princess', True, '815186'],
        ['Manyvids: Alice Warmheart', True, '1007220306'],
        ['Manyvids: Darling Kiyomi', True, '1004595291'],
        ['Manyvids: Luna Kyzz', True, '750209'],
        ['Manyvids: Adeline Lafouine', True, '1003633646'],
        ['Manyvids: Anna Scot', True, '1006868608'],
        ['Manyvids: Emily Piexo', True, '1004184499'],
        ['Manyvids: Lady Heavenian', True, '1005458625'],
        ['Manyvids: Aysha Paige', True, '1006744158'],
        ['Manyvids: Housewife Ginger', True, '1001635291'],
        ['Manyvids: Business Bitch', True, '1003450016'],
        ['Manyvids: Mariah Leonne', True, '76186'],
        ['Manyvids: Nicolette Bloom', True, '1005323080'],
        ['Manyvids: Callie Black', True, '1000158975'],
        ['Manyvids: Olivia Young', True, '149290'],
        ['Manyvids: Emily Adaire TS', True, '1004110648'],
        ['Manyvids: Lexia Lynx', True, '1000560155'],
        ['Manyvids: Crystal Knight', True, '559303'],
        ['Manyvids: Elia Blaine', True, '1003330332'],
        ['Manyvids: Trappybae', True, '1004370602'],
        ['Manyvids: Sofie Skye', True, '1003904073'],
        ['Manyvids: kwgirlx', True, '1002919695'],
        ['Manyvids: Lyra Fae', True, '231529'],
        ['Manyvids: Claudiahon', True, '1006135404'],
        ['Manyvids: Princess_Monica', True, '1003758762'],
        ['Manyvids: Tia Tizzianni', True, '1000160319'],
        ['Manyvids: LilRedVelvet', True, '1002065207'],
        ['Manyvids: Lexia Lynx', True, '1000560155'],
        ['Manyvids: Lorena Brink', True, '1000055009'],
        ['Manyvids: noramakesporn', True, '1001231266'],
        ['Manyvids: Destinationkat', True, '426738'],
        ['Manyvids: footpunkz', False, '1002856970'],
        ['Manyvids: Legendarylootz', True, '1001194277'],
        ['Manyvids: madisynwood', True, '1005851612'],
        ['Manyvids: Mia Jocelyn', True, '1001682538'],
        ['Manyvids: MsEllaVatrap', True, '1006201451'],
        ['Manyvids: zivafey', True, '1001812120'],
        ['Manyvids: phatassedangel69', True, '1003179211'],
        ['Manyvids: PuppyGirlfriend', True, '1003012316'],
        ['Manyvids: FlippingPaiges', True, '1005912090'],
        ['Manyvids: JennyBlighe', True, '103563'],
        ['Manyvids: darlingjosefin', True, '1002072418'],
        ['Manyvids: HOLLYHOTWIFE', True, '1001889166'],
        ['Manyvids: hungfemboy', True, '1006707041'],
        ['Manyvids: satinfuntaboo', True, '1000362617'],
        ['Manyvids: Goddess Arielle', True, '1001436441'],
        ['Manyvids: TheTinyFeetTreat', True, '1004341412'],
        ['Manyvids: Alex Coal', True, '212911'],
        ['Manyvids: McKatenz', True, '1000616398'],
        ['Manyvids: Dirtyburd07', True, '1002997083'],
        ['Manyvids: Irish Skylar', True, '1006518930'],
        ['Manyvids: MILF Nikki Lynn', True, '1006096559'],
        ['Manyvids: Delilah Cass', True, '293322'],
        ['Manyvids: Viera May XXX', True, '1002903057'],
        ['Manyvids: JazzzBerrry', True, '1004935662'],
        ['Manyvids: mel7158', True, '1004274761'],
        ['Manyvids: kayzecutie', True, '1005345102'],
        ['Manyvids: Minka Summers', True, '1006021257'],
        ['Manyvids: Luna Nyx', True, '1004858060'],
        ['Manyvids: Karabella_XXX', True, '1000456360'],
        ['Manyvids: MsBellaTS', True, '1008531962'],
        ['Manyvids: Caillazy', True, '1007357668'],
        ['Manyvids: Kilee Kat', True, '1003883415'],
        ['Manyvids: Jessica Bloom', True, '1005013740'],
        ['Manyvids: Wendy Summers', True, '1000912164'],
        ['Manyvids: Patrappa', True, '1001799554'],
        ['Manyvids: x_Luna_x', True, '1006971945'],
        ['Manyvids: Riley Cyriis', True, '1002824546'],
        ['Manyvids: Jenna J Ross', True, '562476'],
        ['Manyvids: Natalie Mars', True, '1000035308'],
        ['Manyvids: PuppyGirlfriend', True, '1003012316'],
        ['Manyvids: Throat GOAT', False, '1003432123'],
        ['Manyvids: angeldom_mv', True, '1007909332'],
        ['Manyvids: Kelly Payne', True, '369654'],
        ['Manyvids: Harley Sin', True, '1003900589'],
        ['Manyvids: Able Godshark', True, '1002558384'],
        ['Manyvids: Dickdrainers XXX', False, '733716'],
        ['Manyvids: sadbaffoon', True, '292266'],
        ['Manyvids: Lyra Fae', True, '231529'],
        ['Manyvids: Throat GOAT', True, '1003432123'],
        ['Manyvids: GirlOnTop880', True, '1004830774'],
        ['Manyvids: MissTiff', True, '1702'],
        ['Manyvids: Hxllywxxdz', True, '1007287757'],
        ['Manyvids: cute_bean_ting', True, '1003717582'],
        ['Manyvids: JuliaSoftdome', True, '1004595211'],
        ['Manyvids: lilcanadiangirl', True, '683542'],
        ['Manyvids: ARTEM SUCHKOV', True, '1004492966'],
        ['Manyvids: Princess Bambie', True, '570726'],
        ['Manyvids: JessRyan', True, '184888'],
        ['Manyvids: Emmas Secret Life', True, '577443'],
        ['Manyvids: AcrylicKateQuinn', True, '1003829846'],
        ['Manyvids: Nicole Cheshire', True, '1004383440'],
        ['Manyvids: LalaThePala', True, '1004997784'],
        ['Manyvids: Lena Paul', True, '541454'],
        ['Manyvids: Sheena Shaw', True, '479557'],
        ['Manyvids: AKGINGERSNAPS', True, '1000213860'],
        ['Manyvids: Lenorebunny', True, '1004313020'],
        ['Manyvids: Zuzu Flowers', True, '1004604738'],
        ['Manyvids: Aiko Moe', True, '565287'],
        ['Manyvids: shinen2022', True, '1006075140'],
        ['Manyvids: Anastasiaxxx89', True, '748933'],
        ['Manyvids: SaraMills', True, '1000659773'],
        ['Manyvids: Mistress Lucy Khan', True, '654428'],
        ['Manyvids: alicenz', True, '493690'],
        ['Manyvids: Aderes Quin', True, '1003312288'],
        ['Manyvids: Your_Father_Secret', True, '1004654702'],
        ['Manyvids: Bad Dolly', True, '1000030336'],
        ['Manyvids: cutiecabani', True, '1003981322'],
        ['Manyvids: MsNadiaWhite', True, '670690'],
        ['Manyvids: HannahBrooks', True, '373590'],
        ['Manyvids: babychester', True, '1001336064'],
        ['Manyvids: Rebecca de Winter', True, '1000674918'],
        ['Manyvids: Lola James', True, '1005990787'],
        ['Manyvids: Lucyy Avery', True, '451005'],
        ['Manyvids: Irisxjase', True, '1007053479'],
        ['Manyvids: ElenaKoshkaXoXo', True, '1001626607'],
        ['Manyvids: Brickzilla', True, '1002868779'],
        ['Manyvids: Flora Rodgers', True, '831568'],
        ['Manyvids: Clara Dee', True, '1000471578'],
        ['Manyvids: Snugglepunk', True, '391666'],
        ['Manyvids: Cadey Mercury', True, '1000609526'],
        ['Manyvids: Ecchievement', False, '1001123030'],
        ['Manyvids: MarySweetCherry', False, '1004294579'],
        ['Manyvids: Miss_Vexx', False, '1000849288'],
        ['Manyvids: VicaTS', False, '1000782883'],
        ['Manyvids: Visceratio', True, '1000775087'],
        ['Manyvids: Taboo Girl', True, '1003017801'],
        ['Manyvids: Amamizura', True, '1000243724'],
        ['Manyvids: pitykitty', True, '460335'],
        ['Manyvids: AvanelleJules', True, '1005755337'],
        ['Manyvids: Bea York', True, '1000611142'],
        ['Manyvids: Bratty Lindsay', True, '1002606297'],
        ['Manyvids: Brea Rose', True, '1000024307'],
        ['Manyvids: Brookelynne Briar', True, '48084'],
        ['Manyvids: butterybubblebutt', True, '428331'],
        ['Manyvids: FFeZine', True, '1000045578'],
        ['Manyvids: Chloe Night', True, '1000223652'],
        ['Manyvids: coffincouple', True, '1000451958'],
        ['Manyvids: darklordmarkus', True, '483842'],
        ['Manyvids: Dawn Willow', True, '222329'],
        ['Manyvids: DestinyDiaz', True, '109770'],
        ['Manyvids: Ellie Skyes', True, '1004933109'],
        ['Manyvids: Evelin Stone', True, '1000691850'],
        ['Manyvids: Exoticpanda', True, '779142'],
        ['Manyvids: FrostyPrincess', True, '815186'],
        ['Manyvids: OUSweetheart', True, '106308'],
        ['Manyvids: yourgirlnextdoor', True, '1008423521'],
        ['Manyvids: Island Peach', True, '1001402896'],
        ['Manyvids: Annelitt', True, '1007916298'],
        ['Manyvids: KitaLoveXOXO', True, '1006282702'],
        ['Manyvids: Milana Ricci', True, '1000924342'],
        ['Manyvids: Blowketing', False, '1007848193'],
        ['Manyvids: Antodoll', True, '1009651373'],
        ['Manyvids: Sexualmastery', True, '1004081853'],
        ['Manyvids: afterdarkxxxventures', True, '1009340463'],
        ['Manyvids: Lauumiau', True, '1009290581'],
        ['Manyvids: JuicyGao', True, '1006897026'],
        ['Manyvids: FlameHel', False, '1006612274'],
        ['Manyvids: tentenlatinas', False, '1006251848'],
        ['Manyvids: Keeks_3005', True, '1007240594'],
        ['Manyvids: Baddiesonlypov', False, '1005032015'],
        ['Manyvids: Ayumikichi', True, '1006374960', 'Vertical'],
        ['Manyvids: Karneli_Bandi', True, '1002990973'],
        ['Manyvids: Annabelle Blue', True, '1008511883'],
        ['Manyvids: AvaZev', True, '1008074349'],
        ['Manyvids: KatieLin_NextDoor', True, '1003318481'],
        ['Manyvids: WreccItRalph', True, '1006338300'],
        ['Manyvids: FaexxxFae', True, '1004739767'],
        ['Manyvids: Yesimcheta', True, '1004914470'],
        ['Manyvids: Nivia Wolfe', True, '1001457753'],
        ['Manyvids: MsKosmik', True, '1003984662'],
        ['Manyvids: Raysileeum', True, '1007648357'],
        ['Manyvids: Adrianna Rodriguez', True, '1007753700'],
        ['Manyvids: Dreads_Way', True, '1006013732'],
        ['Manyvids: OnlyMikeWilliams', True, '1006548979'],
        ['Manyvids: Bluelah', True, '1005445063'],
        ['Manyvids: swingingcouplexxx', True, '1000941778'],
        ['Manyvids: Scott Stark Studios', False, '1007157741'],
        ['Manyvids: shadowdimitri', True, '1005010941'],
        ['Manyvids: Summerrose69', True, '1002589159'],
        ['Manyvids: MrLdnLad', True, '1006356543'],
        ['Manyvids: Ganjababeuk', True, '1005350571'],
        ['Manyvids: PrincessJas4Ux', True, '1002105775'],
        ['Manyvids: charlottestar', True, '1004004556'],
        ['Manyvids: Ellexxaurus', True, '1007553264'],
        ['Manyvids: peachycatsnack', True, '1005444885'],
        ['Manyvids: hellen511', True, '1002528210'],
        ['Manyvids: MissBlackreey', True, '1008112468'],
        ['Manyvids: Break Her In', False, '1003373430'],
        ['Manyvids: MiniStallion', True, '1003446613'],
        ['Manyvids: Alycia Elvie', True, '1005831976'],
        ['Manyvids: Renity Love', True, '1005325339'],
        ['Manyvids: MisbehavingMads', True, '1009139979'],
        ['Manyvids: Goddessceleste111', True, '1007151639'],
        ['Manyvids: Rileyridesreece', True, '1004638956'],
        ['Manyvids: kiri_amari', True, '1007090765'],
        ['Manyvids: webtolove', True, '1004633725'],
        ['Manyvids: TheRealMilaKoi', True, '1008585447'],
        ['Manyvids: Island Boy Vids', False, '1007765381'],
        ['Manyvids: Sasha Curves', True, '1006003083'],
        ['Manyvids: Sarah Calanthe', True, '1001061960'],
        ['Manyvids: SofiaSimens', True, '1004361605'],
        ['Manyvids: Bianca Beauchamp', True, '8821'],
        ['Manyvids: Princess Rae', True, '1005636504'],
        ['Manyvids: Kakao Chan', True, '1005489816'],
        ['Manyvids: ShadyProducer', False, '1003014243'],
        ['Manyvids: Bondagio', False, '1005448400'],
        ['Manyvids: Mrthroatmonster', False, '1002729613'],
        ['Manyvids: itstommyking', True, '1001037206'],
        ['Manyvids: RocketPowersXXX', False, '1006739926'],
        ['Manyvids: Erika Chanel', True, '1004936475'],
        ['Manyvids: California_girl', True, '1004612889'],
        # ~ ['Manyvids: ', True, ''],
        # ~ ['Manyvids: ', True, ''],
        # ~ ['Manyvids: ', True, ''],
        # ~ ['Manyvids: ', True, ''],
    ]

    name = 'ManyVidsV2'

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False', 'HTTPERROR_ALLOWED_CODES': [403, 404]}

    selector_map = {
        'title': '',
        'description': '//div[contains(@class, "desc-text")]/text()',
        'date': '//div[@class="mb-1"]/span[1]/span[2]|//div[@class="mb-1"]/span[2]/text()',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '',
        'tags': '//script[contains(text(),"tagListApp")]/text()',
        'duration': '//div[@class="video-details"]//i[contains(@class, "mv-icon-video-length")]/following-sibling::text()[contains(., "min")]',
        're_duration': r'(\d{1,2}\:.*?) min',
        'external_id': '',
        'trailer': '',
        'pagination': ''
    }

    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    def start_requests(self):
        url = "https://www.manyvids.com/Profile/1001216419/YouthLust/Store/Videos/"
        yield scrapy.Request(url, callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        self.headers['referer'] = 'https://www.manyvids.com/Profile/1003004427/Sweetie-Fox/Store/Videos/'

        for link in self.start_urls:
            meta['page'] = self.page
            meta['siteid'] = link[2]
            meta['site'] = link[0]
            meta['parse_performer'] = link[1]
            meta['pagination'] = "landscape"
            next_page = self.get_next_page_url(self.page, meta)
            yield scrapy.Request(next_page, callback=self.parse, meta=meta, headers=self.headers)

            if len(link) > 3:
                meta['pagination'] = "vertical"
                next_page = self.get_next_page_url(self.page, meta)
                yield scrapy.Request(next_page, callback=self.parse, meta=meta, headers=self.headers)


    def parse(self, response):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta), callback=self.parse, meta=meta, headers=self.headers)

    def get_next_page_url(self, page, meta):
        if meta['pagination'] == "vertical":
            link = f"https://www.manyvids.com/bff/store/videos/{meta['siteid']}/?page={page}&vertical=1"
        else:
            link = f"https://www.manyvids.com/bff/store/videos/{meta['siteid']}/?page={page}"
        return link

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        if "data" in jsondata and jsondata['data']:
            data = jsondata['data']
            for jsonentry in data:
                meta['id'] = jsonentry['id']
                meta['title'] = string.capwords(html.unescape(jsonentry['title']))
                scenelink = f"https://www.manyvids.com/bff/store/video/{meta['id']}"
                if meta['id']:
                    # ~ print(meta)
                    yield scrapy.Request(scenelink, callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        meta = response.meta
        if meta['parse_performer']:
            performer = re.search(r'Manyvids:(.*)$', meta['site']).group(1).strip()
            return [performer]
        else:
            if meta['site'] == "Cattie":
                return ['Cattie Candescent']
            if "VicaTS" in meta['site']:
                return ['Victoria Gar', 'Milla']
            if "Brandibabes" in meta['site']:
                return ['Brandi Babes']
            if "Gogofukmexxx" in meta['site']:
                return ['Gogo Fukme']
            if "FreyaJade" in meta['site']:
                return ['Freya Jade']
            if "420SexTime" in meta['site']:
                return ['Asteria']
            if "RocketPowersXXX" in meta['site']:
                return ['Rocket Powers']
            if "Queen Zara Sutra" in meta['site']:
                return ['Zara Sutra']
            if "MarySweetCherry" in meta['site']:
                return ['Mary Cherry']
            if "Miss_Vexx" in meta['site']:
                return ['Alexandra Vexx']
            if "OhItsEmmaRose" in meta['site']:
                return ['Emma Rose']
            if "OmankoVivi" in meta['site']:
                return ['Omanko Vivi']
            if "RhiannonRyder1995" in meta['site']:
                return ['Rhiannon Ryder']
            if "Kiittenymph" in meta['site']:
                return ['Lex Kiittenymph']
            if "Misscjmiles" in meta['site']:
                return ['CJ Miles']
            if "Aathenatheslut" in meta['site']:
                return ['Athena May']
            if "AliceNZ" in meta['site']:
                return ['MissAlice']
            if "Ecchievement" in meta['site']:
                return ['Jane Helsing']
            if "BaileyLove6969" in meta['site']:
                return ['Bailey Love']
            if "Brett TylerXXX" in meta['site']:
                return ['Brett Tyler']
            if "Manyvids: Cattie" in meta['site']:
                return ['Cattie Candescent']
            if "Cherry Fae" in meta['site']:
                return ['Krystal Orchid']
            if "JazminTorresBBW" in meta['site']:
                return ['Jazmin Torres']
            if "CuckoldingMILF" in meta['site']:
                return ['Mila Rose']
            if "CutieElly" in meta['site']:
                return ['Hot Cum Challenge']
            if "Danny Blaq Videos" in meta['site']:
                return ['Danny Blaq']
            if "Dinkybum" in meta['site']:
                return ['Didi Demure']
            if "DirtyGardenGirl" in meta['site']:
                return ['Donna Flower']
            if "Doschers Production" in meta['site']:
                return ['Black Ghost']
            if "Dotadasp" in meta['site']:
                return ['Muniky Flor']
            if "FFeZine" in meta['site']:
                return ['UnicornDisney21']
            if "Elunaxc" in meta['site']:
                return ['Jade Skyee']
            if "Fiery Redhead" in meta['site']:
                return ['Fiery Cassie']
            if "FitSid" in meta['site']:
                return ['Fit Sidney']
            if "ForbiddenFruitsFilms" in meta['site']:
                return ['Jodi West']
            if "Funaussiecouple" in meta['site']:
                return ['Goddess Mercy']
            if "Goddess Tangent" in meta['site']:
                return ['Tangent']
            if "HannahJames710" in meta['site']:
                return ['Hannah James']
            if "Hannibal Damage" in meta['site']:
                return ['Cam Damage']
            if "Hottalicia1" in meta['site']:
                return ['Hott Alicia']
            if "Hotwife Heidi Haze" in meta['site']:
                return ['Heidi Haze']
            if "ItsReeseRobins" in meta['site']:
                return ['Reese Robbins']
            if "KalicoKats" in meta['site']:
                return ['Destination Kat', 'KatsCalico']
            if "Karabella" in meta['site']:
                return ['Kayden Harley']
            if "KarmannAndJosie" in meta['site']:
                return ['Josie', 'Karmann']
            if "Katilingus" in meta['site']:
                return ['Kat Danz']
            if "Katy_Ann_XO" in meta['site']:
                return ['Katy Ann']
            if "MaryVincXXX" in meta['site']:
                return ['Maria Romanova']
            if "Playfulsolesandtoes" in meta['site']:
                return ['Lady Waverly']
            if "LilyGaia" in meta['site']:
                return ['Lily Ivy']
            if "Mymindbreaks" in meta['site']:
                return ['RiRi']
            if "Missvioletstarr" in meta['site']:
                return ['Violet Starr']
            if "Nikkiandleigh" in meta['site']:
                return ['Nikki Hearts']
            if "Nalabrooksxxx" in meta['site']:
                return ['Nala Brooks']
            if "OnlyOneRhonda" in meta['site']:
                return ['Rhonda']
            if "PocketRocketMimi" in meta['site']:
                return ['Mimi P']
            if "Puertorockxxx20" in meta['site']:
                return ['Puerto Rock']
            if "PurpleHailStorm" in meta['site']:
                return ['Sara Storm']
            if "OUSweetheart" in meta['site']:
                return ['Summer Hart']
            if "SaintVirginPro" in meta['site']:
                return ['Liza Virgin']
            if "ScarletteD_xo" in meta['site']:
                return ['Scarlette D']
            if "Senorita Satan" in meta['site']:
                return ['Chloe Temple']
            if "TheSophieJames" in meta['site']:
                return ['Sophie James']
            if "TheStartOfUs" in meta['site']:
                return ['Adhara Skai']
            if "TheLedaLotharia" in meta['site']:
                return ['Leda Lotharia']
            if "TheFleshMechanic" in meta['site']:
                return ['The Flesh Mechanic']
            if "Theangelyoungs" in meta['site']:
                return ['Angel Youngs']
            if "TheLunaLain" in meta['site']:
                return ['Luna Lain']
            if "THEYLOVEFLAXK" in meta['site']:
                return ['They Love Flaxk']
            if "tgirloneguy" in meta['site'].lower():
                return ['Kendall Penny']
            if "ThisIsFuckingFun" in meta['site']:
                return ['Eli']
            if "Vince May" in meta['site']:
                return ['Vince May']
            if "Vera1995" in meta['site']:
                return ['Vera']
            if "Yourboyfcisco" in meta['site']:
                performers = ['Troy Francisco']
                title = meta['title']
                if title and ":" in title:
                    title = re.search(r'.*:(.*?)$', title)
                    if title:
                        title = title.group(1)
                        title = title.lower().replace("&amp;", "&").replace(" and ", "&").replace(",", "&")
                        performer_list = title.split("&")
                        for performer in performer_list:
                            if " pt" in performer:
                                performer = re.search(r'(.*) pt', performer).group(1)
                            if " part" in performer:
                                performer = re.search(r'(.*) part', performer).group(1)
                            performers.append(performer)
                        performers = list(map(lambda x: self.cleanup_title(x.strip()), performers))
                        return performers

            if "YourLittleAngel" in meta['site']:
                return ['Katie Darling']
            if "Winterxxdoll" in meta['site']:
                return ['Winter Doll']
        return []

    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return "Manyvids"

    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            if "Manyvids" in meta['site']:
                return "Manyvids"
            return meta['site']
        return "Manyvids"

    def get_network(self, response):
        return "Manyvids"

    def parse_tags(self, tags):
        re_outer = re.compile(r'([^A-Z ])([A-Z])')
        re_inner = re.compile(r'(?<!^)([A-Z])([^A-Z])')
        tags2 = []
        for tag in tags:
            tag = re_outer.sub(r'\1 \2', re_inner.sub(r' \1\2', tag))
            tags2.append(tag)
        return tags2

    def parse_scene(self, response):
        if response.status not in [403]:
            item = SceneItem()
            meta = response.meta
            jsondata = json.loads(response.text)
            jsondata = jsondata['data']
            item['title'] = meta['title']
            item['id'] = meta['id']
            if 'description' in jsondata:
                item['description'] = jsondata['description'].replace("\n", " ").replace("\r", " ").replace("\t", " ")
            else:
                item['description'] = ""
            if "tags" in jsondata:
                item['tags'] = jsondata['tags']
            else:
                item['tags'] = []
            if "tagList" in jsondata and jsondata['tagList']:
                for tag in jsondata['tagList']:
                    item['tags'].append(tag['label'])

            item['tags'] = self.parse_tags(item['tags'])

            if "screenshot" in jsondata:
                item['image'] = jsondata['screenshot'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['image'] = re.sub(r'(.*)(\.\w{3,4})$', r'\1_1\2', item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['date'] = jsondata['launchDate']
            item['trailer'] = None
            item['type'] = 'Scene'
            item['network'] = "Manyvids"
            item['performers'] = self.get_performers(response)
            item['site'] = self.get_site(response)
            item['parent'] = self.get_parent(response)
            item['url'] = "https://www.manyvids.com" + jsondata['url']
            if "videoDuration" in jsondata and jsondata['videoDuration']:
                if ":" in jsondata['videoDuration']:
                    duration = re.search(r'(\d{1,2}:\d{1,2}:?\d{1,2}?)', jsondata['videoDuration'])
                    item['duration'] = self.duration_to_seconds(duration.group(1))
                elif jsondata['videoDuration']:
                    duration = int(jsondata['videoDuration'])
                    if duration:
                        item['duration'] = str(duration * 60)
            else:
                item['duration'] = ""
            parse_scene = True
            if "eastcoastxxx" in item['site'].lower():
                matches = ['-free', '-tube', 'free-preview', 'free preview', '-teaser']
                if any(x in item['url'].lower() for x in matches):
                    parse_scene = False
            if parse_scene:
                yield self.check_item(item, self.days)
