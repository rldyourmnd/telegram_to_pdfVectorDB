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
        # Try to register fonts for Cyrillic support (Windows/macOS/Linux)
        font_paths = [
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            'C:/Windows/Fonts/tahoma.ttf',
            '/System/Library/Fonts/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        ]
        
        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('CyrillicFont', font_path))
                    font_registered = True
                    print(f"Using font: {font_path}")
                    break
                except Exception as e:
                    continue
        
        if not font_registered:
            print("Warning: No suitable font found for Cyrillic, using default (may show squares)")
            return 'Helvetica'
        
        return 'CyrillicFont'
    except Exception as e:
        print(f"Font setup error: {e}")
        return 'Helvetica'

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

def create_optimized_pdf_parts(chat_name, messages, output_dir, max_size_kb=200):
    """Create multiple PDF files if chat is too large, optimized for n8n processing"""
    person_info = extract_person_info(chat_name, messages)
    person_name = person_info['person_name']
    total_messages = len(messages)
    
    # Setup font for Cyrillic text
    font_name = setup_fonts()
    
    # Optimized chunk sizing based on content analysis - ADJUSTED for 200KB target
    avg_msg_length = sum(len(msg.get('text', '')) for msg in messages) / max(len(messages), 1)
    
    # Further reduced chunk sizes to reach 200KB target
    if avg_msg_length < 50:
        chunk_size = 25   # Reduced from 30
    elif avg_msg_length < 150:
        chunk_size = 18   # Reduced from 20  
    else:
        chunk_size = 12   # Reduced from 15
    
    # More conservative estimation for 200KB files
    estimated_kb_per_chunk = max(1.2, avg_msg_length * 0.005)  # Further reduced multiplier
    max_chunks_per_file = int((max_size_kb * 0.8) / estimated_kb_per_chunk)  # 80% target for more safety
    max_chunks_per_file = max(12, min(max_chunks_per_file, 100))  # Lower bounds
    
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
                # Optimized text cleaning - shorter text length for 200KB files
                text = re.sub(r'\s+', ' ', text)
                text = text[:500]  # Reduced from 600 to 500
                
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
                           rightMargin=40, leftMargin=40,
                           topMargin=40, bottomMargin=40,
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
        fontSize=10,
        spaceAfter=4,
        leftIndent=0,
        rightIndent=0,
        leading=12
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
        print(f"Error creating PDF for {chat_name}: {e}")
        return False, 0

def process_telegram_chats_optimized(input_file='result.json'):
    """Main function to process Telegram chats and create optimized PDFs for n8n"""
    print("Creating optimized PDFs for n8n processing (max 200KB per file)...")
    
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
    
    # Create output directory
    try:
        os.makedirs('chats_clean_pdf', exist_ok=True)
    except Exception as e:
        print(f"❌ Error creating output directory: {e}")
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
            print(f"⚠️  Skipping {chat_name}: No messages found")
            skipped_count += 1
            continue
        
        print(f"🔄 Processing [{idx}/{len(chat_list)}]: {chat_name} ({len(messages)} messages)")
        
        chat_messages = []
        
        # Extract and process messages with optimization
        for msg in messages:
            if msg.get('type') != 'message':
                continue
            
            text_content = extract_text_content(msg)
            if not text_content or len(text_content.strip()) < 2:  # Skip very short messages
                continue
            
            # Determine message direction (sent by me or received)
            sender = msg.get('from', 'Unknown')
            sender_id = msg.get('from_id', '')
            
            # Check if message was sent by me (Danil) or received from chat partner
            is_from_me = (sender and 'Danil' in sender) or sender_id == 'user904048578'
            direction = '>' if is_from_me else '<'
            
            # Store essential data with direction
            chat_msg = {
                'text': text_content,
                'direction': direction
            }
            chat_messages.append(chat_msg)
        
        if not chat_messages:
            print(f"⚠️  Skipping {chat_name}: No valid messages after processing")
            skipped_count += 1
            continue
        
        # Create clean PDF files (potentially multiple parts)
        try:
            files_created = create_optimized_pdf_parts(chat_name, chat_messages, 'chats_clean_pdf')
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
                        pdf_path = os.path.join('chats_clean_pdf', filename)
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
                    print(f"   ❌ {filename}: Failed to create PDF")
            
            # Summary for this chat
            if len(files_created) > 1:
                total_size = sum(os.path.getsize(os.path.join('chats_clean_pdf', f[0])) / 1024 
                               for f in files_created if f[1] and os.path.exists(os.path.join('chats_clean_pdf', f[0])))
                print(f"   📊 Total: {len(chat_messages)} messages (Me:{sent_count}, From {person_info['person_name']}:{received_count}) → {len(files_created)} files ({total_size:.1f} KB)")
            else:
                print(f"   📊 Total: {len(chat_messages)} messages (Me:{sent_count}, From {person_info['person_name']}:{received_count})")
        else:
            print(f"❌ {chat_name}: Failed to create any PDF files")
            skipped_count += 1
    
    # Save summary for n8n workflow
    try:
        with open('chats_clean_pdf/metadata_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        print(f"📋 Metadata saved: metadata_summary.json")
    except Exception as e:
        print(f"⚠️  Warning: Could not save metadata: {e}")
    
    # Final summary
    print(f"\n🎯 Processing completed successfully!")
    print(f"📁 Output location: chats_clean_pdf/ directory")
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
    print(f"   ✅ Optimized file size management (max 200KB)")
    print(f"   ✅ Clean message format for n8n processing")
    print(f"   ✅ Enhanced error handling and progress tracking")
    print(f"   ✅ Emoji conversion and text normalization")
    
    print(f"\n🔧 n8n Integration Tips:")
    print(f"   1. Text Splitter settings: chunk_size=800, overlap=200")
    print(f"   2. Process files in batches of 5-8 for optimal memory usage")
    print(f"   3. Search patterns: 'Me:', 'From [NAME]:', person names")
    print(f"   4. Use metadata_summary.json for person identification")
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
    process_telegram_chats_optimized() 