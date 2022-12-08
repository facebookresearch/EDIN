#!/bin/bash

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

mkdir data
cd data

mkdir wikipedia
cd wikipedia
mkdir t1
mkdir t2

# 2021/09/20
wget http://wikipedia.c3sl.ufpr.br/enwiki/20210920/enwiki-20210920-pages-articles-multistream.xml.bz2

# 2019/08/01
wget http://dl.fbaipublicfiles.com/BLINK/enwiki-pages-articles.xml.bz2

cd ..
mkdir wikinews
cd wikinews
wget http://wikipedia.c3sl.ufpr.br/enwikinews/20210901/enwikinews-20210901-pages-articles-multistream.xml.bz2

cd ..
mkdir wikidata
cd wikidata
wget https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

mkdir entities
cd entities
wget http://dl.fbaipublicfiles.com/BLINK/all_entities_large.t7
wget http://dl.fbaipublicfiles.com/BLINK/entity.jsonl

cd ../..
mkdir models
cd models

wget http://dl.fbaipublicfiles.com/BLINK/biencoder_wiki_large.bin
wget wget http://dl.fbaipublicfiles.com/BLINK/biencoder_wiki_large.json