import streamlit as st
import json
import os
from PIL import Image, ImageDraw, ImageFont

# Default values
DEFAULT_VALUES = {
    "text": "Sample Text",
    "text_color": "#FFFFFF",
    "font_size": 1.0,
    "font_family": "arial.ttf",
    "outline_color": "#000000",
    "outline_thickness": 1,
    "shadow_color": "#333333",
    "shadow_opacity": 0.5,
    "text_alignment": "center",
    "bg_color": "#B22222",
    "bg_opacity": 1.0,
    "highlight_color": "#FF0000",
    "highlight_bg_color": "#FFFF00",  # Highlight background color (default: yellow)
    "highlight_bg_opacity": 0.5,  # Highlight background opacity (default: 50%)
    "animation_type": "None",
    "animation_speed": 1.5
}

TEMPLATE_DIR = "Templates"
os.makedirs(TEMPLATE_DIR, exist_ok=True)

def hex_to_rgba(hex_color, opacity=1.0):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (r, g, b, int(opacity * 255))

def generate_preview(text, text_color, font_size, font_family, outline_color, outline_thickness, 
                     shadow_color, shadow_opacity, text_alignment, bg_color, bg_opacity,
                     highlight_color, highlight_bg_color, highlight_bg_opacity):
    width, height = 600, 150
    image = Image.new("RGBA", (width, height), hex_to_rgba(bg_color, bg_opacity))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype(font_family, int(font_size * 40))
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    if text_alignment == "center":
        text_x = (width - text_w) // 2
    elif text_alignment == "left":
        text_x = 20
    else:
        text_x = width - text_w - 20
    text_y = (height - text_h) // 2  
    
    # Draw highlight background
    highlight_padding = 10
    draw.rectangle(
        [(text_x - highlight_padding, text_y - highlight_padding),
         (text_x + text_w + highlight_padding, text_y + text_h + highlight_padding)],
        fill=hex_to_rgba(highlight_bg_color, highlight_bg_opacity)
    )
    
    # Draw shadow
    if shadow_opacity > 0:
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=shadow_color)
    
    # Draw outline
    for offset in [-outline_thickness, outline_thickness]:
        draw.text((text_x + offset, text_y), text, font=font, fill=outline_color)
        draw.text((text_x, text_y + offset), text, font=font, fill=outline_color)
    
    # Draw main text
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    return image

def template_designer_tool():
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        with st.expander("🎨 Text Design", expanded=True):
            text_color = st.color_picker("Text Color", DEFAULT_VALUES["text_color"])
            font_size = st.slider("Font Size", 0.5, 2.0, DEFAULT_VALUES["font_size"])
            font_family = st.selectbox("Font Family", ["arial.ttf", "times.ttf", "verdana.ttf", "cour.ttf"], index=0)
            outline_color = st.color_picker("Outline Color", DEFAULT_VALUES["outline_color"])
            outline_thickness = st.slider("Outline Thickness", 0, 5, DEFAULT_VALUES["outline_thickness"])
            shadow_color = st.color_picker("Shadow Color", DEFAULT_VALUES["shadow_color"])
            shadow_opacity = st.slider("Shadow Opacity", 0.0, 1.0, DEFAULT_VALUES["shadow_opacity"])
    
    with col2:
        with st.expander("📐 Content Positioning", expanded=True):
            text_alignment = st.selectbox("Text Alignment", ["left", "center", "right"], index=1)
            bg_color = st.color_picker("Background Color", DEFAULT_VALUES["bg_color"])
            bg_opacity = st.slider("Background Opacity", 0.0, 1.0, DEFAULT_VALUES["bg_opacity"])
    
    with col3:
        with st.expander("🎞 Animation Effects", expanded=True):
            highlight_color = st.color_picker("Highlight Color", DEFAULT_VALUES["highlight_color"])
            highlight_bg_color = st.color_picker("Highlight Background Color", DEFAULT_VALUES["highlight_bg_color"])
            highlight_bg_opacity = st.slider("Highlight Background Opacity", 0.0, 1.0, DEFAULT_VALUES["highlight_bg_opacity"])
            animation_type = st.selectbox("Animation Type", ["None", "Fade In", "Slide Up", "Bounce", "Typing Effect"], index=0)
            animation_speed = st.slider("Animation Speed", 0.5, 5.0, DEFAULT_VALUES["animation_speed"])
    
    preview_image = generate_preview(
        DEFAULT_VALUES["text"], text_color, font_size, font_family, outline_color, outline_thickness,
        shadow_color, shadow_opacity, text_alignment, bg_color, bg_opacity,
        highlight_color, highlight_bg_color, highlight_bg_opacity
    )
    
    st.subheader("🔍 Live Preview")
    st.write("Adjust settings and see real-time preview.")
    st.image(preview_image, use_container_width=True)
    st.write(f"**Selected Animation:** {animation_type} (Speed: {animation_speed}s)")
    
    # Save Template
    template_name = st.text_input("Template Name")  # Text input for template name
    if st.button("Save Template"):
        template_data = json.dumps({
            "text_design": {"text_color": text_color, "font_size": font_size, "font_family": font_family, "outline_color": outline_color, "outline_thickness": outline_thickness, "shadow_color": shadow_color, "shadow_opacity": shadow_opacity},
            "content_positioning": {"text_alignment": text_alignment, "bg_color": bg_color, "bg_opacity": bg_opacity},
            "animation_effects": {"highlight_color": highlight_color, "highlight_bg_color": highlight_bg_color, "highlight_bg_opacity": highlight_bg_opacity, "animation_type": animation_type, "animation_speed": animation_speed}
        }, indent=4)
        with open(f"{TEMPLATE_DIR}/template.json", "w") as f:
            f.write(template_data)
        st.success("Template saved successfully!")

template_designer_tool()
