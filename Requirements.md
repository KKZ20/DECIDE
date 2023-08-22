# Requirements
All the code are tested under Ubuntu 18.04, GPU is not required. We strongly recommend user to reproduce each of the part below in new virtual Python environments by [Anaconda](https://www.anaconda.com/). Here we list some key third-party Python libraries and their versions:

## DECIDE

- py2neo==2021.2.3
- packaging==21.3.0
- typed-ast==1.5.5

## Knowledge Extraction Example

- beautifulsoup4==4.12.2
- pynvml==11.5.0
- allennlp-models==2.10.1
- en-core-web-sm==2.3.1 (install via local file en_core_web_sm-2.3.1.tar.gz)

## Knowledge Base Query Example

- py2neo==2021.2.3



For Docker user, please also install [Docker](https://www.docker.com/). Our tested version is 24.0.5.

For more details on creating virtual environments and installing third-party libraries, please refer to [Installation.md](./Installation.md).