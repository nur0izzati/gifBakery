import streamlit as st
import os
import subprocess
from PIL import Image

st.set_page_config(page_title="gifBakery", page_icon="🍞")
st.title("🍞 gifBakery")
st.write("Welcome to your personal GIF workshop. Bake fresh GIFs right in your browser!")

# --- FUNCTIONS ---
def compress_gif(input_img, quality, width=None):
    img = Image.open(input_img)
    
    # If a custom width is set, resize the GIF frames while maintaining aspect ratio
    if width and width > 0:
        w_percent = (width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        
        frames = []
        for frame in range(0, img.n_frames):
            img.seek(frame)
            frames.append(img.resize((width, h_size), Image.Resampling.LANCZOS))
        
        output_path = "compressed.gif"
        frames[0].save(output_path, save_all=True, append_images=frames[1:], optimize=True, colors=quality, loop=0)
    else:
        # Standard compression without resizing
        output_path = "compressed.gif"
        img.save(output_path, save_all=True, optimize=True, colors=quality)
        
    return output_path

def images_to_gif(uploaded_files, duration, width):
    frames = []
    for img_file in uploaded_files:
        img = Image.open(img_file)
        # Resize images so they are all uniform size
        w_percent = (width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        resized_img = img.resize((width, h_size), Image.Resampling.LANCZOS)
        frames.append(resized_img)
        
    output_path = "images_animation.gif"
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=duration, loop=0)
    return output_path

def video_to_gif(video_bytes, fps, width):
    with open("temp_video.mp4", "wb") as f:
        f.write(video_bytes.read())
    output_path = "video_animation.gif"
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-i', 'temp_video.mp4',
        '-vf', f'fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
        output_path
    ]
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
    with col2:
        resize_choice = st.checkbox("Change size dimensions?")
        gif_width = st.number_input("New Width (Pixels)", min_value=100, max_value=2000, value=480) if resize_choice else None

    if uploaded_gif and st.button("Bake Compressed GIF"):
        out = compress_gif(uploaded_gif, quality, gif_width)
        st.success("Done!")
        with open(out, "rb") as file:
            st.download_button("📥 Download your GIF", data=file, file_name="compressed.gif")

with tab2:
    st.header("Convert Images into a GIF")
    uploaded_imgs = st.file_uploader("Upload multiple images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Frame Speed (milliseconds)", min_value=100, max_value=2000, value=300)
    with col2:
        img_gif_width = st.slider("Output GIF Width (Pixels)", 240, 1080, 480)
        
    if uploaded_imgs and st.button("Bake Image GIF"):
        out = images_to_gif(uploaded_imgs, duration, img_gif_width)
        st.success("Done!")
        with open(out, "rb") as file:
            st.download_button("📥 Download your GIF", data=file, file_name="image_animation.gif")

with tab3:
    st.header("Convert Video into a GIF")
    uploaded_vid = st.file_uploader("Upload a video clip", type=["mp4", "mov", "avi"])
    
    col1, col2 = st.columns(2)
    with col1:
        fps = st.slider("Frames Per Second (FPS)", 5, 30, 12)
    with col2:
        width = st.slider("GIF Width (Pixels)", 240, 1080, 480)
        
    if uploaded_vid and st.button("Bake Video GIF"):
        try:
            out = video_to_gif(uploaded_vid, fps, width)
            st.success("Done!")
            with open(out, "rb") as file:
                st.download_button("📥 Download your GIF", data=file, file_name="video_animation.gif")
        except Exception as e:
            st.error("Something went wrong with the video bakery process.")
