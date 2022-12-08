# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
 
 
import json
import pickle
import logging

logger = logging.getLogger(__name__)

def main(lang):

    with open("data/wikipedia/t2/en/enwiki0.pkl", "rb") as f:                                                                                                                                                                                                          
        data = pickle.load(f)  
    logger.info("loaded wikipedia data")

    # dict title --> wikidata_id, needed as BLINK format does not contain wikidata_ids
    with open("data/wikidata/lang_title2wikidataID.pkl", "rb") as f:
        title2wikidataid = pickle.load(f)
    title2wikidataid = {k[1]: v.pop() for k, v in title2wikidataid.items() if k[0]==lang}
    logger.info("loaded wikidata data")

    # write out entities t2
    wiki_id2title = {}
    with open("data/entities/entity_all.jsonl", 'w') as f_out:
        for ent in data:
            title = data[ent]['paragraphs'][0].strip()
            
            definition_collected = ''
            for definition in data[ent]['paragraphs'][1:]:
                definition = definition.strip()
                if definition!='' and len(definition.split(" "))>4:
                    definition_collected += definition
                    definition_collected += ' '
                if len(definition_collected.split(" "))>=128:
                    break

            if definition_collected!='':
                entity = {}
                entity['title'] = title
                entity['entity'] = title
                entity['text'] = definition_collected
                entity['idx'] = ent
                if title in title2wikidataid:
                    entity["wikidata_id"] = title2wikidataid[title]
                    timestamp = '_'.join(data[ent]['timestamp'].split('-')[0:2])
                    entity['time_stamp'] = timestamp
                    wiki_id2title[ent] = entity['entity']
                    f_out.write(json.dumps(entity))
                    f_out.write('\n')

    logger.info("Processed all entities t2")

    # adding wikidata id to BLINK entities
    entities = set()
    with open("data/entities/entity.jsonl") as f:
        with open("data/entities/entity_t1.jsonl", 'w') as f_out:
            for line in f:
                line = json.loads(line)
                ent_id = line['idx'].split('=')[-1]
                entities.add(ent_id)
                if ent_id in wiki_id2title:
                    updated_title = wiki_id2title[ent_id]
                    line["wikidata_id"] =  title2wikidataid[updated_title]
                else:
                    line["wikidata_id"] = "None"
                f_out.write(json.dumps(line))
                f_out.write("\n")
    logger.info("Processed all entities t1")

    # write out delta t2-t1   
    with open("data/entities/entity_t2.jsonl", 'w') as f_out:
        for ent in data:
            
            title = data[ent]['paragraphs'][0].strip()
            
            definition_collected = ''
            for definition in data[ent]['paragraphs'][1:]:
                definition = definition.strip()
                if definition!='' and len(definition.split(" "))>4:
                    definition_collected += definition
                    definition_collected += ' '
                if len(definition_collected.split(" "))>=128:
                    break

            if definition_collected!='' and ent not in entities:
                entity = {}
                entity['title'] = title
                entity['entity'] = title
                entity['text'] = definition_collected
                entity['idx'] = ent
                if title in title2wikidataid:
                    entity["wikidata_id"] =  title2wikidataid[title] 
                    timestamp = '_'.join(data[ent]['timestamp'].split('-')[0:2])
                    entity['time_stamp'] = timestamp
                    f_out.write(json.dumps(entity))
                    f_out.write('\n')
    
    logger.info("Processed all entities t2-t1")


if __name__ == '__main__':
    lang = "en"
    main(lang)
