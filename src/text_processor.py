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

    def correct_grammar(self, text):
        """
        Correct spelling and grammar mistakes in Hebrew SRT subtitles.
        Returns the original text if no corrections are needed.
        """
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                print(f"Starting grammar correction with {self.grammar_model} (attempt {retries + 1}/{self.MAX_RETRIES})...")
                response = self.openai_client.chat.completions.create(
                    model=self.grammar_model,
                    messages=[
                        {
                            "role": "system", 
                            "content": """אתה עורך כתוביות המתמחה בתיקון טקסט מדעי וטכני בעברית, עבור קורסי למידה לסטודנטים.

חשוב מאוד: יש לתקן אך ורק את הטעויות בהתאם להנחיות שלהלן.  
מטרת העריכה היא להבטיח דיוק מדעי, טכני ולשוני, תוך התאמה לתוכן שנאמר.  
יש לשמור על נאמנות מלאה למקור ולמונחים מקצועיים, אך ניתן לבצע התאמות לשיפור הבהירות במקרים נחוצים.  

חשוב ביותר: 
1. אין לשנות בשום אופן את מספרי השורות או את חותמות הזמן (timestamps).
2. חובה להחליף את המילה "חול" ל-"חו״ל" בכל מקום שמדובר על חוץ לארץ, במיוחד כשמדובר על:
   - ייצוא לחול → ייצוא לחו״ל
   - מחיר בחול → מחיר בחו״ל
   - שוק חול → שוק חו״ל

---

1. תיקון מונחים מדעיים, טכניים וכלכליים:  
   - יש לוודא שימוש נכון במונחים מקצועיים בהתאם לתחום התוכן.  
   - מונחים כלכליים:  
     - "הצעה" → "היצע" (רק כאשר מדובר במשמעות הכלכלית של היצע וביקוש).  
     - "ההצעה נותרת" → "ההיצע נותר".  
     - "הצעת שוק" → "היצע שוק".  
     - "ביקוש" ו-"היצע" הם בזכר: "הביקוש גדל", "ההיצע יורד" (ולא "גדלה"/"יורדת").  

   - מונחים מדעיים וטכניים:  
     - יש לוודא שהמינוח המדעי מדויק ונכון בהתאם לתחום (פיזיקה, מתמטיקה, מדעי המחשב וכו').  
     - במקרה של שימוש לא נכון במונח מדעי – יש לתקן בהתאם למונח הנכון.  
     - יש לוודא אחידות בכתיבת מונחים לאורך כל הטקסט.  

2. תיקון קיצורים ושמות מוסדות:  
   - כתיבה תקנית של קיצורים נפוצים:  
     - "חול" → "חו״ל" (חובה להחליף בכל מקום שמדובר על חוץ לארץ).  
     - "צהל" → "צה״ל".  
     - "ארהב" → "ארה״ב".  
     - "אום" → "או״ם".  

3. שמירה על סגנון הדיבור של המרצה והתאמה לתוכן:
   - יש להימנע משינוי סגנון הדיבור של המרצה גם אם הוא יומיומי או לא רשמי.  
   - ניתן לבצע תיקונים קלים לשיפור בהירות המשפטים, אך רק כאשר ברור שהטקסט אינו משקף נכון את הנאמר.  
   - יש להימנע משינוי ניסוח אם המשמעות נשארת זהה.  

4. מה לא לשנות:
   - אל תשנה ביטויים יומיומיים, גם אם הם אינם תקניים.  
   - אל תשנה מילים שאינן מונחים מקצועיים.  
   - אל תשנה מבנה של שורות או קודי זמן בכתוביות.  
   - אל תשנה התאמות דקדוקיות במילים שלא הוגדרו במפורש לעיל.  

אם אין טעויות מסוגים אלו – החזר את הטקסט המקורי בדיוק כפי שהוא."""
                        },
                        {"role": "user", "content": text}
                    ],
                    temperature=0.0,
                    timeout=30
                )
                
                return response.choices[0].message.content
                
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
                print(f"Starting Arabic translation with {self.translation_model} (attempt {retries + 1}/{self.MAX_RETRIES})...")
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
                print(f"Starting Russian translation with {self.translation_model} (attempt {retries + 1}/{self.MAX_RETRIES})...")
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
