
import json, ollama, re, os,  requests
STTS_TO_UPOS = {
    "ADJA": "ADJ", 
    "ADJD": "ADJ",
    "ADV": "ADV",
    "APPR": "ADP", 
    "APPRART": "ADP", 
    "APPO": "ADP", 
    "APZR": "ADP",
    "ART": "DET",
    "CARD": "NUM",
    "FM": "X",
    "ITJ": "INTJ",
    "KOUI": "SCONJ", 
    "KOUS": "SCONJ", 
    "KON": "CCONJ", 
    "KOKOM": "CCONJ",
    "NN": "NOUN", 
    "NE": "PROPN",
    "PDS": "PRON", 
    "PDAT": "DET", 
    "PIS": "PRON", 
    "PIAT": "DET",
    "PIDAT": "DET", 
    "PPER": "PRON", 
    "PPOSS": 
    "DET", 
    "PPOSAT": "DET",
    "PRELS": "PRON", 
    "PRELAT": "DET", 
    "PRF": "PRON", 
    "PWS": "PRON", 
    "PWAT": "DET", 
    "PWAV": "ADV",
    "PTKZU": "PART", 
    "PTKNEG": "PART", 
    "PTKVZ": "PART", 
    "PTKA": "PART", 
    "PTKANT": "PART",
    "TRUNC": "X",
    "VVFIN": "VERB", 
    "VVIMP": "VERB", 
    "VVINF": "VERB", 
    "VVIZU": "VERB",
    "VVPP": "VERB", 
    "VAFIN": "AUX", 
    "VAIMP": "AUX",
    "VAINF": "AUX", 
    "VAPP": "AUX",
    "VMFIN": "AUX", 
    "VMINF": "AUX", 
    "VMPP": "AUX",
    "$.": "PUNCT", 
    "$,": "PUNCT", 
    "$(": "PUNCT"
}

def tag_to_pos(tag):
    return STTS_TO_UPOS.get(tag, "X")

def sentence_complexity(sent):
    distances, depths, subtree_sizes = [], [], []
    units = sent.words
 
    children = {}
    for token in units:
        children[token.id] = [] # each token_id is an empty list

    for token in units:
        if hasattr(token, "head") and token.head != 0:
                children[token.head].append(token.id)  # Liste mit allen Token-ids, jeder token id ist Liste mit seinen "Kindern"
    
    for token in units:
        if hasattr(token, "head"):
            # Lineare Distanz
            distances.append(abs(token.id - token.head) if token.head != 0 else 0) # .i index 

            # depth to root (intervener)
            depth = 0
            current = token 
            depth_visited = set([token.id])
            while hasattr(current, "head") and current.head != 0 and current.head not in depth_visited:  # klettert bis zum token, head == 0 means no parent
                parent = next((w for w in sent.words if w.id == current.head), None)
                if not parent:
                    break
                depth += 1
                depth_visited.add(parent.id)
                current = parent
                if depth > len(sent.words):  # safety stop
                    break
            depths.append(depth)

            #subtree_sizes.append(len(list(token.subtree)))
            def count_descendants(w_id):
                count = 0
                stack = [w_id]
                subtree_visited = set()
                while stack:
                    current_id = stack.pop()
                    if current_id in subtree_visited: #if e.g. a child has it's parent (head) as a "child" (would be added again !error!)
                        continue
                    subtree_visited.add(current_id)
                    count += 1 # pop the first node, count it, add it's children
                    for child in children.get(current_id, []):
                        if child not in subtree_visited:
                            stack.append(child)

                    if len(subtree_visited) > len(units):
                        break     
                return count
            subtree_sizes.append(count_descendants(token.id))

    avg_distance = sum(distances) / len(distances) if distances else 0
    avg_depth = sum(depths) / len(depths) if depths else 0
    avg_subtree = sum(subtree_sizes) / len(subtree_sizes) if subtree_sizes else 0

    return {
        "avg_distance": avg_distance,
        "avg_depth": avg_depth,
        "avg_subtree_size": avg_subtree,
    }

def token_analys(token):
    if hasattr(token, "lemma_"):  # spaCy token
        return {
            "txt": token.text,
            "lem": token.lemma_ or token.text.lower(),
            "pos": token.pos_ or "X",
            "tag": token.tag_ or "X",
            "dep": token.dep_ or "X",
            "morph": str(token.morph) or "X",
            "lng": len(token.text)
        }
    elif hasattr(token, "features"): #cltk
        return {
        "txt": token.string,
        "lem": token.lemma if token.lemma else token.string.lower(),
        "pos": token.upos if token.upos else "X",       # Universal POS tag
        "tag": token.xpos if token.xpos else "X",       # Language-specific POS (optional)
        "dep": token.dependency_relation if hasattr(token, "dependency_relation") else "X",
        "morph": str(token.features) if token.features else "",
        "lng": len(token.string)
        }
    else:  # Stanza token
        return {
            "txt": token.text,
            "lem": getattr(token, "lemma", "X"),
            "pos": getattr(token, "upos", "X"),
            "tag": getattr(token, "xpos", "X"),
            "dep": getattr(token, "deprel", "X"),
            "morph": getattr(token, "feats", "X"),
            "lng": len(token.text)
        }
    

class DummToken:
    def __init__(self, idx, head_id, text, dep):
        self.id = idx
        self.head = head_id if head_id != 0 else 0
        self.text = text
        self.dep = dep
class DummSent:
    def __init__(self, words):
        self.words = words
        
api_key = os.environ.get("OLLAMA_API_KEY")

client = ollama.Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {api_key}'}
)
example_json = '[{"idx": 1, "head_id": 2, "text": "Wir", "dep": "nsubj"}, {"idx": 2, "head_id": 0, "text": "zelen", "dep": "root"}]'
def dep_parse_ollama(sentence):
    if isinstance(sentence, list):
        sentence = " ".join(sentence)

    prompt = f"""
    Perform dependency parsing on this Middle High German sentence.
    Return ONLY valid JSON array with objects containing:  
      - "idx": integer token index
      - "head_id": integer index of head token, 0 for root 
      - "text": string token text
      - "dep": string dependency relation label (such as "nsubj", "obj", "root", etc.)
    Use proper JSON syntax with double quotes around all strings.
    
    Sentence: "{sentence}"

    Example format:
    {example_json}
    """
    response = client.chat(model= "gpt-oss:120b", messages = [{"role": "user", "content": prompt}], stream=False)
    try:
        content = extract_oll_content(response)
        tokens = extract_json(content) #list[dict] object, liste die dicts enthält
        dumm_tokens = []
        for t in tokens:
            dumm_tokens.append(DummToken(t["idx"], t["head_id"], t["text"], t["dep"]))
        sent_obj = DummSent(dumm_tokens)
 
    except Exception as e:
        print(f"dep_parse_ollama: Ollama failed or returned invalid JSON. Error:", e)
        return {
            "avg_distance": None, "avg_depth": None, "avg_subtree_size": None
        }
      
    try:
        tokens_by_idx = {}
        for t in tokens:
            if not all(k in t for k in ("idx", "head_id", "text", "dep")):
                raise ValueError("Token missing required key(s).")
            idx = int(t["idx"])
            tokens_by_idx[idx] = {"text": t["text"], "dep": t["dep"]}

    except Exception as e:
        print("dep_parse_ollama: validation/parsing error:", e)
        return {"avg_distance": None, "avg_depth": None, "avg_subtree_size": None}

    return [sentence_complexity(sent_obj), sent_obj] #returns two arrays


def split_ollama(text):
    prompt = f"""
    Split the following Middle High German text into sentences.
    Return ONLY a JSON array of strings, each string being a sentence (no explanations).
    One sentence per array element.
    Text: "{text}"
    """
    response = client.chat(model= "gpt-oss:120b", messages = [{"role": "user", "content": prompt}])
    content = extract_oll_content(response) #returned 
    try:
        sentences = extract_json(content) 
        if isinstance (sentences, list):
            return [s.strip() for s in sentences if s.strip()] #entfernt spaces am Anfang und Ende
        
    except Exception as e:
        print("split_ollama fallback: ", e)
        naive = re.split(r'(?<=[\.\?\!…])\s+(?=[A-ZÄÖÜẞa-zàèé…])', text.strip())
        naive = [s.strip() for s in naive if s.strip()] 
        #print(naive)
        return naive

def extract_oll_content(response):
    if not response:
        return None
    if isinstance(response, dict):
        # Typical Ollama dict structure
        msg = response.get("message") or response.get("messages")
        if isinstance(msg, dict):
            return msg.get("content")
        elif isinstance(msg, list) and msg and isinstance(msg[0], dict):
            return msg[0].get("content")
        return response.get("content")
    # Fallback: if response is an object string
    if hasattr(response, "message") and hasattr(response.message, "content"):
        return response.message.content
    return str(response)

from json_repair import repair_json

def extract_json(corrupted_json):
    try:
        # Use json_repair to fix the corrupted JSON
        repaired_json = repair_json(corrupted_json)
        return json.loads(repaired_json)
    except Exception as e:
        raise ValueError(f"Unable to fix corrupted JSON: {e}")

def classify_category(pos_seq, dep_seq):
    # These should now be strings from individual cells
    if isinstance(pos_seq, str):
        pos_seq = pos_seq.split()
    if isinstance(dep_seq, str):
        dep_seq = dep_seq.split()
    
    tokens = list(zip(pos_seq, dep_seq))
    
    subject_indices = [i for i, (pos, dep) in enumerate(tokens) 
                      if dep in ["nsubj", "nsubj:pass", "csubj", "csubj:pass"]]
    
    object_indices = [i for i, (pos, dep) in enumerate(tokens) 
                     if dep in ["obj", "iobj", "obl", "obl:npmod", "obl:tmod", "obl:agent"]]

    verb_indices = [i for i, (pos, dep) in enumerate(tokens) 
                   if pos in ["VERB", "AUX"] and dep in ["root", "aux", "conj", "ccomp", "xcomp"]]

    if not verb_indices:
        has_noun = any(pos in ["NOUN", "PROPN"] for pos, dep in tokens)
        has_root = any(dep == "root" for pos, dep in tokens)
        if has_noun and has_root:
            return "NO"  # Noun-only phrase
        else:
            return "Unknown"

    if not subject_indices or not object_indices:
        return "Unknown"

    s_idx = subject_indices[0]
    v_idx = verb_indices[0] 
    o_idx = object_indices[0]

    # Determine word order category
    if v_idx < s_idx and v_idx < o_idx:
        return "VSO"
    elif s_idx < v_idx and v_idx < o_idx:
        return "SVO"
    elif s_idx < o_idx and o_idx < v_idx:
        return "SOV"
    elif v_idx < o_idx and o_idx < s_idx:
        return "VOS"
    elif o_idx < v_idx and v_idx < s_idx:
        return "OVS"
    elif o_idx < s_idx and s_idx < v_idx:
        return "OSV"
    else:
        return "Unknown"