# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import argparse
import glob
import gzip
import json
import logging
import os

from transformers import AutoTokenizer
from utils.utils_preprocess import split_paragraph_max_seq_length

logger = logging.getLogger(__name__)


def filter_data(metadata_path):

    base_path = '/'.join(metadata_path.split('/')[0:2])
    text_path = base_path + "/packaged/en/"
    idx = metadata_path.split("_")[-1].split(".")[0] 
    output_path = base_path + "/processed/en_part_" + idx + ".jsonl"
    
    if os.path.exists(output_path):
        return

    with open(output_path, 'w') as f_out:
        with open(metadata_path) as f_metadata:
            with gzip.open(text_path + 'en_part_' + idx + '.txt.gz', 'rb') as f:
                
                metadata = next(f_metadata)
                metadata = json.loads(metadata)
                offset = metadata['offset']
                length =  int(metadata['nb_sentences'])
                text_collected = ''
                keep = False
                
                for i, line in enumerate(f):
                    if i in range(offset, offset + length):
                        keep = True
                        text = line.decode('UTF-8').strip()
                        if 'image caption' not in text:
                            text_collected += text
                            text_collected += " "
                    elif keep:
                        
                        output = {}
                        output = {"text": text_collected.strip(), "metadata": metadata}
                        
                        f_out.write(json.dumps(output))
                        f_out.write('\n')
                        
                        metadata = next(f_metadata)
                        metadata = json.loads(metadata)
                        offset = metadata['offset']
                        length =  int(metadata['nb_sentences'])
                        text_collected = ''
                        keep = False

def prep4labeling(metadata_path, model, max_seq_length):

    base_path = '/'.join(metadata_path.split('/')[0:2])
    idx = metadata_path.split("_")[-1].split(".")[0] 
    data_path = base_path + "/processed/en_part_" + idx + '.jsonl'
    output_path = base_path + "/processed_4labeling/en_part_" + idx + '_label.jsonl'

    tokenizer = AutoTokenizer.from_pretrained(model)
    
    with open(output_path, 'w') as f_out:
        with open(data_path) as f:
            
            for line in f:
                
                line = json.loads(line)
                
                if len(line['text'])!=0:
                    split_paragraph_max_seq_length(line, f_out, tokenizer, max_seq_length)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base_path",
        default="data/OSCAR-2109/",
        type=str,
    )
    parser.add_argument(
        "--model",
        default="bert-large-cased",
        type=str,
    )
    parser.add_argument(
        "--max_seq_length",
        default=128,
        type=int,
    )
    args, _ = parser.parse_known_args()
    
    processed_path = args.base_path + "/processed/"
    if not os.path.exists(processed_path):
        os.mkdir(processed_path)

    processed_path = args.base_path + "/processed_4labeling/"
    if not os.path.exists(processed_path):
        os.mkdir(processed_path)

    metadata_paths = glob.glob(args.base_path + "metadata_processed/*")

    logger.info("Collect data from OSCAR dumps")
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        {executor.submit(filter_data, metadata_path): metadata_path for metadata_path in metadata_paths}
    
    logger.info("Tokenize for labeling")

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        {executor.submit(prep4labeling, metadata_path, args.model, args.max_seq_length): metadata_path for metadata_path in metadata_paths}
