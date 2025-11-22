# Cognitive-Complexity-Analysis-MHG-Hebrew
A Stanza, Spacy, and CLTK based python program to analyze linguistic complexity characteristics and specific phrase characteristics of Middle High German and Rabbinical Hebrew texts. 
The code collects the following data points for each sentence of a sample text: 
Linear Dependency Distance, Intervener Complexity, Subtree Size, Subtree Size, token information (lemma, POS-Tag, Dependency-Tag, Morphology, Length), POS Sequence, Dependency Sequence

For each POS and Dependency sequence tuple:
phrase type, word order typology 

The Analysis folder contains all analytical code. dep_analysis is the phrase characteristics analysis, while the [language]-analysis files are the linguistic complexity characteristics analysis. 
The data_files contain the language samples used to test the program. The files containing the collected language data points are labeled by date, only the most recent date depicts what the analysis files will return and can be used as orientation. 
