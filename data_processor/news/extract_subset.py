# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import argparse
import glob
import gzip
import json
import os
import tqdm

from newsplease import NewsPlease

URLS = {"bbc": "https://www.bbc.com/",
        "cnn": "https://www.cnn.com/",
        "dw": "https://www.dw.com/en/",
        "reuters": "https://www.reuters.com/article/",
        "guardian": "https://www.theguardian.com/",
        "ap": "https://apnews.com/article/"}

def filter_data(base_path):
    filenames = glob.glob(base_path + "/en_metadata/en_meta_part_*.jsonl.gz")
    filenames = filenames[::-1]
    for filename in tqdm.tqdm(filenames):
        
        idx = filename.split('_')[-1].split('.')[0]
        output_path = base_path + "/metadata_processed/metadata_processed_" + str(idx) + ".jsonl"
        if os.path.exists(output_path):
            continue
        
        with open(output_path, 'w') as f_out:
            with gzip.open(filename, 'rb') as f:
                for i, line in enumerate(f):
                    
                    line = json.loads(line)
                    
                    process = False
                    for url_key in URLS:
                        url = URLS[url_key]
                        if url in line['headers']['warc-target-uri']:
                            process =True
                            name = url_key

                    if process:
                        if 'content-type' in line['headers']:
                            if 'text/plain'==line['headers']['content-type']:
                                try:
                                    article = NewsPlease.from_url(line['headers']['warc-target-uri'])
                                    current_year = article.date_publish.year
                                    current_month = article.date_publish.month
                                    line["time_stamp"] = str(current_year) + '_' + str(current_month)
                                    line["data_source_name"] = name
                                    line["data_example_id"] = str(idx) + "_" + str(i)
                                    f_out.write(json.dumps(line))
                                    f_out.write('\n')
                                except:
                                    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base_path",
        default='data/OSCAR-2109/', 
        type=str,
    )
    args, _ = parser.parse_known_args()
    filter_data(args.base_path)