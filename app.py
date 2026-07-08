import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os

# --- Page Configurations ---
st.set_page_config(page_title="Kenyan Languages Translator", page_icon="🇰🇪", layout="centered")
st.title("🇰🇪 Multilingual Kenyan Translator")
st.write("Translate sentences instantly using a custom Bible Knowledge Base & Meta's NLLB AI.")

# --- Load the Aligned Bible Database ---
@st.cache_data
def load_knowledge_base():
    csv_path = "clean_kenyan_bibles.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path).fillna("")
    return None

df_bible = load_knowledge_base()

# --- Load Hugging Face NLLB Model ---
@st.cache_resource
def load_nllb_model():
    model_name = "facebook/nllb-200-distilled-600M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

# Language definitions with their exact NLLB FLORES-200 codes
LANGUAGES = {
    "Swahili": {"code": "swh_Latn", "col": "Swahili"},
    "Dholuo (Luo)": {"code": "luo_Latn", "col": "Luo"},
    "Gĩkũyũ (Kikuyu)": {"code": "kik_Latn", "col": "Kikuyu"}
}

# --- UI Layout Elements ---
src_lang = st.selectbox("Translate From:", list(LANGUAGES.keys()), index=0)
tgt_lang = st.selectbox("Translate To:", list(LANGUAGES.keys()), index=1)

user_text = st.text_area("Enter word, phrase, or verse to translate:", "Hapo mwanzo Mungu aliumba mbingu na dunia.")

if st.button("Run Translation", type="primary"):
    if not user_text.strip():
        st.warning("Tafadhali andika kitu (Please enter some text).")
    else:
        # --- STRATEGY 1: Exact Knowledge Base Match ---
        found_in_kb = False
        if df_bible is not None:
            src_col = LANGUAGES[src_lang]["col"]
            tgt_col = LANGUAGES[tgt_lang]["col"]
            
            # Simple lookup: match exact text string in our database
            matched_rows = df_bible[df_bible[src_col].str.lower() == user_text.strip().lower()]
            
            if not matched_rows.empty and matched_rows.iloc[0][tgt_col]:
                translation = matched_rows.iloc[0][tgt_col]
                ref = matched_rows.iloc[0]["Reference"]
                
                st.success("✅ **Verified Human Translation Found in Bible Knowledge Base:**")
                st.info(f"📖 **Reference:** {ref}")
                st.subheader(translation)
                found_in_kb = True

        # --- STRATEGY 2: Fallback to NLLB Model ---
        if not found_in_kb:
            st.info("🤖 Phrase not in Bible. Processing with NLLB-200 AI Model...")
            with st.spinner("Analyzing grammar and translating text..."):
                try:
                    tokenizer, model = load_nllb_model()
                    
                    src_code = LANGUAGES[src_lang]["code"]
                    tgt_code = LANGUAGES[tgt_lang]["code"]
                    
                    tokenizer.src_lang = src_code
                    inputs = tokenizer(user_text, return_tensors="pt")
                    
                    translated_tokens = model.generate(
                        **inputs, 
                        forced_bos_token_id=tokenizer.lang_code_to_id[tgt_code], 
                        max_length=512
                    )
                    
                    translation = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
                    
                    st.success("✨ **AI Generated Translation:**")
                    st.subheader(translation)
                except Exception as e:
                    st.error(f"Inference error: {e}")

