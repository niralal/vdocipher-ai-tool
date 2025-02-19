"""
MediaProcessor: Handles audio transcription using OpenAI's Whisper API.
Includes handling of large audio files by reducing quality.
"""

from openai import OpenAI
import os
import shutil

class MediaProcessor:
    def __init__(self, openai_api_key, config=None):
        """Initialize with OpenAI API key and optional config"""
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.MAX_SIZE = 24 * 1024 * 1024  # 24MB limit for Whisper API
        self.config = config
        
        # Create tmp directory in project root
        self.tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp")
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        print(f"Using project tmp directory: {self.tmp_dir}")

    def reduce_audio_quality(self, audio_path):
        """Reduce audio quality to decrease file size and processing time"""
        try:
            temp_filename = os.path.basename(audio_path).replace(".mp3", "_reduced.mp3")
            temp_path = os.path.join(self.tmp_dir, temp_filename)
            
            print(f"Reducing audio quality, saving to: {temp_path}")
            
            # More aggressive quality reduction
            os.system(f'ffmpeg -i "{audio_path}" -ac 1 -ar 16000 -b:a 24k "{temp_path}"')
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) < self.MAX_SIZE:
                return temp_path
                
            print("Failed to reduce file size sufficiently")
            return None
            
        except Exception as e:
            print(f"Error reducing audio quality: {str(e)}")
            return None

    def transcribe_audio(self, audio_path, model="medium", language="he", output_format="srt"):
        """Transcribe audio file, reducing quality if file is too large"""
        try:
            # File is already in /tmp, no need to copy
            file_size = os.path.getsize(audio_path)
            working_file = audio_path
            
            if file_size > self.MAX_SIZE:
                print(f"File too large ({file_size/1024/1024:.1f}MB), reducing quality...")
                reduced_path = self.reduce_audio_quality(working_file)
                if not reduced_path:
                    return None
                working_file = reduced_path
            
            print("Starting transcription with Whisper...")
            with open(working_file, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.config.WHISPER_MODEL if self.config else "whisper-1",
                    language=language,
                    response_format="srt",
                    temperature=0.0,
                    prompt="זהו תוכן טכני ומדעי בעברית. יש להקפיד על דיוק בתעתוק מונחים מתמטיים ומדעיים. יש לחלק משפטים ארוכים לחלקים של עד 10 מילים כל אחד."
                )
            
            # Save transcription
            srt_filename = os.path.basename(audio_path).replace(".mp3", ".srt")
            output_path = os.path.join(self.tmp_dir, srt_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            
            print(f"Saved transcription to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None
