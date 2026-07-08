import re
import pandas as pd

def parse_haiola_bible(file_path):
    """Parses standard Haiola text exports into a clean dictionary mapping."""
    bible_dict = {}
    current_book = "Unknown"
    current_chapter = "0"
    
    # We will track standard book markers. 
    # This regex looks for lines indicating a page header like 'Mwanzo 1:1' or 'Chakruok 1:1'
    header_pattern = re.compile(r'^([1-3]?\s?[A-Za-zÀ-ÿ’\s]+)\s+(\d+):(\d+)')
    # Regex to find verse lines starting with a number
    verse_pattern = re.compile(r'^(\d+)\s+(.*)')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_verse_num = None
    current_verse_text = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line indicates a new book/chapter from page headers
        header_match = header_pattern.match(line)
        if header_match:
            current_book = header_match.group(1).strip()
            current_chapter = header_match.group(2)
            continue
            
        # Check if line is the start of a verse
        verse_match = verse_pattern.match(line)
        if verse_match:
            # Save previous verse before starting a new one
            if current_verse_num:
                key = f"{current_book}_{current_chapter}_{current_verse_num}"
                bible_dict[key] = current_verse_text.strip()
                
            current_verse_num = verse_match.group(1)
            current_verse_text = verse_match.group(2)
        else:
            # If line doesn't start with a number, it's a continuation of the previous verse
            if current_verse_num:
                # Filter out system artifacts, headers or page numbers
                if "PDF generated using" not in line and "copyright" not in line:
                    current_verse_text += " " + line
                    
    # Save the final verse
    if current_verse_num:
        key = f"{current_book}_{current_chapter}_{current_verse_num}"
        bible_dict[key] = current_verse_text.strip()
        
    return bible_dict

print("Parsing Swahili Bible...")
swa_bible = parse_haiola_bible("swa.txt")

print("Parsing Luo Bible...")
luo_bible = parse_haiola_bible("luo.txt")

print("Parsing Kikuyu Bible...")
kik_bible = parse_haiola_bible("kik.txt")

print("Parsing Gusii Bible...")
guz_bible = parse_haiola_bible("guz.txt")

# Standardize index using Bible structural keys to align them line-by-line
# We use Swahili as the base reference mapping
aligned_data = []
for key, swa_text in swa_bible.items():
    # Structural keys look like 'Mwanzo_1_1'
    # We match it across other dictionaries using safe lookups
    parts = key.split('_')
    chap_verse = f"{parts[1]}:{parts[2]}"
    
    # Try to align corresponding text lines safely
    luo_text = luo_bible.get(key, "")
    kik_text = kik_bible.get(key, "")
    guz_text = guz_bible.get(key, "")
    
    aligned_data.append({
        "Reference": f"{parts[0]} {chap_verse}",
        "Swahili": swa_text,
        "Luo": luo_text,
        "Kikuyu": kik_text,
        "Gusii": guz_text
    })

# Convert to DataFrame and save to CSV
df = pd.DataFrame(aligned_data)
df.to_csv("aligned_kenyan_bibles.csv", index=False, encoding='utf-8')
print(f"🎉 Alignment complete! Saved {len(df)} verses to aligned_kenyan_bibles.csv")

