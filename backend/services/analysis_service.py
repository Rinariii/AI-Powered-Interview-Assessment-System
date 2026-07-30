import re
from .llm_service import (
    clean_text_semantic,
    semantic_sim,
    analyze_ai_suspect_from_embedding,
    generate_keywords_from_llm
)

def clean_text_raw(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def analyze_fluency_from_silence(total_silence, total_duration, gaps):
    silence_ratio = total_silence / total_duration if total_duration > 0 else 0
    avg_gap = total_silence / len(gaps) if len(gaps) > 0 else 0
    gap_freq = len(gaps) / total_duration if total_duration > 0 else 0

    score = 4

    # Silence ratio (persentase jeda)
    if silence_ratio > 0.25:
        score -= 3
    elif silence_ratio > 0.15:
        score -= 2
    elif silence_ratio > 0.08:
        score -= 1

    # Average gap length
    if avg_gap > 2.0:
        score -= 2
    elif avg_gap > 1.2:
        score -= 1

    # Gap frequency
    if gap_freq > (1/4):  # lebih dari 1 gap setiap 4 detik
        score -= 1

    score = max(1, min(score, 4))

    return {
        "fluency_score": score,
        "silence_ratio": silence_ratio,
        "avg_gap": avg_gap,
        "gap_frequency": gap_freq
    }

def analyze_ai_suspect_from_silence(total_silence, total_duration, gaps):
    if total_duration == 0:
        return 0

    silence_ratio = total_silence / total_duration
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    gap_variance = (max(gaps) - min(gaps)) if len(gaps) > 1 else 0

    score = 0

    # 1. AI hampir tanpa jeda
    if silence_ratio < 0.02:
        score += 2

    # 2. Jeda pendek → AI
    if avg_gap < 0.40:
        score += 1

    # 3. Variasi jeda stabil
    if gap_variance < 0.3:
        score += 1

    # 4. Jeda seragam → AI
    if len(gaps) > 0 and all(0.20 < g < 0.55 for g in gaps):
        score += 1

    return min(score, 4)

def analyze_ai_combined(text, total_silence, total_duration, gaps):
    silence_score = analyze_ai_suspect_from_silence(total_silence, total_duration, gaps)
    emb_data = analyze_ai_suspect_from_embedding(text)

    embedding_score = emb_data["embedding_score"]
    total_score = silence_score + embedding_score

    if total_score >= 6:
        label = "Highly AI-like"
    elif total_score >= 4:
        label = "Likely AI-like"
    elif total_score >= 2:
        label = "Somewhat AI-like"
    else:
        label = "Likely Human"

    return {
        "silence_score": silence_score,
        "embedding_similarity": emb_data["similarity"],
        "embedding_score": embedding_score,
        "ai_score_total": total_score,
        "ai_label": label
    }

def rubric_scoring(clean_text, question_keywords):
    kw = question_keywords

    specific_hit = any(k.lower() in clean_text for k in kw["specific_keywords"])
    action_hit   = any(k.lower() in clean_text for k in kw["action_keywords"])
    concept_hit  = any(k.lower() in clean_text for k in kw["conceptual_keywords"])
    general_hit  = any(k.lower() in clean_text for k in kw["general_keywords"])

    semantic_scores = []
    for ref in kw["semantic_reference"]:
        semantic_scores.append(semantic_sim(clean_text, ref))
    semantic_best = max(semantic_scores) if semantic_scores else 0

    # Scoring rules
    if (specific_hit and action_hit and concept_hit) and semantic_best > 0.60:
        return 4, "Highly detailed answer aligned with expected standards."
    if specific_hit and (action_hit or concept_hit or semantic_best > 0.45):
        return 3, "Specific answer with clear reasoning."
    if general_hit:
        return 2, "General explanation lacking detail."
    if len(clean_text.split()) < 20:
        return 1, "Minimal or vague response."
    return 1, "Vague response lacking structure."


def evaluate_answer(
    text,
    total_silence,
    total_duration,
    gaps,
    question_keywords
):
    # 1. Raw cleaning
    raw = clean_text_raw(text)

    # 2. Fluency dari silence
    fluency_data = analyze_fluency_from_silence(total_silence, total_duration, gaps)

    # 3. AI detection (silence only + combined)
    ai_silence_only = analyze_ai_suspect_from_silence(total_silence, total_duration, gaps)
    ai_combined = analyze_ai_combined(raw, total_silence, total_duration, gaps)

    # 4. Clean for semantic scoring
    clean = clean_text_semantic(raw)

    # 5. Rubric scoring
    rscore, rreason = rubric_scoring(clean, question_keywords)

    # 6. Bundle final
    return {
        "raw_text": raw,
        "clean_text": clean,
        "fluency_score": fluency_data["fluency_score"],
        "fluency_meta": fluency_data,
        "ai_suspect_silence_only": ai_silence_only,
        "ai_suspect": ai_combined,
        "rubric_score": rscore,
        "rubric_reason": rreason,
        "final_score": rscore
    }
