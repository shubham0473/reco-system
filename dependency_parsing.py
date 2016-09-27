import os
import StanfordDependencies
import nltk
from nltk.parse import stanford
from nltk.tree import *
import nltk.data
import operator
from nltk.tokenize import RegexpTokenizer
import logging




########## Initialisation ##########
java_path = "C:/Program Files (x86)/Java/jre1.8.0_60/bin/java.exe"
os.environ['JAVA_HOME'] = java_path
os.environ['STANFORD_PARSER'] = 'C:\\JARS'
os.environ['STANFORD_MODELS'] = 'C:\\JARS'


t_parser = stanford.StanfordParser(model_path="C:\\JARS\\englishPCFG.ser.gz")
d_parser = StanfordDependencies.get_instance(jar_filename='E:\Old Jars\stanford-parser.jar')

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
word_tokenizer = RegexpTokenizer(r'\w+')
######################################








##########  Main Call to Function: Paragraph and Sentence Tokenization ##########
def find_features_advanced(review_list,class_words_list):

 try:
    feature_dictionary = {}
    for paragraph in review_list:
        review_sentences = tokenizer.tokenize(paragraph)
        for sentence in review_sentences:
                    
                    tokens = word_tokenizer.tokenize(sentence)
                    
                    ### Finding features in sentences with length below 80 ###
                    if(len(tokens) < 80):
                        trees = t_parser.raw_parse_sents((sentence,))
                        for tree in trees:
                            for node in tree:
                                str_tr = str(node)
                                dependencies = find_dependencies(str_tr)
                                feature_dictionary = find_double_prop_features(dependencies,feature_dictionary)
                                feature_dictionary = find_part_whole_features(dependencies,feature_dictionary,class_words_list)

                                


    cleaned_dictionary = remove_irr_features(feature_dictionary)
    return cleaned_dictionary
 except Exception, e:
     pass

        
########## Dependency Parsing and Feature Finding ##########
def find_dependencies(tree):
    with open('log.txt', 'a') as log_file:
        try:
            dependencies = d_parser.convert_tree(tree)
            return dependencies
        except Exception, e:
            log_file.write("Exception")
            pass
        log_file.close()

############################################################    



########## Double Propagation Method ##########
def find_double_prop_features(dependencies,feature_dictionary):
    for token in dependencies:
            if token[7] == 'nsubj' and (dependencies[token[6]-1][4] == 'JJ' or dependencies[token[6]-1][4] == 'JJS'):
                feature_nsubj = token[1]
                opinion_nsubj = dependencies[token[6]-1][1]
                feature_dictionary[feature_nsubj] = opinion_nsubj

            if token[7] == 'amod' and (dependencies[token[6]-1][4] == 'NN' or dependencies[token[6]-1][4] == 'NNS'):
                feature_amod = dependencies[token[6]-1][1]
                opinion_amod = token[1]
                feature_dictionary[feature_amod] = opinion_amod
                
    return feature_dictionary

#################################################

########## Remove Irrelevant Features ############
def remove_irr_features(feature_dictionary):

    irr_list = ['features','feature']
    irr_feat = []

    for key in feature_dictionary:
        if key in irr_list:
            irr_feat.append(key)
            
            
    for feature in irr_feat:
            del feature_dictionary[feature]
            
    return feature_dictionary

##################################################



########## Part Whole Features ##########
def find_part_whole_features(dependencies,feature_dictionary,class_concept_list):

    cleaned_dependencies = remove_determiners(dependencies)
    loop_run = len(cleaned_dependencies)

    noun_pos_list = ['NN','NNS']
    prep_pos_list = ['IN']
    prep_word_list = ['of','in','on']
    verb_pos_list = ['VB','VBD','VBG','VBN','VBP','VBZ']
    indicative_verb_list = ['has','have','include','contain','consist','comprise']

    

    for i in range(0,loop_run-3):

        present_token_type = cleaned_dependencies[i][4]
        between_token_type = cleaned_dependencies[i+1][4]
        next_token_type = cleaned_dependencies[i+2][4]

        between_token_word = cleaned_dependencies[i+1][1]
        next_token_word = cleaned_dependencies[i+2][1]
        present_token_word = cleaned_dependencies[i][1]


       

        #### Pattern 1 ####
        if (present_token_type in noun_pos_list) and (between_token_type in prep_pos_list) and (next_token_type in noun_pos_list):
            
            if between_token_word in prep_word_list:

                if next_token_word in class_concept_list:

                    feature_dictionary[present_token_word] = ""



        #### Pattern 2 ####
        if (present_token_type in noun_pos_list) and (between_token_word == 'with') and (next_token_type in noun_pos_list):
            
                if present_token_word in class_concept_list:

                    feature_dictionary[next_token_word] = ""


        #### Sentence Pattern ####
        if (present_token_type in noun_pos_list) and (between_token_type in verb_pos_list ) and (next_token_type in noun_pos_list):

            if between_token_word in indicative_verb_list:
                
                if present_token_word in class_concept_list:

                    feature_dictionary[next_token_word] = ""

                    


    for i in range(0,loop_run-2):

        present_token_type = cleaned_dependencies[i][4]
        next_token_type = cleaned_dependencies[i+1][4]

        present_token_word = cleaned_dependencies[i][1]
        next_token_word = cleaned_dependencies[i+1][1]

        
        #### Pattern 3 ####
        if (present_token_type in noun_pos_list) and (next_token_type in noun_pos_list):
            
                if present_token_word in class_concept_list:

                    feature_dictionary[next_token_word] = ""

                elif next_token_word in class_concept_list:

                    feature_dictionary[present_token_word] = ""

        #### Pattern 3 ####
        if (present_token_word == 'no') and (next_token_type in noun_pos_list):

            feature_dictionary[next_token_word] = ""

            


    return feature_dictionary
            

    
    


#########################################

########## Determiner Removal ##########
def remove_determiners(dependencies):

    for token in dependencies:
        if token[4] == 'DT' and token[1] != 'no':
            dependencies.remove(token)
            
    return dependencies
            

#########################################











#Command: java -ea -cp C:\stanford-parser.jar edu.stanford.nlp.trees.EnglishGrammaticalStructure -basic -treeFile c:\users\naveen~1\appdata\local\temp\tmpnrw8ig -keepPunct
