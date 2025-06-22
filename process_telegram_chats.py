import json
import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import platform

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Configuration from environment variables with defaults
class Config:
    """Configuration class that loads settings from environment variables"""
    
    # Input/Output settings
    INPUT_FILE = os.getenv('INPUT_FILE', 'result.json')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'chats_clean_pdf')
    METADATA_DIR = os.getenv('METADATA_DIR', 'metadata')
    METADATA_FILE = os.getenv('METADATA_FILE', 'metadata_summary.json')
    
    # User identification
    USER_NAME = os.getenv('USER_NAME', 'Your Name')
    USER_ID = os.getenv('USER_ID', 'user123456789')
    
    # PDF generation settings
    MAX_FILE_SIZE_KB = int(os.getenv('MAX_FILE_SIZE_KB', '200'))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '500'))
    PDF_FONT_SIZE = int(os.getenv('PDF_FONT_SIZE', '10'))
    PDF_LINE_SPACING = int(os.getenv('PDF_LINE_SPACING', '12'))
    PDF_MARGIN_TOP = int(os.getenv('PDF_MARGIN_TOP', '40'))
    PDF_MARGIN_BOTTOM = int(os.getenv('PDF_MARGIN_BOTTOM', '40'))
    PDF_MARGIN_LEFT = int(os.getenv('PDF_MARGIN_LEFT', '40'))
    PDF_MARGIN_RIGHT = int(os.getenv('PDF_MARGIN_RIGHT', '40'))
    
    # Chunking algorithm settings
    SHORT_MESSAGE_CHUNK_SIZE = int(os.getenv('CHUNK_SIZE_SHORT', '25'))
    MEDIUM_MESSAGE_CHUNK_SIZE = int(os.getenv('CHUNK_SIZE_MEDIUM', '18'))
    LONG_MESSAGE_CHUNK_SIZE = int(os.getenv('CHUNK_SIZE_LONG', '12'))
    MIN_CHUNKS_PER_FILE = int(os.getenv('MIN_CHUNKS_PER_FILE', '12'))
    MAX_CHUNKS_PER_FILE = int(os.getenv('MAX_CHUNKS_PER_FILE', '100'))
    SIZE_ESTIMATION_MULTIPLIER = float(os.getenv('SIZE_ESTIMATION_MULTIPLIER', '0.005'))
    TARGET_SIZE_PERCENTAGE = float(os.getenv('TARGET_SIZE_PERCENTAGE', '0.8'))
    
    # Text processing settings
    MIN_MESSAGE_LENGTH = int(os.getenv('MIN_MESSAGE_LENGTH', '2'))
    SHORT_MESSAGE_THRESHOLD = int(os.getenv('SHORT_MESSAGE_THRESHOLD', '50'))
    LONG_MESSAGE_THRESHOLD = int(os.getenv('LONG_MESSAGE_THRESHOLD', '150'))
    
    # Font paths
    WINDOWS_FONTS = os.getenv('WINDOWS_FONTS', 'C:/Windows/Fonts/arial.ttf,C:/Windows/Fonts/calibri.ttf,C:/Windows/Fonts/tahoma.ttf').split(',')
    MACOS_FONTS = os.getenv('MACOS_FONTS', '/System/Library/Fonts/Arial.ttf').split(',')
    LINUX_FONTS = os.getenv('LINUX_FONTS', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf').split(',')
    DEFAULT_FONT = os.getenv('DEFAULT_FONT', 'Helvetica')
    
    # Debug and logging
    VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
    SHOW_FONT_INFO = os.getenv('SHOW_FONT_INFO', 'false').lower() == 'true'
    SHOW_PROGRESS = os.getenv('SHOW_PROGRESS', 'true').lower() == 'true'

def sanitize_filename(name):
    """Clean filename from invalid characters"""
    if name is None:
        return "Unknown"
    return re.sub(r'[<>:"/\\|?*]', '_', str(name))

def convert_emojis_to_text(text):
    """Convert common emojis to text descriptions for better text processing"""
    emoji_map = {
        '😀': '[smile]', '😃': '[joy]', '😄': '[laugh]', '😁': '[grin]', '😆': '[laughing]',
        '😅': '[sweat_smile]', '🤣': '[rofl]', '😂': '[joy_tears]', '🙂': '[slight_smile]', '🙃': '[upside_down]',
        '😉': '[wink]', '😊': '[blush]', '😇': '[innocent]', '🥰': '[heart_eyes]', '😍': '[heart_eyes]',
        '🤩': '[star_struck]', '😘': '[kiss]', '😗': '[kissing]', '☺️': '[relaxed]', '😚': '[kissing_closed_eyes]',
        '😙': '[kissing_smiling_eyes]', '🥲': '[smiling_tear]', '😋': '[yum]', '😛': '[stuck_out_tongue]', '😜': '[stuck_out_tongue_winking_eye]',
        '🤪': '[zany_face]', '😝': '[stuck_out_tongue_closed_eyes]', '🤑': '[money_mouth]', '🤗': '[hugs]', '🤭': '[hand_over_mouth]',
        '🤫': '[shushing]', '🤔': '[thinking]', '🤐': '[zipper_mouth]', '🤨': '[raised_eyebrow]', '😐': '[neutral]',
        '😑': '[expressionless]', '😶': '[no_mouth]', '😏': '[smirk]', '😒': '[unamused]', '🙄': '[eye_roll]',
        '😬': '[grimacing]', '🤥': '[lying]', '😔': '[pensive]', '😕': '[confused]', '🙁': '[slight_frown]',
        '☹️': '[frowning]', '😣': '[persevere]', '😖': '[confounded]', '😫': '[tired]', '😩': '[weary]',
        '🥺': '[pleading]', '😢': '[cry]', '😭': '[sob]', '😤': '[huff]', '😠': '[angry]',
        '😡': '[rage]', '🤬': '[swearing]', '🤯': '[exploding_head]', '😳': '[flushed]', '🥵': '[hot]',
        '🥶': '[cold]', '😱': '[scream]', '😨': '[fearful]', '😰': '[anxious]', '😥': '[disappointed_relieved]',
        '😓': '[cold_sweat]', '🤗': '[hugs]', '🤔': '[thinking]', '🤫': '[shushing]', '🤭': '[hand_over_mouth]',
        '🙈': '[see_no_evil]', '🙉': '[hear_no_evil]', '🙊': '[speak_no_evil]', '💀': '[skull]', '☠️': '[skull_crossbones]',
        '👻': '[ghost]', '👽': '[alien]', '🤖': '[robot]', '💩': '[poop]', '😺': '[smiley_cat]',
        '😸': '[smile_cat]', '😹': '[joy_cat]', '😻': '[heart_eyes_cat]', '😼': '[smirk_cat]', '😽': '[kissing_cat]',
        '🙀': '[scream_cat]', '😿': '[crying_cat]', '😾': '[pouting_cat]', '❤️': '[red_heart]', '🧡': '[orange_heart]',
        '💛': '[yellow_heart]', '💚': '[green_heart]', '💙': '[blue_heart]', '💜': '[purple_heart]', '🖤': '[black_heart]',
        '🤍': '[white_heart]', '🤎': '[brown_heart]', '💔': '[broken_heart]', '❣️': '[heart_exclamation]', '💕': '[two_hearts]',
        '💞': '[revolving_hearts]', '💓': '[heartbeat]', '💗': '[growing_heart]', '💖': '[sparkling_heart]', '💘': '[cupid]',
        '💝': '[gift_heart]', '💟': '[heart_decoration]', '☮️': '[peace]', '✝️': '[cross]', '☪️': '[crescent]',
        '🕉️': '[om]', '☸️': '[dharma]', '✡️': '[star_of_david]', '🔯': '[six_pointed_star]', '🕎': '[menorah]',
        '☯️': '[yin_yang]', '☦️': '[orthodox_cross]', '🛐': '[place_of_worship]', '⛎': '[ophiuchus]', '♈': '[aries]',
        '♉': '[taurus]', '♊': '[gemini]', '♋': '[cancer]', '♌': '[leo]', '♍': '[virgo]',
        '♎': '[libra]', '♏': '[scorpio]', '♐': '[sagittarius]', '♑': '[capricorn]', '♒': '[aquarius]',
        '♓': '[pisces]', '🆔': '[id]', '⚛️': '[atom]', '🉑': '[accept]', '☢️': '[radioactive]',
        '☣️': '[biohazard]', '📴': '[mobile_phone_off]', '📳': '[vibration_mode]', '🈶': '[not_free_of_charge]', '🈚': '[free_of_charge]',
        '🈸': '[application]', '🈺': '[open_for_business]', '🈷️': '[monthly_amount]', '✴️': '[eight_pointed_star]', '🆚': '[vs]',
        '💮': '[white_flower]', '🉐': '[bargain]', '㊙️': '[secret]', '㊗️': '[congratulations]', '🈴': '[passing_grade]',
        '🈵': '[no_vacancy]', '🈹': '[discount]', '🈲': '[prohibited]', '🅰️': '[a_button]', '🅱️': '[b_button]',
        '🆎': '[ab_button]', '🆑': '[cl_button]', '🅾️': '[o_button]', '🆘': '[sos]', '❌': '[cross_mark]',
        '⭕': '[heavy_large_circle]', '🛑': '[stop_sign]', '⛔': '[no_entry]', '📛': '[name_badge]', '🚫': '[prohibited]',
        '💯': '[hundred]', '💢': '[anger]', '♨️': '[hot_springs]', '🚷': '[no_pedestrians]', '🚯': '[no_littering]',
        '🚳': '[no_bicycles]', '🚱': '[non_potable_water]', '🔞': '[no_one_under_eighteen]', '📵': '[no_mobile_phones]', '🚭': '[no_smoking]',
        '❗': '[exclamation]', '❕': '[white_exclamation]', '❓': '[question]', '❔': '[white_question]', '‼️': '[double_exclamation]',
        '⁉️': '[interrobang]', '🔅': '[low_brightness]', '🔆': '[high_brightness]', '〽️': '[part_alternation_mark]', '⚠️': '[warning]',
        '🚸': '[children_crossing]', '🔱': '[trident]', '⚜️': '[fleur_de_lis]', '🔰': '[japanese_symbol_for_beginner]', '♻️': '[recycling]',
        '✅': '[check_mark]', '🈯': '[reserved]', '💹': '[chart_increasing_with_yen]', '❇️': '[sparkle]', '✳️': '[eight_spoked_asterisk]',
        '❎': '[cross_mark_button]', '🌐': '[globe_with_meridians]', '💠': '[diamond_with_a_dot]', 'Ⓜ️': '[circled_m]', '🌀': '[cyclone]',
        '💤': '[zzz]', '🏧': '[atm]', '🚾': '[water_closet]', '♿': '[wheelchair]', '🅿️': '[p_button]',
        '🈳': '[vacancy]', '🈂️': '[service_charge]', '🛂': '[passport_control]', '🛃': '[customs]', '🛄': '[baggage_claim]',
        '🛅': '[left_luggage]', '🚹': '[mens]', '🚺': '[womens]', '🚼': '[baby_symbol]', '🚻': '[restroom]',
        '🚮': '[litter_in_bin]', '🎦': '[cinema]', '📶': '[signal_strength]', '🈁': '[here]', '🔣': '[symbols]',
        'ℹ️': '[information]', '🔤': '[abc]', '🔡': '[abcd]', '🔠': '[capital_abcd]', '🆖': '[ng_button]',
        '🆗': '[ok_button]', '🆙': '[up_button]', '🆒': '[cool_button]', '🆕': '[new_button]', '🆓': '[free_button]',
        '0️⃣': '[keycap_0]', '1️⃣': '[keycap_1]', '2️⃣': '[keycap_2]', '3️⃣': '[keycap_3]', '4️⃣': '[keycap_4]',
        '5️⃣': '[keycap_5]', '6️⃣': '[keycap_6]', '7️⃣': '[keycap_7]', '8️⃣': '[keycap_8]', '9️⃣': '[keycap_9]',
        '🔟': '[keycap_10]', '🔢': '[input_numbers]', '#️⃣': '[hash]', '*️⃣': '[asterisk]', '⏏️': '[eject]',
        '▶️': '[play]', '⏸️': '[pause]', '⏯️': '[play_pause]', '⏹️': '[stop]', '⏺️': '[record]',
        '⏭️': '[next_track]', '⏮️': '[previous_track]', '⏩': '[fast_forward]', '⏪': '[rewind]', '⏫': '[fast_up]',
        '⏬': '[fast_down]', '◀️': '[reverse]', '🔼': '[up_button]', '🔽': '[down_button]', '➡️': '[right_arrow]',
        '⬅️': '[left_arrow]', '⬆️': '[up_arrow]', '⬇️': '[down_arrow]', '↗️': '[up_right_arrow]', '↘️': '[down_right_arrow]',
        '↙️': '[down_left_arrow]', '↖️': '[up_left_arrow]', '↕️': '[up_down_arrow]', '↔️': '[left_right_arrow]', '↪️': '[left_arrow_curving_right]',
        '↩️': '[right_arrow_curving_left]', '⤴️': '[right_arrow_curving_up]', '⤵️': '[right_arrow_curving_down]', '🔀': '[twisted_rightwards_arrows]', '🔁': '[repeat]',
        '🔂': '[repeat_single]', '🔄': '[counterclockwise_arrows]', '🔃': '[clockwise_vertical_arrows]', '🎵': '[musical_note]', '🎶': '[musical_notes]',
        '➕': '[plus]', '➖': '[minus]', '➗': '[divide]', '✖️': '[multiply]', '♾️': '[infinity]',
        '💲': '[heavy_dollar_sign]', '💱': '[currency_exchange]', '™️': '[trademark]', '©️': '[copyright]', '®️': '[registered]',
        '〰️': '[wavy_dash]', '➰': '[curly_loop]', '➿': '[double_curly_loop]', '🔚': '[end]', '🔙': '[back]',
        '🔛': '[on]', '🔝': '[top]', '🔜': '[soon]', '✔️': '[check_mark]', '☑️': '[check_box_with_check]',
        '🔘': '[radio_button]', '🔴': '[red_circle]', '🟠': '[orange_circle]', '🟡': '[yellow_circle]', '🟢': '[green_circle]',
        '🔵': '[blue_circle]', '🟣': '[purple_circle]', '⚫': '[black_circle]', '⚪': '[white_circle]', '🟤': '[brown_circle]',
        '🔺': '[red_triangle_pointed_up]', '🔻': '[red_triangle_pointed_down]', '🔸': '[small_orange_diamond]', '🔹': '[small_blue_diamond]', '🔶': '[large_orange_diamond]',
        '🔷': '[large_blue_diamond]', '🔳': '[white_square_button]', '🔲': '[black_square_button]', '▪️': '[black_small_square]', '▫️': '[white_small_square]',
        '◾': '[black_medium_small_square]', '◽': '[white_medium_small_square]', '◼️': '[black_medium_square]', '◻️': '[white_medium_square]', '🟥': '[red_square]',
        '🟧': '[orange_square]', '🟨': '[yellow_square]', '🟩': '[green_square]', '🟦': '[blue_square]', '🟪': '[purple_square]',
        '⬛': '[black_large_square]', '⬜': '[white_large_square]', '🟫': '[brown_square]', '🔈': '[speaker_low_volume]', '🔇': '[muted_speaker]',
        '🔉': '[speaker_medium_volume]', '🔊': '[speaker_high_volume]', '🔔': '[bell]', '🔕': '[bell_with_slash]', '📣': '[megaphone]',
        '📢': '[loudspeaker]', '👁‍🗨': '[eye_in_speech_bubble]', '💬': '[speech_balloon]', '💭': '[thought_balloon]', '🗯️': '[right_anger_bubble]',
        '♠️': '[spade_suit]', '♣️': '[club_suit]', '♥️': '[heart_suit]', '♦️': '[diamond_suit]', '🃏': '[joker]',
        '🎴': '[flower_playing_cards]', '🀄': '[mahjong_red_dragon]', '🍻': '[beer]', '🧿': '[nazar_amulet]'
    }
    
    # Replace emojis with text descriptions for better text processing
    for emoji, description in emoji_map.items():
        text = text.replace(emoji, description)
    
    return text

def extract_text_content(msg):
    """Extract clean text content from message object"""
    text = msg.get('text', '')
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and 'text' in item:
                text_parts.append(item['text'])
        text = ''.join(text_parts)
    
    # Convert emojis to text descriptions for better processing
    text = convert_emojis_to_text(str(text).strip() if text else '')
    
    # Additional text cleaning for better processing
    if text:
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters except common punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\[\]\"\'а-яёА-ЯЁ]+', '', text)
        text = text.strip()
    
    return text

def setup_fonts():
    """Setup fonts for Cyrillic text support"""
    try:
        # Get font paths from configuration based on OS
        system = platform.system().lower()
        
        if system == 'windows':
            font_paths = Config.WINDOWS_FONTS
        elif system == 'darwin':  # macOS
            font_paths = Config.MACOS_FONTS
        else:  # Linux and others
            font_paths = Config.LINUX_FONTS
        
        font_registered = False
        for font_path in font_paths:
            font_path = font_path.strip()  # Remove any whitespace
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('CyrillicFont', font_path))
                    font_registered = True
                    if Config.SHOW_FONT_INFO:
                        print(f"Using font: {font_path}")
                    break
                except Exception as e:
                    if Config.VERBOSE_LOGGING:
                        print(f"Failed to load font {font_path}: {e}")
                    continue
        
        if not font_registered:
            if Config.SHOW_FONT_INFO:
                print(f"Warning: No suitable font found for Cyrillic, using {Config.DEFAULT_FONT}")
            return Config.DEFAULT_FONT
        
        return 'CyrillicFont'
    except Exception as e:
        if Config.VERBOSE_LOGGING:
            print(f"Font setup error: {e}")
        return Config.DEFAULT_FONT

def extract_person_info(chat_name, messages):
    """Extract person information from chat name and messages"""
    # Clean chat name
    person_name = chat_name.strip()
    
    # Remove common prefixes and suffixes
    person_name = re.sub(r'^@', '', person_name)  # Remove @ prefix
    person_name = re.sub(r'\s+\(.*\)$', '', person_name)  # Remove (info) suffix
    
    # Try to extract telegram username if present
    telegram_username = ""
    if chat_name.startswith('@'):
        telegram_username = chat_name
    
    # Extract first/last name if possible
    name_parts = person_name.split()
    first_name = name_parts[0] if name_parts else person_name
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
    
    return {
        'person_name': person_name,
        'first_name': first_name,
        'last_name': last_name,
        'telegram_username': telegram_username
    }

def create_optimized_pdf_parts(chat_name, messages, output_dir=None, max_size_kb=None):
    """Create multiple PDF files if chat is too large, optimized for n8n processing"""
    # Use configuration values if not provided
    if output_dir is None:
        output_dir = Config.OUTPUT_DIR
    if max_size_kb is None:
        max_size_kb = Config.MAX_FILE_SIZE_KB
        
    person_info = extract_person_info(chat_name, messages)
    person_name = person_info['person_name']
    total_messages = len(messages)
    
    # Setup font for Cyrillic text
    font_name = setup_fonts()
    
    # Optimized chunk sizing based on content analysis
    avg_msg_length = sum(len(msg.get('text', '')) for msg in messages) / max(len(messages), 1)
    
    # Dynamic chunk sizes based on configuration
    if avg_msg_length < Config.SHORT_MESSAGE_THRESHOLD:
        chunk_size = Config.SHORT_MESSAGE_CHUNK_SIZE
    elif avg_msg_length < Config.LONG_MESSAGE_THRESHOLD:
        chunk_size = Config.MEDIUM_MESSAGE_CHUNK_SIZE
    else:
        chunk_size = Config.LONG_MESSAGE_CHUNK_SIZE
    
    # File size estimation based on configuration
    estimated_kb_per_chunk = max(1.2, avg_msg_length * Config.SIZE_ESTIMATION_MULTIPLIER)
    max_chunks_per_file = int((max_size_kb * Config.TARGET_SIZE_PERCENTAGE) / estimated_kb_per_chunk)
    max_chunks_per_file = max(Config.MIN_CHUNKS_PER_FILE, min(max_chunks_per_file, Config.MAX_CHUNKS_PER_FILE))
    
    # Group messages into chunks with better memory efficiency
    all_chunks = []
    
    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i+chunk_size]
        chunk_texts = []
        
        for idx, msg in enumerate(chunk):
            text = msg.get('text', '').strip()
            direction = msg.get('direction', '?')
            # Calculate global message number in chat
            global_msg_num = i + idx + 1
            
            if text:
                # Text cleaning with configurable length limit
                text = re.sub(r'\s+', ' ', text)
                text = text[:Config.MAX_MESSAGE_LENGTH]
                
                # Add chronological numbering to message format
                if direction == '>':
                    chunk_texts.append(f"[{global_msg_num}/{total_messages}] Me: {text}")
                else:
                    chunk_texts.append(f"[{global_msg_num}/{total_messages}] From {person_name}: {text}")
        
        if chunk_texts:
            # Join with separator optimized for vector search
            combined_text = " | ".join(chunk_texts)
            all_chunks.append(combined_text)
    
    # Memory-efficient file creation
    total_chunks = len(all_chunks)
    if total_chunks <= max_chunks_per_file:
        # Single file
        success, chunks = create_single_pdf_file(chat_name, all_chunks, output_dir, person_info, total_messages, font_name)
        return [(f"{sanitize_filename(chat_name)}.pdf", success, chunks)]
    else:
        # Multiple files with optimized splitting
        files_created = []
        chunks_per_file = max_chunks_per_file
        file_count = (total_chunks + chunks_per_file - 1) // chunks_per_file
        
        for file_idx in range(file_count):
            start_idx = file_idx * chunks_per_file
            end_idx = min(start_idx + chunks_per_file, total_chunks)
            file_chunks = all_chunks[start_idx:end_idx]
            
            # Optimized filename generation
            base_name = sanitize_filename(chat_name)
            part_filename = f"{base_name}_part{file_idx + 1}of{file_count}.pdf"
            
            success, chunks = create_single_pdf_file(
                f"{chat_name} (Part {file_idx + 1}/{file_count})", 
                file_chunks, 
                output_dir, 
                person_info, 
                total_messages, 
                font_name,
                custom_filename=part_filename
            )
            
            files_created.append((part_filename, success, chunks))
        
        return files_created

def create_single_pdf_file(chat_name, chunks, output_dir, person_info, total_messages, font_name, custom_filename=None):
    """Create a single PDF file from chunks with person name in metadata"""
    if custom_filename:
        filename = custom_filename
        filepath = os.path.join(output_dir, filename)
    else:
        filename = f"{sanitize_filename(chat_name)}.pdf"
        filepath = os.path.join(output_dir, filename)
    
    person_name = person_info['person_name']
    
    # Create PDF document with person name in title metadata only
    doc = SimpleDocTemplate(filepath, pagesize=A4, 
                           rightMargin=Config.PDF_MARGIN_RIGHT, 
                           leftMargin=Config.PDF_MARGIN_LEFT,
                           topMargin=Config.PDF_MARGIN_TOP, 
                           bottomMargin=Config.PDF_MARGIN_BOTTOM,
                           title=person_name,  # Person name in PDF metadata for identification
                           author="",  # Empty author
                           subject="",  # Empty subject
                           creator="",  # Empty creator
                           keywords="")  # Empty keywords
    
    # Container for PDF content
    story = []
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Simple text style optimized for readability
    text_style = ParagraphStyle(
        'CleanText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=Config.PDF_FONT_SIZE,
        spaceAfter=4,
        leftIndent=0,
        rightIndent=0,
        leading=Config.PDF_LINE_SPACING
    )
    
    # Add chunks to PDF - clean text only, no headers
    for chunk_text in chunks:
        text_para = Paragraph(chunk_text, text_style)
        story.append(text_para)
        story.append(Spacer(1, 6))
    
    # Build PDF
    try:
        doc.build(story)
        return True, len(chunks)
    except Exception as e:
        if Config.VERBOSE_LOGGING:
            print(f"Error creating PDF for {chat_name}: {e}")
        return False, 0

def process_telegram_chats_optimized(input_file=None):
    """Main function to process Telegram chats and create optimized PDFs for n8n"""
    # Use configuration value if not provided
    if input_file is None:
        input_file = Config.INPUT_FILE
    
    print(f"Creating optimized PDFs for n8n processing (max {Config.MAX_FILE_SIZE_KB}KB per file)...")
    
    # Load chat data with better error handling
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {input_file}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading {input_file}: {e}")
        return False
    
    chat_list = data.get('chats', {}).get('list', [])
    if not chat_list:
        print("❌ No chats found in the data!")
        return False
    
    print(f"📂 Found {len(chat_list)} chats to process")
    
    # Create output directories
    try:
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(Config.METADATA_DIR, exist_ok=True)
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False
    
    # Processing counters
    processed_count = 0
    skipped_count = 0
    total_messages = 0
    total_chunks = 0
    total_files = 0
    
    # Summary data for n8n metadata
    summary_data = []
    
    # Process each chat with progress tracking
    for idx, chat in enumerate(chat_list, 1):
        if chat.get('type') != 'personal_chat':
            skipped_count += 1
            continue
        
        chat_name = chat.get('name') or f"Chat_{chat.get('id', 'Unknown')}"
        messages = chat.get('messages', [])
        
        if not messages:
            if Config.SHOW_PROGRESS:
                print(f"⚠️  Skipping {chat_name}: No messages found")
            skipped_count += 1
            continue
        
        if Config.SHOW_PROGRESS:
            print(f"🔄 Processing [{idx}/{len(chat_list)}]: {chat_name} ({len(messages)} messages)")
        
        chat_messages = []
        
        # Extract and process messages with optimization
        for msg in messages:
            if msg.get('type') != 'message':
                continue
            
            text_content = extract_text_content(msg)
            if not text_content or len(text_content.strip()) < Config.MIN_MESSAGE_LENGTH:
                continue
            
            # Determine message direction (sent by me or received)
            sender = msg.get('from', 'Unknown')
            sender_id = msg.get('from_id', '')
            
            # Check if message was sent by me or received from chat partner
            is_from_me = (sender and Config.USER_NAME in sender) or sender_id == Config.USER_ID
            direction = '>' if is_from_me else '<'
            
            # Store essential data with direction
            chat_msg = {
                'text': text_content,
                'direction': direction
            }
            chat_messages.append(chat_msg)
        
        if not chat_messages:
            if Config.SHOW_PROGRESS:
                print(f"⚠️  Skipping {chat_name}: No valid messages after processing")
            skipped_count += 1
            continue
        
        # Create clean PDF files (potentially multiple parts)
        try:
            files_created = create_optimized_pdf_parts(chat_name, chat_messages)
        except Exception as e:
            print(f"❌ Error processing {chat_name}: {e}")
            skipped_count += 1
            continue
        
        if files_created:
            processed_count += 1
            total_messages += len(chat_messages)
            
            # Extract person info for summary
            person_info = extract_person_info(chat_name, chat_messages)
            
            # Count sent vs received messages
            sent_count = sum(1 for msg in chat_messages if msg['direction'] == '>')
            received_count = sum(1 for msg in chat_messages if msg['direction'] == '<')
            
            # Process each created file
            for filename, success, chunk_count in files_created:
                if success:
                    total_files += 1
                    total_chunks += chunk_count
                    
                    # Get file size safely
                    try:
                        pdf_path = os.path.join(Config.OUTPUT_DIR, filename)
                        file_size = os.path.getsize(pdf_path) / 1024
                    except:
                        file_size = 0
                    
                    # Determine if this is a multi-part file
                    is_multipart = 'part' in filename.lower()
                    part_info = ""
                    if is_multipart:
                        part_match = re.search(r'part(\d+)of(\d+)', filename.lower())
                        if part_match:
                            part_info = f" [Part {part_match.group(1)}/{part_match.group(2)}]"
                    
                    if Config.SHOW_PROGRESS:
                        print(f"   ✅ {filename}: {chunk_count} chunks ({file_size:.1f} KB){part_info}")
                    
                    # Add to summary for n8n
                    summary_data.append({
                        'filename': filename,
                        'person_name': person_info['person_name'],
                        'first_name': person_info['first_name'],
                        'last_name': person_info['last_name'],
                        'telegram_username': person_info['telegram_username'],
                        'original_chat': chat_name,
                        'is_multipart': is_multipart,
                        'chunk_count': chunk_count,
                        'file_size_kb': round(file_size, 1),
                        'total_messages_in_chat': len(chat_messages),
                        'sent_count': sent_count,
                        'received_count': received_count
                    })
                else:
                    if Config.SHOW_PROGRESS:
                        print(f"   ❌ {filename}: Failed to create PDF")
            
            # Summary for this chat
            if Config.SHOW_PROGRESS:
                if len(files_created) > 1:
                    total_size = sum(os.path.getsize(os.path.join(Config.OUTPUT_DIR, f[0])) / 1024 
                                   for f in files_created if f[1] and os.path.exists(os.path.join(Config.OUTPUT_DIR, f[0])))
                    print(f"   📊 Total: {len(chat_messages)} messages (Me:{sent_count}, From {person_info['person_name']}:{received_count}) → {len(files_created)} files ({total_size:.1f} KB)")
                else:
                    print(f"   📊 Total: {len(chat_messages)} messages (Me:{sent_count}, From {person_info['person_name']}:{received_count})")
        else:
            print(f"❌ {chat_name}: Failed to create any PDF files")
            skipped_count += 1
    
    # Save summary for n8n workflow
    try:
        metadata_path = os.path.join(Config.METADATA_DIR, Config.METADATA_FILE)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        print(f"📋 Metadata saved: {Config.METADATA_DIR}/{Config.METADATA_FILE}")
    except Exception as e:
        print(f"⚠️  Warning: Could not save metadata: {e}")
    
    # Final summary
    print(f"\n🎯 Processing completed successfully!")
    print(f"📁 Output location: {Config.OUTPUT_DIR}/ directory")
    print(f"📊 Results:")
    print(f"   ✅ Processed: {processed_count} chats")
    print(f"   ⚠️  Skipped: {skipped_count} chats")
    print(f"   📄 Created: {total_files} PDF files")
    print(f"   💬 Total messages: {total_messages}")
    print(f"   📦 Total chunks: {total_chunks}")
    
    if processed_count > 0:
        avg_messages_per_chat = total_messages / processed_count
        avg_chunks_per_file = total_chunks / total_files if total_files > 0 else 0
        print(f"   📈 Average: {avg_messages_per_chat:.1f} messages/chat, {avg_chunks_per_file:.1f} chunks/file")
    
    print(f"\n💡 Optimizations applied:")
    print(f"   ✅ Dynamic chunk sizing based on message length")
    print(f"   ✅ Memory-efficient processing")
    print(f"   ✅ Optimized file size management (max {Config.MAX_FILE_SIZE_KB}KB)")
    print(f"   ✅ Clean message format for n8n processing")
    print(f"   ✅ Enhanced error handling and progress tracking")
    print(f"   ✅ Emoji conversion and text normalization")
    
    print(f"\n🔧 n8n Integration Tips:")
    print(f"   1. Text Splitter settings: chunk_size=800, overlap=200")
    print(f"   2. Process files in batches of 5-8 for optimal memory usage")
    print(f"   3. Search patterns: 'Me:', 'From [NAME]:', person names")
    print(f"   4. Use {Config.METADATA_DIR}/{Config.METADATA_FILE} for person identification")
    print(f"   5. Vector dimensions: 1536 (OpenAI) or 768 (local models)")
    print(f"   6. Recommended embedding model: text-embedding-ada-002")
    print(f"   7. PDF text extraction: use 'pdf-parse' node before text splitter")
    
    # Show multipart files info
    large_chats = [item for item in summary_data if item['is_multipart']]
    if large_chats:
        print(f"\n⚠️  Large chats (split into multiple files):")
        multipart_chats = {}
        for item in large_chats:
            chat = item['original_chat']
            if chat not in multipart_chats:
                multipart_chats[chat] = 0
            multipart_chats[chat] += 1
        
        for chat, file_count in multipart_chats.items():
            print(f"   📂 {chat}: {file_count} parts")
    else:
        print(f"\n✅ All chats fit in single files (optimal for processing)")
    
    return True

if __name__ == "__main__":
    # Setup fonts for PDF generation
    setup_fonts()
    
    # Process chats with configuration settings
    if Config.VERBOSE_LOGGING:
        print(f"🔧 Configuration loaded:")
        print(f"   Input file: {Config.INPUT_FILE}")
        print(f"   Output directory: {Config.OUTPUT_DIR}")
        print(f"   Max file size: {Config.MAX_FILE_SIZE_KB}KB")
        print(f"   User: {Config.USER_NAME} (ID: {Config.USER_ID})")
        print(f"   Font: {Config.DEFAULT_FONT}")
        print()
    
    # Run the main processing function
    success = process_telegram_chats_optimized()
    
    if not success:
        print("\n❌ Processing failed!")
        exit(1)
    else:
        print("\n✅ All done! Ready for n8n processing.")
        if Config.VERBOSE_LOGGING:
            print(f"📁 Check {Config.OUTPUT_DIR}/ directory for generated PDFs")
            print(f"📋 Check {Config.METADATA_DIR}/{Config.METADATA_FILE} for processing metadata") 