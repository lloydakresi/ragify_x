import pdfplumber as pp
import os
from dotenv import load_dotenv
import chromadb
client = chromadb.Client()
collection = client.create_collection(name="doc_collection")
load_dotenv()
ENV = os.getenv("ENV", "local")

corpus_path = "../corpus/d2l-en.pdf"

with pp.open(corpus_path) as f:
    for page in f.pages:
        collection.add(
            ids = [str(page.page_number)],
            documents=[page.extract_text()]
        )
        break
