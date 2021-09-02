from enum import Enum

class ExperiencerContext(Enum):
    PATIENT = 1
    OTHER = 2

experiencer_triggers = {}

persons = ['vader', 'vdr', 'moeder', 'mdr', 'broer', 'broertje', 'zus', 'zusje', 'oom', 'tante', 'neef', 'neefje', 'nicht', 'nichtje', 'opa', 'oma', 'grootvader', 'grootmoeder', 'buurman', 'buurvrouw', 'zoon', 'zoontje', 'dochter', 'dochtertje', 'huisgenoot', 'huisgenote', 'familie', 'fam', 'voogd', 'papa', 'mama', 'pleegvader', 'pleegmoeder', 'schoonzus', 'schoonbroer', 'zwager', 'zuster', 'partner', 'echtgenoot', 'echtgenote', 'vriend', 'vriendje', 'vriendin', 'vriendinnetje', 'medepatient', 'medepatiente', 'medept', 'groepsgenoot',
'groepsgenote', 'gg', 'klasgenoot', 'klasgenote', 'medeleerling', 'medestudent', 'buurjongen', 'buurmeisje']
persons_plural = ['broers', 'broertjes', 'zussen', 'zusjes', 'ooms', 'tantes', 'neven', 'neefjes', 'nichten', 'nichtjes', 'zoons', 'zoontjes', 'dochters', 'dochtertjes', 'huisgenoten', 'huisgenotes', 'ouders', 'grootouders', 'stiefouders', 'pleegouders', 'buren', 'vrienden', 'vriendinnen', 'vriendinnetjes', 'ggn', 'ggen', 'groepsgenoten', 'klasgenoten', 'medeleerlingen', 'medestudenten', 'medepatienten', 'medepten', 'anderen']

persons_professional =  ['juf', 'mentor', 'decaan', 'collega', 'werkgever', 'begeleider', 'woonbegeleider', 'trajectbegeleider', 'behandelaar', 'therapeut', 'psychotherapeut', 'psychiater', 'psycholoog', 'dienstdoende', 'arts', 'groepsleiding', 'verpl', 'verpleging', 'verpleegkundige', 'buurtteam', 'wijkteam', 'crisisdienst', 'zorgverlener', 'og', 'advocaat', 'tolk', 'chirurg', 'vrijwilliger']
persons_professional_plural = ['zorgverleners', 'buurtteams', 'wijkteams', 'therapeuten', 'psychotherapeuten', 'behandelaren',  'behandelaars', 'artsen', 'verpleegkundigen', 'vpken', 'psychiaters', 'psychologen', 'vrijwilligers']
### Phrases
experiencer_triggers[ExperiencerContext.OTHER, 'phrase', 'preceding'] = [
    'familiair',
    'familiaire',
    'familieleden',
    'familiegeschiedenis',
    'moederszijde',
    'vaderszijde',
]

experiencer_triggers[ExperiencerContext.OTHER, 'phrase', 'following'] = [
    'in de familie',
    'in familie',
]

experiencer_triggers[ExperiencerContext.OTHER, 'phrase', 'pseudo'] = [
    'door familie',
    'familie',
    'met familie',
    'naar familie',
]

experiencer_triggers[ExperiencerContext.OTHER, 'phrase', 'termination'] = [
    'beslist',
    'besloot',
    'daarnaast',
    'geen',
    'hijzelf',
    'huidig',
    'klaagt',
    'niet',
    'nu',
    'patient haar',
    'patient zijn',
    'patient',
    'pt haar',
    'pt zijn',
    'pt',
    'rapporteerde',
    'vandaag',
    'welke',
    'zelf',
    'zijzelf',
    ','
]

### Patterns
experiencer_triggers[ExperiencerContext.OTHER, 'pattern', 'preceding'] = [

    # broer
    # broers
    [{'LOWER' : {'IN' : persons + persons_plural}}],

    # broer zijn
    # zus haar
    [{'LOWER' : {'IN' : persons}},
     {'LOWER' : {'IN' : ['zijn', 'haar']}}
    ],

    # broers hun
    [{'LOWER' : {'IN' : persons_plural}},
     {'LOWER' : 'hun'}
    ],

    # broer's
    [{'LOWER' : {'IN' : persons}},
     {'LOWER' : r"'"},
     {'LOWER' : 's'}
    ],
]

experiencer_triggers[ExperiencerContext.OTHER, 'pattern', 'following'] = [
    # bij broer
    [{'LOWER' : 'bij'},
     {'LOWER' : {'IN' : persons + persons_plural}}
    ],
]

experiencer_triggers[ExperiencerContext.OTHER, 'pattern', 'pseudo'] = [

    # door broer
    # met broer
    [{'LOWER' : {'IN' : ['door', 'met', 'naar', 'volgens', 'vertelt', 'vertelde', 'vertellen', 'vertelden']}},
     {'LOWER' : {'IN' : persons + persons_plural}}
    ],

    # broer belde
    # broer zei
    # broer vond
    # broers belden
    # broers zeiden
    # broers vonden
    [{'LOWER' : {'IN' : persons + persons_plural}},
     {'LOWER' : {'IN' : ['belde', 'belden', 'zei', 'zeiden', 'maakte', 'vond', 'vonden', 'vertelt', 'vertelde', 'vertellen', 'vertelden']}}
    ],

    # broef gaf aan
    # broers gaven aan
    [{'LOWER' : {'IN' : persons + persons_plural}},
     {'LOWER' : {'IN' : ['gaf', 'gaven']}},
     {'LOWER' : {'IN' : ['aan']}}
    ],
    
    # overlijden van zijn haar familielid
    [{'LOWER': 'overlijden'},
     {'LOWER': 'van'},
     {'LOWER' : {'IN' : ['zijn', 'haar']}},
     {'LOWER' : {'IN' : persons + persons_plural}},
    ],
]

experiencer_triggers[ExperiencerContext.OTHER, 'pattern', 'termination'] = [

]

### Regexps
experiencer_triggers[ExperiencerContext.OTHER, 'regexp', 'preceding'] = [

]

experiencer_triggers[ExperiencerContext.OTHER, 'regexp', 'following'] = [

]

experiencer_triggers[ExperiencerContext.OTHER, 'regexp', 'pseudo'] = [

]

experiencer_triggers[ExperiencerContext.OTHER, 'regexp', 'termination'] = [

]
