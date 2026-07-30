from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
import numpy as np
from numpy.linalg import norm
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

# --- Load Models ---
EMBEDDER_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
embedder = SentenceTransformer(EMBEDDER_MODEL_ID)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
client = OpenAI(api_key=api_key, base_url=base_url) if api_key and base_url else None


def _require_client():
    if client is None:
        raise RuntimeError(
            "OPENAI_API_KEY and OPENAI_BASE_URL must be configured in the "
            "environment or in backend/.env before running the app."
        )

MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"

AI_STYLE_PROMPTS = [
    "I believe my greatest strength is my ability to stay focused under pressure.",
    "I am highly motivated and always eager to improve myself.",
    "I work well in teams and enjoy collaborative environments.",
    "I consistently strive for professionalism and clear communication.",
]

def build_ai_style_embedding(prompts):
    _require_client()
    vectors = []
    for p in prompts:
        resp = client.embeddings.create(
             model=EMBED_MODEL,
             input=p
        )
        vectors.append(np.array(resp.data[0].embedding))
    return np.mean(vectors, axis=0)

# Pre-compute centroid lazily so missing credentials do not crash import time
AI_CENTROID = None


def get_ai_centroid():
    global AI_CENTROID
    if AI_CENTROID is None:
        AI_CENTROID = build_ai_style_embedding(AI_STYLE_PROMPTS)
    return AI_CENTROID


def call_llm(prompt, max_tokens=500, temperature=0.2):
    _require_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content

def generate_keywords_from_llm(question, rubric_desc_4):
    prompt = f"""
You are an HR expert. Generate structured keyword sets based on:

INTERVIEW QUESTION:
{question}

PERFECT ANSWER (Score 4):
{rubric_desc_4}

Respond ONLY in this JSON format:

{{
  "specific_keywords": [],
  "action_keywords": [],
  "conceptual_keywords": [],
  "general_keywords": [],
  "semantic_reference": []
}}
"""
    output = call_llm(prompt)

    # extract JSON
    json_start = output.find("{")
    json_end = output.rfind("}") + 1
    json_str = output[json_start:json_end]

    # cleanup
    json_str = json_str.replace("\n", " ").replace("\t", " ")
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)

    return json.loads(json_str)

def clean_text_semantic(text):
    text = text.lower()
    filler = ["uh", "um", "emm", "hmm", "erm", "you know", "like", "kinda", "sorta"]
    for f in filler:
        text = text.replace(f, "")

    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def semantic_sim(a, b):
    emb1 = embedder.encode(a, convert_to_tensor=True, normalize_embeddings=True)
    emb2 = embedder.encode(b, convert_to_tensor=True, normalize_embeddings=True)
    return float(util.cos_sim(emb1, emb2).item())

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def analyze_ai_suspect_from_embedding(text, ai_centroid=None):
    _require_client()
    if ai_centroid is None:
        ai_centroid = get_ai_centroid()

    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    emb = np.array(resp.data[0].embedding)

    sim = cosine_similarity(emb, ai_centroid)

    # Skor AI-likeness dari similarity
    if sim > 0.90:
        score = 3
    elif sim > 0.87:
        score = 2
    elif sim > 0.83:
        score = 1
    else:
        score = 0

    return {
        "similarity": sim,
        "embedding_score": score
    }
