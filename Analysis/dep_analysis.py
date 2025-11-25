import pandas as pd
import re
from typing import List, Tuple, Any
def process_sequences(csv_path, chunks_output_path):
    df = pd.read_csv(csv_path)

    def analyze_word_order(chunk: List[str], pos_tags: List[str]) -> str:  #chunk is a dep_seq, i.e. a list of strings
        positions = {}
        anyv = False
        anys = False
        anyo = False
        for i, (dep, pos) in enumerate(zip(chunk, pos_tags)):
            if (any(verb_tag in pos.upper() for verb_tag in ['VERB', 'AUX']) or dep.lower() in ['cop', 'aux', 'root', 'aux:pass']) and anyv == False and any(tag in dep.lower() for tag in ['nsubj', 'nsubj:pass', 'csubj', 'csubj:pass']) == False: 
                if dep.lower() == 'root':
                    positions['verb'] = i
                    anyv = True
                else:
                    positions['non_root_verb'] = i
            elif any(subj_tag in dep for subj_tag in ['nsubj', 'nsubj:pass', 'csubj', 'csubj:pass']) and anys == False:
                positions['subject'] = i
            
                anys = True
            elif any(obj_tag in dep for obj_tag in ['obj', 'dobj', 'iobj', 'obl']) and anyo == False:
                positions['object'] = i
                anyo = True
        if 'verb' in positions:
            if 'subject' in positions and 'object' in positions:
                s, v, o = positions['subject'], positions['verb'], positions['object']
                if v < s and v < o:
                    if s < o:
                        return 'pso' # for predicate
                    else:
                        return 'pos' #
                elif s < v and s < o:
                    if v < o:
                        return 'spo'
                    else:
                        return 'sop'
                elif o < s and o < v:
                    if s < v:
                        return 'osp'
                    else:
                        return 'ops'
            elif 'subject' in positions:
                s,v = positions['subject'], positions['verb']
                if s < v:
                    return 'sp' # for predicate
                else:
                    return 'ps'
            elif 'object' in positions:
                v,o = positions['verb'], positions['object']
                if o < v:
                    return 'op' # for predicate
                else:
                    return 'po'
            else:
                return 'p'

        if 'non_root_verb' in positions:
            if 'subject' in positions and 'object' in positions:
                s, v, o = positions['subject'], positions['non_root_verb'], positions['object']
                if v < s and v < o:
                    if s < o:
                        return 'vso'
                    else:
                        return 'vos'
                elif s < v and s < o:
                    if v < o:
                        return 'svo'
                    else:
                        return 'sov'
                elif o < s and o < v:
                    if s < v:
                        return 'osv'
                    else:
                        return 'ovs'
    
            elif 'subject' in positions:
                s,v = positions['subject'], positions['non_root_verb']
                if s < v:
                    return 'sv' # for predicate
                else:
                    return 'vs'
            elif 'object' in positions:
                v,o = positions['non_root_verb'], positions['object']
                if o < v:
                    return 'ov' # for predicate
                else:
                    return 'vo'
            else:
                    return 'v'
        elif 'subject' in positions and 'object' in positions:
            s,o = positions['subject'], positions['object']
            if o < s:
                return 'os'
            else:
                return 'so'
        elif 'subject' in positions:
            return 's'
        return 'unknown'
    
    def identify_chunk_type(chunk: List[str], pos_tags: List[str]) -> Tuple[str, str]: # soll chunk einer dep_seq bekommen und ihm seine "pattern" und word order zuordnen
        chunk_str = ' '.join(chunk).lower()
 
        patterns = {
            'prepositional_phrase': [r'.*case.*', r'.*prep.*', r'.*adp.*'],
            'subordinate_clause': [r'.*mark.*', r'.*advcl.*'],
            'adverbial_clause': [r'.*advcl.*', r'.*advmod.*'],
            'noun_phrase': [r'.*det.*', r'.*amod.*', r'.*compound.*'],
            'infinitive_clause': [r'.*xcomp.*'],
            'complement_clause': [r'.*ccomp.*'],
            'main_clause': [r'.*root.*']
        }
        category_ch = "unknown_chunk"

        for category, pattern_list in patterns.items():
            if any(re.search(pattern, chunk_str) for pattern in pattern_list):
                category_ch = category  
                break
            if category_ch != "unknown_chunk":
                break
        word_or = analyze_word_order(chunk, pos_tags)
        return category_ch, word_or  # returns both
    
    def split_into_chunks(deps: List[str], pos_tags: List[str]) -> List[Tuple[str, Tuple[str, str]]]:
        chunks = []
        current_chunk = []
        current_pos = []

        boundaries = ['mark', 'case', 'prep', 'adp', 'conj', 'ccomp', 'punct', 'cc']  #removed cc
        
        def is_complete_chunk(pos_tags: List[str], chunk: List[str]) -> bool:
            pos = ''.join(pos_tags)
            dep = ''.join(chunk)
            has_verb = any(verb_tag in pos for verb_tag in ['VERB', 'AUX'])
            has_verbd = any(verb_tag in dep for verb_tag in ['cop', 'aux', 'root', 'aux:pass'])
            return has_verb and has_verbd  #ignores noun phrases...
        
        for (dep, pos) in zip(deps, pos_tags): 
            sent_lower = dep.lower()
            is_relative = any(rel in sent_lower for rel in ['relcl', 'acl:relcl'])
            is_boundary = any(weak in sent_lower for weak in boundaries)
        
            if is_relative:
                if current_chunk and is_complete_chunk(current_pos, current_chunk) and len(current_chunk) >= 2:
                    chunk_type_info = identify_chunk_type(current_chunk, current_pos)  # category, word order
                    if chunk_type_info[1].find('s') == -1: # doesn't have an s (no subject in the relative clause)
                        chunk_type_info = (chunk_type_info[0], 's' + chunk_type_info[1]) # add s at the start (bacause thats where the relative particle is)
                    chunks.append((' '.join(current_chunk), chunk_type_info))
                    current_chunk = []
                    current_pos = []
                current_chunk.append(dep)
                current_pos.append(pos)
            
            elif is_boundary and current_chunk and is_complete_chunk(current_pos, current_chunk) and len(current_chunk) >= 2:
                chunk_type_info = identify_chunk_type(current_chunk, current_pos)
                chunks.append((' '.join(current_chunk), chunk_type_info))
                current_chunk = [dep]
                current_pos = [pos]
            
            else:
                current_chunk.append(dep)
                current_pos.append(pos)

        if current_chunk:
            chunk_type_info = identify_chunk_type(current_chunk, current_pos)
            chunks.append((' '.join(current_chunk), chunk_type_info))
        
        new_chunks = []
        for i, chunk in enumerate(chunks):
            chunkt, (category, word_order) = chunk 
            
            if 's' not in word_order and ('v' in word_order or 'p' in word_order):
                main_clause_order = None
                for other_chunk in chunks:
                    other_category, other_order = other_chunk[1]
                    if 's' in other_order and ('v' in other_order or 'p' in other_order):
                        main_clause_order = other_order
                        break
                if main_clause_order:
                    s = main_clause_order.find('s')
                    current_c = [c for c in word_order if c != 's']
                    if s < len(current_c):
                        new_c = current_c[:s] + ['s'] + current_c[s:]
                    else:
                        new_c = current_c + ['s']
                    new_order = ''.join(new_c)
                    new_chunks.append((chunkt, (category, new_order)))
                else:
                    new_chunks.append(chunk)
            else:
                new_chunks.append(chunk)
            chunks = new_chunks
        return chunks

    all_chunks_data = []
    for (dep_seq, pos_seq) in zip(df["dep_seq"], df["pos_seq"]):
        deps = dep_seq.split()
        pos_tags = pos_seq.split()
        chunks = split_into_chunks(deps, pos_tags) #list of dep_seq chunks
        
        for chunk_text, (phrase_type, word_order) in chunks:
            all_chunks_data.append({
                "chunk": chunk_text,
                "phrase_type": phrase_type,
                "word_order": word_order
            })

    chunk_df = pd.DataFrame(all_chunks_data) 
    chunk_df.to_csv(chunks_output_path, index=False)
    
    return chunk_df
chunk_df = process_sequences("he_sent_analysis_1711.csv", "chunks_he_2211.csv")
chunk_df = process_sequences("mhg_sent_analysis_1011.csv", "chunks_mhg_2211.csv")
