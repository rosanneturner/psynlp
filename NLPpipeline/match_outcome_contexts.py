print("loading python functionality...")

import psynlp
import pandas
import numpy as np

from psynlp.preprocessing import BasicNormalizer
from psynlp.entity import BasicEntityMatcher
from psynlp.context import ContextMatcher
from psynlp.entity import Entity

from experiencer import ExperiencerContext, experiencer_triggers
from temporality import TemporalityContext, temporality_triggers
from negation import NegationContext, negation_triggers
from plausibility import PlausibilityContext, plausibility_triggers
from patientbeleving import PatientBelevingContext, patientbeleving_triggers

import patientbeleving
import temporality

def checkContext():
    print(patientbeleving.__file__)
    print(temporality.__file__)
    print([e.name for e in TemporalityContext])

def normalize(textvec):
    bn = BasicNormalizer()
    out = [bn.normalize(text) for text in textvec]
    return out

def createEntitiesToMatch(file_path_phrase_patterns,
                          file_path_change_patterns,
                          file_path_change_patterns2):
    phrases_patterns = pandas.read_json(file_path_phrase_patterns, lines = True)
    change_patterns = pandas.read_json(file_path_change_patterns, lines = True)
    change_patterns2 = pandas.read_json(file_path_change_patterns2, lines = True)
    
    entity_words = {}
    entity_words['phrase'] = phrases_patterns["pattern"].to_list()
    entity_words['change'] = change_patterns["pattern"].to_list() + change_patterns2["pattern"].to_list()
      
    return entity_words

def loadEntityMatcher(entities_to_match):
    print("Loading entitiy matcher...")
    bem = BasicEntityMatcher(entities_to_match)
    return(bem)

def createEntities(bem, entities_detected, entities_comp, veranderwoorden, pr_sentences):
    entities = []
    print("Started matching entities..")
    basicPb = 0
    for phrases_detected, phrases_comp_detected, veranderwoorden_detected, preprocessed_zin in zip(entities_detected,entities_comp,veranderwoorden,pr_sentences):
        entitiesCustom = []
        doc = bem.nlp(preprocessed_zin)
        
        basicPb = basicPb + 1
        if basicPb % 1000 == 0:
            print(basicPb, "out of", len(entities_detected))

        if phrases_detected != "":
            for phrase in phrases_detected.split(','):
                #selecteer de matchende tokens in de zin
                tokens_start = [i for i, v in enumerate(doc) if phrase in v.lower_]
                for token_start in tokens_start: 
                    newEntity = Entity(token_start = token_start,
                               token_end = token_start + 1,
                               rule = 'phrase',
                               text = doc[token_start:token_start+1])
                    entitiesCustom.append(newEntity)
                               
        if phrases_comp_detected != "":
            for phrase_comp in phrases_comp_detected.split(','):
                #selecteer de matchende tokens in de zin
                tokens_start = [i for i, v in enumerate(doc) if phrase_comp in v.lower_]
                for token_start in tokens_start: 
                    newEntity = Entity(token_start = token_start,
                               token_end = token_start + 1,
                               rule = 'phrase_comp',
                               text = doc[token_start:token_start+1])
                    entitiesCustom.append(newEntity)
                    
        if veranderwoorden_detected != "":            
            for veranderwoord in veranderwoorden_detected.split(','):
                #selecteer de matchende tokens in de zin
                tokens_start = [i for i, v in enumerate(doc) if veranderwoord in v.lower_]
                for token_start in tokens_start: 
                    newEntity = Entity(token_start = token_start,
                               token_end = token_start + 1,
                               rule = 'change',
                               text = doc[token_start:token_start+1])
                    entitiesCustom.append(newEntity)
        
        entities.append(entitiesCustom)                                                                                                                 
        
    return entities

def loadContextMatcher(beleving = False):
    #laad de contextmatcher in
    print("Loading context matcher...")
    customCM = ContextMatcher(add_preconfig_triggers=False)
    
    #nu voegen we onze bewerkte triggerlijsten en contexten toe
    customCM.add_custom_context(ExperiencerContext, experiencer_triggers)
    customCM.add_custom_context(TemporalityContext, temporality_triggers)
    customCM.add_custom_context(NegationContext, negation_triggers)
    customCM.add_custom_context(PlausibilityContext, plausibility_triggers)
    
    if beleving:
      customCM.add_custom_context(PatientBelevingContext, patientbeleving_triggers)
    
    return(customCM)

def matchCustomContexts(pr_sentences, entities, customCM, beleving = False):
    print("Started matching contexts...")
    basicPb = 0
    for sentence, entity in zip(pr_sentences, entities):
        basicPb = basicPb + 1
        if basicPb % 1000 == 0:
            print(basicPb, "out of", len(entities))
        customCM.match_context(sentence,entity)
        
    data = pandas.DataFrame()    
    data["rules"] = np.asarray(list(map(lambda x: str.join(",", [y.rule for y in x]), entities)))
    data["texts"] = np.asarray(list(map(lambda x: str.join(",", [str(y.text) for y in x]), entities)))
    data["start_token"] = np.asarray(list(map(lambda x: str.join(",", [str(y.token_start) for y in x]), entities)))

    data["context_experiencer"] = np.asarray(list(map(lambda x: str.join(",", [str(y.context[0]) for y in x]), entities)))
    data["context_negated"] = np.asarray(list(map(lambda x: str.join(",", [str(y.context[2]) for y in x]), entities)))
    data["context_plausibility"] = np.asarray(list(map(lambda x: str.join(",", [str(y.context[3]) for y in x]), entities)))
    data["context_time"] = np.asarray(list(map(lambda x: str.join(",", [str(y.context[1]) for y in x]), entities)))
    
    if beleving:
      data["context_patient"] = np.asarray(list(map(lambda x: str.join(",", [str(y.context[4]) for y in x]), entities)))
    
    return data

def checkCorrectPosition(rules, start_tokens, sentences, bem):
    correct_combination_filter = []      
    print("Started checking correct positions...")
    basicPb = 0
    
    for rule, position, text in zip(rules, start_tokens, sentences):
        basicPb = basicPb + 1
        if basicPb % 1000 == 0:
            print(basicPb, "out of", len(rules))
      
        any_combination_correct = False
        doc = bem.nlp(text)
        
        phrase_positions = list(position.split(",")[i] for i,v in enumerate(rule.split(",")) if 'phrase' in v)
        phrase_positions = [int(i) for i in phrase_positions]
        change_positions = list(position.split(",")[i] for i,v in enumerate(rule.split(",")) if 'change' in v)
        change_positions = [int(i) for i in change_positions]
        for i in phrase_positions:
            for j in change_positions:
                #check if phrase is a (grand)parent of a change
                phrase_is_parent = str(doc[j]).lower() in [str(child).lower() for child in doc[i].subtree]
                #check if phrase is a (grand)child of a change
                phrase_is_child = str(doc[i]).lower() in [str(child).lower() for child in doc[j].subtree]
               
                if phrase_is_parent or phrase_is_child:
                    any_combination_correct = True  
                    break 
                #check if phrase and change have the same parent
                elif doc[i].head.text in doc[j].head.text:
                    any_combination_correct = True  
                    break 
                
                #check if niece: "toenemende klachten van stress en PANIEK" 
                #"paniek"" is conjunct of "stress"", which shares a parent with "toenemende"
                phrase_is_niece = 'conj' in doc[i].dep_ and doc[i].head.head.text in doc[j].head.text
                    
                if phrase_is_niece:
                    any_combination_correct = True  
                    break 
            if any_combination_correct:
                break
                
        correct_combination_filter.append(any_combination_correct)
        
    return correct_combination_filter
        
    
print("finished")
