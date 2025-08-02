import os
import json
import yaml
from typing import List, Dict, Optional
from app.database import SessionLocal
from app.models import Story
from app.crud import create_story, get_stories_by_filter

# Try to import Google Generative AI, but make it optional
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

# Load configuration
try:
    with open("prompts.yaml", "r") as f:
        config = yaml.safe_load(f)
    STORY_CONTENT_PROMPT = config["generate_story_content"]
    CONTEXTUAL_STORIES_PROMPT = config["generate_contextual_stories"]
    GEMINI_MODEL_NAME = config["gemini_model"]
except (FileNotFoundError, KeyError) as e:
    print(f"Error loading configuration from prompts.yaml: {e}")
    STORY_CONTENT_PROMPT = ""
    CONTEXTUAL_STORIES_PROMPT = ""
    GEMINI_MODEL_NAME = "models/gemini-1.5-flash-latest"

# Configure Gemini
GEMINI_MODEL = None
if GENAI_AVAILABLE:
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            GEMINI_MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)
        else:
            print("Warning: GEMINI_API_KEY not found in environment")
    except Exception as e:
        print(f"Warning: Could not configure Gemini: {e}")
else:
    print("Warning: google-generativeai not installed, AI features disabled")


def enrich_story_with_ai(story_data: Dict) -> Dict:
    """Enrich a basic story with AI-generated content"""
    if not GEMINI_MODEL:
        return story_data
    
    try:
        prompt = STORY_CONTENT_PROMPT.format(
            story_title=story_data.get('title_en', ''),
            story_context=story_data.get('content_en', ''),
            story_type=story_data.get('story_type', 'trivia'),
            era=story_data.get('era', 'General')
        )
        
        response = GEMINI_MODEL.generate_content(prompt)
        result = json.loads(response.text)
        
        # Update story data with AI-generated content
        story_data.update({
            'content_en': result.get('content_en', story_data.get('content_en')),
            'content_he': result.get('content_he'),
            'summary_en': result.get('summary_en'),
            'summary_he': result.get('summary_he')
        })
        
    except Exception as e:
        print(f"Error enriching story with AI: {e}")
    
    return story_data


def generate_contextual_stories(era: Optional[str] = None, 
                              category: Optional[str] = None,
                              team: Optional[str] = None,
                              count: int = 5) -> List[Dict]:
    """Generate stories based on current filter context"""
    if not GEMINI_MODEL:
        return []
    
    try:
        # Check if we already have enough stories for this context
        db = SessionLocal()
        existing_stories = get_stories_by_filter(db, era=era, team=team, limit=count)
        db.close()
        
        if len(existing_stories) >= count:
            return []  # We have enough stories already
        
        prompt = CONTEXTUAL_STORIES_PROMPT.format(
            era=era or "All Eras",
            category=category or "All Categories",
            team=team or "All Teams"
        )
        
        response = GEMINI_MODEL.generate_content(prompt)
        stories_data = json.loads(response.text)
        
        # Save generated stories to database
        db = SessionLocal()
        for story_data in stories_data:
            create_story(db, story_data)
        db.close()
        
        return stories_data
        
    except Exception as e:
        print(f"Error generating contextual stories: {e}")
        return []


def get_or_generate_stories(era: Optional[str] = None,
                          category: Optional[str] = None,
                          team: Optional[str] = None,
                          limit: int = 10) -> List[Story]:
    """Get stories from DB or generate new ones if needed"""
    db = SessionLocal()
    
    # First, try to get existing stories
    stories = get_stories_by_filter(db, era=era, team=team, limit=limit)
    
    # If we don't have enough stories, generate some
    if len(stories) < 5:
        generated = generate_contextual_stories(era, category, team, count=5)
        if generated:
            # Fetch the newly created stories
            stories = get_stories_by_filter(db, era=era, team=team, limit=limit)
    
    db.close()
    return stories


# Predefined story templates for quick population
DEFAULT_STORIES = [
    {
        "title_en": "The Bicycle Kick Against Juventus",
        "title_he": "בעיטת האופניים המדהימה נגד יובנטוס",
        "content_en": "On April 3, 2018, Cristiano Ronaldo scored one of the most spectacular goals in Champions League history. Playing for Real Madrid against Juventus in the quarter-finals, Ronaldo launched himself into the air to execute a perfect bicycle kick from Dani Carvajal's cross. The goal was so extraordinary that even the Juventus fans stood up to applaud.",
        "content_he": "ב-3 באפריל 2018, כריסטיאנו רונאלדו כבש אחד השערים הכי מרהיבים בהיסטוריה של ליגת האלופות. במשחק רבע הגמר בין ריאל מדריד ליובנטוס, רונאלדו זינק לאוויר וביצע בעיטת אופניים מושלמת מהמסירה של דני קרבחל. השער היה כל כך יוצא דופן שאפילו אוהדי יובנטוס קמו לתשואות. הכדור עף בקשת מושלמת לפינה העליונה, והשוער בופון נשאר ללא סיכוי. זה היה רגע של גאונות טהורה - שילוב של כושר גופני מדהים, תזמון מושלם ויכולת טכנית שמעטים כדורגלנים בעולם יכולים להשיג. המשחק הזה הפך לאחד הרגעים הכי זכורים בקריירה של רונאלדו, וכיום הוא נחשב לאחד השערים הכי יפים שנכבשו אי פעם באצטדיון ברנבאו.",
        "summary_en": "Ronaldo's incredible bicycle kick goal against Juventus earned a standing ovation from opposition fans.",
        "summary_he": "שער בעיטת האופניים המדהים של רונאלדו נגד יובנטוס זכה לתשואות עמידה אפילו מאוהדי הקבוצה היריבה.",
        "story_type": "match",
        "era": "Madrid",
        "team": "Real Madrid",
        "year": "2018",
        "category_relevance": "jerseys,memorabilia",
        "importance_score": 10,
        "related_search_terms": "madrid,real,2018,champions,juventus"
    },
    {
        "title_en": "First Ballon d'Or at Manchester United",
        "title_he": "כדור הזהב הראשון במנצ'סטר יונייטד",
        "content_en": "In 2008, Cristiano Ronaldo won his first Ballon d'Or while playing for Manchester United. At just 23 years old, he had scored 42 goals in all competitions, helping United win both the Premier League and Champions League. This marked the beginning of his rivalry with Lionel Messi for individual honors.",
        "content_he": "ב-2008, כריסטיאנו רונאלדו זכה בכדור הזהב הראשון שלו כשחיקן של מנצ'סטר יונייטד. בגיל 23 בלבד, הוא כבש 42 שערים בכל המחלקות ועזר ליונייטד לזכות גם בפרימיירליג וגם בליגת האלופות. זה היה עונה קסמים עבור הפורטוגלי הצעיר - הוא הפך למלך של אולד טראפורד, כבש שערים מדהימים ועשה קסמים עם הכדור. סאר אלכס פרגוסון ידע שיש לו יהלום נדיר בין ידיו. הזכייה בכדור הזהב סימנה את תחילת היריבות הגדולה עם ליאו מסי, שתשלוט על עולם הכדורגל לעשור הבא. זה היה הרגע שבו רונאלדו הוכיח שהוא לא רק נער מוכשר ממדיירה, אלא אחד השחקנים הטובים בעולם. האוהדים באולד טראפורד לא יכלו להאמין שהם זוכים לראות כישרון כל כך נדיר.",
        "summary_en": "Ronaldo won his first Ballon d'Or in 2008 after a spectacular season with Manchester United.",
        "summary_he": "רונאלדו זכה בכדור הזהב הראשון שלו ב-2008 לאחר עונה מדהימה במנצ'סטר יונייטד.",
        "story_type": "milestone",
        "era": "United",
        "team": "Manchester United",
        "year": "2008",
        "category_relevance": "jerseys,signed_items",
        "importance_score": 9,
        "related_search_terms": "united,manchester,2008,ballon,dor"
    },
    {
        "title_en": "Euro 2016 Triumph",
        "title_he": "הניצחון הגדול ביורו 2016",
        "content_en": "Portugal's victory at Euro 2016 was one of Ronaldo's most emotional moments. Despite being injured early in the final against France, Ronaldo became a motivational figure on the sidelines, passionately coaching his teammates. Eder's extra-time goal sealed Portugal's first major tournament victory.",
        "content_he": "הניצחון של פורטוגל ביורו 2016 היה אחד הרגעים הכי רגשיים בקריירה של רונאלדו. למרות שנפצע בתחילת הגמר נגד צרפת, הוא הפך לדמות מעוררת השראה מהקו הצדדי, אימן בלהט את חבריו לקבוצה וזרק להם כוח ואמונה. כשאדר כבש בהארכה, רונאלדו פרץ בבכי של שמחה - סוף סוף! הטרופי הגדול הראשון שלו עם הנבחרת. זה היה רגע שפורטוגל חיכתה לו עשרות שנים. רונאלדו, שכבר נחשב לאחד הגדולים בהיסטוריה, עדיין חסר היה לו התואר הבינלאומי הגדול. עכשיו, עם הטרופי באמס, הוא יכול היה להגיד שהוא עשה הכל. הדמעות שזלגו מעיניו בסטאד דה פראנס סיפרו את כל הסיפור - נער ממדיירה שהפך למלך של פורטוגל.",
        "summary_en": "Ronaldo led Portugal to their first major trophy at Euro 2016, despite injury in the final.",
        "summary_he": "רונאלדו הוביל את פורטוגל לתואר הגדול הראשון ביורו 2016, למרות הפציעה בגמר.",
        "story_type": "milestone",
        "era": "Portugal",
        "team": "Portugal National Team",
        "year": "2016",
        "category_relevance": "jerseys,memorabilia",
        "importance_score": 10,
        "related_search_terms": "portugal,euro,2016,final,france"
    },
    {
        "title_en": "700 Career Goals Milestone",
        "title_he": "אבן הדרך של 700 שערים בקריירה",
        "content_en": "On October 14, 2019, Cristiano Ronaldo reached the incredible milestone of 700 career goals, scoring for Portugal against Ukraine. He became only the sixth player in football history to achieve this feat, joining an elite group including Pele and Puskas.",
        "content_he": "ב-14 באוקטובר 2019, כריסטיאנו רונאלדו הגיע לאבן דרך מדהימה של 700 שערים בקריירה, כשכבש עבור פורטוגל נגד אוקראינה. הוא הפך לשחקן השישי בלבד בהיסטוריה של הכדורגל שהשיג את ההישג הזה, והצטרף לקבוצת עילית שכוללת את פלה ופושקאש. זה היה רגע של אמת עבור אחד הכדורגלנים הגדולים בכל הזמנים. 700 שערים - מספר שנשמע כמו פנטזיה, אבל עבור רונאלדו זה היה רק תחנה נוספת במסע המדהים שלו. מהימים הראשונים בספורטינג ליסבון, דרך השערים במנצ'סטר יונייטד, הפלאות בריאל מדריד, ההצלחות ביובנטוס ועד לנבחרת פורטוגל - כל שער ספר את הסיפור של גאון שלא מפסיק להפתיע. הקהל באולימפייסקי קייב קם על הרגליים כדי לכבד את הגדול.",
        "summary_en": "Ronaldo became the sixth player in history to score 700 career goals.",
        "summary_he": "רונאלדו הפך לשחקן השישי בהיסטוריה שכבש 700 שערים בקריירה.",
        "story_type": "record",
        "era": "Portugal",
        "year": "2019",
        "category_relevance": "boots,cards",
        "importance_score": 9,
        "related_search_terms": "700,goals,milestone,ukraine,portugal"
    },
    {
        "title_en": "Growing Up in Madeira",
        "title_he": "ילדות צנועה במדיירה",
        "content_en": "Cristiano Ronaldo grew up in a humble family in Funchal, Madeira. His father worked as a kit man at a local club, where young Cristiano first fell in love with football. At age 12, he made the difficult decision to leave his family and move to Lisbon to join Sporting's academy, showing early signs of the dedication that would define his career.",
        "content_he": "כריסטיאנו רונאלדו גדל במשפחה צנועה בפונשל שבמדיירה. אביו עבד כשומר ציוד במועדון מקומי, שם הצעיר כריסטיאנו התאהב לראשונה בכדורגל. בגיל 12, הוא קיבל את ההחלטה הקשה לעזוב את המשפחה שלו ולעבור ללישבון כדי להצטרף לאקדמיה של ספורטינג. זה היה רגע מכונן - נער קטן מאי קטן באטלנטי, עוזב את הבית, את האמא שלו דולורס שבכתה ימים שלמים, ואת החיים הפשוטים שהכיר. האקדמיה של ספורטינג הייתה עולם אחר לגמרי - ילדים מכל פורטוגל שחלמו להיות כדורגלנים מקצועיים. כריסטיאנו היה הכי קטן, הכי רזה והכי שקט מכולם, אבל כשנגע בכדור, כולם הבינו שיש כאן משהו מיוחד. הוא התאמן כאילו החיים שלו תלויים בזה, כי בעצם כך זה היה.",
        "summary_en": "Ronaldo's journey from humble beginnings in Madeira to football stardom began at age 12.",
        "summary_he": "המסע של רונאלדו מהתחלות צנועות במדיירה לכוכבות עולמית התחיל בגיל 12.",
        "story_type": "personal",
        "era": "Sporting",
        "year": "1997",
        "category_relevance": "memorabilia",
        "importance_score": 7,
        "related_search_terms": "madeira,childhood,sporting,academy,portugal"
    },
    {
        "title_en": "La Decima - Real Madrid's 10th Champions League",
        "title_he": "לה דצ'ימה - ליגת האלופות ה-10 של ריאל מדריד",
        "content_en": "In 2014, Real Madrid finally achieved their dream of La Decima - the 10th Champions League title. Ronaldo scored the crucial penalty and later added another goal in extra time against Atletico Madrid, becoming the tournament's top scorer.",
        "content_he": "ב-2014, ריאל מדריד סוף סוף השיגה את החלום שלה על לה דצ'ימה - תואר ליגת האלופות ה-10. רונאלדו כבש את הפנדל החשוב ומאוחר יותר הוסיף עוד שער בהארכה נגד אתלטיקו מדריד, והפך למלך השערים של הטורניר. זה היה רגע של זמזום בברנבאו - 12 שנים של צמא וציפייה הגיעו לסיומם. רונאלדו, עם השרירים המתוחים והמבט הנחוש, עמד מול הכדור בנקודת הפנדל ברגע הכי חשוב. 90,000 אוהדים עצרו נשימה. הוא רץ, בעט, וכבש. אתלטיקו השווה, אבל רונאלדו לא התייאש. בהארכה, הוא הראה מדוע הוא נקרא 'מיסטר צ'מפיונס ליג' - שער נוסף שחתם על הניצחון ההיסטורי. לה דצ'ימה הגיעה סוף סוף הביתה.",
        "summary_en": "Ronaldo led Real Madrid to their historic 10th Champions League title in 2014.",
        "summary_he": "רונאלדו הוביל את ריאל מדריד לתואר ליגת האלופות ה-10 ההיסטורי ב-2014.",
        "story_type": "milestone",
        "era": "Madrid",
        "team": "Real Madrid",
        "year": "2014",
        "category_relevance": "jerseys,memorabilia",
        "importance_score": 10,
        "related_search_terms": "madrid,real,champions,2014,atletico,decima"
    },
    {
        "title_en": "Hat-trick in World Cup vs Spain",
        "title_he": "שלושער במונדיאל נגד ספרד",
        "content_en": "At the 2018 World Cup, Ronaldo produced one of the greatest individual performances against Spain, scoring a magnificent hat-trick including a stunning free-kick to secure a 3-3 draw.",
        "content_he": "במונדיאל 2018, רונאלדו הפיק אחד המופעים האישיים הגדולים ביותר נגד ספרד, כבש שלושער מדהים כולל בעיטה חופשית מרהיבה שהבטיחה תיקו 3-3. זה היה יום שכל פורטוגל לא תשכח. ספרד, אלופת העולם והיורו, נגד פורטוגל של רונאלדו בגיל 33. כולם חשבו שהזמן עובר עליו, שזה לא עוד יהיה הרונאלדו שאנחנו מכירים. אבל ברגע הראשון הוא הוכיח את כולם לטועים. פנדל מושלם, שער מקצועי, ואז הפנינה - בעיטה חופשית מ-30 מטר שעפה כמו טיל לפינה העליונה. דיוויד דה חאה, השוער הספרדי, רק יכול היה להסתכל. רונאלדו רץ לקהל, הרים את הזרועות, וכל העולם הבין: הוא עדיין כאן, עדיין המלך.",
        "summary_en": "Ronaldo's brilliant hat-trick against Spain in the 2018 World Cup remains one of his greatest individual performances.",
        "summary_he": "השלושער המבריק של רונאלדו נגד ספרד במונדיאל 2018 נשאר אחד המופעים האישיים הגדולים שלו.",
        "story_type": "match",
        "era": "Portugal",
        "team": "Portugal National Team",
        "year": "2018",
        "category_relevance": "jerseys,boots",
        "importance_score": 9,
        "related_search_terms": "portugal,spain,2018,world,cup,hattrick"
    },
    {
        "title_en": "Moving to Al-Nassr - New Chapter",
        "title_he": "המעבר לאל-נאסר - פרק חדש",
        "content_en": "In 2023, Ronaldo shocked the football world by joining Al-Nassr in Saudi Arabia, becoming the highest-paid footballer in history and pioneering a new era of football in the Middle East.",
        "content_he": "ב-2023, רונאלדו זעזע את עולם הכדורגל כשהצטרף לאל-נאסר בערב הסעודית, הפך לכדורגלן הכי משתכר בהיסטוריה וחלץ עידן חדש של כדורגל במזרח התיכון. כולם שאלו: למה? למה רונאלדו, שעדיין יכול לשחק ברמה הגבוהה ביותר, בוחר לעזוב את אירופה? התשובה הייתה פשוטה: הוא רוצה להיות חלוץ, לא רק בשערים אלא גם בפתיחת שווקים חדשים. המעבר לאל-נאסר לא היה רק על כסף - זה היה על מורשת. רונאלדו הבין שהוא יכול להיות השגריר שיביא את הכדורגל העולמי למזרח התיכון, שיעזור לפתח דור חדש של כדורגלנים ערבים. האוהדים בריאד קיבלו אותו כמו מלך, ועכשיו הוא ממשיך לכבש שערים ולשבור שיאים גם בגיל 38.",
        "summary_en": "Ronaldo's move to Al-Nassr in 2023 opened a new chapter in football history in the Middle East.",
        "summary_he": "המעבר של רונאלדו לאל-נאסר ב-2023 פתח פרק חדש בהיסטוריה של הכדורגל במזרח התיכון.",
        "story_type": "milestone",
        "era": "Al-Nassr",
        "team": "Al-Nassr",
        "year": "2023",
        "category_relevance": "jerseys,memorabilia",
        "importance_score": 8,
        "related_search_terms": "nassr,saudi,arabia,2023,transfer"
    },
    {
        "title_en": "The Legendary Free-Kick Technique",
        "title_he": "טכניקת הבעיטות החופשיות האגדית",
        "content_en": "Ronaldo's free-kick technique evolved throughout his career, from the knuckleball effect at Manchester United to the power shots at Real Madrid, becoming one of the most feared set-piece takers in football history.",
        "content_he": "טכניקת הבעיטות החופשיות של רונאלדו התפתחה לאורך הקריירה שלו, מאפקט הנאקלבול במנצ'סטר יונייטד ועד לבעיטות הכוח בריאל מדריד, והפכה לאחת הכי מפחידות בהיסטוריה של הכדורגל. היה משהו מהפנוטי בדרך שבה רונאלדו עמד מול הכדור לפני בעיטה חופשית. הרגליים רחבות, הגב זקוף, המבט נעוץ בשער. שוערים ידעו שמשהו מיוחד עומד לקרות, אבל הם פשוט לא יכלו לחזות מה. ברונאלדו הצעיר במנצ'סטר, הכדור רקד באוויר בצורה בלתי צפויה - אפקט הנאקלבול שהפך אותו למפורסם. ברונאלדו הבוגר במדריד, זה היה כוח טהור - בעיטות שעפו כמו טילים ישר לרשת. למעלה מ-50 שערים מבעיטות חופשיות בקריירה שלו, וכל אחד מהם סיפור בפני עצמו.",
        "summary_en": "Ronaldo's free-kick mastery evolved from knuckleball effects to powerful shots, terrorizing goalkeepers worldwide.",
        "summary_he": "שליטת רונאלדו בבעיטות חופשיות התפתחה מאפקטי נאקלבול לבעיטות כוח, והטילה אימה על שוערים בכל העולם.",
        "story_type": "trivia",
        "era": "General",
        "year": "2004-2023",
        "category_relevance": "boots,cards",
        "importance_score": 7,
        "related_search_terms": "freekick,technique,goals,united,madrid"
    },
    {
        "title_en": "Champions League Top Scorer Record",
        "title_he": "שיא מלך השערים של ליגת האלופות",
        "content_en": "Ronaldo holds the record as the all-time top scorer in Champions League history with 140 goals. His dominance in Europe's premier competition includes 7 top scorer awards and 5 titles.",
        "content_he": "רונאלדו מחזיק בשיא של מלך השערים בכל הזמנים של ליגת האלופות עם 140 שערים. השליטה שלו בתחרות הכי יוקרתית באירופה כוללת 7 תארי מלך שערים ו-5 תארים. זה לא סתם שיא - זה אימפריה. כל רביעי-בערב באירופה, כששמעו את ההמנון של ליגת האלופות, הם ידעו: עכשיו זה הזמן של רונאלדו. לא משנה איך הוא שיחק בליגה, לא משנה כמה הוא היה עייף - ברגע שהפעמונים התחילו לצלצל, משהו נדלק בו. 140 שערים זה לא רק מספר, זה סיפור של 16 שנים של גאונות. שערים נגד ליברפול, נגד יובנטוס, נגד בארצלונה, נגד כל הגדולים. מההתחלה הצנועה עם ספורטינג ועד לשערים עם אל-נאסר - ליגת האלופות הייתה הבמה שלו, והוא היה הכוכב הבלתי מעורער.",
        "summary_en": "With 140 goals, Ronaldo is the undisputed Champions League top scorer of all time.",
        "summary_he": "עם 140 שערים, רונאלדו הוא מלך השערים הבלתי מעורער של ליגת האלופות בכל הזמנים.",
        "story_type": "record",
        "era": "General",
        "year": "2003-2022",
        "category_relevance": "jerseys,memorabilia,cards",
        "importance_score": 10,
        "related_search_terms": "champions,league,goals,record,140"
    },
    {
        "title_en": "The Juventus Years - Serie A Mastery",
        "title_he": "שנות יובנטוס - שליטה בסרייה A",
        "content_en": "Ronaldo's move to Juventus in 2018 proved his adaptability, conquering Serie A with typical determination and adding another dimension to his legendary career in Italian football.",
        "content_he": "המעבר של רונאלדו ליובנטוס ב-2018 הוכיח את כושר ההסתגלות שלו, כבש את סרייה A עם הנחישות הטיפוסית שלו והוסיף עוד מימד לקריירה האגדית שלו בכדורגל האיטלקי. אחרי 9 שנים מדהימות במדריד, כולם חשבו שרונאלדו יגמור שם את הקריירה שלו. אבל הוא הפתיע את כולם - יובנטוס! הקבוצה הכי מצליחה באיטליה, ששנים חיפשה את הכוכב שיביא להם את ליגת האלופות. רונאלדו הגיע לטורינו בגיל 33, וכולם שאלו: האם הוא יצליח בסרייה A הטקטית והקשה? התשובה באה מהר. 101 שערים ב-134 משחקים, 2 תארי סרייה A, ומופעים שהזכירו לכולם מי הוא באמת. הקהל הישן של יובנטוס, שראה את דל פיירו ובאג'ו, קם על הרגליים לכבד את הפורטוגלי. איטליה הכירה את המלך.",
        "summary_en": "Ronaldo's successful adaptation to Serie A with Juventus proved his ability to excel in any league.",
        "summary_he": "ההסתגלות המוצלחת של רונאלדו לסרייה A עם יובנטוס הוכיחה את יכולתו להצטיין בכל ליגה.",
        "story_type": "milestone",
        "era": "Juventus",
        "team": "Juventus",
        "year": "2018-2021",
        "category_relevance": "jerseys,memorabilia",
        "importance_score": 8,
        "related_search_terms": "juventus,seria,italy,2018,goals"
    }
]


def populate_default_stories():
    """Populate database with default stories"""
    db = SessionLocal()
    try:
        for story_data in DEFAULT_STORIES:
            # Enrich with AI if available
            enriched = enrich_story_with_ai(story_data)
            create_story(db, enriched)
        print(f"✅ Populated {len(DEFAULT_STORIES)} default stories")
    except Exception as e:
        print(f"Error populating default stories: {e}")
    finally:
        db.close()