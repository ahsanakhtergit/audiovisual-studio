import streamlit as st
import cv2
import moviepy.editor as mp
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# ✅ Streamlit Page Config
st.set_page_config(page_title="MP4 Subtitle Animation Tool", layout="wide")

# ---------------- HELPER FUNCTIONS ---------------- #

def wrap_text(text, max_length=40):
    """ Wraps text into lines of a given max character length """
    words = text.split()
    lines, current_line = [], ""

    for word in words:
        if len(current_line) + len(word) + 1 > max_length:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line += word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines

def break_text_for_frames(subtitle, max_chars=40):
    """ Breaks text into multiple frames if exceeding max_chars """
    return [subtitle[i:i+max_chars] for i in range(0, len(subtitle), max_chars)]

def hex_to_bgr(hex_color):
    """Convert HEX color (#RRGGBB) to BGR tuple for OpenCV."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))  # Convert to BGR

def add_emoji(img, emoji, word_position, word_size, emoji_size_multiplier=1.5):
    """Adds an emoji as an image above the highlighted word using Twemoji PNG."""
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    # 🔥 Fetch Twemoji PNG Image
    emoji_img = get_twemoji_image(emoji)
    
    if emoji_img is None:
        print("❌ Emoji loading failed!")
        return img  # Return original if emoji not found
    
    # ⚡ Resize emoji based on word height
    emoji_size = int(word_size[1] * emoji_size_multiplier)
    emoji_img = emoji_img.resize((emoji_size, emoji_size), Image.ANTIALIAS)

    # 🟢 Adjust emoji position above the highlighted word
    emoji_x = word_position[0] + (word_size[0] // 2) - (emoji_size // 2)
    emoji_y = word_position[1] - (emoji_size + 10)  # Extra padding
    
    # 🔥 Paste emoji on image
    pil_img.paste(emoji_img, (emoji_x, emoji_y), emoji_img)

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def get_twemoji_image(emoji_char):
    """Fetches Twemoji PNG image for a given emoji character."""
    try:
        # 🟢 Get Twemoji PNG URL
        code = '-'.join(f"{ord(c):x}" for c in emoji_char)
        url = f"https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/{code}.png"
        
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)).convert("RGBA")
        
    except Exception as e:
        print("⚠️ Error in fetching emoji:", str(e))
    
    return None  # Return None if failed


def apply_subtitle_style(frame, segment, width, height, time_sec, template):
    """Applies animated subtitles to a video frame with emoji support."""
    img = frame.copy()
    img.setflags(write=1)

    # Debug: Print frame dimensions
    print(f"Debug: Frame dimensions = ({width}, {height})")

    # Extract settings from template with default values
    text_design = template.get("text_design", {})
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = text_design.get("font_size", 1.5)  # Default: 1.5
    thickness = text_design.get("stroke_thickness", 3)  # Default: 3
    font_color = hex_to_bgr(text_design.get("text_color", "#FFFFFF"))  # Default: White
    highlight_color = hex_to_bgr(text_design.get("highlight_color", "#FF0000"))  # Default: Red
    stroke_color = hex_to_bgr(text_design.get("stroke_color", "#000000"))  # Default: Black
    letter_spacing = text_design.get("letter_spacing", 0)  # Default: 0
    line_spacing = text_design.get("line_spacing", 1.2)  # Default: 1.2
    text_alignment = text_design.get("text_alignment", "center")  # Default: Center
    text_case = text_design.get("text_case", "none").lower()  # Default: No case transformation
    print(f"Debug: text_case = {text_case}")  # Debug: Print the text_case value


    content_positioning = template.get("content_positioning", {})
    padding_x = content_positioning.get("padding_x", 30)  # Default: 30
    padding_y = content_positioning.get("padding_y", 20)  # Default: 20
    show_box = content_positioning.get("show_box", False)  # Default: False
    max_line_chars = content_positioning.get("max_line_chars", 40)  # Default: 40
    multi_line = content_positioning.get("multi_line", False)  # Default: False
    box_vertical_position = content_positioning.get("box_vertical_position", 850)  # Default: 850

    emoji_config = template.get("emoji_config", {})
    emoji_path = emoji_config.get("emoji_path", None)  # Default: None
    emoji_scale = emoji_config.get("emoji_scale", 1.0)  # Default: 1.0
    emoji_opacity = emoji_config.get("emoji_opacity", 1.0)  # Default: 1.0
    emoji_position = emoji_config.get("emoji_position", "top-right")  # Default: top-right
    emoji_margin_x = emoji_config.get("emoji_margin_x", 10)  # Default: 10 (horizontal margin)
    emoji_margin_y = emoji_config.get("emoji_margin_y", 10)  # Default: 10 (vertical margin)

    # Load emoji image if provided
    emoji = None
    if emoji_path:
        if emoji_path.startswith(("http://", "https://")):
            # Download emoji from URL
            emoji = download_image_from_url(emoji_path)
        else:
            # Load emoji from local file
            emoji = cv2.imread(emoji_path, cv2.IMREAD_UNCHANGED)  # Load with alpha channel

        if emoji is None:
            print(f"Error: Emoji image not found at {emoji_path}")
        else:
            # Resize emoji based on scale
            if emoji_scale != 1.0:
                emoji = cv2.resize(emoji, None, fx=emoji_scale, fy=emoji_scale, interpolation=cv2.INTER_AREA)
            print(f"Debug: Emoji size after scaling = {emoji.shape}")  # Debug: Print emoji size

    # Ensure segment contains words
    if "words" not in segment:
        return img

    words = segment["words"]

    # Track highlighted words using index
    highlighted_indices = set()

    # Break text based on multi_line flag
    lines = []
    current_line = []
    line_start = None
    line_end = None

    for word in words:
        current_line.append(word)
        if line_start is None:
            line_start = word["start"]
        line_end = word["end"]

        text_preview = " ".join([w["word"] for w in current_line])

        if (multi_line and len(text_preview) > max_line_chars) or (not multi_line and len(text_preview) >= max_line_chars):
            lines.append({"text": text_preview, "start": line_start, "end": line_end})
            current_line = []
            line_start = None

    if current_line:
        text_preview = " ".join([w["word"] for w in current_line])
        lines.append({"text": text_preview, "start": line_start, "end": line_end})

    # Find the correct line for the current time
    active_line = None
    for line in lines:
        if line["start"] <= time_sec <= line["end"]:
            active_line = line
            break

    if not active_line:
        return img

    text_to_display = active_line["text"]
    print(f"DEBUG: Time {time_sec:.2f}s | Active Line: {text_to_display}")

    # Apply text case transformation
    if text_case == "uppercase":
        text_to_display = text_to_display.upper()
    elif text_case == "lowercase":
        text_to_display = text_to_display.lower()
    elif text_case == "capitalize":
        text_to_display = text_to_display.title()

    # Debug: Print the original and transformed text
    print(f"Debug: Original text = {active_line['text']}")
    print(f"Debug: Transformed text = {text_to_display}")

    # Calculate box & position
    num_lines = len(lines) if multi_line else 1
    text_height = int(35 * line_spacing * num_lines)

    # Find max text width among all lines
    max_text_width = max(cv2.getTextSize(line["text"], font, font_scale, thickness)[0][0] for line in lines)
    box_width = min(width - 100, max_text_width + 2 * padding_x)
    box_x_start = (width - box_width) // 2
    box_y_start = box_vertical_position

    # Debug: Print box position and size
    print(f"Debug: Box position = ({box_x_start}, {box_y_start}), Size = ({box_width}, {text_height})")

    # Draw background box
    if show_box:
        overlay = img.copy()
        cv2.rectangle(overlay,
                      (box_x_start, box_y_start),
                      (box_x_start + box_width, box_y_start + text_height + 2 * padding_y),
                      hex_to_bgr(content_positioning.get("bg_color", "#FFFF99")),  # Default: Yellow
                      -1)
        img = cv2.addWeighted(overlay, content_positioning.get("bg_opacity", 1.0), img, 1 - content_positioning.get("bg_opacity", 1.0), 0)

    # Animate word-by-word highlighting
    y = box_y_start + padding_y + int(35 * line_spacing / 2)

    for line_idx, line in enumerate(lines if multi_line else [active_line]):
        words_in_line = line["text"].split()

        # Calculate text width dynamically for alignment
        total_text_width = sum(cv2.getTextSize(word + " ", font, font_scale, thickness)[0][0] + letter_spacing for word in words_in_line) - letter_spacing

        if text_alignment == "left":
            x = box_x_start + padding_x
        elif text_alignment == "right":
            x = box_x_start + box_width - padding_x - total_text_width
        else:  # Center
            x = box_x_start + (box_width - total_text_width) // 2

        for word_idx, word in enumerate(words_in_line):
            # Apply text case transformation to each word
            word_text = word + " "
            if text_case == "uppercase":
                word_text = word_text.upper()
            elif text_case == "lowercase":
                word_text = word_text.lower()
            elif text_case == "capitalize":
                word_text = word_text.title()

            word_size = cv2.getTextSize(word_text, font, font_scale, thickness)[0]

            # Highlight only the first occurrence at the right time
            highlight = False
            for w_idx, w in enumerate(words):
                if w["word"].strip().lower() == word.strip().lower() and w["start"] <= time_sec <= w["end"]:
                    if w_idx not in highlighted_indices:  # Only highlight first occurrence
                        highlight = True
                        highlighted_indices.add(w_idx)
                    break  # Stop searching after finding the correct word

            color = highlight_color if highlight else font_color

            # Draw text with stroke
            cv2.putText(img, word_text, (x, y), font, font_scale, stroke_color, thickness + 2, cv2.LINE_AA)
            cv2.putText(img, word_text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

            x += word_size[0] + letter_spacing  # Move forward

        y += int(35 * line_spacing)  # Move to next line

    # Add emoji at a fixed position relative to the box
    if emoji is not None:
        emoji_height, emoji_width = emoji.shape[:2]

        # Calculate emoji position based on emoji_position parameter
        if emoji_position == "top-left":
            emoji_x = box_x_start + padding_x + emoji_margin_x
            emoji_y = box_y_start - emoji_height - emoji_margin_y
        elif emoji_position == "top-right":
            emoji_x = box_x_start + box_width - padding_x - emoji_width - emoji_margin_x
            emoji_y = box_y_start - emoji_height - emoji_margin_y
        elif emoji_position == "top-center":
            emoji_x = box_x_start + (box_width - emoji_width) // 2
            emoji_y = box_y_start - emoji_height - emoji_margin_y
        elif emoji_position == "bottom-left":
            emoji_x = box_x_start + padding_x + emoji_margin_x
            emoji_y = box_y_start + text_height + padding_y + emoji_margin_y
        elif emoji_position == "bottom-right":
            emoji_x = box_x_start + box_width - padding_x - emoji_width - emoji_margin_x
            emoji_y = box_y_start + text_height + padding_y + emoji_margin_y
        elif emoji_position == "bottom-center":
            emoji_x = box_x_start + (box_width - emoji_width) // 2
            emoji_y = box_y_start + text_height + padding_y + emoji_margin_y
        else:
            # Default to top-right if position is invalid
            emoji_x = box_x_start + box_width - padding_x - emoji_width - emoji_margin_x
            emoji_y = box_y_start - emoji_height - emoji_margin_y

        # Ensure emoji stays within frame bounds
        emoji_x = max(0, min(emoji_x, width - emoji_width))  # Clamp X position
        emoji_y = max(0, min(emoji_y, height - emoji_height))  # Clamp Y position

        # Debug: Print emoji position and size
        print(f"Debug: Emoji position = ({emoji_x}, {emoji_y}), Size = ({emoji_width}, {emoji_height})")

        # Overlay emoji with alpha blending
        if emoji_y >= 0 and emoji_x >= 0 and emoji_x + emoji_width <= width and emoji_y + emoji_height <= height:
            alpha_s = emoji[:, :, 3] / 255.0 * emoji_opacity  # Apply emoji opacity
            alpha_l = 1.0 - alpha_s
            for c in range(0, 3):
                img[emoji_y:emoji_y + emoji_height, emoji_x:emoji_x + emoji_width, c] = (
                    alpha_s * emoji[:, :, c] + alpha_l * img[emoji_y:emoji_y + emoji_height, emoji_x:emoji_x + emoji_width, c]
                )
            print("Debug: Emoji overlaid successfully.")
        else:
            print("Debug: Emoji is out of bounds and will not be displayed.")

    return img

# ---------------- MAIN PROCESSING FUNCTION ---------------- #

def mp4_subtitle_animation_tool():
    st.header("🎞 MP4 Subtitle Animation")
    st.write("Upload an MP4 file, an Audio JSON file, and select a subtitle style template.")

    uploaded_mp4 = st.file_uploader("Upload MP4 Video", type=["mp4"])
    uploaded_json = st.file_uploader("Upload Audio JSON File", type=["json"])

    templates = [f.replace(".json", "") for f in os.listdir("Templates") if f.endswith(".json")]
    selected_template = st.selectbox("Choose a subtitle template", ["Default"] + templates)

    if st.button("Generate Animated Subtitle Video"):
        if uploaded_mp4 and uploaded_json:
            st.success("Processing...")

            # Save uploaded files
            mp4_path, json_path = "input_video.mp4", "audio.json"
            with open(mp4_path, "wb") as f:
                f.write(uploaded_mp4.read())
            with open(json_path, "wb") as f:
                f.write(uploaded_json.read())

            # Load JSON subtitle data
            try:
                with open(json_path, "r") as f:
                    subtitle_data = json.load(f)
            except json.JSONDecodeError:
                st.error("Invalid JSON format.")
                return

            # Load selected template
            template = {}
            if selected_template != "Default":
                with open(os.path.join("Templates", f"{selected_template}.json"), "r") as f:
                    template = json.load(f)

            # Load video details
            video = mp.VideoFileClip(mp4_path)
            width, height, fps = int(video.w), int(video.h), int(video.fps)

            # Temporary output file
            temp_video_path = "temp_video.mp4"
            out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

            subtitle_queue = []
            active_segment = None

            # Process frames
            for frame in video.iter_frames(fps=fps, dtype="uint8"):
                img = frame.copy()
                img.setflags(write=1)
                time_sec = video.reader.pos / fps

                # Determine the active subtitle segment
                for segment in subtitle_data["segments"]:
                    if segment["start"] <= time_sec <= segment["end"]:
                        active_segment = segment
                        break

                if active_segment:
                    img = apply_subtitle_style(img, segment, width, height, time_sec, template)

                # Write processed frame
                out.write(img)

            # Release video writer
            out.release()
            st.success("Video processing completed. Merging with audio...")

            # Merge audio with processed video
            final_output = "output_video.mp4"
            processed_video = mp.VideoFileClip(temp_video_path)
            processed_video = processed_video.set_audio(video.audio)
            processed_video.write_videofile(final_output, codec="libx264", fps=fps)

            # Show result & download option
            if os.path.exists(final_output):
                st.success("Final video with subtitles is ready!")
                st.video(final_output)

                with open(final_output, "rb") as file:
                    video_bytes = file.read()
                st.download_button("Download Video", video_bytes, file_name="output_video.mp4", mime="video/mp4")
            else:
                st.error("Error: Video file was not generated.")

# Run the function
mp4_subtitle_animation_tool()

