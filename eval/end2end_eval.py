# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import argparse
from ast import literal_eval
import numpy as np
import json
from sklearn import metrics
from collections import defaultdict

from utils.datamodule import EntityCatalogue


def compute_f1_p_r(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
    return f1, precision, recall


def acc_unfiltered(target_predictions_dict, ent_catalogue_t1, ent_catalogue_t2, known=True):
    
    support = 0
    tp = 0
    fp = 0
    
    for sample in target_predictions_dict:

        example_predictions = target_predictions_dict[sample]['prediciton']
        example_targets = target_predictions_dict[sample]['target']
        # iterate over targets
        for pos, ent in example_targets.items():
            # if target is unknown entity
            if (int(ent) in ent_catalogue_t1.idx_reverse and known) or (
                int(ent) not in ent_catalogue_t1.idx_reverse and not known
            ):
                support += 1
                # if mention is detected and disambiguated
                if pos in example_predictions:
                    # if mention is detected and correctly disambiguated, else fn+=1
                    if ent_catalogue_t2.idx_reverse[ent]==ent_catalogue_t2.idx_reverse[example_predictions[pos]]:
                        tp += 1

        # iterate over detected mentions that are disambiguated                
        for pos, ent in example_predictions.items():

            # if prediction is novel entity
            if int(ent) not in ent_catalogue_t1.idx_reverse and known:
                continue
            elif int(ent) in ent_catalogue_t1.idx_reverse and not known:
                continue

            # if mention is false positive OR if metion is true positive but disambiguation is false positve
            if pos not in example_targets or ent_catalogue_t2.idx_reverse[example_targets[pos]] != ent_catalogue_t2.idx_reverse[ent]:
                fp += 1

    fn = support - tp
    f1, precision, recall = compute_f1_p_r(tp, fp, fn)

    return f1, precision, recall


def clust_unfiltered(target_predictions_dict, ent_catalogue_t1, ent_catalogue_t2, known=True):
    
    labels_pred = []
    labels_true = []
    num_notmention = 0
    
    # everything that is a known entity or was predicted as a known entity
    
    for sample in target_predictions_dict:

        example_predictions = target_predictions_dict[sample]['prediciton']
        example_targets = target_predictions_dict[sample]['target']

        for pos, ent in example_targets.items():
            if pos in example_predictions:
                
                if (example_predictions[pos] in ent_catalogue_t1.idx_reverse and known) or (
                        example_predictions[pos] not in ent_catalogue_t1.idx_reverse and not known):
                    labels_true.append(ent)
                    labels_pred.append(example_predictions[pos])

        for pos, ent in example_predictions.items():

            if ent not in ent_catalogue_t1.idx_reverse and known:
                continue
            elif ent in ent_catalogue_t1.idx_reverse and not known:
                continue
            elif ent_catalogue_t2.idx_reverse[ent] not in ent_catalogue_t2 and not known:
                continue

            if pos not in example_targets or example_targets[pos] != ent:
                if pos not in example_targets:
                    labels_true.append(len(ent_catalogue_t2)+num_notmention)
                    labels_pred.append(ent)
                    num_notmention+=1
                else:
                    labels_true.append(example_targets[pos])
                    labels_pred.append(ent)

    return metrics.normalized_mutual_info_score(labels_true, labels_pred)



def eval(predictions_path, novel_entities_name):
    
    '''predictions format .jsonl file:
    {"data_example_id: 0, "predictions": {{"(0, 1)": 0},}, "targets": {{"(0, 1)": 0},}}
    {"data_example_id: 1, "predictions": {{"(0, 1)": 0},}, "targets": {{"(0, 1)": 0},}}
    '''

    ent_catalogue_idx_path = 'data/entities/entity_t1.jsonl'
    novel_entity_idx_path = 'data/entities/' + novel_entities_name + '.jsonl'


    ent_catalogue_t1 = EntityCatalogue(ent_catalogue_idx_path, None, True)
    ent_catalogue_t2 = EntityCatalogue(ent_catalogue_idx_path, novel_entity_idx_path, True)
    
    target_predictions_dict = defaultdict(dict)
    with open(predictions_path + ".jsonl") as f:
        for line in f:
            line = json.loads(line)

            prediction = {literal_eval(k): v for k, v in line['predictions'].items()}
            target = {literal_eval(k): v for k, v in line['targets'].items()}
            target_predictions_dict[line['id']]['prediciton'] = prediction
            target_predictions_dict[line['id']]['target'] = target

    nmi_known = clust_unfiltered(target_predictions_dict, ent_catalogue_t1, ent_catalogue_t2, known=True)
    nmi_unknown = clust_unfiltered(target_predictions_dict, ent_catalogue_t1, ent_catalogue_t2, known=False)
    
    _, precision_known, recall_known = acc_unfiltered(target_predictions_dict, ent_catalogue_t1, ent_catalogue_t2, known=True)
    _, precision_unknown, recall_unknown = acc_unfiltered(target_predictions_dict, ent_catalogue_t1, ent_catalogue_t2, known=False)

    results = {'nmi_known': nmi_known,
               'nmi_unknown': nmi_unknown,
               "precision_known": precision_known,
               "recall_known": recall_known,
               "precision_unknown": precision_unknown,
               "recall_unknown": recall_unknown}
    
    print(results)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--predictions_path",
        type=str,
        help='path to predictions',
        default='./EDIN/predicitons',
    )
    parser.add_argument(
        "--novel_entities_name",
        type=str,
        help='name to unknown entities that are added at t2',
        default='entity_t2',
    )

    args, _ = parser.parse_known_args()

    eval(args.predictions_path, args.novel_entities_name)
    