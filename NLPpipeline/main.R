require(dplyr)
require(tidyr)
require(readr)
require(stringr)
require(lubridate)
require(tokenizers)
require(jsonlite)

#-------------------------------------------------------------------------------
#helper functions---------------------------------------------------------------
#-------------------------------------------------------------------------------

#' pastes values in vector that are not NA and collapses with comma
#'
#' @param x vector of strings
#'
#' @return string
paste_not_NA <- function(x){
  paste(x[!is.na(x)], collapse = ",")
}

#functions for importing the JSON files with phrases ---------------------------

#' convert json string to regex
#'
#' @param json_patterns
#'
#' @return regex pattern
jsonl_to_regex <- function(json_patterns){
  regex_pattern <-  json_patterns  %>%
    str_extract_all("pattern.*") %>%
    str_replace_all("\\\"sentiment.*", "") %>%
    str_replace_all("pattern.*\\:\"", "") %>%
    gsub(pattern = ".{2}$", replacement = "")%>%
    paste0(collapse = "|")
  
  return(regex_pattern)
}

#' function for importing phrase lists from json and converting them to lists of
#' regex expressions
#'
#' @param entity_filename name of the file that contains the entity (theme) phrases
#' @param dir directory that contains the folder with phrase lists
#' @param positive_filename name of the file that contains positive change phrases 
#' @param negative_filename name of the file that contains negative change phrases 
#'
#' @return list with regular expressions for the theme and change phrases
get_patterns <- function(entity_filename,
                         dir,
                         positive_filename = "jsonfiles/positieve_verandering_patterns.jsonl",
                         negative_filename = "jsonfiles/negatieve_verandering_patterns.jsonl"){
  phrases_entity <- read_lines(file.path(dir, entity_filename)) %>%
    jsonl_to_regex()
  phrases_positive <- read_lines(file.path(dir, positive_filename)) %>%
    jsonl_to_regex()
  phrases_negative <- read_lines(file.path(dir, negative_filename)) %>%
    jsonl_to_regex()
  
  return(list(
    entity = phrases_entity,
    positive = phrases_positive,
    negative = phrases_negative
  ))
}

#functions for filtering clinical notes sentences with phrases------------------

#' helper to neatly extract all matched phrases and collapse with comma
#'
#' @param text string to search
#' @param pattern regex pattern
#'
#' @return collapsed found phrases
find_and_paste <- function(text, pattern){
  paste(unlist(str_extract_all(text, pattern)), collapse = ",")
}

#' filter a dataframe with sentences by theme and change phrases
#' and extract these phrases
#'
#' @param df data frame with columns TextID, text, entity and entity_comp (booleans
#' indicating whether a phrase was detected in the previous step), increasing_change 
#' and decreasing change (booleans indicating whether a change phrase was detected 
#' in the previous step)
#' @param entity column name of the boolean column indicating if a theme phrase was present
#' @param entity_comp column name of the boolean column indicating if a comparative theme phrase was present
#' @param entity_patterns regex patterns of theme phrases
#' @param entity_comp_patterns regex patterns of comparative theme phrases
#' @param change_patterns regex patterns of change phrases
#'
#' @return filtered data frame with the theme and change phrases extracted from the text
filter_by_entity_and_extract <- function(df, entity, entity_comp = NULL, 
                                         entity_patterns, entity_comp_patterns = NULL,
                                         change_patterns){
  
  if(!is.null(entity_comp_patterns)){
    sentences_entity_change <- df %>%
      filter(({{ entity }}&(decreasing_change | increasing_change)) | {{ entity_comp }}) %>%
      select(TextID, text, 
             {{ entity }}, {{ entity_comp }}, increasing_change, decreasing_change) %>%
      #filter alvast de patronen er uit voor de contextmatcher
      mutate(entity_detected = sapply(text, find_and_paste, pattern = entity_patterns),
             entity_comp_detected = sapply(text, find_and_paste, pattern = entity_comp_patterns),
             change_detected = sapply(text, find_and_paste, pattern = change_patterns)
      )
  } else {
    sentences_entity_change <- df %>%
      filter({{ entity }}&(decreasing_change | increasing_change)) %>%
      select(TextID, text,
             {{ entity }}, increasing_change, decreasing_change) %>%
      #filter alvast de patronen er uit voor de contextmatcher
      mutate(entity_detected = sapply(text, find_and_paste, pattern = entity_patterns),
             entity_comp_detected = "",
             change_detected = sapply(text, find_and_paste, pattern = change_patterns))
  }
  
  return(sentences_entity_change)
}

#Filters 1  and 2 -----------------------------------------------------------

#' from a data frame with clinical notes sentences, create a list with data frames
#' with filtered sentences and extracted phrases, one for each theme.
#'
#' @param clinical_notes_cleaned data frame with clinical notes sentences with columns "text" and "TextID".
#' strings in text should be all lower case.
#' @param dir directory where json files with patterns are stored
#'
#' @return list with four dataframes
#' @examples 
#' testdf <- data.frame(TextID = c(1,2),
#'   text = c("meer angstig", "minder depressief")
#'   )
#' res <- create_filtered_sentences_per_theme(testdf, dir = "")
create_filtered_sentences_per_theme <- function(clinical_notes_cleaned, dir){
  
  #import the phrases from json 
  patterns_klacht <- get_patterns(entity_filename = "jsonfiles/klachten_patterns.jsonl", dir = dir)
  patterns_maatschappelijk <- get_patterns(entity_filename = "jsonfiles/maatschappelijk_patterns.jsonl", dir = dir)
  patterns_welzijn <- get_patterns(entity_filename = "jsonfiles/welbevinden_patterns.jsonl", dir = dir)
  patterns_experience <- get_patterns(entity_filename = "jsonfiles/beleving_patterns.jsonl", dir = dir)
  #also for the comparative phrases
  patterns_klacht_comp <- get_patterns(entity_filename = "jsonfiles/klachten_comparative.jsonl", dir = dir)
  patterns_maatschappelijk_comp <- get_patterns(entity_filename = "jsonfiles/maatschappelijk_comparative.jsonl", dir = dir)
  patterns_welzijn_comp <- get_patterns(entity_filename = "jsonfiles/welbevinden_comparative.jsonl", dir = dir)
  
  #for efficiency, search clinical notes before extracting the phrases
  clinical_notes_with_changes <- clinical_notes_cleaned %>%
    mutate(klacht_comp = str_detect(text, patterns_klacht_comp$entity),
           maatschappelijk_comp = str_detect(text, patterns_maatschappelijk_comp$entity),
           welzijn_comp = str_detect(text, patterns_welzijn_comp$entity),
           decreasing_change = str_detect(text, patterns_klacht$positive),
           increasing_change = str_detect(text, patterns_klacht$negative))
  clinical_notes_entities <- clinical_notes_with_changes %>%
    filter(klacht_comp|maatschappelijk_comp|welzijn_comp|decreasing_change|increasing_change) %>%
    mutate(kernklacht = str_detect(text, patterns_klacht$entity),
           maatschappelijk = str_detect(text, patterns_maatschappelijk$entity),
           welbevinden = str_detect(text, patterns_welzijn$entity),
           experience = str_detect(text, patterns_experience$entity))
  
  #return only sentences with a comparative, or a theme phrase + change phrase
  alle_change_words <- paste(c(patterns_klacht$positive, patterns_klacht$negative), collapse = "|")
  sentences_klacht <- clinical_notes_entities %>%
    filter_by_entity_and_extract(entity = kernklacht, entity_comp = klacht_comp, 
                                 entity_patterns = patterns_klacht$entity, entity_comp_patterns = patterns_klacht_comp$entity, 
                                 change_patterns = alle_change_words)
  sentences_sociaal <- clinical_notes_entities %>%
    filter_by_entity_and_extract(entity = maatschappelijk, entity_comp = maatschappelijk_comp, 
                                 entity_patterns = patterns_maatschappelijk$entity, 
                                 entity_comp_patterns = patterns_maatschappelijk_comp$entity, 
                                 change_patterns = alle_change_words)
  sentences_welzijn <- clinical_notes_entities %>%
    filter_by_entity_and_extract(entity = welbevinden, entity_comp = welzijn_comp, 
                                 entity_patterns = patterns_welzijn$entity, 
                                 entity_comp_patterns = patterns_welzijn_comp$entity, 
                                 change_patterns = alle_change_words)
  sentences_experience <- clinical_notes_entities %>%
    filter_by_entity_and_extract(entity = experience, 
                                 entity_patterns = patterns_experience$entity, 
                                 change_patterns = alle_change_words)
  
  return(list(
    klachten = sentences_klacht,
    maatschappelijk = sentences_sociaal,
    welbevinden = sentences_welzijn,
    beleving = sentences_experience
  ))
}

#Filter 3 and add sentiment per theme ------------------------------------------


#' Match contexts to theme and change phrases in clincial notes sentences,
#' filter by correct contexts and add sentiment scores.
#'
#' @param text_df data frame created in create_filtered_sentences_per_theme
#' @param theme theme corresponding to the theme filtered in text_df
#' @param dir directory where the json files with phrases are stored
#'
#' @return data frame with sentences, extracted theme phrases and sentiment scores.
match_context_add_sentiment <- function(text_df, theme, dir){
  theme <- match.arg(theme, choices = c("klachten", "maatschappelijk", "welbevinden", "beleving"))
  
  use_python(Sys.which("python"))
  source_python("match_outcome_contexts.py")
  
  if(theme == "beleving"){
    cm <- loadContextMatcher(beleving = TRUE)
  } else {
    cm <- loadContextMatcher()
  }
  
  entities_to_match <- createEntitiesToMatch(file.path(dir, "jsonfiles", paste0(theme, "_patterns.jsonl")),
                                             file.path(dir, "jsonfiles", "positieve_verandering_patterns.jsonl"),
                                             file.path(dir, "jsonfiles", "negatieve_verandering_patterns.jsonl"))
  bem <- loadEntityMatcher(entities_to_match)
  
  entities <- createEntities(bem, 
                             text_df$entity_detected, 
                             text_df$entity_comp_detected, 
                             text_df$change_detected, 
                             text_df$text)
  
  if(theme == "beleving"){
    entities_contexts <- matchCustomContexts(text_df$text, entities, cm, beleving = TRUE)
  } else {
    entities_contexts <- matchCustomContexts(text_df$text, entities, cm)
  }
  
  positionfilter <- checkCorrectPosition(entities_contexts$rules, 
                                         entities_contexts$start_token, 
                                         text_df$text, 
                                         bem
  )
  
  cm_result <- cbind(text_df %>% select(TextID, text), 
                     entities_contexts, 
                     correct_positions = positionfilter)
  
  if(theme == "beleving"){
    filtered_sentences <- cm_result %>%
      filter_correct_contexts(isBeleving = TRUE)
  } else {
    filtered_sentences <- cm_result %>%
      filter_correct_contexts()
  }
  
  filtered_sentences_sentiment <- tryCatch(filtered_sentences %>% add_sentiment_scores(dir = dir, theme = theme),
                                           error = function(e){
                                             warning("failed to add sentiment scores") 
                                             return(filtered_sentences)
                                           }
  )
  
  return(filtered_sentences_sentiment)
}

#' Filter a dataframe with sentences, theme and change phrases and contexts
#' by correct contexts
#'
#' @param data dataframe with clinical notes, extracted text phrases and matched contexts
#' @param isBeleving boolean indicating if the theme to analyze is patient experience
#'
#' @return filtered data frame with sentences with phrases and changes in the correct contexts
#' 
#' @examples 
#' testdf <- data.frame(TextID = c(1,2,3),
#'   text = c("meer angstig", "minder depressief", "niet minder depressief"),
#'   rules = c("phrase,change", "phrase,change", "phrase,change"),
#'   texts = c("angstig,meer", "depressief,minder", "depressief,minder"),
#'   context_experiencer = c("PATIENT,PATIENT","PATIENT,PATIENT", "PATIENT,PATIENT"),
#'   context_negated = c("AFFIRMED,AFFIRMED","AFFIRMED,AFFIRMED", "NEGATED,AFFIRMED"),
#'   context_plausibility = c("PLAUSIBLE,PLAUSIBLE","PLAUSIBLE,PLAUSIBLE","PLAUSIBLE,PLAUSIBLE"),
#'   context_time = c("CURRENT,CURRENT","CURRENT,CURRENT","CURRENT,CURRENT"),
#'   context_patient = c("PATIENT,PATIENT","PATIENT,PATIENT","PATIENT,PATIENT"),
#'   correct_positions = c(TRUE,TRUE,TRUE)
#'  )
#' filter_correct_contexts(testdf)
filter_correct_contexts <- function(data, isBeleving = FALSE){
  if(isBeleving){
    filtered_contexts <- data %>%
      #fix for tokenization error
      mutate(nkomma = str_count(texts, ","), nkomma2 = str_count(rules, ",")) %>% 
      filter(nkomma == nkomma2) %>%
      select(TextID, text, rules, texts, context_experiencer, context_negated, 
             context_plausibility, context_time, context_patient, correct_positions) %>%
      separate_rows(rules:context_patient, sep =",") %>%
      #only check change context for experiencer, plausibility, time
      #i.e. if rule is phrase it is ok, otherwise need correct context
      filter(rules == "phrase" | context_experiencer == "PATIENT") %>%
      filter(rules == "phrase" | context_plausibility == "PLAUSIBLE") %>%
      filter(rules == "phrase" | context_time == "CURRENT") %>%
      #check extra context:if the patient is the actor for the experience phrase
      filter(rules == "change" | context_patient == "PATIENT")
  } else {
    filtered_contexts <- data %>%
      #fix for tokenization error
      mutate(nkomma = str_count(texts, ","), nkomma2 = str_count(rules, ",")) %>% 
      filter(nkomma == nkomma2) %>%
      select(TextID, text, rules, texts, context_experiencer, context_negated, 
             context_plausibility, context_time, correct_positions) %>%
      separate_rows(rules:context_time, sep =",") %>%
      filter(context_experiencer == "PATIENT") %>%
      filter(context_negated == "AFFIRMED") %>%
      filter(context_plausibility == "PLAUSIBLE") %>%
      filter(context_time == "CURRENT")
  }
  filtered_contexts <- filtered_contexts %>%
    filter(correct_positions|rules == "phrase_comp") %>%
    pivot_wider(names_from = rules, values_from = texts, 
                values_fn = list(texts = paste_not_NA))
  
  if(!"phrase_comp" %in% colnames(filtered_contexts)){
    filtered_contexts <- filtered_contexts %>% mutate(phrase_comp = "")
  }
  
  #only keep sentences where phrase + change, or phrase_comp
  filtered_contexts %>% 
    filter(phrase_comp != "" | (phrase != "" & change != "")) %>%
    select(TextID, text, phrase, phrase_comp, change) %>%
    rename(entity = phrase, entity_comp = phrase_comp)
}

#' Add sentiment to data frame with clinical notes sentences, detected theme and 
#' change phrases
#'
#' @param change_sentences_df data frame returned by filter_correct_contexts
#' @param dir directory where json phrase patterns are stored
#' @param theme theme to analyze
#'
#' @return data frame with sentences and sentiment scores
add_sentiment_scores <- function(change_sentences_df, dir, theme){
  change_words_toename <- read_table(file.path(dir, "jsonfiles", "negatieve_verandering_patterns.jsonl"), col_names = FALSE) %>%
    mutate(change_phrase = sapply(X1, function(x){parse_json(x)$pattern}),
           change_sentiment = 1) %>%
    select(-X1)
  
  change_words_afname <- read_table(file.path(dir, "jsonfiles", "positieve_verandering_patterns.jsonl"), col_names = FALSE) %>%
    mutate(change_phrase = sapply(X1, function(x){parse_json(x)$pattern}),
           change_sentiment = -1) %>%
    select(-X1)
  
  change_words_sentiment <- rbind(change_words_toename, change_words_afname)
  
  if(theme == "beleving"){
    #for patient experience: 
    #all sentiments are exactly opposite, entities are neutral and do not have sentiment
    change_words_sentiment_experience <- change_words_sentiment %>%
      mutate(change_sentiment = -1*change_sentiment)
    
    change_sentences_sentiment <- change_sentences_df %>%
      mutate(sentence_id = row_number()) %>%
      filter(entity != "" & change != "") %>%
      #filter ")" in entities; causes error in str_locate
      filter(!str_detect(entity, "\\)|\\(|\\\\|\\}") & !str_detect(change, "\\)|\\(|\\\\|\\}") & !str_detect(text, "\\\\|\\}")) %>%
      separate_rows(entity, sep = ",") %>%
      separate_rows(change, sep = ",") %>%
      mutate(startchar = str_locate(text, entity)[,1],
             changeend = str_locate(text, regex(change, ignore_case = TRUE))[,2]) %>%
      mutate(nchar_from_entity = abs(changeend - startchar)) %>%
      group_by(sentence_id, entity) %>%
      filter(nchar_from_entity == min(nchar_from_entity)) %>%
      slice(1)%>%
      ungroup() %>%
      select(-nchar_from_entity, - startchar, - changeend) %>%
      #the patterns returned by python are not exact matches anymore, 
      #so a left join is not possible
      mutate(change_match = str_extract(change, paste(change_words_sentiment_experience$change_phrase, collapse = "|")))
    
    sentiment_per_sentence <- change_sentences_sentiment %>%
      left_join(change_words_sentiment_experience%>%rename(change_match = change_phrase), by = "change_match") %>%
      group_by(sentence_id) %>%
      summarise(total_sentiment = sum(change_sentiment))
    
    change_sentences_df <- change_sentences_df %>%
      mutate(sentence_id = row_number()) %>%
      left_join(sentiment_per_sentence, by = "sentence_id") %>%
      select(-sentence_id)
  } else {
    patterns_sentiment <- read_table(file.path(dir, paste0("jsonfiles/", theme, "_patterns.jsonl")), 
                                     col_names = FALSE) %>%
      mutate(entity = sapply(X1, function(x){parse_json(x)$pattern}),
             sentiment = as.numeric(sapply(X1, function(x){parse_json(x)$sentiment}))) %>%
      select(-X1)
    
    patterns_comparative <- read_table(file.path(dir, paste0("jsonfiles/", theme, "_comparative.jsonl"))
                                       , col_names = FALSE) %>%
      mutate(entity = sapply(X1, function(x){parse_json(x)$pattern}),
             sentiment = as.numeric(sapply(X1, function(x){parse_json(x)$sentiment}))) %>%
      select(-X1)
    
    change_sentences_sentiment <- change_sentences_df %>%
      mutate(sentence_id = row_number()) %>%
      select(-entity_comp) %>%
      filter(entity != "" & change != "") %>%
      #filter ")" in entities; causes error in str_locate
      filter(!str_detect(entity, "\\)|\\(|\\\\|\\}") & !str_detect(change, "\\)|\\(|\\\\|\\}") & !str_detect(text, "\\\\|\\}")) %>%
      separate_rows(entity, sep = ",") %>%
      #check which veranderwoord is closest and match that one
      separate_rows(change, sep = ",") %>%
      mutate(startchar = str_locate(text, entity)[,1],
             changeend = str_locate(text, change)[,2]) %>%
      mutate(nchar_from_entity = abs(changeend - startchar)) %>%
      group_by(sentence_id, entity) %>%
      filter(nchar_from_entity == min(nchar_from_entity)) %>%
      slice(1)%>%
      ungroup() %>%
      select(-nchar_from_entity, - startchar, - changeend) %>%
      #the patterns returned by python are not exact matches anymore, so a left join is not possible
      mutate(entity_match = str_extract(entity, paste(patterns_sentiment$entity, collapse = "|"))) %>%
      mutate(change_match = str_extract(change, paste(change_words_sentiment$change_phrase, collapse = "|")))
    
    sentiment_per_sentence <- change_sentences_sentiment %>%
      left_join(patterns_sentiment%>%rename(entity_match = entity), by = "entity_match") %>%
      left_join(change_words_sentiment%>%rename(change_match = change_phrase), by = "change_match") %>%
      #some change words ALWAYS indicate something bad or something good
      #independent of the sentiment of the theme phrase, correct for this.
      mutate(sentiment_per_pattern = case_when(
        str_detect(change_match, "beter|normalis|opkla|opknap|vooruitgang|bijtrek|bijgetrokken") ~ abs(sentiment * change_sentiment),
        str_detect(change_match, "achteruit|erger|slechter|escale|decompen") ~ -1*abs(sentiment * change_sentiment),
        TRUE ~ sentiment * change_sentiment
      )) %>%
      group_by(sentence_id) %>%
      summarise(sentimentscore = sum(sentiment_per_pattern))
    
    change_sentences_comparative_sentiment <- change_sentences_df %>%
      mutate(sentence_id = row_number()) %>%
      filter(entity_comp != "") %>%
      separate_rows(entity_comp, sep = ",") %>%
      mutate(entity_match = str_extract(entity_comp, paste(patterns_comparative$entity, collapse = "|"))) %>%
      left_join(patterns_comparative%>%rename(entity_match = entity), by ="entity_match") %>%
      group_by(sentence_id) %>%
      summarise(sentimentscore_comparative = sum(sentiment))
    
    change_sentences_sentiment_totaal <- sentiment_per_sentence %>%
      full_join(change_sentences_comparative_sentiment, by = "sentence_id") %>%
      mutate(sentimentscore_comparative = replace_na(sentimentscore_comparative, replace = 0)) %>%
      mutate(sentimentscore = replace_na(sentimentscore, replace = 0)) %>%
      mutate(total_sentiment = sentimentscore + sentimentscore_comparative) %>%
      select(-sentimentscore,-sentimentscore_comparative)
    
    change_sentences_df <- change_sentences_df %>%
      mutate(sentence_id = row_number()) %>%
      left_join(change_sentences_sentiment_totaal, by = "sentence_id") %>%
      select(-sentence_id)
  }
  
  return(change_sentences_df)
}

