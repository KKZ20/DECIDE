
# Knowledge-based Version Incompatibility Detection for Deep Learning [![](https://img.shields.io/badge/arXiv-2308.13276-b31b1b.svg)](https://arxiv.org/abs/2308.13276) [![DOI](https://zenodo.org/badge/681461566.svg)](https://zenodo.org/doi/10.5281/zenodo.10211987)

This repository contains data and code of DECIDE, a version incompatibility detection tool based on pre-trained language models proposed in *"Knowledge-based Version Incompatibility Detection for Deep Learning"*. Meanwhile, this repository also contains data and code to replicate experiment results in the paper. This repository has been made publicly available on GitHub to support Open Science. 

## Introduction

 This repository contains data and code to replicate experiment results in the paper, which are:

- `DECIDE`: contains the source code of DECIDE. To help users know the whole pipeline, we also provide examples of building knowledge graph (in `DECIDE/Knowledge-Extraction-Example`) and examples on querying knowledge graph (in `DECIDE/Knowledge-Base-Query-Example`).
- `Experiments`: contains the scripts and data which help reproduce experiments in the paper (Section 6). For more details, see section Experiments.
- `Requirements.md`: contains the hardware and third-party library requirements for DECIDE.
- `Installation.md`: contains the installation instructions to set up an Python environment and run our code.

## Prerequisites & Installation

Please refer to [Requirements.md](./Requirements.md) and [Installation.md](./Installation.md).

## Experiments


### RQ1: How effectively can  DECIDE detect version compatibility issues in real DL projects?
In RQ1, we first present the details of our evaluation benchmark in `Experiments/RQ1/RQ1-Benchmark_Details.xlsx`. The benchmark consists 10 popular deep learning projects from GitHub. To evaluate the performance of DECIDE, we compare DECIDE against two state-of-the-art baselines: Watchman[^fn1] and PyEGo[^fn2]. The benchmark detection results generated by out tool, DECIDE, have been already copied in `Experiments/RQ1/result`.  Follow the steps below to reproduce Figure 6 and Table 6 in Section 6.1.

First, to get the data parsed from the output of DECIDE, run: 

```shell
$ cd PATH/TO/Experiments/RQ1
$ python parse_result.py
```

This Python script would parse our tool's detection result and generate the data for Figure 6 and Table 6 in folder `Experiments/RQ1/data/DECIDE.log`. Note that for Watchman and PyEGo, we manually analyzed their outputs and present the result in `Experiments/RQ1/data/Watchman.log` and `Experiments/RQ1/data/PyEGo.log` using the same format as DECIDE.

Table 6 shows the performance of version incompatibility detection of the three approaches in precision, recall, and F1 score. To reproduce Table 6, run:

```shell
$ cd PATH/TO/Experiments/RQ1
$ python table6.py
```

The result will be output in folder `Experiments/RQ1/figures&tables/table6.log`.

Figure 6 shows the number of version issues detected by DECIDE, PyEGo, and Watchman on different DL stack layers. To reproduce the result, run:

```shell
$ cd PATH/TO/Experiments/RQ1
$ python figure6.py
```

The result will be output in folder `Experiments/RQ1/figures&tables/figure6.png`.

[^fn1]: Ying Wang, Ming Wen, Yepang Liu, Yibo Wang, Zhenming Li, Chao Wang, Hai Yu, Shing-Chi Cheung, Chang Xu, and Zhiliang Zhu. 2020.  Watchman: Monitoring Dependency Conflicts for Python Library Ecosystem. In  Proceedings of the ACM/IEEE 42nd International Conference on Software Engineering  (Seoul, South Korea)  (ICSE ’20). Association for Computing Machinery, New York, NY, USA, 125–135.
[^fn2]: Hongjie Ye, Wei Chen, Wensheng Dou, Guoquan Wu, and Jun Wei. 2022. Knowledge-Based Environment Dependency Inference for Python Programs. In 2022 IEEE/ACM 44th International Conference on Software Engineering (ICSE).

### RQ2: How accurate is the extracted knowledge in the resulting knowledge graph produced by DECIDE?
In RQ2, we evaluate the quality of our knowledge graph. We present all the sampled data with manual label in folder `Experiments/RQ2`. There are 5 files:

- `RQ2-ALL.xlsx`: consists 343 version relations sampled from the knowledge graph.
- `RQ2-Correct.xlsx`: consists 287 correct version relations in the sampled data (287 / 343 = 83.7%).
- `RQ2-Version_Mismatch.xlsx`: consists 36 incorrect version relations due to the mismatch between a component name and a version number (36 / 56 = 64%).
- `RQ2-QA_Wrong.xlsx`: consists 15 incorrect version relations due to incorrect predictions from UnifiedQA (15 / 56 = 27%).
- `RQ2-Post_Wrong.xlsx`: consists 5 incorrect version relations due to the incorrect version knowledge shared in the original SO post (5 / 56 = 9%).

### RQ3: How accurately can the pre-trained QA model in DECIDE infer compatibility relations between versioned DL components?
In RQ3, we evaluate the performance of the pre-trained QA model in inferring compatibility relations between versioned DL components. We randomly sampled 360 of the 5,532 queries that the UnifiedQA received to construct the whole knowledge graph, which is in `Experiments/RQ3/data/Q12.log`. We also provide the manually labeled ground truth in `Experiments/RQ3/data/ground_truth.txt`. To compare the model output with the ground truth, run:

```shell
$ cd PATH/TO/Experiments/RQ3
$ python compare.py > res.log
# Or simply run:
# ./test.sh
```

The results will be output in `Experiments/RQ4/res.log`.

Overall, we found that UnifiedQA achieved 84.2% precision (303 / 360 = 84.2%) and 91.3% recall (303 / 332 = 91.3%) on these 360 queries. Among the incorrect predictions, there are:

- 7 due to the misunderstanding of the UnifiedQA (7 / 57 = 12%).
- 30 due to the two DL components were just mentioned in the given paragraph but did not have dependency relationship (30 / 57 = 53%).
- 20 due to the mismatch of components and their versions in the query (20 / 57 = 35%).

### RQ4: To what extent can different question templates affect the accuracy of the pre-trained QA model in DECIDE?
In RQ4, we evaluate the impact of different question templates by measuring the precision and recall of each template and different combination strategies of templates. The QA model's output using different question templates are presented in `Experiments/RQ4/data/`. To reproduce the result in Table 7 and Table 8, one can run:

```shell
$ cd PATH/TO/Experiments/RQ4
$ python compare.py
```

### RQ5: To what extent can different knowledge consolidation strategies affect the accuracy of the resulting knowledge graph?
In RQ5, we evaluate three different knowledge consolidation strategies (*majority vote*, *weighted majority vote*, and *vote by loss*). We randomly sampled 228  of the 558 relations which were consolidated from multiple predicted relations in the knowledge. We present the manually labeled results in `Experiments/RQ5/RQ5-ALL.xlsx`. Note that to fully evaluate the knowledge consolidation strategies, we excluded 25 incorrect relations that were caused by the mismatch between component names and versions. Thus, we get 203 relations.

Overall, there are 193 correct relations using majority vote (193 / 203 = 95.1%), 190 correct relations using majority vote (193 / 203 = 93.6%), and 186 correct relations using majority vote (186 / 203 = 91.6%).

## Citation
```
@inproceedings{zhao2023knowledge,
  title={Knowledge-Based Version Incompatibility Detection for Deep Learning},
  author={Zhao, Zhongkai and Kou, Bonan and Ibrahim, Mohamed Yilmaz and Chen, Muhao and Zhang, Tianyi},
  booktitle={Proceedings of the 31st ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
  pages={708--719},
  year={2023}
}
