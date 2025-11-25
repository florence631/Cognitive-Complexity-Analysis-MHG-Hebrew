import shutup, stanza, math, json, csv
#shutup.please()
import pandas as pd
from humanities_fct import sentence_complexity, token_analys, classify_category
#stanza.download("hbo")
nlp_he = stanza.Pipeline("he", processors="tokenize,pos,lemma,depparse")

hebdata = pd.read_csv("heb_data.csv")
heb =  hebdata["text"].tolist()
results_sent_he =[]
results_token_he=[]
for book_id, text in enumerate(heb):
    print(f"\nProcessing text {book_id} ...")
    doc_he = nlp_he(str(text.strip('" :.')))
    for sent_id, sent in enumerate(doc_he.sentences):
        complexity = sentence_complexity(sent)
        
        token_list_he =[]
        for token in sent.words:
            token_inf = token_analys(token)
            appendix = {
                "txt": token_inf["txt"],
                "lem": token_inf["lem"],
                "pos": token_inf["pos"],
                "tag": token_inf["tag"],
                "dep": token_inf["dep"],
                "morph": str(token_inf["morph"]),
                "lng": token_inf["lng"]
            }
            token_list_he.append(appendix)
            results_token_he.append(appendix)
        sent_entry = {
            "sent_id": sent_id, #zweimal gleich?
            "sentence_text": sent.text,  #was printed das?
            "distance": complexity["avg_distance"],
            "depth": complexity["avg_depth"],
            "subtree_size": complexity["avg_subtree_size"],
            "sent_lng": len(sent.text), #ist liste
            "tokens": json.dumps(token_list_he, ensure_ascii=False) 
        }
        results_sent_he.append(sent_entry)
    
df_results_sent = pd.DataFrame(results_sent_he)# columns = {})
df_results_token = pd.DataFrame(results_token_he)#, columns={})

df_results_sent["pos_seq"] = df_results_sent["tokens"].apply(
    lambda t: " ".join(json.loads(t)[i]["pos"] for i in range(len(json.loads(t))))
)
df_results_sent["dep_seq"] = df_results_sent["tokens"].apply(
    lambda t: " ".join(json.loads(t)[i]["dep"] for i in range(len(json.loads(t))))
)
df_results_sent['category'] = df_results_sent.apply(lambda row: classify_category(row['pos_seq'], row['dep_seq']), axis=1)

freq = df_results_sent["category"].value_counts(normalize=True) #??
df_results_sent["suprisal value"] = df_results_sent["category"].map(lambda s: -math.log2(freq[s]))

#add the means and the modes later in excel
df_results_token.reset_index().to_csv("he_token_analysis.csv", mode="w", index=False)
df_results_sent.reset_index().to_csv("he_sent_analysis.csv", mode="w", index=False) #a for append
