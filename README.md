# KRISTthem2prosModule

This repository contains two modules for the generation of thematicity-based prosody for TTS in KRISTINA

    - mod1_syn2them.py : annotates thematicity structure from syntax. It uses the library to read conll by Carlini and Soler. The original script has been modified to include a 15th column for the annotation of thematicity and it is provided in this repository (conll.py, pyc and init files are also included here).
        Input: conll file annotated with dependencies using TIGER labels
        Output: conll file with one extra column for thematicity
    - mod2_them2ssml.py : it derives ssml prosody tags based on thematicity generated in the previous module.
        Input: conll file annotated with thematicity
        Output: txt file with SSML prosody tags

# Citation
If you use, modify or publish any articles based on the contents of this repository, please cite the following paper:

Domínguez, M., Burga, A., Farrús, M and Wanner, L. Towards expressive prosody generation in TTS for reading aloud applications. In proceedings of IberSPEECH 2018, Sarcelona, Spain.

