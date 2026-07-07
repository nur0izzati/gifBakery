import streamlit as st
import os
import subprocess
from PIL import Image

st.set_page_config(page_title="gifBakery", page_icon="🍞")
st.title("🍞 gifBakery")
st.write("Welcome to your personal GIF workshop. Bake fresh GIFs right in your browser!")

# --- HELPERS ---
def crop_to_square(img):
    """Crops an image from the center into a perfect square."""
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    return img.crop((left, top, right, bottom))

# --- FUNCTIONS ---
def compress_gif(input_img, quality, width=None, force_square=False):
    img = Image.open(input_img)
    output_path = "compressed.gif"
    
    frames = []
    for frame in range(0, img.n_frames):
        img.seek(frame)
        current_frame = img.copy()
        
        if force_square:
            current_frame = crop_to_square(current_frame)
            current_frame = current_frame.resize((width, width), Image.Resampling.LANCZOS)
        elif width and width > 0:
            w_percent = (width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            current_frame = current_frame.resize((width, h_size), Image.Resampling.LANCZOS)
            
        frames.append(current_frame)
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], optimize=True, colors=quality, loop=0)
    return output_path

def images_to_gif(uploaded_files, duration, width, force_square=False):
    frames = []
    for img_file in uploaded_files:
        img = Image.open(img_file)
        if force_square:
            img = crop_to_square(img)
            resized_img = img.resize((width, width), Image.Resampling.LANCZOS)
        else:
            w_percent = (width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            resized_img = img.resize((width, h_size), Image.Resampling.LANCZOS)
        frames.append(resized_img)
        
    output_path = "images_animation.gif"
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=duration, loop=0)
    return output_path

def video_to_gif(video_bytes, fps, width, force_square=False):
    with open("temp_video.mp4", "wb") as f:
        f.write(video_bytes.read())
    output_path = "video_animation.gif"
    
    vf_chain = f"fps={fps},"
    if force_square:
        vf_chain += f"crop='ih':'ih',scale={width}:{width}:flags=lanczos"
    else:
        vf_chain += f"scale={width}:-1:flags=lanczos"
        
    vf_chain += ",split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    
    ffmpeg_cmd = ['ffmpeg', '-y', '-i', 'temp_video.mp4', '-vf', vf_chain, output_path]
    subprocess.run(ffmpeg_cmd, check=True)
    return output_path

# --- UI TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ Compress GIF", "📸 Images to GIF", "🎬 Video to GIF"])

with tab1:
    st.header("Compress & Resize a GIF")
    uploaded_gif = st.file_uploader("Upload a GIF", type=["gif"], key="gif_comp")
    
    col1, col2 = st.columns(2)
    with col1:
        quality = st.slider("Quality (Colors)", 2, 256, 32, key="q_slide")
        make_square_1 = st.checkbox("Force into a 200x200 Square?", key="sq1")
    with col2:
        if make_square_1:
            gif_width = 200
            st.info("Dimensions locked to 200x200 square!")
        else:
            resize_choice = st.checkbox("Change size dimensions?")
            gif_width = st.number_input("New Width (Pixels)", min_value=100, max_value=2000, value=480) if resize_choice else None

    if uploaded_gif and st.button("Bake Compressed GIF"):
        out = compress_gif(uploaded_gif, quality, gif_width, force_square=make_square_1)
        st.success("Baked Successfully!")
        
        # --- PREVIEW WINDOW ---
        st.subheader("👀 Preview:")
        st.image(out)
        
        with open(out, "rb") as file:
            st.download_button("📥 Download your GIF", data=file, file_name="compressed.gif")

with tab2:
    st.header("Convert Images into a GIF")
    uploaded_imgs = st.file_uploader("Upload multiple images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Frame Speed (milliseconds)", min_value=100, max_value=2000, value=300)
        make_square_2 = st.checkbox("Force into a 200x200 Square?", key="sq2")
    with col2:
        if make_square_2:
            img_gif_width = 200
            st.info("Dimensions locked to 200x200 square!")
        else:
            img_gif_width = st.slider("Output GIF Width (Pixels)", 240, 1080, 480)
        
    if uploaded_imgs and st.button("Bake Image GIF"):
        out = images_to_gif(uploaded_imgs, duration, img_gif_width, force_square=make_square_2)
        st.success("Baked Successfully!")
        
        # --- PREVIEW WINDOW ---
        st.subheader("👀 Preview:")
        st.image(out)
        
        with open(out, "rb") as file:
            st.download_button("📥 Download your GIF", data=file, file_name="image_animation.gif")

with tab3:
    st.header("Convert Video into a GIF")
    uploaded_vid = st.file_uploader("Upload a video clip", type=["mp4", "mov", "avi"])
    
    col1, col2 = st.columns(2)
    with col1:
        fps = st.slider("Frames Per Second (FPS)", 5, 30, 12)
        make_square_3 = st.checkbox("Force into a 200x200 Square?", key="sq3")
    with col2:
        if make_square_3:
            width = 200
            st.info("Dimensions locked to 200x200 square!")
        else:
            width = st.slider("GIF Width (Pixels)", 240, 1080, 480)
        
    if uploaded_vid and st.button("Bake Video GIF"):
        try:
            out = video_to_gif(uploaded_vid, fps, width, force_square=make_square_3)
            st.success("Baked Successfully!")
            
            # --- PREVIEW WINDOW ---
            st.subheader("👀 Preview:")
            st.image(out)
            
            with open(out, "rb") as file:
                st.download_button("📥 Download your GIF", data=file, file_name="video_animation.gif")
        except Exception as e:
            st.error("Something went wrong with the video bakery process.")
