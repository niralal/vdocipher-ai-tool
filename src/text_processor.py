"""
TextProcessor: Handles grammar correction using OpenAI's GPT-4.
This module takes SRT format subtitles and corrects only spelling/grammar mistakes
while preserving exact meaning, timing, and word choice, with special attention
to Hebrew technical and scientific content.
"""

import time
from openai import OpenAI

class TextProcessor:
    def __init__(self, openai_api_key, config=None):
        """Initialize with OpenAI API key and optional config"""
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.config = config
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        # Get models from config or use defaults
        self.grammar_model = self.config.GRAMMAR_MODEL if self.config else "gpt-3.5-turbo"
        self.translation_model = self.config.TRANSLATION_MODEL if self.config else "gpt-3.5-turbo"

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
        Handles large files by splitting into chunks.
        """
        try:
            chunks = self.split_srt_into_chunks(text)
            corrected_chunks = []
            
            for i, chunk in enumerate(chunks, 1):
                print(f"- Correcting grammar chunk {i}/{len(chunks)}...")
                retries = 0
                while retries < self.MAX_RETRIES:
                    try:
                        response = self.openai_client.chat.completions.create(
                            model=self.grammar_model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": """אתה עורך לשוני מומחה בעברית, המתמחה בתיקון טקסט מדעי וטכני.

הנחיות לתיקון:

1. תיקוני דקדוק ותחביר:
   - תיקון התאמת זכר/נקבה
   - תיקון התאמת יחיד/רבים
   - תיקון שגיאות כתיב נפוצות
   - תיקון משפטים לא תקינים תחבירית

2. תיקונים ספציפיים:
   - "בשביל ש" → "כדי ש"
   - "על מנת" → "כדי"
   - "מה ש" → "מה ש" (לוודא רווח)
   - "אנחנו" בתחילת משפט → "אנו"
   - "בגלל ש" → "מפני ש" / "משום ש"
   - "חול" → "חו״ל" (כשמדובר על חוץ לארץ)

3. תיקון מונחים מקצועיים:
   - "הצעה" → "היצע" (בהקשר כלכלי)
   - "ביקוש" ו"היצע" הם בזכר
   - לתקן מונחים טכניים ומדעיים שגויים

4. כללי זהב:
   - אין לשנות את המשמעות
   - אין לשנות מספרי שורות או זמנים
   - לשמור על סגנון הדיבור של המרצה
   - לתקן רק טעויות ברורות
   - להשאיר ביטויים יומיומיים

אם אין טעויות - החזר בדיוק את אותו טקסט."""
                                },
                                {"role": "user", "content": chunk}
                            ],
                            temperature=0.0,
                            timeout=180  # 3 minutes per chunk
                        )
                        corrected_text = response.choices[0].message.content
                        
                        # Check if this chunk needs corrections
                        if not self.is_srt_format(corrected_text):
                            corrected_chunks.append(chunk)  # Use original if no corrections needed
                        else:
                            corrected_chunks.append(corrected_text)
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
        """Renumber SRT entries sequentially"""
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
                lines[0] = str(counter)  # Replace number with sequential counter
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
        Handles large files by splitting into chunks.
        """
        try:
            chunks = self.split_srt_into_chunks(text)
            translated_chunks = []
            
            for i, chunk in enumerate(chunks, 1):
                print(f"- Translating chunk {i}/{len(chunks)}...")
                retries = 0
                while retries < self.MAX_RETRIES:
                    try:
                        response = self.openai_client.chat.completions.create(
                            model=self.translation_model,
                            messages=[
                                {
                                    "role": "system", 
                                    "content": """You are a professional translator from Hebrew to Arabic.

Rules:
1. Translate the text between timestamps from Hebrew to Arabic
2. Keep all SRT formatting exactly the same:
   - Keep subtitle numbers
   - Keep timestamps exactly as they are
   - Keep line breaks in the same places
3. Maintain technical and scientific terms accuracy
4. Keep any numbers and special characters
5. Do not change or translate timestamps"""
                                },
                                {"role": "user", "content": chunk}
                            ],
                            temperature=0.0,
                            timeout=180  # 3 minutes per chunk
                        )
                        translated_chunks.append(response.choices[0].message.content)
                        break
                    except Exception as e:
                        retries += 1
                        if retries < self.MAX_RETRIES:
                            print(f"Translation error (attempt {retries}): {str(e)}")
                            print(f"Retrying in {self.RETRY_DELAY} seconds...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print(f"Failed to translate chunk after {self.MAX_RETRIES} attempts: {str(e)}")
                            return None
            
            # Combine chunks and fix numbering
            return self.combine_chunks(translated_chunks)
                
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return None

    def translate_to_russian(self, text):
        """
        Translate Hebrew SRT subtitles to Russian while preserving SRT format.
        Handles large files by splitting into chunks.
        """
        try:
            chunks = self.split_srt_into_chunks(text)
            translated_chunks = []
            
            for i, chunk in enumerate(chunks, 1):
                print(f"- Translating chunk {i}/{len(chunks)}...")
                retries = 0
                while retries < self.MAX_RETRIES:
                    try:
                        response = self.openai_client.chat.completions.create(
                            model=self.translation_model,
                            messages=[
                                {
                                    "role": "system", 
                                    "content": """You are a professional translator from Hebrew to Russian.

Rules:
1. Translate the text between timestamps from Hebrew to Russian
2. Keep all SRT formatting exactly the same:
   - Keep subtitle numbers
   - Keep timestamps exactly as they are
   - Keep line breaks in the same places
3. Maintain technical and scientific terms accuracy
4. Keep any numbers and special characters
5. Do not change or translate timestamps"""
                                },
                                {"role": "user", "content": chunk}
                            ],
                            temperature=0.0,
                            timeout=180  # 3 minutes per chunk
                        )
                        translated_chunks.append(response.choices[0].message.content)
                        break
                    except Exception as e:
                        retries += 1
                        if retries < self.MAX_RETRIES:
                            print(f"Translation error (attempt {retries}): {str(e)}")
                            print(f"Retrying in {self.RETRY_DELAY} seconds...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print(f"Failed to translate chunk after {self.MAX_RETRIES} attempts: {str(e)}")
                            return None
            
            # Combine chunks and fix numbering
            return self.combine_chunks(translated_chunks)
                
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return None
