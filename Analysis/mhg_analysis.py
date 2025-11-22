#import shutup
#shutup.please()
import spacy, json, math, re, time
import pandas as pd
#from cltk.nlp import NLP
from humanities_fct import token_analys, dep_parse_ollama, split_ollama, classify_category, tag_to_pos

#nlp_mhg = NLP(language="gmh", suppress_banner=True)
nlp_mhg = spacy.load(r"C:\Users\Galaxy Book\Desktop\humanities-program\model-best")

e = 0
mhg_data = pd.read_csv("mhg_data.csv")
mhg = zip(mhg_data["name"].tolist(), mhg_data["text"].tolist())
results_sent_mhg = []
results_token_mhg =[]
for book_id, (name, book) in enumerate(mhg): 
    print(f'processing book {book_id}')
    #doc_mhg_cltk = nlp_mhg_cltk(str(book))
    #sentences = split_ollama(book)
    sentences = [s.strip() for s in re.split(r'\.\s+|\:\s+', book) if s.strip()]
    for sent_id, sent in enumerate(sentences):
        doc_mhg = nlp_mhg(sent)
        token_list_mhg =[]
        try:
            complexity, sent_obj = dep_parse_ollama(sent) #two arrays 
            for token in doc_mhg: #.words: #zerlegt es das automatisch in eine liste?
                token_inf = token_analys(token)
                token_list_mhg.append({
                    "txt": token_inf["txt"],
                    "lem": token_inf["lem"],
                    "pos": tag_to_pos(token_inf["tag"]),
                    "tag": token_inf["tag"],
                    "dep": token_inf["dep"],
                    "morph": str(token_inf["morph"]),
                    "lng": token_inf["lng"]
                })
            # More explicit version that clearly shows modification
            for i in range(len(token_list_mhg)):
                if i < len(sent_obj.words):
                    token_list_mhg[i]["dep"] = sent_obj.words[i].dep
                else:
                    token_list_mhg[i]["dep"] = token_list_mhg[i].get("dep", "UNKNOWN")
            
            for i in range(len(token_list_mhg)):
                results_token_mhg.append(token_list_mhg[i])

            results_sent_mhg.append({
                "text_id": sent_id,
                "sentence_text": doc_mhg.text, 
                "avg_distance": complexity["avg_distance"],
                "avg_depth": complexity["avg_depth"],
                "avg_subtree_size": complexity["avg_subtree_size"],
                "sent_lng": len([token for token in doc_mhg]), ##ist eine liste??? oder ein string
                "tokens": json.dumps(token_list_mhg, ensure_ascii=False)
            })
        except:
            print(dep_parse_ollama(sent))
            print(f'exception {e}')
            e += 1


df_results_sent = pd.DataFrame(results_sent_mhg)
#df_results_token = pd.DataFrame(results_token_mhg)

df_results_sent["pos_seq"] = df_results_sent["tokens"].apply(
    lambda t: " ".join(json.loads(t)[i]["pos"] for i in range(len(json.loads(t))))
)
df_results_sent["dep_seq"] = df_results_sent["tokens"].apply(
    lambda t: " ".join(json.loads(t)[i]["dep"] for i in range(len(json.loads(t))))
)
df_results_sent['category'] = df_results_sent.apply(lambda row: classify_category(row['pos_seq'], row['dep_seq']), axis=1)

freq = df_results_sent["category"].value_counts(normalize=True) 
df_results_sent["suprisal value"] = df_results_sent["category"].map(lambda s: -math.log2(freq[s]))

#df_results_token.reset_index().to_csv("mhg_token_analysis.csv", mode="w", index=False)
df_results_sent.reset_index().to_csv("mhg_sent_analysis.csv",mode="w", index=False)

## IN POST: Add morpholocial things (through pos, morphology etc. of the tokens of the sentences (e.g. for the unknown word order sentences to determine if there are any similarities in these))