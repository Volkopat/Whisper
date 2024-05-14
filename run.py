import gradio as gr
import whisper
import os
import torch
import logging
import zipfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_audio(file, model_size):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_size, device=device)
    results = []
    os.makedirs("outputs", exist_ok=True)
    
    audio_path = file.name
    logger.info(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path)
    transcription_path = os.path.join("outputs", os.path.splitext(os.path.basename(audio_path))[0] + ".txt")
    
    with open(transcription_path, "w") as text_file:
        text_file.write(result["text"])
    
    results.append(transcription_path)
    logger.info(f"Transcription complete for {audio_path}. Output saved to {transcription_path}")

    zip_filename = "transcriptions.zip"
    zip_path = os.path.join("outputs", zip_filename)
    zip_files(results, zip_path)
    logger.info(f"All transcriptions complete. ZIP file generated: {zip_path}")
    
    return zip_path

def zip_files(files, zip_path):
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for file in files:
            zip_file.write(file, arcname=os.path.basename(file))

with gr.Blocks() as demo:
    gr.Markdown("# Whisper Audio Transcription")
    gr.Markdown("Upload an audio file and select a model size to transcribe it.")
    
    with gr.Row():
        file_input = gr.File(label="Upload your audio file", type="filepath")
        model_selector = gr.Dropdown(label="Select Model Size", choices=["tiny", "base", "small", "medium", "large"], value="medium")
        submit_button = gr.Button("Transcribe")
    
    download_output = gr.File(label="Download Processed Files", type="filepath")

    submit_button.click(fn=transcribe_audio, inputs=[file_input, model_selector], outputs=download_output)

demo.launch(server_name="0.0.0.0", server_port=7860)
