"""
TextProcessor: Handles grammar correction using OpenAI's GPT-4.
This module takes SRT format subtitles and corrects only spelling/grammar mistakes
while preserving exact meaning, timing, and word choice, with special attention
to Hebrew technical and scientific content.
"""

import time
from openai import OpenAI

class TextProcessor:
    def __init__(self, openai_api_key):
        """Initialize with OpenAI API key"""
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5  # seconds

    def correct_grammar(self, text):
        """
        Correct spelling and grammar mistakes in Hebrew SRT subtitles.
        Returns the original text if no corrections are needed.
        """
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                print(f"Starting grammar correction with GPT-3.5 (attempt {retries + 1}/{self.MAX_RETRIES})...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": """אתה עורך כתוביות המתמחה בתיקון טקסט מדעי וטכני בעברית.

כללים חשובים:
1. תקן מונחים טכניים ומדעיים שגויים שנובעים מטעויות הקלטה, לדוגמה:
   - "צד חשמלי" → "שדה חשמלי"
   
2. תקן שגיאות דקדוק ואיות ברורות:
   - "צרייך" → "צריך"
   - "אנחנו רוצה" → "אנחנו רוצים"

3. אם אין טעויות לתיקון, החזר את הטקסט המקורי בדיוק כפי שהוא

4. אל תשנה:
   - מונחים טכניים נכונים
   - מבנה משפטים תקין
   - סגנון דיבור
   - קודי זמן ומבנה שורות"""
                        },
                        {"role": "user", "content": text}
                    ],
                    temperature=0.0,
                    timeout=30
                )
                
                corrected_text = response.choices[0].message.content
                
                # If we got the confirmation message, return original text
                if "הכתוביות נכתבו באופן תקין" in corrected_text:
                    print("No corrections needed, keeping original text")
                    return text
                
                return corrected_text
                
            except Exception as e:
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Error (attempt {retries}): {str(e)}")
                    print(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    print(f"Failed after {self.MAX_RETRIES} attempts. Using original text.")
                    return text

    def translate_to_arabic(self, text):
        """
        Translate Hebrew SRT subtitles to Arabic while preserving SRT format.
        Includes retry logic and better timeout handling.
        """
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                print(f"Starting Arabic translation with GPT-3.5 (attempt {retries + 1}/{self.MAX_RETRIES})...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
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
5. Do not change or translate timestamps

Example Input:
1
00:00:01,000 --> 00:00:04,000
זהו משפט בעברית
עם שתי שורות

Example Output:
1
00:00:01,000 --> 00:00:04,000
هذه جملة بالعبرية
مع سطرين"""
                        },
                        {"role": "user", "content": text}
                    ],
                    temperature=0.0,
                    timeout=60  # Increased timeout for longer content
                )
                return response.choices[0].message.content
                
            except Exception as e:
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Translation error (attempt {retries}): {str(e)}")
                    print(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    print(f"Failed to translate after {self.MAX_RETRIES} attempts: {str(e)}")
                    return None

    def translate_to_russian(self, text):
        """
        Translate Hebrew SRT subtitles to Russian while preserving SRT format.
        Includes retry logic and better timeout handling.
        """
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                print(f"Starting Russian translation with GPT-3.5 (attempt {retries + 1}/{self.MAX_RETRIES})...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
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
5. Do not change or translate timestamps

Example Input:
1
00:00:01,000 --> 00:00:04,000
זהו משפט בעברית
עם שתי שורות

Example Output:
1
00:00:01,000 --> 00:00:04,000
Это предложение на иврите
с двумя строками"""
                        },
                        {"role": "user", "content": text}
                    ],
                    temperature=0.0,
                    timeout=60
                )
                return response.choices[0].message.content
                
            except Exception as e:
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Translation error (attempt {retries}): {str(e)}")
                    print(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    print(f"Failed to translate after {self.MAX_RETRIES} attempts: {str(e)}")
                    return None
