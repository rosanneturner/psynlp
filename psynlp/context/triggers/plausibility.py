from enum import Enum

class PlausibilityContext(Enum):
    PLAUSIBLE = 1
    HYPOTHETICAL = 2

plausibility_triggers = {}

### Phrases
plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'phrase', 'preceding'] = [
    'als er',
    'als',
    'ambivalent',
    'bang te zijn',
    'beoordelen van',
    'bv',
    'bij',
    'cave',
    'dd', 
    'diagnostiek',
    'doel',
    'doelen',
    'differentiaal diagnostisch',  
    'eventueel',
    'eventuele',
    'evt',
    'hoopt',
    'hypothese',
    'hypothesen',
    'hypotheses',
    'indien er',
    'indien',
    'in geval van',
    'kan indiceren',
    'kan worden',
    'kan zijn',
    'kan',
    'kans op',
    'mgl',
    'mochten',
    'mocht',
    'mogelijk gerelateerd aan',
    'mogelijk',
    'mogelijke',
    'neiging tot',
    'niet duidelijk',
    'normaal gesproken',
    'observeren van',
    'onduidelijk',
    #'op indicatie',
    'rekening houden met',
    'risico op',
    'twijfel',
    'uitsluiten',
    'verdenking',
    'vermoedde',
    'vermoedden',
    'vermoeden van',
    'vermoeden',
    'vermoedt', 
    'verwacht',
    'verwachten',
    'verwachting',
    'voorlopige diagnose',
    'vraag',
    'vraagt',
    'wanneer',
    'wellicht',
    'wel of niet',
    'wordt gedacht aan',
    'zorgen voor',
    'zou',
    'dan',

]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'phrase', 'following'] = [ 
   '?',
   'ambivalent',
   'kan worden',
   'kan zijn',
   'niet besproken',
   'niet duidelijk',
   'niet uitgevraagd', 
   'onduidelijk',
   'vermoedde',
   'vermoedden',
   'zou worden',
   'zou zijn',
]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'phrase', 'pseudo'] = [ 
    'als baby',
    'als kind',
    'als puber', 
    'als tiener',
    'geduid als',
    'in verwachting',
    'niet mogelijk',
    'niet duidelijk van waar',
    'opname bij',
    'ontslag bij',
]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'phrase', 'termination'] = [ 
    'aanwezig',
    'door',
    'ter preventie',
    'waarna',
    'zeer waarschijnlijk',
    'zeker',
    'zonder twijfel',
    ',',
    '(',
    ')',
]

### Patterns
plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'pattern', 'preceding'] = [ 
    
    [{'LOWER' :  {'IN' : ['angst', 'angstig', 'bang']}},
     {'LOWER' : {'IN' : ['voor', 'om', 'dat']}}
    ]

]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'pattern', 'following'] = [ 

]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'pattern', 'pseudo'] = [ 

]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'pattern', 'termination'] = [ 

]

### Regexps
plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'regexp', 'preceding'] = [ 

]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'regexp', 'following'] = [ 

]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'regexp', 'pseudo'] = [ 

]

plausibility_triggers[PlausibilityContext.HYPOTHETICAL, 'regexp', 'termination'] = [ 

]
