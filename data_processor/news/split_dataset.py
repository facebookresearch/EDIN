# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import glob
import json
import logging
import os
import random

random.seed(10)

logger = logging.getLogger()

def process_OSCAR_based_data(base_path):

    title_wikidata_id = {}
    entity_path = "data/entities/entity_all.jsonl"
    with open(entity_path) as f:
        for line in f:
            line = json.loads(line)
            title_wikidata_id[line['title']] = line['wikidata_id']

    with open(base_path + "all.jsonl", "w") as f_out:
        for dataset_path in glob.glob(base_path + "labled/*_label.jsonl_processed"):
            idx = dataset_path.split('_')[2]
            with open(base_path + "labled/en_part_" + idx + "_label.jsonl_processed", "rb") as f:
                with open(base_path + "processed_4labeling/en_part_" + idx + "_label.jsonl", "rb") as g:
                    for line, line_ in zip(f, g):
                        
                        line = json.loads(line)
                        line_ = json.loads(line_)
                        
                        # filter out entities with low linking score
                        line['entities'] = [ent for ent in line['entities'] if ent["score"]>=0.4]

                        # filter out entities not part of the enity index
                        line['entities'] = [ent for ent in line['entities'] if ent["entity_id"] in title_wikidata_id]
                        if len(line['entities'])==0:
                            continue
                        line["time_stamp"] = line_["time_stamp"]
                        if int(line['time_stamp'].split("_")[0])>2000:
                            f_out.write(json.dumps(line))
                            f_out.write("\n")

def split_data_t2(base_path, time_split, ids_t1_train_dev, num_train=20000, num_val=5000):

    year_ref, month_ref = time_split.split("_")
    month_ref = int(month_ref)
    year_ref = int(year_ref)

    with open(base_path + "all.jsonl") as f, \
            open(base_path + 't2/train.jsonl', 'w') as f_train, \
            open(base_path + 't2/dev.jsonl', 'w') as f_valid, \
            open(base_path + 't2/test.jsonl', 'w') as f_test:
        
        idcs_t2 = []
        for line in f:
            line = json.loads(line)
            year, month = line['time_stamp'].split("_")
            year = int(year)
            month = int(month)
            if year>year_ref or (year==year_ref and month>=month_ref):
                idcs_t2.append(line["data_example_id"])
        f.seek(0)

        idcs_t2 = idcs_t2 + ids_t1_train_dev
        random.shuffle(idcs_t2)

        start = 0
        idcs_train = idcs_t2[start:num_train]

        start+=num_train
        idcs_dev = idcs_t2[start:start+num_val]
        start+=num_val

        data_test = {}
        for line in f:
            line_ = json.loads(line)
            idx = line_["data_example_id"]
            if idx in idcs_train:
                f_train.write(line)
            elif idx in idcs_dev:
                f_valid.write(line)
            elif idx not in ids_t1_train_dev:
                f_test.write(line)

        
def split_data_t1(base_path, time_split, num_train=20000, num_val=5000):

    year_ref, month_ref = time_split.split("_")
    month_ref = int(month_ref)
    year_ref = int(year_ref)

    with open(base_path + "all.jsonl") as f, \
            open(base_path + 't1/train.jsonl', 'w') as f_train, \
            open(base_path + 't1/dev.jsonl', 'w') as f_valid, \
            open(base_path + 't1/test.jsonl', 'w') as f_test:
        idcs_t1 = []
        for line in f:
            line = json.loads(line)
            year, month = line['time_stamp'].split("_")
            year = int(year)
            month = int(month)
            if year<year_ref or (year==year_ref and month<month_ref):
                idcs_t1.append(line["data_example_id"])

        f.seek(0)

        random.shuffle(idcs_t1)

        start = 0
        idcs_train = idcs_t1[start:num_train]
        print(len(idcs_train))
        start+=num_train
        idcs_dev = idcs_t1[start:start+num_val]
        start+=num_val
        idcs_test = idcs_t1[start:]

        logger.info("Number of training samples %d", len(idcs_train))
        logger.info("Number of dev samples %d", len(idcs_dev))
        logger.info("Number of test samples %d", len(idcs_test))

        data_test = {}
        for line in f:
            line_ = json.loads(line)
            idx = line_["data_example_id"]
            if idx in idcs_train:
                f_train.write(line)
            elif idx in idcs_dev:
                f_valid.write(line)
            elif idx in idcs_test:
                f_test.write(line)
                

    return idcs_train, idcs_dev

def collect_ids(base_path):

    ids_train, ids_dev = [], []
    with open(base_path + 't1/train.jsonl') as f:
        for line in f:
            line = json.loads(line)
            ids_train.append(line['data_example_id'])

    with open(base_path + 't1/dev.jsonl') as f:
        for line in f:
            line = json.loads(line)
            ids_dev.append(line['data_example_id'])
    
    return ids_train, ids_dev


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base_path",
        type=str,
        default='data/OSCAR-2109/',
    )
    parser.add_argument(
        "--time_split",
        type=str,
    )

    args, _ = parser.parse_known_args()
    
    if not os.path.exists(args.base_path + 'all.jsonl'):
        process_OSCAR_based_data(args.base_path)

    if not os.path.exists(args.base_path + 't1/train.jsonl'):
        logger.info("Preprocess t1")
        if not os.path.isdir(args.base_path + 't1/'):
            os.mkdir(args.base_path + 't1/')

        ids_train, ids_dev = split_data_t1(args.base_path, args.time_split)
    else:
        logger.info("Collect ids t1")
        print("collect_ids")   
        ids_train, ids_dev = collect_ids(args.base_path)
    
    #if not os.path.exists(args.base_path + 't2/train.jsonl'): 
    logger.info("Preprocess t2")   
    if not os.path.isdir(args.base_path + 't2/'):
        os.mkdir(args.base_path + 't2/')
    idcs_train_dev = ids_train + ids_dev

    split_data_t2(args.base_path, args.time_split, idcs_train_dev)