# Preprocessing Wikipedia and Wikinews data

1. Download data and models

```bash download.sh```

2. Process Wikipedia data
   1. WikiExtractor with timestamps
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/WikiExtractor_timestamp.py data/wikinews/enwikinews-20210901-pages-articles-multistream.xml -o data/wikinews/en -l```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/WikiExtractor_timestamp.py data/wikipedia/enwiki-pages-articles.xml.bz2 -o data/wikipedia/t1/en -l```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/WikiExtractor_timestamp.py  data/wikipedia/enwiki-20220301-pages-articles-multistream.xml.bz2 -o data/wikipedia/t2/en -l```
   
   2. Compress wikidata, generate useful dictionary's, e.g., title -> ID, ID -> title or alias tables:
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_wikidata.py --base_wikidata data/wikidata/ compress```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_wikidata.py --base_wikidata data/wikidata/ dicts```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_wikidata.py --base_wikidata data/wikidata/ redirects```
   
   3. Prepare novel entity descriptions
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/entities_t2.py```

   4. Process wikinews

   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_extract.py  --lang en --base_wikipedia data/wikinews/```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikinews/ --base_wikidata /fsx/kassner/wikidata/ prepare```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikinews/ --base_wikidata /fsx/kassner/wikidata/ solve```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikinews/ --base_wikidata /fsx/kassner/wikidata/ fill```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/process4labeling.py --base_path data/wikinews/```
   
   5. Process wikipedia t1
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_extract.py  --lang en --base_wikipedia data/wikipedia/t1/```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikipedia/t1/ --base_wikidata /fsx/kassner/wikidata/ prepare```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikipedia/t1/ --base_wikidata /fsx/kassner/wikidata/ solve```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikipedia/t1/ --base_wikidata /fsx/kassner/wikidata/ fill```
   
   6. Process wikipedia t2
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_extract.py  --lang en --base_wikipedia data/wikipedia/t2/```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikipedia/t2/ --base_wikidata /fsx/kassner/wikidata/ prepare```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikipedia/t2/ --base_wikidata /fsx/kassner/wikidata/ solve```
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/preprocess_anchors.py --lang en --base_wikipedia data/wikipedia/t2/ --base_wikidata /fsx/kassner/wikidata/ fill```
   
   7. Prepare pretraining data t1
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/split_data.py```   
   8. Prepare pretraining data t2
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/split_data.py --t2 True```

   9. Prepare subset labeling

   ```cd data/wikipedia```
   ```wget http://dl.fbaipublicfiles.com/KILT/blink-dev-kilt.jsonl```
   ```wget http://dl.fbaipublicfiles.com/KILT/blink-train-kilt.jsonl```

   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/process4labeling.py --timesplit t1 --split test,jointtrain,jointdev```
   
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/wikipedia/process4labeling.py --timesplit t2 --split test,jointtrain,jointdev```






