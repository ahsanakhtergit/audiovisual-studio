import os
# Set the path to the ImageMagick binary
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

import ffmpeg
import vosk
import json
import wave
import cv2
import numpy as np
import os
from moviepy.editor import VideoFileClip

def extract_audio(video_path, audio_path):
    """Extract audio from the video."""
    ffmpeg.input(video_path).output(audio_path, acodec='pcm_s16le', ar='16000').run(overwrite_output=True)

def transcribe_audio_vosk(audio_path, model_path="models/vosk-model-small-en-us-0.15"): 
    """Transcribe the audio using Vosk and get timestamps."""
    wf = wave.open(audio_path, "rb")
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, wf.getframerate())
    recognizer.SetWords(True)
    
    transcript = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if 'result' in result:
                transcript.extend(result['result'])
    
    wf.close()
    return transcript

def generate_video_with_highlights(video_path, transcript, output_path="output.mp4"):
    """Overlay highlighted words onto the video using OpenCV."""
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        current_time = frame_count / fps
        for word_data in transcript:
            start_time, end_time, text = word_data['start'], word_data['end'], word_data['word']
            if start_time <= current_time <= end_time:
                cv2.putText(frame, text, (50, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3, cv2.LINE_AA)
                break
        
        out.write(frame)
        frame_count += 1
        
        if frame_count % 100 == 0:
            print(f"Processing: {frame_count}/{total_frames} frames")
    
    cap.release()
    out.release()
    print("Video processing complete.")
    return output_path

# Example usage
video_file = "input.mp4"
audio_file = "audio.wav"
extract_audio(video_file, audio_file)
transcription = transcribe_audio_vosk(audio_file)
final_video = generate_video_with_highlights(video_file, transcription)
print(f"Processed video saved as {final_video}")
