import json, csv, re
'''with open('heb_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('heb_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['index', 'text'])  # header
    ind = 0
    for version in data['versions']:
        for text_array in version['text']:
            for item in text_array:
                segm = re.split(r'(?<=\\")|(?<=\.)|(?<=,)', item)
                for segm in segm:
                  if segm.strip():
                    writer.writerow([ind, segm.strip(":")])
                    ind += 1
''''''

def clean_text(text):
    # Split into lines
    lines = text.split('\n')
    
    cleaned_lines = []
    for line in lines:
        if line.strip().isdigit():
            continue
        cleaned_lines.append(line.strip())
    
    # Join all lines into one string
    full_text = ' '.join(cleaned_lines)
    
    # Replace problematic characters and patterns
    replacements = [
        (' ,', ','),
        (' .', '.'),
        (' !', '!'),
        (' :', ':'),
        ('< ', ''),
        (' >', ''),
        (' ?', ''),
        ('  ', ' ')   
    ]
    
    for old, new in replacements:
        full_text = full_text.replace(old, new)
    
    # Final cleanup of any remaining double spaces
    while '  ' in full_text:
        full_text = full_text.replace('  ', ' ')
    
    return full_text.strip()

clean_text = clean_text(text)
with open('text.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['text'])  # header
    ind = 0
    writer.writerow([clean_text])
'''