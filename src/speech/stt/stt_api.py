import nemo.collections.asr as nemo_asr
import numpy as np
import soundfile as sf
import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import io
import os
from typing import Optional

app = FastAPI(title="Parakeet-TDT-0.6b-v2 API")

# Load the Parakeet model (ensure GPU is available if possible)
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v2")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
asr_model = asr_model.to(device)
asr_model.eval()

def process_audio(audio_file: UploadFile) -> tuple:
    """
    Process the uploaded audio file and return transcription with timestamps.
    """
    # Read audio file
    audio_data, sample_rate = sf.read(io.BytesIO(audio_file.file.read()))

    # Ensure mono channel
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)

    # Resample to 16kHz if necessary
    if sample_rate != 16000:
        from scipy import signal
        audio_data = signal.resample(audio_data, int(len(audio_data) * 16000 / sample_rate))
        sample_rate = 16000

    # Save audio to temporary file for NeMo processing
    temp_audio_path = "temp_audio.wav"
    sf.write(temp_audio_path, audio_data, sample_rate)

    # Transcribe audio
    with torch.no_grad():
        output = asr_model.transcribe([temp_audio_path], timestamps=True)

    # Clean up temporary file
    os.remove(temp_audio_path)

    # Extract transcription and timestamps
    transcription = output[0].text
    word_timestamps = output[0].timestamp['word']
    segment_timestamps = output[0].timestamp['segment']

    return transcription, word_timestamps, segment_timestamps

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...), output_format: Optional[str] = "text"):
    """
    Endpoint to transcribe audio files.
    - Accepts WAV or FLAC audio files.
    - Returns transcription in text, CSV, or SRT format.
    """
    # Validate file extension
    if not file.filename.lower().endswith((".wav", ".flac")):
        return JSONResponse(
            status_code=400,
            content={"error": "Only WAV or FLAC files are supported."}
        )

    try:
        transcription, word_timestamps, segment_timestamps = process_audio(file)

        if output_format.lower() == "csv":
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["start", "end", "word"])
            for stamp in word_timestamps:
                writer.writerow([stamp['start'], stamp['end'], stamp['word']])
            result = output.getvalue()
            output.close()
            return {"transcription": transcription, "csv": result}

        elif output_format.lower() == "srt":
            srt_output = ""
            for i, stamp in enumerate(segment_timestamps, 1):
                start_time = stamp['start']
                end_time = stamp['end']
                start_srt = f"{int(start_time // 3600):02d}:{int(start_time % 3600 // 60):02d}:{start_time % 60:06.3f}".replace(".", ",")
                end_srt = f"{int(end_time // 3600):02d}:{int(end_time % 3600 // 60):02d}:{end_time % 60:06.3f}".replace(".", ",")
                srt_output += f"{i}\n{start_srt} --> {end_srt}\n{stamp['segment']}\n\n"
            return {"transcription": transcription, "srt": srt_output}

        else:
            return {"transcription": transcription, "word_timestamps": word_timestamps}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Transcription failed: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)