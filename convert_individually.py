import re
import pandas as pd

def convert_txt_to_excel_with_meta(input_txt, output_excel, column_name):
    """
    Parses a raw text Bible line-by-line. Tracks book and chapter changes,
    and formats the output with columns for Book, Chapter, Verse, and Text.
    """
    print(f"📖 Processing {input_txt}...")
    records = []
    
    # Tracking variables for metadata
    current_book = "Introduction/Preface"
    current_chapter = "0"
    current_verse_num = None
    current_verse_text = ""
    
    with open(input_txt, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip noise lines
            if not line or "PDF generated" in line or "copyright" in line or "Biblica" in line:
                continue
            
            # Skip the table of contents lines completely
            if ". . ." in line or "Contents" in line:
                continue

            # 1. DETECT CHAPTER/BOOK HEADINGS
            # Matches formats like "Mwanzo 1", "Omochakano 1", "1 Samweli 5", or just a standalone number "12"
            heading_match = re.match(r'^([A-Za-zÀ-ÿ’\s\-1-3\u02bc]+)?\s*(\d+)$', line)
            
            # We ensure it's not a verse line (verses start with numbers but always contain text after)
            if heading_match and not re.match(r'^\d+\s+\w+', line):
                # If there's an ongoing verse in memory, save it before changing headings
                if current_verse_num is not None:
                    records.append({
                        "Book": current_book,
                        "Chapter": current_chapter,
                        "Verse": int(current_verse_num),
                        column_name: current_verse_text.strip()
                    })
                    current_verse_num = None
                
                detected_book_name = heading_match.group(1)
                detected_chap_num = heading_match.group(2)
                
                # Update tracking details
                if detected_book_name:
                    current_book = detected_book_name.strip()
                current_chapter = detected_chap_num
                continue

            # 2. DETECT VERSE LINES (Lines starting with a number followed by space/text)
            verse_match = re.match(r'^(\d+)\s+(.*)', line)
            if verse_match:
                # Save the completed previous verse before initializing the new row
                if current_verse_num is not None:
                    records.append({
                        "Book": current_book,
                        "Chapter": current_chapter,
                        "Verse": int(current_verse_num),
                        column_name: current_verse_text.strip()
                    })
                
                current_verse_num = verse_match.group(1)
                current_verse_text = verse_match.group(2)
            else:
                # 3. SENTENCE CONTINUATION
                # If the line is plain text, add it to the active verse
                if current_verse_num is not None:
                    current_verse_text += " " + line
                elif len(line) > 3 and not line.islower() and not line.startswith(('1','2','3')):
                    # If text appears before any verse number has been logged, it's likely a standalone Book title
                    current_book = line
                    current_chapter = "1"

        # Save the absolute last verse of the file string array
        if current_verse_num is not None:
            records.append({
                "Book": current_book,
                "Chapter": current_chapter,
                "Verse": int(current_verse_num),
                column_name: current_verse_text.strip()
            })

    # Pack into a data frame and export to Excel workbook
    df = pd.DataFrame(records)
    
    # Move introductory text to the top and format nicely
    df.to_excel(output_excel, index=False)
    print(f"💾 Success! Saved {len(df)} verses with Book & Chapter headers to: {output_excel}\n")

# --- Run the conversion scripts individually ---
convert_txt_to_excel_with_meta("swa.txt", "swa.xlsx", "Swahili_Text")
convert_txt_to_excel_with_meta("luo.txt", "luo.xlsx", "Luo_Text")
convert_txt_to_excel_with_meta("kik.txt", "kik.xlsx", "Kikuyu_Text")
convert_txt_to_excel_with_meta("guz.txt", "guz.xlsx", "Gusii_Text")

print("🚀 All 4 individual Excel files with headers generated successfully!")

