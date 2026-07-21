from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.run_config import RunConfig
from langchain_openai import ChatOpenAI
from ragas.embeddings import HuggingfaceEmbeddings
from datasets import Dataset
from app.pipeline import ingest, pipeline
import json
import os

# load eval dataset
with open("eval/eval_dataset.json") as f:
    eval_data = json.load(f)

# filter out of scope questions
in_scope = [q for q in eval_data if q["type"] != "out_of_scope"]

# ingest d2l
session = ingest("corpus/d2l-en.pdf")

# run pipeline on each question
questions = []
answers = []
contexts = []
ground_truths = []

for item in in_scope:
    query = item["question"]
    response, _ = pipeline(session, query)

    # get contexts directly from retrieval
    from app.retrieval import retrieval_and_reranking
    top_k_chunks, _ = retrieval_and_reranking(session, query)
    chunk_texts = top_k_chunks["documents"]

    questions.append(query)
    answers.append(response)
    contexts.append(chunk_texts)
    ground_truths.append(item["ideal_answer"])

# build dataset
dataset = Dataset.from_dict({
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truth": ground_truths
})

# configure groq as the eval llm
llm = LangchainLLMWrapper(
    ChatOpenAI(
        model="llama-3.1-8b-instant",
        openai_api_key=os.getenv("GROQ_INFERENCE_KEY"),
        openai_api_base="https://api.groq.com/openai/v1",
        n=1
    )
)
embeddings = HuggingfaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
# run evaluation
results = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=llm,
    embeddings=embeddings,
    run_config=RunConfig(max_workers=2, timeout=120)
)

print(results)
results.to_pandas().to_csv("eval_results.csv", index=False)
