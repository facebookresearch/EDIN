# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import argparse
import json
import nltk
from nltk.tokenize import word_tokenize
import os
import pickle
import random
import tqdm
import logging
from transformers import AutoTokenizer

random.seed(10)
nltk.download('punkt')

tokenizer = AutoTokenizer.from_pretrained("bert-large-cased")

logger = logging.getLogger(__name__)
def write_out(entities, paragraph, data_example_id, time_stamp, title, wiki_ids, f_out):
    
    '''diff = 0
    for entity in entities:
        entity['start'] += diff
        entity['end'] += diff

        start = int(entity['start'])
        end = int(entity['end'])
        if end < len(paragraph):
            if paragraph[end] == "-":
                paragraph = paragraph[:end] + " - " + paragraph[end + 1:]
                diff += 2
        if start!=0:
            try:
                if paragraph[start - 1] == "-":
                    paragraph = paragraph[:start - 1] + " - " + paragraph[start:]
                    diff += 2
                    entity['start'] += 2
                    entity['end'] += 2
            except:
                pass'''
    # tokenize
    paragraph_tokenized = []
    gt_entities = []
    entities_raw = []
    pre = 0
    for entity in entities:
        start = int(entity['start'])
        end = int(entity['end'])
        pre_paragraph = word_tokenize(paragraph[pre:start])
        entity_tokenized = word_tokenize(paragraph[start:end])
        pre = end
        paragraph_tokenized.extend(pre_paragraph)
        wiki_id = next(iter(entity['wikidata_ids']))
        for wiki_id in entity['wikidata_ids']:
            if wiki_id in wiki_ids:
                gt_entities.append([len(paragraph_tokenized), len(entity_tokenized), wiki_id, "wiki"])
                entities_raw.append([entity['start'], entity['end']-entity['start'], wiki_id, 'wiki'])
                break
        paragraph_tokenized.extend(entity_tokenized)

    post_paragraph = word_tokenize(paragraph[pre:])
    paragraph_tokenized.extend(post_paragraph)

    keep = True
    for token in paragraph_tokenized:
        if len(tokenizer.encode(token))==2:
            keep = False
    
    '''keep = True
    if len(gt_entities)!=0:
        for ent in gt_entities:
            try:
                paragraph_tokenized[ent[0]:ent[0]+ent[1]]
                paragraph_tokenized[ent[0]]
                paragraph_tokenized[ent[0]+ent[1]-1]
            except:
                keep = False
                print(paragraph_tokenized)

        if keep:'''
    if keep:
        template = {
            "data_example_id": data_example_id,
            "text": paragraph_tokenized,
            "text_raw": paragraph,
            "gt_entities": gt_entities,
            "entities_raw": entities_raw,
            "time_stamp": time_stamp,
            "title": title}
        f_out.write(json.dumps(template))
        f_out.write("\n")


def process_wiki_based_data(base_dataset, lang):
    
    if 't1' in base_dataset:
        entity_path = "data/entities/entity_t1.jsonl"
    else:
        entity_path = "data/entities/entity_all.jsonl"
    
    wikidata_ids = set()
    with open(entity_path) as f:
        for line in f:
            line = json.loads(line)
            wikidata_ids.add(line['wikidata_id'])

    with open(base_dataset + lang + "/" + lang + "wiki0.pkl", "rb") as f:
        data = pickle.load(f)
    
    with open(base_dataset + lang + ".jsonl", "w") as f_out:
        data_example_id = 0
        for d in tqdm.tqdm(data):
            if len(data[d]['anchors']) > 0:
                paragraph_id = data[d]['anchors'][0]['paragraph_id']
                entities = []
                time_stamp = "_".join(data[d]['timestamp'].split(":")[0].split("-")[:2])
                title = data[d]['title']
                for anchor in data[d]['anchors']:
                    
                    if len(anchor['wikidata_ids'])==0:
                            continue

                    # process paragraph by paragraph
                    paragraph_id_current = anchor['paragraph_id']
                    if paragraph_id_current == paragraph_id: 
                        entities.append(anchor)

                    else:
                        # only give examples containing entities
                        if paragraph_id > 1 and len(entities) > 0:                        
                            keep = True
                            paragraph = data[d]['paragraphs'][paragraph_id].strip()

                            if len(data[d]['paragraphs'][paragraph_id])>10:
                                for ent in entities:

                                    # filter out parsing errors
                                    start_id = ent['start']
                                    end_id = ent['end'] 
                                    if start_id >=len(paragraph)-1 or end_id > len(paragraph)-1 or start_id==end_id:
                                        keep = False

                                if keep:   
                                    write_out(entities, data[d]['paragraphs'][paragraph_id], data_example_id, time_stamp, title, wikidata_ids, f_out)
                                    data_example_id += 1
                        
                        paragraph_id = anchor['paragraph_id']
                        entities = [anchor]


def split_data_t1(base_dataset, lang, num_pretrain=17000000, num_preval=5000, num_jointrain=20000, num_jointval=5000):

    titles = {'pretrain': set(), 'predev': set(), 'jointtrain': set(), 'jointdev': set(), 'test': set()}
    with open(base_dataset + "/" + lang + ".jsonl") as f, \
            open(base_dataset + "/" + lang + "_pretrain.jsonl", 'w') as f_pretrain, \
            open(base_dataset + "/" + lang + "_predev.jsonl", 'w') as f_prevalid, \
            open(base_dataset + "/" + lang + "_jointtrain.jsonl", 'w') as f_jointtrain, \
            open(base_dataset + "/" + lang + "_jointdev.jsonl", 'w') as f_jointvalid, \
            open(base_dataset + "/" + lang + "_test.jsonl", 'w') as f_test:
        num_instances = sum(1 for _ in f)
        f.seek(0)

        num_test = num_instances-num_pretrain-num_preval-num_jointrain-num_jointval

        p_pretrain = num_pretrain/(num_instances-num_jointrain-num_jointval-(num_test/2))
        p_preval = 1-(num_preval/(num_instances-num_jointrain-num_jointval-(num_test/2)))

        p_jointtrain = num_jointrain / (num_instances - num_pretrain-num_preval-(num_test/2))

        p_jointval = 1 - (num_jointval / (num_instances - num_pretrain-num_preval-(num_test/2)))

        p_joint = (num_pretrain+num_preval+(num_test/2))/num_instances

        n_pretrain = 0
        n_preval = 0
        n_jointrain = 0
        n_joinval = 0
        for line in f:
            line_ = json.loads(line)
            r = random.random()
            if r < p_joint:
                r = random.random()
                if n_pretrain < num_pretrain and r < p_pretrain:
                    f_pretrain.write(line)
                    titles['pretrain'].add(line_["title"])
                    n_pretrain += 1
                elif n_preval < num_preval and r > p_preval:
                    f_prevalid.write(line)
                    titles['predev'].add(line_["title"])
                    n_preval += 1
                else:
                    f_test.write(line)
            else:
                r = random.random()
                if n_jointrain < num_jointrain and r < p_jointtrain:
                    f_jointtrain.write(line)
                    titles['jointtrain'].add(line_["title"])
                    n_jointrain += 1
                elif n_joinval < num_preval and r > p_jointval:
                    f_jointvalid.write(line)
                    titles['jointdev'].add(line_["title"])
                    n_joinval += 1

                else:
                    f_test.write(line)
                    titles['test'].add(line_["title"])

    for key in titles:
        titles[key] = list(titles[key])
        
    with open(base_dataset + "titles.json", 'w') as f:
        json.dump(titles, f)

def split_data_t2(base_dataset, lang, titles, num_pretrain=17000000, num_preval=5000, num_jointrain=20000, num_jointval=5000):
    idcs = {'train_dev': [], 'test': [], 'novel': []}
    num_instances = 0
    titles['train_dev'] = set(titles['pretrain'])
    titles['train_dev'].update(set(titles['predev']))
    titles['train_dev'].update(set(titles['jointtrain']))
    titles['train_dev'].update(set(titles['jointdev']))

    titles['test'] = set(titles['test'])
    with open(base_dataset + "/" + lang + ".jsonl") as f:
        for i, line in enumerate(f):
            line = json.loads(line)
            idx = line["data_example_id"]
            if line['title'] in titles['train_dev']:
                idcs['train_dev'].append(idx)
            if line['title'] in titles['test']:
                idcs['test'].append(idx)
            if line['title'] not in titles['train_dev'] and line['title'] not in titles['test']:
                idcs['novel'].append(idx)
            num_instances += 1

    with open(base_dataset + "/" + lang + ".jsonl") as f, \
            open(base_dataset  + lang + "/pretrain.jsonl", 'w') as f_pretrain, \
            open(base_dataset + lang + "/predev.jsonl", 'w') as f_prevalid, \
            open(base_dataset + lang + "/jointtrain.jsonl", 'w') as f_jointtrain, \
            open(base_dataset + lang + "/jointdev.jsonl", 'w') as f_jointvalid, \
            open(base_dataset + lang +"/test.jsonl", 'w') as f_test:
        idcs_train = idcs['train_dev']+ idcs['novel']
        random.shuffle(idcs_train)
        idcs_test = idcs['test']

        start = 0
        idcs_pretrain = set(idcs_train[start:num_pretrain])
        start+=num_pretrain
        idcs_predev = set(idcs_train[start:start+num_preval])
        start+=num_preval
        idcs_jointtrain = set(idcs_train[start:start+num_jointrain])
        start+=num_jointrain
        idcs_jointdev = set(idcs_train[start:start+num_jointval])

        all_train = set().union(*[idcs_pretrain, idcs_predev, idcs_jointtrain, idcs_jointdev])
        # add all novel idcs not part of train and dev to the test set
        for idx in idcs['novel']:
            if idx not in all_train:
                idcs_test.append(idx)

        for i, line in enumerate(f):
            line_ = json.loads(line)
            idx = line_["data_example_id"]
            if idx in idcs_pretrain:
                f_pretrain.write(line)
            elif idx in idcs_predev:
                f_prevalid.write(line)
            elif idx in idcs_jointtrain:
                f_jointtrain.write(line)
            elif idx in idcs_jointdev:
                f_jointvalid.write(line)
            else:
                f_test.write(line)              

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--t2",
        type=bool,
    )
    parser.add_argument(
        "--lang",
        default="en",
        type=str,
    )

    args, _ = parser.parse_known_args()

    base_dataset = 'data/wikipedia/'
    if args.t2:
        base_dataset += "t2/"
    else:
        base_dataset += "t1/"
    
    # tokenize
    if not os.path.isfile(base_dataset + "/" + args.lang + ".jsonl"):
        process_wiki_based_data(base_dataset, args.lang)
        
    # train, dev, test split
    if args.t2 and not os.path.isfile(base_dataset + "/" + args.lang + "_pretrain.jsonl"):
        print("split t2")
        with open("data/wikipedia/t1/titles.json") as f:
            titles = json.load(f)
        split_data_t2(base_dataset, args.lang, titles)
    if not os.path.isfile(base_dataset + "/" + args.lang + "_pretrain.jsonl"):
        split_data_t1(base_dataset, args.lang)