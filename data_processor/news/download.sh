# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

cd data
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/datasets/oscar-corpus/OSCAR-2109

cd OSCAR-2109
mkdir processed

for i in {0..1336}; do
        git lfs pull --include packaged/en/en_meta_part_"$i".jsonl.gz
        git lfs pull --include packaged/en/en_part_"$i".txt.gz
done