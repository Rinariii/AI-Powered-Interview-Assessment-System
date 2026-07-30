from pydantic import BaseModel
from typing import List, Optional

class VideoAnalysis(BaseModel):
    video_id: int
    file_path: str
    question: str
    final_score: int
    rubric_reason: str
    fluency_score: int
    ai_likeness_label: str
    ai_silence_score: int
    full_transcript: str
    segments: List[list]
    pauses: List[float]
    duration_sec: float

class AnalysisResponse(BaseModel):
    generated_at: str
    total_videos: int
    videos: List[VideoAnalysis]

class QuestionRubric(BaseModel):
    question: str
    rubric: str

class AnalysisRequestMetadata(BaseModel):
    questions: List[str]
    rubrics: List[str]
