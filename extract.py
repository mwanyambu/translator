from pypdf import PdfReader
import sys

# Change these filenames to match your exact file names!
pdf_path = "luo.pdf"
output_txt_path = "luo.txt"

print(f"Starting extraction from {pdf_path}...")

try:
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"Found {total_pages} pages. Extracting text...")
    
    with open(output_txt_path, "w", encoding="utf-8") as f:
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                f.write(text + "\n")
            # Show progress every 50 pages so you know it's working
            if (idx + 1) % 50 == 0 or (idx + 1) == total_pages:
                print(f"Processed {idx + 1}/{total_pages} pages...")

    print(f"🎉 Success! Raw text extracted to: {output_txt_path}")

except FileNotFoundError:
    print(f"❌ Error: Could not find the file '{pdf_path}'. Check your spelling and try again.")
except Exception as e:
    print(f"❌ An error occurred: {e}")

