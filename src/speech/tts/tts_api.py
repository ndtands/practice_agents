import tempfile
import time
from pathlib import Path
from typing import Optional
import numpy as np
import soundfile as sf
import torch
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dia.model import Dia

app = FastAPI(title="Nari Text-to-Speech API")

# Load Nari model and config
print("Loading Dia-1.6B model...")
try:
    model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")
except Exception as e:
    print(f"Error loading Nari model: {e}")
    raise

class GenerationParams(BaseModel):
    max_new_tokens: int = 3072
    cfg_scale: float = 3.0
    temperature: float = 1.3
    top_p: float = 0.95
    cfg_filter_top_k: int = 30
    speed_factor: float = 0.94

@app.post("/generate_audio/", response_class=FileResponse)
async def generate_audio(
    text_input: str = Form(...),
    audio_prompt: Optional[UploadFile] = File(None),
    max_new_tokens: int = Form(3072),
    cfg_scale: float = Form(3.0),
    temperature: float = Form(1.3),
    top_p: float = Form(0.95),
    cfg_filter_top_k: int = Form(30),
    speed_factor: float = Form(0.94)
):
    """
    Generate audio from text input and optional audio prompt using the Nari model.
    Returns the generated audio as a WAV file.
    """
    if not text_input or text_input.isspace():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    temp_txt_file_path = None
    temp_audio_prompt_path = None
    output_audio = (44100, np.zeros(1, dtype=np.float32))

    try:
        prompt_path_for_generate = None
        if audio_prompt is not None:
            # Read and process audio prompt
            audio_content = await audio_prompt.read()
            if not audio_content:
                print("Warning: Audio prompt is empty, ignoring prompt.")
            else:
                # Save audio prompt to temporary file
                with tempfile.NamedTemporaryFile(mode="wb", suffix=".wav", delete=False) as f_audio:
                    temp_audio_prompt_path = f_audio.name
                    f_audio.write(audio_content)

                # Load audio using soundfile
                audio_data, sr = sf.read(temp_audio_prompt_path, dtype='float32')

                # Check if audio_data is valid
                if audio_data.size == 0 or audio_data.max() == 0:
                    print("Warning: Audio prompt seems empty or silent, ignoring prompt.")
                else:
                    # Ensure mono
                    if audio_data.ndim > 1:
                        audio_data = np.mean(audio_data, axis=1 if audio_data.shape[1] in [1, 2] else 0)
                        audio_data = np.ascontiguousarray(audio_data)
                    sf.write(temp_audio_prompt_path, audio_data, sr, subtype="FLOAT")
                    prompt_path_for_generate = temp_audio_prompt_path
                    print(f"Created temporary audio prompt file: {temp_audio_prompt_path} (orig sr: {sr})")

        # Run Generation
        start_time = time.time()
        with torch.inference_mode():
            output_audio_np = model.generate(
                text_input,
                max_tokens=max_new_tokens,
                cfg_scale=cfg_scale,
                temperature=temperature,
                top_p=top_p,
                cfg_filter_top_k=cfg_filter_top_k,
                use_torch_compile=False,
                audio_prompt=prompt_path_for_generate,
            )
        end_time = time.time()
        print(f"Generation finished in {end_time - start_time:.2f} seconds.")

        # Convert Codes to Audio
        if output_audio_np is not None:
            output_sr = 44100
            # Slow down audio
            original_len = len(output_audio_np)
            speed_factor = max(0.1, min(speed_factor, 5.0))
            target_len = int(original_len / speed_factor)
            if target_len != original_len and target_len > 0:
                x_original = np.arange(original_len)
                x_resampled = np.linspace(0, original_len - 1, target_len)
                resampled_audio_np = np.interp(x_resampled, x_original, output_audio_np)
                output_audio = (output_sr, resampled_audio_np.astype(np.float32))
                print(f"Resampled audio from {original_len} to {target_len} samples for {speed_factor:.2f}x speed.")
            else:
                output_audio = (output_sr, output_audio_np)
                print(f"Skipping audio speed adjustment (factor: {speed_factor:.2f}).")

            # Convert to int16 for compatibility
            if output_audio[1].dtype in [np.float32, np.float64]:
                audio_for_output = np.clip(output_audio[1], -1.0, 1.0)
                audio_for_output = (audio_for_output * 32767).astype(np.int16)
                output_audio = (output_sr, audio_for_output)
                print("Converted audio to int16 for output.")

        else:
            print("Generation finished, but no valid tokens were produced.")
            raise HTTPException(status_code=500, detail="Generation produced no output.")

        # Save output audio to temporary file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".wav", delete=False) as f_output:
            temp_output_path = f_output.name
            sf.write(temp_output_path, output_audio[1], output_audio[0], subtype="PCM_16")
            print(f"Saved generated audio to: {temp_output_path}")

        return FileResponse(
            temp_output_path,
            media_type="audio/wav",
            filename="generated_audio.wav"
        )

    except Exception as e:
        print(f"Error during inference: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    finally:
        # Cleanup temporary files
        for temp_path in [temp_txt_file_path, temp_audio_prompt_path]:
            if temp_path and Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                    print(f"Deleted temporary file: {temp_path}")
                except OSError as e:
                    print(f"Warning: Error deleting temporary file {temp_path}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)