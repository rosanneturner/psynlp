# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 12:22:15 2021

@author: rturner
"""
from enum import Enum

class PatientBelevingContext(Enum):
    PATIENT = 1
    OTHER = 2

patientbeleving_triggers = {}

persons = ['vader', 'vdr', 'moeder', 'mdr', 'broer', 'broertje', 'zus', 'zusje', 'oom', 'tante', 'neef', 'neefje', 'nicht', 'nichtje', 'opa', 'oma', 'grootvader', 'grootmoeder', 'buurman', 'buurvrouw', 'zoon', 'zoontje', 'dochter', 'dochtertje', 'huisgenoot', 'huisgenote', 'familie', 'fam', 'voogd', 'papa', 'mama', 'pleegvader', 'pleegmoeder', 'schoonzus', 'schoonbroer', 'zwager', 'zuster', 'partner', 'echtgenoot', 'echtgenote', 'vriend', 'vriendje', 'vriendin', 'vriendinnetje', 'medepatient', 'medepatiente', 'medept', 'groepsgenoot',
'groepsgenote', 'gg', 'klasgenoot', 'klasgenote', 'medeleerling', 'medestudent', 'buurjongen', 'buurmeisje']
persons_plural = ['broers', 'broertjes', 'zussen', 'zusjes', 'ooms', 'tantes', 'neven', 'neefjes', 'nichten', 'nichtjes', 'zoons', 'zoontjes', 'dochters', 'dochtertjes', 'huisgenoten', 'huisgenotes', 'ouders', 'grootouders', 'stiefouders', 'pleegouders', 'buren', 'vrienden', 'vriendinnen', 'vriendinnetjes', 'ggn', 'ggen', 'groepsgenoten', 'klasgenoten', 'medeleerlingen', 'medestudenten', 'medepatienten', 'medepten', 'anderen']

persons_professional =  ['juf', 'mentor', 'decaan', 'collega', 'werkgever', 'begeleider', 'woonbegeleider', 'trajectbegeleider', 'behandelaar', 'therapeut', 'psychotherapeut', 'psychiater', 'psycholoog', 'dienstdoende', 'arts', 'groepsleiding', 'verpl', 'verpleging', 'verpleegkundige', 'buurtteam', 'wijkteam', 'crisisdienst', 'zorgverlener', 'og', 'advocaat', 'tolk', 'chirurg', 'vrijwilliger']
persons_professional_plural = ['zorgverleners', 'buurtteams', 'wijkteams', 'therapeuten', 'psychotherapeuten', 'behandelaren',  'behandelaars', 'artsen', 'verpleegkundigen', 'vpken', 'psychiaters', 'psychologen', 'vrijwilligers']

### Phrases
patientbeleving_triggers[PatientBelevingContext.OTHER, 'phrase', 'preceding'] = [
    #de schrijver (arts, vpk) vind/ beleeft iets:
    'ik',
]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'phrase', 'following'] = [
]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'phrase', 'pseudo'] = [
]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'phrase', 'termination'] = [
    'en',
    ','
]

### Patterns
patientbeleving_triggers[PatientBelevingContext.OTHER, 'pattern', 'preceding'] = [

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

patientbeleving_triggers[PatientBelevingContext.OTHER, 'pattern', 'following'] = [

]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'pattern', 'pseudo'] = [
]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'pattern', 'termination'] = [

]

### Regexps
patientbeleving_triggers[PatientBelevingContext.OTHER, 'regexp', 'preceding'] = [

]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'regexp', 'following'] = [

]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'regexp', 'pseudo'] = [

]

patientbeleving_triggers[PatientBelevingContext.OTHER, 'regexp', 'termination'] = [

]
