from pathlib import Path
import fitz
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter



def extract(file_path):
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=1750,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " "]
    )
    p = {}
    p["text"], p["metadata"] = [], []
    #skipping the first 24 pages
    skips = 0
    with fitz.open(file_path) as doc:
        for page in doc:

            text = page.get_text("text")
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            text = re.sub(r"(?m)^\d+\s*$", "", text)
            text = re.sub(r"-\n", "", text)
            num = page.number + 1

            split_text = splitter.split_text(text)
            for t in split_text:
                p["text"].append(t)
                p["metadata"].append(
                    {"page_number":num}
                )
    return p, skips, num


"""
p, skips, num = extract("corpus/d2l-en.pdf")
print(f"Total number of pages:{num}")
print(f"Pages skipped:{skips}")
print(f"Total number of chunks: {len(p["ids"])}")
total_char = 0
for x in p["text"]:
    total_char += len(x)

average_chunk_len = total_char/len(p["ids"])
print(f"Average chunk length: {average_chunk_len}")
"""
