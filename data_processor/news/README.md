# Preprocessing OSCAR data

1. Download OSCAR data from:

Please login with your huggingface credentials as OSCAR 21.09 is behind a [request access feature](https://huggingface.co/docs/transformers/model_sharing#preparation) on HuggingFace side:
```huggingface-cli login```

```sh download.sh```

2. Process OSCAR data:

   1. Filter OSCAR to news subset
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/OSCAR/extract_subset.py```
   2. Process for labeling (Please adapt this to the input format of your upper bound model)
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/OSCAR/process4labeling.py```
   3. Split into train, adapt, dev, test and order by time (please adapt ```process_OSCAR_based_data``` to your upper bound model)
   ```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/OSCAR/split_dataset.py --time_split 2019_8```

3. Fill stand-off annotation:

```PYTHONPATH=.:$PYTHONPATH python bela/preprocessing/OSCAR/fill_stand-off.py```



