from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import json
import shutil
import os
from datetime import datetime
from contextlib import asynccontextmanager

from models import AnalysisResponse, VideoAnalysis
from services.audio_processor import process_audio
from services.llm_service import generate_keywords_from_llm
from services.analysis_service import evaluate_answer

# Preload things if needed (though our services initialize models on file load mainly)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup resources
    os.makedirs("temp_uploads", exist_ok=True)
    yield
    # Cleanup resources
    if os.path.exists("temp_uploads"):
        shutil.rmtree("temp_uploads", ignore_errors=True)

app = FastAPI(lifespan=lifespan)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_videos(
    files: List[UploadFile] = File(...),
    metadata: str = Form(...) # JSON string with questions and rubrics
):
    try:
        meta = json.loads(metadata)
        questions = meta.get("questions", [])
        rubrics = meta.get("rubrics", [])
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON format")

    if len(questions) != len(files) or len(rubrics) != len(files):
        raise HTTPException(status_code=400, detail="Number of files, questions, and rubrics must match")

    videos_result = []

    # 1. Generate Keywords for all questions first (or sequentially inside loop)
    # Sequentially is fine for now
    
    for idx, (file, question, rubric) in enumerate(zip(files, questions, rubrics), start=1):
        # Save temp file
        temp_filename = f"temp_uploads/{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # 1. Audio Processing
            # Note: process_audio uses internal index for naming, we can pass idx
            audio_result = process_audio(temp_filename, idx)
            
            # 2. Generate Keywords
            keywords = generate_keywords_from_llm(question, rubric)
            
            # 3. Analyze
            analysis = evaluate_answer(
                text=audio_result["full_transcript"],
                total_silence=audio_result["total_silence"],
                total_duration=audio_result["duration"],
                gaps=audio_result["pauses"],
                question_keywords=keywords
            )
            
            # 4. Format Result
            video_analysis = VideoAnalysis(
                video_id=idx,
                file_path=file.filename, # Returning original filename as path per requirement/mock
                question=question,
                final_score=analysis["final_score"],
                rubric_reason=analysis["rubric_reason"],
                fluency_score=analysis["fluency_score"],
                ai_likeness_label=analysis["ai_suspect"]["ai_label"],
                ai_silence_score=analysis["ai_suspect_silence_only"],
                full_transcript=audio_result["full_transcript"],
                segments=audio_result["segments"],
                pauses=audio_result["pauses"],
                duration_sec=audio_result["duration"]
            )
            videos_result.append(video_analysis)

        finally:
             if os.path.exists(temp_filename):
                os.remove(temp_filename)
    
    return AnalysisResponse(
        generated_at=datetime.now().isoformat(),
        total_videos=len(videos_result),
        videos=videos_result
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)