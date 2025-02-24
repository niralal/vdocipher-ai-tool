"""
SubtitleGenerator: Main class for handling the subtitle generation workflow.
Supports processing multiple videos from a CSV file.
"""

from src.config import Config
from src.vdocipher_client import VdoCipherClient
from src.media_processor import MediaProcessor
from src.text_processor import TextProcessor
import os
import tempfile
import csv

class SubtitleGenerator:
    def __init__(self):
        """Initialize with configuration and required clients"""
        self.config = Config()
        self.vdo_client = VdoCipherClient(self.config.VDOCIPHER_API_KEY)
        self.media_processor = MediaProcessor(
            openai_api_key=self.config.OPENAI_API_KEY,
            config=self.config  # Pass the config here
        )
        self.text_processor = TextProcessor(self.config.OPENAI_API_KEY, self.config)
        # Use the same tmp directory as MediaProcessor
        self.tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp")

    def process_videos_from_csv(self, csv_path):
        """Process multiple videos listed in a CSV file"""
        results = []
        
        try:
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    video_id = row.get('video_id')
                    if not video_id:
                        print(f"Skipping row - no video_id found: {row}")
                        continue
                        
                    print(f"\nProcessing video: {video_id}")
                    success = self.process_video(video_id)
                    results.append({
                        'video_id': video_id,
                        'status': 'success' if success else 'failed'
                    })
                    
            # Save results to CSV
            output_path = os.path.join(self.tmp_dir, 'processing_results.csv')
            with open(output_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['video_id', 'status'])
                writer.writeheader()
                writer.writerows(results)
                
            print(f"\nResults saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error processing videos from CSV: {str(e)}")
            return False

    def process_video(self, video_id):
        """
        Process a video to generate and upload subtitles.
        
        Args:
            video_id (str): The VdoCipher video ID to process
            
        Returns:
            bool: True if successful, False otherwise
            
        Steps:
        1. Get video information from VdoCipher
        2. Delete existing subtitles
        3. Find the original file with audio
        4. Download the audio
        5. Generate transcription using Whisper
        6. Correct grammar using GPT-4
        7. Upload corrected subtitles back to VdoCipher
        """
        try:
            print(f"\nProcessing video: {video_id}")
            print("1/5: Getting video info...")
            video_info = self.vdo_client.get_video_info(video_id)
            
            # Delete existing subtitles
            print("2/5: Removing existing subtitles...")
            self.vdo_client.delete_subtitles(video_id)
            
            # Find audio URL
            print("3/5: Finding audio stream...")
            file_url = None
            if isinstance(video_info, list):
                for item in video_info:
                    if (item.get('encryption_type') == 'original' and 
                        item.get('audio_codec') == 'aac' and 
                        item.get('isDownloadable')):
                        file_url = self.vdo_client.get_download_url(video_id, item['id'])
                        break
            else:
                for stream in video_info.get("HLS_Stream", {}).get("params", {}).get("streams", []):
                    if stream.get("contentType") == "audio":
                        file_url = stream.get("url")
                        break

            if not file_url:
                raise ValueError("No audio stream found")

            # Get transcription
            print("4/5: Downloading and transcribing audio...")
            downloaded_path = self.vdo_client.download_file(
                file_url,
                os.path.join(self.tmp_dir, f"{video_id}.mp3")
            )
            
            original_text = self.media_processor.transcribe_audio(
                downloaded_path,
                language=self.config.LANGUAGE
            )

            # Save original transcription
            original_path = os.path.join(self.tmp_dir, f"{video_id}_original.srt")
            with open(original_path, "w", encoding="utf-8") as file:
                file.write(original_text)
            print("- Original transcription saved")

            # Grammar correction (if enabled)
            if self.config.ENABLE_GRAMMAR_CORRECTION:
                print("- Correcting Hebrew grammar...")
                corrected_text = self.text_processor.correct_grammar(original_text)
                
                if corrected_text is None:
                    print("- No grammar corrections needed")
                    hebrew_path = original_path
                else:
                    hebrew_path = os.path.join(self.tmp_dir, f"{video_id}_he.srt")
                    with open(hebrew_path, "w", encoding="utf-8") as file:
                        file.write(corrected_text)
                    print("- Grammar corrections saved")
            else:
                print("- Grammar correction disabled, using original transcription")
                hebrew_path = original_path

            # Handle Arabic translation if enabled
            arabic_success = True
            if self.config.ENABLE_ARABIC_TRANSLATION:
                print("- Translating to Arabic...")
                arabic_text = self.text_processor.translate_to_arabic(original_text)
                if arabic_text:
                    arabic_path = os.path.join(self.tmp_dir, f"{video_id}_ar.srt")
                    with open(arabic_path, "w", encoding="utf-8") as file:
                        file.write(arabic_text)
                    print("- Arabic translation saved")
                    arabic_success = self.vdo_client.upload_subtitle(video_id, arabic_path, "ar")
                else:
                    print("- Arabic translation failed")
                    arabic_success = False

            # Handle Russian translation if enabled
            russian_success = True
            if self.config.ENABLE_RUSSIAN_TRANSLATION:
                print("- Translating to Russian...")
                russian_text = self.text_processor.translate_to_russian(original_text)
                if russian_text:
                    russian_path = os.path.join(self.tmp_dir, f"{video_id}_ru.srt")
                    with open(russian_path, "w", encoding="utf-8") as file:
                        file.write(russian_text)
                    print("- Russian translation saved")
                    russian_success = self.vdo_client.upload_subtitle(video_id, russian_path, "ru")
                else:
                    print("- Russian translation failed")
                    russian_success = False

            # Upload Hebrew subtitles to VdoCipher
            hebrew_success = self.vdo_client.upload_subtitle(video_id, hebrew_path, "he")
            
            # Upload Hebrew subtitles to Baumann API
            baumann_success = self.vdo_client.upload_hebrew_captions_to_baumann(video_id, hebrew_path)
            
            # Handle Arabic and Russian translations...
            
            if hebrew_success and arabic_success and russian_success and baumann_success:
                print("✓ All processing completed successfully")
            else:
                print("✗ Some operations failed")
            
            return hebrew_success and arabic_success and russian_success and baumann_success
            
        except Exception as e:
            print(f"✗ Error processing video: {str(e)}")
            return False
