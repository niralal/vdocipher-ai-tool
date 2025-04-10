"""
TextProcessor: Handles grammar correction using OpenAI's GPT-4 or Groq.
This module takes SRT format subtitles and corrects only spelling/grammar mistakes
while preserving exact meaning, timing, and word choice, with special attention
to Hebrew technical and scientific content.
"""

import time
from openai import OpenAI
import groq

class TextProcessor:
    def __init__(self, openai_api_key, config=None):
        """Initialize with OpenAI API key and optional config"""
        self.openai_client = OpenAI(api_key=openai_api_key)
        if hasattr(config, 'GROQ_API_KEY') and config.GROQ_API_KEY:
            self.groq_client = groq.Groq(api_key=config.GROQ_API_KEY)
        else:
            self.groq_client = None
        self.config = config
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        # Get models from config or use defaults
        self.grammar_model = self.config.GRAMMAR_MODEL if self.config else "gpt-3.5-turbo"
        self.translation_model = self.config.TRANSLATION_MODEL if self.config else "gpt-3.5-turbo"
        self.use_groq = getattr(config, 'USE_GROQ', False)
        self.groq_model = getattr(config, 'GROQ_MODEL', 'mixtral-8x7b-32768')

    def is_srt_format(self, text):
        """Check if text follows SRT format"""
        if not text:
            return False
            
        lines = text.strip().split('\n')
        if len(lines) < 4:  # Minimum SRT entry: number, timestamp, text, blank line
            return False
            
        # Check first line is a number
        if not lines[0].isdigit():
            return False
            
        # Check second line is timestamp format
        if ' --> ' not in lines[1]:
            return False
            
        return True

    def correct_grammar(self, text):
        """
        Correct spelling and grammar mistakes in Hebrew SRT subtitles.
        Uses either Groq or OpenAI based on configuration.
        """
        try:
            chunks = self.split_srt_into_chunks(text)
            corrected_chunks = []
            
            print(f"\nUsing {'Groq' if self.use_groq else 'OpenAI'} for grammar correction")
            print(f"Model: {self.groq_model if self.use_groq else self.grammar_model}")
            
            for i, chunk in enumerate(chunks, 1):
                print(f"- Correcting grammar chunk {i}/{len(chunks)}...")
                retries = 0
                while retries < self.MAX_RETRIES:
                    try:
                        if self.use_groq and self.groq_client:
                            response = self.groq_client.chat.completions.create(
                                model=self.groq_model,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": """אתה עורך לשוני מקצועי בעברית. עליך לתקן את הטקסט תוך שמירה על פורמט SRT.

חובה לבצע את התיקונים הבאים:

1. תיקון מילים שגויות:
   - המילה "חול" כשהכוונה לחוץ לארץ חייבת להיות מתוקנת ל"חו״ל"
   - "את השלום המס" חייב להיות מתוקן ל"תשלום המס"
   - בהקשר של מחירים: "פי 0" חייב להיות "P0"

2. תיקוני דקדוק:
   - התאמת זכר/נקבה (לדוגמה: "הצעה" בהקשר כלכלי צריך להיות "היצע")
   - התאמת יחיד/רבים
   - תיקון משפטים לא תקינים

3. דוגמאות לתיקונים נדרשים:
   מקור: "המחיר בחול הוא 200 שקלים"
   תיקון: "המחיר בחו״ל הוא 200 שקלים"

   מקור: "לאחר את השלום המס"
   תיקון: "לאחר תשלום המס"

   מקור: "במחיר פי 0"
   תיקון: "במחיר P0"

חשוב:
- חובה לשמור על מספרי השורות והתזמונים המקוריים
- חובה לתקן כל שגיאת כתיב שמופיעה
- יש לשמור על המשמעות המקורית
- אם אין צורך בתיקון, החזר את הטקסט המקורי

בדוק כל שורה בקפידה ותקן את כל השגיאות שמופיעות."""
                                    },
                                    {"role": "user", "content": chunk}
                                ],
                                temperature=0.1,
                            )
                        else:
                            response = self.openai_client.chat.completions.create(
                                model=self.grammar_model,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": """אתה עורך לשוני מקצועי בעברית. עליך לתקן את הטקסט תוך שמירה על פורמט SRT.

חובה לבצע את התיקונים הבאים:

1. תיקון מילים שגויות:
   - המילה "חול" כשהכוונה לחוץ לארץ חייבת להיות מתוקנת ל"חו״ל"
   - "את השלום המס" חייב להיות מתוקן ל"תשלום המס"
   - בהקשר של מחירים: "פי 0" חייב להיות "P0"

2. תיקוני דקדוק:
   - התאמת זכר/נקבה (לדוגמה: "הצעה" בהקשר כלכלי צריך להיות "היצע")
   - התאמת יחיד/רבים
   - תיקון משפטים לא תקינים

3. דוגמאות לתיקונים נדרשים:
   מקור: "המחיר בחול הוא 200 שקלים"
   תיקון: "המחיר בחו״ל הוא 200 שקלים"

   מקור: "לאחר את השלום המס"
   תיקון: "לאחר תשלום המס"

   מקור: "במחיר פי 0"
   תיקון: "במחיר P0"

חשוב:
- חובה לשמור על מספרי השורות והתזמונים המקוריים
- חובה לתקן כל שגיאת כתיב שמופיעה
- יש לשמור על המשמעות המקורית
- אם אין צורך בתיקון, החזר את הטקסט המקורי

בדוק כל שורה בקפידה ותקן את כל השגיאות שמופיעות."""
                                    },
                                    {"role": "user", "content": chunk}
                                ],
                                temperature=0.2,
                                timeout=180
                            )
                        
                        corrected_text = response.choices[0].message.content
                        
                        # If the response is valid SRT or contains actual corrections, use it
                        if self.is_srt_format(corrected_text):
                            corrected_chunks.append(corrected_text)
                        else:
                            # If the model returned plain text without SRT formatting,
                            # it might indicate no corrections were needed
                            corrected_chunks.append(chunk)
                        break
                        
                    except Exception as e:
                        retries += 1
                        if retries < self.MAX_RETRIES:
                            print(f"Grammar correction error (attempt {retries}): {str(e)}")
                            print(f"Retrying in {self.RETRY_DELAY} seconds...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print(f"Failed to correct chunk after {self.MAX_RETRIES} attempts: {str(e)}")
                            return None
            
            # Combine chunks and fix numbering
            return self.combine_chunks(corrected_chunks)
                
        except Exception as e:
            print(f"Grammar correction failed: {str(e)}")
            return None

    def split_srt_into_chunks(self, text, chunk_size=20):
        """Split SRT file into chunks of subtitles"""
        chunks = []
        current_chunk = []
        current_size = 0
        
        entries = text.strip().split('\n\n')
        for entry in entries:
            if current_size >= chunk_size:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(entry)
            current_size += 1
            
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
        return chunks

    def fix_srt_numbering(self, text):
        """Renumber SRT entries sequentially and fix timestamp formatting"""
        if not text:
            return text
        
        entries = text.strip().split('\n\n')
        fixed_entries = []
        counter = 1
        
        for entry in entries:
            if not entry.strip():
                continue
            
            lines = entry.split('\n')
            if len(lines) >= 2:  # Valid SRT entry should have at least number and timestamp
                # Fix the entry number
                lines[0] = str(counter)
                
                # Fix timestamp formatting - remove any extra spaces
                if len(lines) > 1 and ' --> ' in lines[1]:
                    timestamp_parts = lines[1].split(' --> ')
                    if len(timestamp_parts) == 2:
                        start_time = timestamp_parts[0].strip()
                        end_time = timestamp_parts[1].strip()
                        lines[1] = f"{start_time} --> {end_time}"
                
                fixed_entries.append('\n'.join(lines))
                counter += 1
            
        return '\n\n'.join(fixed_entries)

    def combine_chunks(self, chunks):
        """Combine chunks and fix numbering"""
        combined = '\n\n'.join(chunks)
        return self.fix_srt_numbering(combined)

    def translate_to_arabic(self, text):
        """
        Translate Hebrew SRT subtitles to Arabic while preserving SRT format.
        Uses either Groq or OpenAI based on configuration.
        """
        try:
            chunks = self.split_srt_into_chunks(text)
            translated_chunks = []
            
            print(f"\nUsing {'Groq' if self.use_groq else 'OpenAI'} for Arabic translation")
            print(f"Model: {self.groq_model if self.use_groq else self.translation_model}")
            
            for i, chunk in enumerate(chunks, 1):
                print(f"- Translating chunk {i}/{len(chunks)}...")
                retries = 0
                while retries < self.MAX_RETRIES:
                    try:
                        system_prompt = """You are a professional translator from Hebrew to Arabic.

Rules:
1. Translate ONLY the text content between timestamps from Hebrew to Arabic
2. DO NOT modify any of these elements:
   - Subtitle numbers (e.g., "1", "2", "3")
   - Timestamps (e.g., "00:00:01,000 --> 00:00:05,000")
   - Line breaks position
3. Maintain technical and scientific terms accuracy
4. Keep any numbers and special characters exactly as they appear
5. Each subtitle block must maintain this exact format:

[number]
[timestamp] --> [timestamp]
[translated text]
[empty line]

Example of correct format:
1
00:00:01,000 --> 00:00:05,000
النص المترجم هنا
"""
                        if self.use_groq and self.groq_client:
                            response = self.groq_client.chat.completions.create(
                                model=self.groq_model,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": chunk}
                                ],
                                temperature=0.0,
                            )
                        else:
                            response = self.openai_client.chat.completions.create(
                                model=self.translation_model,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": chunk}
                                ],
                                temperature=0.0
                            )
                        
                        translated_text = response.choices[0].message.content.strip()
                        
                        # Verify the translation maintains SRT format
                        if self.is_srt_format(translated_text):
                            # Add timestamp validation before accepting the translation
                            if self.validate_timestamps(translated_text):
                                translated_chunks.append(translated_text)
                                break
                            else:
                                print(f"Warning: Invalid timestamps detected, retrying...")
                                retries += 1
                        else:
                            print(f"Warning: Translation returned invalid SRT format, retrying...")
                            retries += 1
                            
                    except Exception as e:
                        retries += 1
                        if retries < self.MAX_RETRIES:
                            print(f"Translation error (attempt {retries}): {str(e)}")
                            print(f"Retrying in {self.RETRY_DELAY} seconds...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print(f"Failed to translate chunk after {self.MAX_RETRIES} attempts: {str(e)}")
                            return None
            
            # Combine chunks and validate final format
            final_translation = self.combine_chunks(translated_chunks)
            if not self.validate_timestamps(final_translation):
                print("Error: Final translation contains invalid timestamps")
                return None
            
            return final_translation
                
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return None

    def validate_timestamps(self, text):
        """
        Validate that all timestamps in the SRT text are in correct format.
        """
        import re
        
        # Regular expression for SRT timestamp format
        timestamp_pattern = r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s-->\s(\d{2}):(\d{2}):(\d{2}),(\d{3})'
        
        lines = text.split('\n')
        for line in lines:
            if '-->' in line:
                # Check if the line matches the timestamp pattern
                match = re.match(timestamp_pattern, line.strip())
                if not match:
                    return False
                
                # Extract start and end times
                start_h, start_m, start_s, start_ms = map(int, match.groups()[:4])
                end_h, end_m, end_s, end_ms = map(int, match.groups()[4:])
                
                # Convert to milliseconds for comparison
                start_time = ((start_h * 3600 + start_m * 60 + start_s) * 1000) + start_ms
                end_time = ((end_h * 3600 + end_m * 60 + end_s) * 1000) + end_ms
                
                # Verify end time is after start time
                if end_time <= start_time:
                    return False
        
        return True

    def translate_to_russian(self, text):
        """
        Translate Hebrew SRT subtitles to Russian while preserving SRT format.
        Uses either Groq or OpenAI based on configuration.
        """
        try:
            chunks = self.split_srt_into_chunks(text)
            translated_chunks = []
            
            print(f"\nUsing {'Groq' if self.use_groq else 'OpenAI'} for Russian translation")
            print(f"Model: {self.groq_model if self.use_groq else self.translation_model}")
            
            for i, chunk in enumerate(chunks, 1):
                print(f"- Translating chunk {i}/{len(chunks)}...")
                retries = 0
                while retries < self.MAX_RETRIES:
                    try:
                        system_prompt = """You are a professional translator from Hebrew to Russian.

Rules:
1. Translate ONLY the text content between timestamps from Hebrew to Russian
2. DO NOT modify any of these elements:
   - Subtitle numbers (e.g., "1", "2", "3")
   - Timestamps (e.g., "00:00:01,000 --> 00:00:05,000")
   - Line breaks position
3. Maintain technical and scientific terms accuracy
4. Keep any numbers and special characters exactly as they appear
5. Each subtitle block must maintain this exact format:

[number]
[timestamp] --> [timestamp]
[translated text]
[empty line]

Example of correct format:
1
00:00:01,000 --> 00:00:05,000
Переведенный текст здесь
"""
                        if self.use_groq and self.groq_client:
                            response = self.groq_client.chat.completions.create(
                                model=self.groq_model,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": chunk}
                                ],
                                temperature=0.0,
                            )
                        else:
                            response = self.openai_client.chat.completions.create(
                                model=self.translation_model,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": chunk}
                                ],
                                temperature=0.0
                            )
                        
                        translated_text = response.choices[0].message.content.strip()
                        
                        # Verify the translation maintains SRT format
                        if self.is_srt_format(translated_text):
                            translated_chunks.append(translated_text)
                            break
                        else:
                            print(f"Warning: Translation returned invalid SRT format, retrying...")
                            retries += 1
                            
                    except Exception as e:
                        retries += 1
                        if retries < self.MAX_RETRIES:
                            print(f"Translation error (attempt {retries}): {str(e)}")
                            print(f"Retrying in {self.RETRY_DELAY} seconds...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print(f"Failed to translate chunk after {self.MAX_RETRIES} attempts: {str(e)}")
                            return None
            
            # Combine chunks and validate final format
            final_translation = self.combine_chunks(translated_chunks)
            if not self.is_srt_format(final_translation):
                print("Error: Final translation is not in valid SRT format")
                return None
            
            return final_translation
                
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return None
