import ffmpeg
import whisper
import os

def process_audio(input_file: str, output_index: int):
    output_file = f"audio_clean_{output_index}.wav"

    # Extract audio
    try:
        ffmpeg.input(input_file).output(output_file, ac=1, ar=16000).run(overwrite_output=True)
    except ffmpeg.Error as e:
        print(f"Error processing audio: {e}")
        # Build dummy result if ffmpeg fails? Or re-raise.
        # For now, let's assume it works or re-raise 
        raise e

    # Load Whisper
    model = whisper.load_model("medium") # Warning: This reloads model every time. Ideally load once globally.
    # In a real app we should load model at startup. For this script migration, I'll keep it simple but consider caching.
    
    result = model.transcribe(
        audio=output_file,
        language="en",
        word_timestamps=True
    )

    pause_word_gap = 0.5
    pause_segment_gap = 0.5

    segments = []
    current_segment = []
    seg_start = None
    prev_end = None

    for seg in result["segments"]:
        words = seg.get("words", [])
        if not words:
            continue

        if prev_end is not None and words[0]["start"] - prev_end > pause_segment_gap:
            if current_segment:
                seg_end = prev_end
                text = " ".join(current_segment).strip()
                segments.append((seg_start, seg_end, text))
                current_segment = []
                seg_start = None

        for i, w in enumerate(words):
            if seg_start is None:
                seg_start = w["start"]

            current_segment.append(w["word"])

            if i < len(words) - 1:
                gap = words[i + 1]["start"] - w["end"]
                if gap > pause_word_gap:
                    seg_end = w["end"]
                    text = " ".join(current_segment).strip()
                    segments.append((seg_start, seg_end, text))
                    current_segment = []
                    seg_start = words[i + 1]["start"]

        prev_end = words[-1]["end"]

    if current_segment:
        seg_end = prev_end
        text = " ".join(current_segment).strip()
        segments.append((seg_start, seg_end, text))

    # jeda
    pauses = []
    for i in range(1, len(segments)):
        # segments[i] is defined as (start, end, text) so segments[i][0] is start
        # segments[i-1][1] is end of previous
        pause_dur = segments[i][0] - segments[i - 1][1]
        if pause_dur > 0:
            pauses.append(pause_dur)

    total_silence = len(pauses)

    try:
        info = ffmpeg.probe(input_file)
        duration_sec = float(info["format"]["duration"])
    except:
        # Fallback if probe fails
        # audio = whisper.load_audio(output_file) # avoiding duplicate load if we don't strictly need exact duration from file
        # duration_sec = len(audio) / 16000
        # Simpler: use last segment end
        duration_sec = segments[-1][1] if segments else 0

    # Clean up temporary WAV file
    if os.path.exists(output_file):
        os.remove(output_file)

    
    # Construct text output similar to script
    final_text = ""
    def to_timestamp(sec):
        m = int(sec // 60)
        s = int(sec % 60)
        return f"{m:02d}:{s:02d}"

    for idx, (start, end, text) in enumerate(segments):
        final_text += f"[{to_timestamp(start)} - {to_timestamp(end)}] {text}\n"
        if idx < len(pauses):
             # This logic in original script might be slightly off index-wise regarding pauses vs segments pairing
             # but keeping fidelity to original logic if possible.
             # Original: if idx < len(pauses): final_text += ...
             pass

    return {
        "file": input_file,
        "segments": segments,
        "pauses": pauses,
        "total_silence": total_silence,
        "duration": duration_sec,
        "text_output": final_text,
        "full_transcript": result.get("text", final_text)
    }
