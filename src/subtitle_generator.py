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
        completed_videos = set()
        
        try:
            # First load existing results if any
            results_path = os.path.join(self.tmp_dir, 'processing_results.csv')
            try:
                with open(results_path, 'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Only add to results if it has all required fields
                        if all(key in row for key in ['video_id', 'sent_to_baumann', 'ru_translated', 'ar_translated', 'vdocipher_uploaded']):
                            results.append(row)
                            if row.get('vdocipher_uploaded', '').lower() == 'true':
                                completed_videos.add(row['video_id'])
            except (FileNotFoundError, KeyError):
                # Either file doesn't exist or has wrong format - start fresh
                results = []
                completed_videos = set()

            # Read video IDs from CSV
            video_ids = []
            with open(csv_path, 'r') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header if exists
                for row in reader:
                    if row and row[0]:  # Check if row exists and has an ID
                        video_ids.append(row[0].strip())

            # Process each video that hasn't been completed
            for video_id in video_ids:
                if video_id in completed_videos:
                    print(f"\nSkipping video {video_id} - already processed")
                    continue
                    
                print(f"\nProcessing video: {video_id}")
                success, status = self.process_video(video_id)
                
                # Update or add result
                result = {
                    'video_id': video_id,
                    'sent_to_baumann': str(status.get('baumann', False)).lower(),
                    'ru_translated': str(status.get('russian', False)).lower(),
                    'ar_translated': str(status.get('arabic', False)).lower(),
                    'vdocipher_uploaded': str(status.get('vdocipher', False)).lower()
                }
                
                # Remove old result if exists
                results = [r for r in results if r['video_id'] != video_id]
                results.append(result)
                    
                # Save results after each video
                with open(results_path, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=[
                        'video_id', 'sent_to_baumann', 'ru_translated', 
                        'ar_translated', 'vdocipher_uploaded'
                    ])
                    writer.writeheader()
                    writer.writerows(results)
                
            print(f"\nAll results saved to: {results_path}")
            return True
            
        except Exception as e:
            print(f"Error processing videos from CSV: {str(e)}")
            return False

    def process_video(self, video_id):
        """Process a video and return success status for each operation"""
        status = {
            'baumann': False,
            'russian': False,
            'arabic': False,
            'vdocipher': False
        }
        
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
                
                if corrected_text is None or not self.text_processor.is_srt_format(corrected_text):
                    print("- Using original text (no valid corrections)")
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
            if self.config.ENABLE_ARABIC_TRANSLATION:
                print("- Translating to Arabic...")
                arabic_text = self.text_processor.translate_to_arabic(original_text)
                if arabic_text:
                    arabic_path = os.path.join(self.tmp_dir, f"{video_id}_ar.srt")
                    with open(arabic_path, "w", encoding="utf-8") as file:
                        file.write(arabic_text)
                    print("- Arabic translation saved")
                    status['arabic'] = self.vdo_client.upload_subtitle(video_id, arabic_path, "ar")
                else:
                    print("- Arabic translation failed")

            # Handle Russian translation if enabled
            if self.config.ENABLE_RUSSIAN_TRANSLATION:
                print("- Translating to Russian...")
                russian_text = self.text_processor.translate_to_russian(original_text)
                if russian_text:
                    russian_path = os.path.join(self.tmp_dir, f"{video_id}_ru.srt")
                    with open(russian_path, "w", encoding="utf-8") as file:
                        file.write(russian_text)
                    print("- Russian translation saved")
                    status['russian'] = self.vdo_client.upload_subtitle(video_id, russian_path, "ru")
                else:
                    print("- Russian translation failed")

            # Upload Hebrew subtitles
            status['vdocipher'] = self.vdo_client.upload_subtitle(video_id, hebrew_path, "he")
            
            # Upload to Baumann API
            status['baumann'] = self.vdo_client.upload_hebrew_captions_to_baumann(video_id, hebrew_path)
            
            if all(status.values()):
                print("✓ All processing completed successfully")
            else:
                print("✗ Some operations failed")
                failed = [k for k, v in status.items() if not v]
                print(f"  Failed operations: {', '.join(failed)}")
            
            # Update results file
            self._update_results_file(video_id, status)
            
            return all(status.values()), status
            
        except Exception as e:
            print(f"✗ Error processing video: {str(e)}")
            # Update results file even in case of error
            self._update_results_file(video_id, status)
            return False, status

    def _update_results_file(self, video_id, status):
        """Update the results CSV file with the current video status"""
        results_path = os.path.join(self.tmp_dir, 'processing_results.csv')
        
        # Create tmp directory if it doesn't exist
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        
        # Read existing results
        results = []
        try:
            if os.path.exists(results_path):
                with open(results_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Keep all rows that don't relate to the current video
                        if row.get('video_id') != video_id:
                            results.append(row)
        except Exception as e:
            print(f"Warning: Error reading results file: {str(e)}")
        
        # Add the new result
        result = {
            'video_id': video_id,
            'sent_to_baumann': str(status.get('baumann', False)).lower(),
            'ru_translated': str(status.get('russian', False)).lower(),
            'ar_translated': str(status.get('arabic', False)).lower(),
            'vdocipher_uploaded': str(status.get('vdocipher', False)).lower()
        }
        results.append(result)
        
        # Write the file
        try:
            with open(results_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['video_id', 'sent_to_baumann', 'ru_translated', 
                             'ar_translated', 'vdocipher_uploaded']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
                
            # Flush buffer to disk
            file.flush()
            os.fsync(file.fileno())
            
            print(f"✓ Updated results file for video {video_id}")
        except Exception as e:
            print(f"✗ Error updating results file: {str(e)}")
