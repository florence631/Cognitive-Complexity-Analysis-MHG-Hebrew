# Cognitive-Complexity-Analysis-MHG-Hebrew
A Stanza, Spacy, and CLTK based python program to analyze linguistic complexity characteristics and specific phrase characteristics of Middle High German and Rabbinical Hebrew texts. 
The code collects the following data points for each sentence of a sample text: 
Linear Dependency Distance, Intervener Complexity, Subtree Size, Subtree Size, token information (lemma, POS-Tag, Dependency-Tag, Morphology, Length), POS Sequence, Dependency Sequence

For each POS and Dependency sequence tuple:
phrase type, word order typology 

The Analysis folder contains all analytical code. dep_analysis is the phrase characteristics analysis, while the [language]-analysis files are the linguistic complexity characteristics analysis. 
The data_files contain the language samples used to test the program. The files containing the collected language data points are labeled by date, only the most recent date depicts what the analysis files will return and can be used as orientation. 

## Referencing this work
Grosse, Florence. 'Linguistic Universals In The Cognitive Complexity Processing Of Syntax'. Sächsisches Landesgymnasium St. Afra Meißen. 2025.

## References
Hinkelmanns, P. (2021). Spacy-Model-for-Middle-High_German. Retrieved from Github: https://github.com/Middle-High-German-Conceptual-Database/Spacy-Model-for-Middle-High-German/tree/master?tab=MIT-1-ov-file#readme
Johnson, K. P. (2021). The Classical Language Toolkit: An NLP Framework for Pre-Modern Languages. In H. P. Ji (Ed.), Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing: System Demonstrations (pp. 20-29). Association for Computational Linguistics. doi:10.18653/v1/2021.acl-demo.3
Qi, P. Z. (2020). Stanza: A Python Natural Language Processing Toolkit for Many Human Languages. arXiv. doi:https://doi.org/10.48550/arXiv.2003.07082


