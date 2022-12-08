# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import argparse
import json
from collections import defaultdict

def fill(news_data, annotations):
    
    data_filled = defaultdict(dict)
    with open(annotations + ".jsonl") as f:
        for line in f:
            line = json.loads(line)
            data_filled[line['data_example_id']] = line
    
    with open(news_data + ".jsonl") as f:
        for line in f:
            line = json.loads(line)
            if line['data_example_id'] in data_filled:
                data_filled[line['data_example_id']]['text'] = line['text']

    with open(annotations + "_filled.jsonl", 'w') as f:
        for idx in data_filled:
            if 'text' in data_filled[idx]:
                f.write(json.dumps(data_filled[idx]))
                f.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--news_data",
        default="path to processed news data",
        type=str,
    )
    parser.add_argument(
        "--standoff_annotations",
        type=str,
    )
    args, _ = parser.parse_known_args()

    fill(args.news_data, args.standoff_annotations)