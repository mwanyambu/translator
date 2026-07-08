import re
import pandas as pd

# Standard 66 universal Bible book codes
STANDARD_CODES = [
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOSH", "JDG", "RUTH", "1SAM", "2SAM", 
    "1KIN", "2KIN", "1CHR", "2CHR", "EZRA", "NEH", "EST", "JOB", "PSA", "PRO", 
    "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN", "HOS", "JOEL", "AMOS", 
    "OBA", "JON", "MIC", "NAH", "HAB", "ZEP", "HAG", "ZECH", "MAL",
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1COR", "2COR", "GAL", "EPH", 
    "PHP", "COL", "1THS", "2THS", "1TIM", "2TIM", "TIT", "PHLM", "HEB", "JAS", 
    "1PET", "2PET", "1JHN", "2JHN", "3JHN", "JUDE", "REV"
]

# Exact lowercase book names from your verified map
BOOK_MAPS = {
    "swa": ["mwanzo", "kutoka", "mambo ya walawi", "hesabu", "kumbukumbu la torati", "yoshua", "waamuzi", "ruthu", "1 samweli", "2 samweli", "1 wafalme", "2 wafalme", "1 mambo ya nyakati", "2 mambo ya nyakati", "ezra", "nehemia", "esta", "ayubu", "zaburi", "mithali", "mhubiri", "wimbo ulio bora", "isaya", "yeremia", "maombolezo", "ezekieli", "danieli", "hosea", "yoeli", "amosi", "obadia", "yona", "mika", "nahumu", "habakuki", "sefania", "hagai", "zekaria", "malaki", "mathayo", "marko", "luka", "yohana", "matendo ya mitume", "warumi", "1 wakorintho", "2 wakorintho", "wagalatia", "waefeso", "wafilipi", "wakolosai", "1 wathesalonike", "2 wathesalonike", "1 timotheo", "2 timotheo", "tito", "filemoni", "waebrania", "yakobo", "1 petro", "2 petro", "1 yohana", "2 yohana", "3 yohana", "yuda", "ufunuo"],
    "luo": ["chakruok", "wuok", "tim jo-lawi", "kwan", "rapar mar chik", "joshua", "jongʼad bura", "ruth", "1_samuel", "2_samuel", "1 ruodhi", "2 ruodhi", "1 weche mag ndalo", "2 weche mag ndalo", "ezra", "nehemia", "esta", "ayub", "zaburi", "ngeche", "eklesiastes", "wer mamit", "isaya", "yeremia", "ywagruok", "ezekiel", "daniel", "hosea", "joel", "amos", "obadia", "yona", "mika", "nahum", "habakuk", "zefania", "hagai", "zekaria", "malaki", "mathayo", "mariko", "luka", "johana", "tich joote", "jo-rumi", "1 jo-korintho", "2 jo-korintho", "jo-galatia", "jo-efeso", "jo-filipi", "jo-kolosai", "1 jo-thesalonika", "2 jo-thesalonika", "1 timotheo", "2 timotheo", "tito", "filemon", "jo-hibrania", "jakobo", "1 petro", "2 petro", "1 johana", "2 johana", "3 johana", "juda", "fweny"],
    "kik": ["kĩambĩrĩria", "thaama", "alawii", "ndari", "gũcookerithia", "joshua", "atiirĩrĩri", "ruthu", "1 samũeli", "2 samũeli", "1 athamaki", "2 athamaki", "1 maũndũ ma matukũ ma tene", "2 maũndũ ma matukũ ma tene", "ezara", "nehemia", "esiteri", "ayubu", "thaburi", "thimo", "kohelethu", "rwĩmbo", "isaia", "jeremia", "macakaya", "ezekieli", "danieli", "hosea", "joeli", "amosi", "obadia", "jona", "mika", "nahumu", "habakuku", "zefania", "hagai", "zekaria", "malaki", "mathayo", "mariko", "luka", "johana", "atũmwo", "aroma", "1 akorinitho", "2 akorinitho", "agalatia", "aefeso", "afilipi", "akolosai", "1 athesalonike", "2 athesalonike", "1 timotheo", "2 timotheo", "tito", "filemona", "ahibirania", "jakubu", "1 petero", "2 petero", "1 johana", "2 johana", "3 johana", "judasi", "kũguũrĩrio"],
    "guz": ["okaochi", "okorwa", "abalawi", "emanyeso", "ekerorano", "yosuwa", "abaria", "ruthi", "1 samweli", "2 samweli", "1 abarwoti", "2 abarwoti", "1 amang'ana 'ebiro", "2 amang'ana 'ebiro", "ezra", "nehemia", "eseteri", "yobu", "zaburi", "kamang'ana", "omotemeri", "omoasani", "isaya", "yeremia", "kamanyong'o", "ezekieli", "danieli", "hosea", "yoeli", "amosi", "obadia", "yona", "mika", "nahumu", "habakuki", "zefania", "hagai", "zekaria", "malaki", "matayo", "mariko", "luka", "yohana", "ogokora", "abaromi", "1 abakorinto", "2 abakorinto", "abagalatia", "abaefeso", "abafilipi", "abakolosai", "1 abatesalonika", "2 abatesalonika", "1 timoteo", "2 timoteo", "tito", "filemoni", "abaheberi", "yakobo", "1 petero", "2 petero", "1 yohana", "2 yohana", "3 yohana", "yuda", "ogokusurwa"]
}

def parse_bible_adaptive(file_path, lang_code):
    bible_dict = {}
    local_books = BOOK_MAPS[lang_code]
    
    current_book_idx = -1
    current_code = "UNKNOWN"
    current_chap = "1"
    current_verse = None
    current_text = ""
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "PDF generated" in line or "copyright" in line or "Biblica" in line or ". . ." in line:
                continue
                
            # 1. Look for Standalone Book Name Lines (Case-insensitive matching)
            cleaned_line = line.lower().replace("ʼ", "ʼ").strip()
            
            # Look ahead for the next chronological book name
            next_idx = current_book_idx + 1
            if next_idx < len(local_books) and local_books[next_idx] == cleaned_line:
                current_book_idx = next_idx
                current_code = STANDARD_CODES[current_book_idx]
                current_chap = "1" # Reset chapter count for the new book
                current_verse = None
                continue
                
            # 2. Track automatic chapter boundaries when verse hits 1 again (excluding the first instance)
            verse_match = re.match(r'^(\d+)\s+(.*)', line)
            if verse_match:
                v_num = verse_match.group(1)
                v_text = verse_match.group(2)
                
                # If verse numbers loop back to 1 inside the same book, increment the chapter!
                if v_num == "1" and current_verse is not None:
                    # Save trailing verse from the previous chapter first
                    if current_code != "UNKNOWN":
                        ref_key = f"{current_code}_{current_chap}_{current_verse}"
                        bible_dict[ref_key] = current_text.strip()
                    
                    current_chap = str(int(current_chap) + 1)
                    current_verse = v_num
                    current_text = v_text
                    continue

                # Normal verse saving step
                if current_verse and current_code != "UNKNOWN":
                    ref_key = f"{current_code}_{current_chap}_{current_verse}"
                    bible_dict[ref_key] = current_text.strip()
                
                current_verse = v_num
                current_text = v_text
            else:
                # Text continuation line
                if current_verse:
                    current_text += " " + line
                    
        # Grab final verse
        if current_verse and current_code != "UNKNOWN":
            ref_key = f"{current_code}_{current_chap}_{current_verse}"
            bible_dict[ref_key] = current_text.strip()
            
    return bible_dict

# --- Process files independently ---
print("⏳ Extracting Swahili parallel records...")
swa_dataset = parse_bible_adaptive("swa.txt", "swa")
print(f"   Found {len(swa_dataset)} Swahili verses.")

print("⏳ Extracting Luo parallel records...")
luo_dataset = parse_bible_adaptive("luo.txt", "luo")
print(f"   Found {len(luo_dataset)} Luo verses.")

print("⏳ Extracting Kikuyu parallel records...")
kik_dataset = parse_bible_adaptive("kik.txt", "kik")
print(f"   Found {len(kik_dataset)} Kikuyu verses.")

print("⏳ Extracting Gusii parallel records...")
guz_dataset = parse_bible_adaptive("guz.txt", "guz")
print(f"   Found {len(guz_dataset)} Gusii verses.")

# --- Cross-link dataset ---
print("🔗 Cross-linking languages into a master system array...")
master_records = []
all_keys = set(list(swa_dataset.keys()) + list(luo_dataset.keys()) + list(kik_dataset.keys()) + list(guz_dataset.keys()))

if len(all_keys) == 0:
    print("\n❌ ERROR: Still found 0 records. Check if text file paths are accurate.")
else:
    for key in sorted(all_keys):
        parts = key.split("_")
        readable_ref = f"{parts} {parts}:{parts}"
        
        master_records.append({
            "Reference": readable_ref,
            "Swahili": swa_dataset.get(key, ""),
            "Luo": luo_dataset.get(key, ""),
            "Kikuyu": kik_dataset.get(key, ""),
            "Gusii": guz_dataset.get(key, "")
        })

    df = pd.DataFrame(master_records, columns=["Reference", "Swahili", "Luo", "Kikuyu", "Gusii"])
    df = df[df[["Swahili", "Luo", "Kikuyu", "Gusii"]].any(axis=1)]
    df.to_csv("clean_kenyan_bibles.csv", index=False, encoding="utf-8")
    print(f"🎉 SUCCESS! Aligned {len(df)} entries into clean_kenyan_bibles.csv")

