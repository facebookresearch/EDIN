# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import logging
import json

logger = logging.getLogger()

class EntityCatalogue:
    def __init__(self, idx_path, novel_entity_idx_path, reverse=False):
        logger.info(f"Reading entity catalogue index {idx_path}")
        self.idx = {}
        self.mapping = {}
        self.id2title = {}
        with open(idx_path, "rt") as fd:
            for idx, line in enumerate(fd):
                line = json.loads(line)
                if line["wikidata_id"]!="None":
                    ent_id = line["wikidata_id"]
                    self.id2title[line["wikidata_id"]] = line["entity"]
                else:
                    ent_id = line["entity"] + "_title"
                if ent_id in self.idx:
                    ent_id += "_novel"
                self.idx[ent_id] = idx
                self.mapping[ent_id] = [idx]
        logger.info(f"Number of entities {len(self.idx)}")

        if novel_entity_idx_path is not None:
            logger.info(f"Reading novel entity catalogue index {novel_entity_idx_path}")
            with open(novel_entity_idx_path, "r") as f:
                for line in f:
                    idx += 1
                    line = json.loads(line)
                    if line["wikidata_id"]!="None":
                        self.id2title[line["wikidata_id"]] = line["entity"]
                        line = line["wikidata_id"]
                    else:
                        line = line["entity"]
                    if line not in self.idx:
                        self.idx[line] = idx
                        self.mapping[line] = [idx]
                    else:
                        self.mapping[line].append(idx)

        logger.info(f"Number of entities {len(self.idx)}")
        if reverse:
            self.idx_reverse = {}
            for ent in self.idx:
                self.idx_reverse[self.idx[ent]] = ent
            for ent in self.mapping:
                for idx in self.mapping[ent]:
                    self.idx_reverse[idx] = ent

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, entity_id):
        ent_index = self.idx[entity_id]
        return ent_index

    def __contains__(self, entity_id):
        return entity_id in self.idx