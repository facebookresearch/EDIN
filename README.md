# EDIN: An End-to-end Benchmark and Pipeline for Unknown Entity Discovery and Indexing

Existing work on Entity Linking mostly assumes that the reference knowledge base is complete, and therefore all mentions can be linked. In practice this is hardly ever the case, as knowledge bases are incomplete and because novel concepts arise constantly. We introduce the temporally segmented Unknown Entity Discovery and Indexing (EDIN)-benchmark where unknown entities, that is entities not part of the knowledge base and without descriptions and labeled mentions, have to be integrated into an existing entity linking system.


## Download EDIN benchmark data

### Reference knowledge base

[All entities](https://dl.fbaipublicfiles.com/edin/entity_all.jsonl)

### News data

Please note that part of the data is only provided as stand-off annotations, see [news-README](data_processor/News/README.md) for instruction on how to covert to in-place annotations.

[news data](https://dl.fbaipublicfiles.com/edin/news.tar.gz)

### Wikipedia data

[wikipedia data](https://dl.fbaipublicfiles.com/edin/wikipedia.tar.gz)

## Convert stand-off annotations to in-place annotations

1. Download OSCAR data. Note that this is terabytes of data! If you don't have enough space, checkout the data_example ids and only download the necessary files.

Please login with your huggingface credentials as OSCAR 21.09 is behind a [request access feature](https://huggingface.co/docs/transformers/model_sharing#preparation) on HuggingFace side:
```huggingface-cli login```

```sh download.sh```

2. ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/news/fill_stand-off.py```

## Collect data for future timestamps

Follow the instructions listed in [wikipedia-README](data_processor/wikipedia/README.md) and [news-README](data_processor/News/README.md)

## Evaluation

```PYTHONPATH=./ python eval/end2end_eval.py```

##

If you use the this code ase, please cite the following paper:
```bibtex
@misc{https://doi.org/10.48550/arxiv.2205.12570,
  doi = {10.48550/ARXIV.2205.12570},
  url = {https://arxiv.org/abs/2205.12570},
  author = {Kassner, Nora and Petroni, Fabio and Plekhanov, Mikhail and Riedel, Sebastian and Cancedda, Nicola},
  keywords = {Computation and Language (cs.CL), FOS: Computer and information sciences, FOS: Computer and information sciences},
  title = {EDIN: An End-to-end Benchmark and Pipeline for Unknown Entity Discovery and Indexing},
  publisher = {arXiv},
  year = {2022},
  copyright = {Creative Commons Attribution 4.0 International}
}
```

If you use the news-based dataset, please cite the following paper:

```bibtex
@inproceedings{AbadjiOrtizSuarezRomaryetal.2021,
  author    = {Julien Abadji and Pedro Javier Ortiz Su{\'a}rez and Laurent Romary and Beno{\^i}t Sagot},
  title     = {Ungoliant: An optimized pipeline for the generation of a very large-scale multilingual web corpus},
  series = {Proceedings of the Workshop on Challenges in the Management of Large Corpora (CMLC-9) 2021. Limerick, 12 July 2021 (Online-Event)},
  editor    = {Harald L{\"u}ngen and Marc Kupietz and Piotr Bański and Adrien Barbaresi and Simon Clematide and Ines Pisetta},
  publisher = {Leibniz-Institut f{\"u}r Deutsche Sprache},
  address   = {Mannheim},
  doi       = {10.14618/ids-pub-10468},
  url       = {https://nbn-resolving.org/urn:nbn:de:bsz:mh39-104688},
  pages     = {1 -- 9},
  year      = {2021},
  abstract  = {Since the introduction of large language models in Natural Language Processing, large raw corpora have played a crucial role in Computational Linguistics. However, most of these large raw corpora are either available only for English or not available to the general public due to copyright issues. Nevertheless, there are some examples of freely available multilingual corpora for training Deep Learning NLP models, such as the OSCAR and Paracrawl corpora. However, they have quality issues, especially for low-resource languages. Moreover, recreating or updating these corpora is very complex. In this work, we try to reproduce and improve the goclassy pipeline used to create the OSCAR corpus. We propose a new pipeline that is faster, modular, parameterizable, and well documented. We use it to create a corpus similar to OSCAR but larger and based on recent data. Also, unlike OSCAR, the metadata information is at the document level. We release our pipeline under an open source license and publish the corpus under a research-only license.},
  language  = {en}
}
```

