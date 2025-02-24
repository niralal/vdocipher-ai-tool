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

    def process_srt(self, text):
        """Post-process SRT to enforce line length and timing rules"""
        lines = text.split('\n')
        processed_lines = []
        current_block = []
        block_number = 1

        for line in lines:
            # Handle timestamp lines
            if '-->' in line:
                # Fix timestamp format - remove any extra numbers after milliseconds
                timestamps = line.split(' --> ')
                if len(timestamps) == 2:
                    start_time = timestamps[0].split(',')[0] + ',' + timestamps[0].split(',')[1][:3]
                    end_time = timestamps[1].split(',')[0] + ',' + timestamps[1].split(',')[1][:3]
                    line = f"{start_time} --> {end_time}"

            if line.strip().isdigit():  # New subtitle block
                if current_block:
                    processed_lines.extend(self.format_block(current_block, block_number))
                    block_number += 1
                    current_block = []
            current_block.append(line)

        # Process last block
        if current_block:
            processed_lines.extend(self.format_block(current_block, block_number))

        return '\n'.join(processed_lines)

    def format_block(self, block, number):
        """Format a subtitle block to match our rules"""
        if len(block) < 3:  # Invalid block
            return block

        timing = block[1]
        text_lines = block[2:]
        text = ' '.join(line.strip() for line in text_lines if line.strip())
        
        # Split into chunks of max 10 words
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= 10:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        # Format the block
        formatted_block = [
            str(number),
            timing
        ]
        formatted_block.extend(chunks)
        formatted_block.append('')  # Empty line between blocks
        
        return formatted_block

    def transcribe_audio(self, audio_path, model="medium", language="he", output_format="srt"):
        """Transcribe audio file and post-process the output"""
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
                    temperature=0.0
                )
            
            # Post-process the transcription
            processed_transcript = self.process_srt(transcript)
            
            # Return the processed transcript without saving
            return processed_transcript
            
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None
