# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/vehicle_layout.py
# Compiled at: 2014-12-03 09:27:27
from dossiers2.common.DossierBlockBuilders import *
from battle_statistics_layouts import *
from dossiers2.custom.dependencies import ACHIEVEMENT15X15_DEPENDENCIES
from dossiers2.custom.dependencies import ACHIEVEMENT7X7_DEPENDENCIES
from dossiers2.custom.dependencies import FORT_ACHIEVEMENTS_DEPENDENCIES
TOTAL_BLOCK_LAYOUT = ['creationTime',
 'lastBattleTime',
 'battleLifeTime',
 'treesCut',
 'mileage']
_totalBlockBuilder = StaticSizeBlockBuilder('total', TOTAL_BLOCK_LAYOUT, {}, [])
_a15x15BlockBuilder = StaticSizeBlockBuilder('a15x15', A15X15_BLOCK_LAYOUT, A15X15_STATS_DEPENDENCIES, [])
_a15x15_2BlockBuilder = StaticSizeBlockBuilder('a15x15_2', A15X15_2_BLOCK_LAYOUT, {}, [])
_clanBlockBuilder = StaticSizeBlockBuilder('clan', CLAN_BLOCK_LAYOUT, CLAN_STATS_DEPENDENCIES, [])
_clan2BlockBuilder = StaticSizeBlockBuilder('clan2', CLAN2_BLOCK_LAYOUT, {}, [])
_companyBlockBuilder = StaticSizeBlockBuilder('company', COMPANY_BLOCK_LAYOUT, {}, [])
_company2BlockBuilder = StaticSizeBlockBuilder('company2', COMPANY2_BLOCK_LAYOUT, {}, [])
_a7x7BlockBuilder = StaticSizeBlockBuilder('a7x7', A7X7_BLOCK_LAYOUT, A7X7_STATS_DEPENDENCIES, [])
_rated7x7BlockBuilder = StaticSizeBlockBuilder('rated7x7', RATED_7X7_BLOCK_LAYOUT, {}, [])
_historicalBlockBuilder = StaticSizeBlockBuilder('historical', HISTORICAL_BLOCK_LAYOUT, HISTORICAL_STATS_DEPENDENCIES, [])
_fortBattlesInClanBlockBuilder = StaticSizeBlockBuilder('fortBattlesInClan', FORT_BLOCK_LAYOUT, {}, [])
_fortSortiesInClanBlockBuilder = StaticSizeBlockBuilder('fortSortiesInClan', FORT_BLOCK_LAYOUT, {}, [])
_fortBattlesBlockBuilder = StaticSizeBlockBuilder('fortBattles', FORT_BLOCK_LAYOUT, FORT_BATTLES_STATS_DEPENDENCIES, [])
_fortSortiesBlockBuilder = StaticSizeBlockBuilder('fortSorties', FORT_BLOCK_LAYOUT, FORT_SORTIES_STATS_DEPENDENCIES, [])
_maxPopUps = ['maxXP', 'maxFrags', 'maxDamage']
_max15x15BlockBuilder = StaticSizeBlockBuilder('max15x15', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_max7x7BlockBuilder = StaticSizeBlockBuilder('max7x7', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxHistoricalBlockBuilder = StaticSizeBlockBuilder('maxHistorical', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxFortBattlesBlockBuilder = StaticSizeBlockBuilder('maxFortBattles', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxFortSortiesBlockBuilder = StaticSizeBlockBuilder('maxFortSorties', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxRated7x7BlockBuilder = StaticSizeBlockBuilder('maxRated7x7', MAX_BLOCK_LAYOUT, {}, [])
_vehTypeFragsBlockBuilder = DictBlockBuilder('vehTypeFrags', 'I', 'H', VEH_TYPE_FRAGS_DEPENDENCIES)
_ACHIEVEMENTS15X15_BLOCK_LAYOUT = ['fragsBeast',
 'sniperSeries',
 'maxSniperSeries',
 'invincibleSeries',
 'maxInvincibleSeries',
 'diehardSeries',
 'maxDiehardSeries',
 'killingSeries',
 'fragsSinai',
 'maxKillingSeries',
 'piercingSeries',
 'maxPiercingSeries',
 'battleHeroes',
 'warrior',
 'invader',
 'sniper',
 'defender',
 'steelwall',
 'supporter',
 'scout',
 'evileye',
 'medalKay',
 'medalCarius',
 'medalKnispel',
 'medalPoppel',
 'medalAbrams',
 'medalLeClerc',
 'medalLavrinenko',
 'medalEkins',
 'medalWittmann',
 'medalOrlik',
 'medalOskin',
 'medalHalonen',
 'medalBurda',
 'medalBillotte',
 'medalKolobanov',
 'medalFadin',
 'medalRadleyWalters',
 'medalBrunoPietro',
 'medalTarczay',
 'medalPascucci',
 'medalDumitru',
 'medalLehvaslaiho',
 'medalNikolas',
 'medalLafayettePool',
 'sinai',
 'heroesOfRassenay',
 'beasthunter',
 'mousebane',
 'tankExpertStrg',
 'raider',
 'kamikaze',
 'lumberjack',
 'medalBrothersInArms',
 'medalCrucialContribution',
 'medalDeLanglade',
 'medalTamadaYoshio',
 'bombardier',
 'huntsman',
 'alaric',
 'sturdy',
 'ironMan',
 'luckyDevil',
 'pattonValley',
 'fragsPatton',
 'markOfMastery',
 'sniper2',
 'mainGun',
 'marksOnGun',
 'movingAvgDamage',
 'medalMonolith',
 'medalAntiSpgFire',
 'medalGore',
 'medalCoolBlood',
 'medalStark',
 'damageRating',
 'impenetrable',
 'maxAimerSeries',
 'shootToKill',
 'fighter',
 'duelist',
 'demolition',
 'arsonist',
 'bonecrusher',
 'charmed',
 'even']
_achievements15x15PopUps = ['tankExpert',
 'tankExpert0',
 'tankExpert1',
 'tankExpert2',
 'tankExpert3',
 'tankExpert4',
 'tankExpert5',
 'tankExpert6',
 'tankExpert7',
 'tankExpert8',
 'tankExpert9',
 'tankExpert10',
 'tankExpert11',
 'tankExpert12',
 'tankExpert13',
 'tankExpert14',
 'markOfMastery',
 'marksOnGun',
 'impenetrableshootToKill',
 'fighter',
 'duelist',
 'demolition',
 'arsonist',
 'bonecrusher',
 'charmed',
 'even']
_achievements15x15BlockBuilder = StaticSizeBlockBuilder('achievements', _ACHIEVEMENTS15X15_BLOCK_LAYOUT, ACHIEVEMENT15X15_DEPENDENCIES, _achievements15x15PopUps)
ACHIEVEMENTS7X7_BLOCK_LAYOUT = ['wolfAmongSheep',
 'wolfAmongSheepMedal',
 'geniusForWar',
 'geniusForWarMedal',
 'kingOfTheHill',
 'tacticalBreakthroughSeries',
 'maxTacticalBreakthroughSeries',
 'armoredFist',
 'godOfWar',
 'fightingReconnaissance',
 'fightingReconnaissanceMedal',
 'willToWinSpirit',
 'crucialShot',
 'crucialShotMedal',
 'forTacticalOperations',
 'promisingFighter',
 'promisingFighterMedal',
 'heavyFire',
 'heavyFireMedal',
 'ranger',
 'rangerMedal',
 'fireAndSteel',
 'fireAndSteelMedal',
 'pyromaniac',
 'pyromaniacMedal',
 'noMansLand',
 'guerrilla',
 'guerrillaMedal',
 'infiltrator',
 'infiltratorMedal',
 'sentinel',
 'sentinelMedal',
 'prematureDetonation',
 'prematureDetonationMedal',
 'bruteForce',
 'bruteForceMedal',
 'awardCount',
 'battleTested']
_achievements7x7BlockBuilder = StaticSizeBlockBuilder('achievements7x7', ACHIEVEMENTS7X7_BLOCK_LAYOUT, ACHIEVEMENT7X7_DEPENDENCIES, [])
UNIQUE_VEH_ACHIEVEMENT_VALUES = []
_uniqueVehAchievementPopUps = []
_uniqueVehAchievementBlockBuilder = BinarySetDossierBlockBuilder('uniqueAchievements', UNIQUE_VEH_ACHIEVEMENT_VALUES, {}, _uniqueVehAchievementPopUps)
_SINGLE_ACHIEVEMENTS_VALUES = ['titleSniper',
 'invincible',
 'diehard',
 'handOfDeath',
 'armorPiercer',
 'tacticalBreakthrough',
 'aimer']
_singleAchievementsPopUps = ['titleSniper',
 'invincible',
 'diehard',
 'handOfDeath',
 'armorPiercer',
 'tacticalBreakthrough',
 'aimer']
_singleAchievementsBlockBuilder = BinarySetDossierBlockBuilder('singleAchievements', _SINGLE_ACHIEVEMENTS_VALUES, {}, _singleAchievementsPopUps)
FORT_ACHIEVEMENTS_BLOCK_LAYOUT = ['conqueror',
 'fireAndSword',
 'crusher',
 'counterblow',
 'kampfer',
 'soldierOfFortune',
 'wins',
 'capturedBasesInAttack',
 'capturedBasesInDefence']
_fortPersonalAchievementsPopUps = ['conqueror',
 'fireAndSword',
 'crusher',
 'counterblow',
 'kampfer',
 'soldierOfFortune']
_fortPersonalAchievementsBlockBuilder = StaticSizeBlockBuilder('fortAchievements', FORT_ACHIEVEMENTS_BLOCK_LAYOUT, FORT_ACHIEVEMENTS_DEPENDENCIES, _fortPersonalAchievementsPopUps)
CLAN_ACHIEVEMENTS_BLOCK_LAYOUT = ['medalRotmistrov']
_clanAchievementsBlockBuilder = StaticSizeBlockBuilder('clanAchievements', CLAN_ACHIEVEMENTS_BLOCK_LAYOUT, {}, [])
_playerInscriptionsBlockBuilder = ListBlockBuilder('inscriptions', 'H', {})
_playerEmblemsBlockBuilder = ListBlockBuilder('emblems', 'H', {})
_camouflagesBlockBuilder = ListBlockBuilder('camouflages', 'H', {})
COMPENSATION_BLOCK_LAYOUT = ['gold']
_compensationBlockBuilder = StaticSizeBlockBuilder('compensation', COMPENSATION_BLOCK_LAYOUT, {}, [])
vehicleDossierLayout = (_a15x15BlockBuilder,
 _a15x15_2BlockBuilder,
 _clanBlockBuilder,
 _clan2BlockBuilder,
 _companyBlockBuilder,
 _company2BlockBuilder,
 _a7x7BlockBuilder,
 _achievements15x15BlockBuilder,
 _vehTypeFragsBlockBuilder,
 _totalBlockBuilder,
 _max15x15BlockBuilder,
 _max7x7BlockBuilder,
 _playerInscriptionsBlockBuilder,
 _playerEmblemsBlockBuilder,
 _camouflagesBlockBuilder,
 _compensationBlockBuilder,
 _achievements7x7BlockBuilder,
 _historicalBlockBuilder,
 _maxHistoricalBlockBuilder,
 _uniqueVehAchievementBlockBuilder,
 _fortBattlesBlockBuilder,
 _maxFortBattlesBlockBuilder,
 _fortSortiesBlockBuilder,
 _maxFortSortiesBlockBuilder,
 _fortPersonalAchievementsBlockBuilder,
 _singleAchievementsBlockBuilder,
 _clanAchievementsBlockBuilder,
 _rated7x7BlockBuilder,
 _maxRated7x7BlockBuilder)
