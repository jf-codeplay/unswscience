from nltk.tag import StanfordNERTagger
import os
from extract_experience import config as config


def tagger(sentence):
    os.environ['JAVAHOME'] = config.java_path
    st = StanfordNERTagger(config.classifier_path, config.jar_path)
    named_entities = []
    temp_entity_name = ''
    temp_named_entity = None
    tag_iter = st.tag(sentence.split())
    tag_iter.append(('pseudo-term', 'O'))  # Make sure the last item has 'O' as the tag so that the last
    # temp_named_entity can be picked up after the if condition
    for term, tag in tag_iter:
        if tag == 'PERSON':
            temp_entity_name = ' '.join([temp_entity_name, term]).strip()
            temp_named_entity = (temp_entity_name, tag)
        else:
            if temp_named_entity:
                named_entities.append(temp_named_entity)
                temp_entity_name = ''
                temp_named_entity = None
    return named_entities

