import streamlit as st
import os
import subprocess
from PIL import Image

st.set_page_config(page_title="gifBakery", page_icon="🍞")
st.title("🍞 gifBakery")
st.write("Bake, customize, and preview your GIFs live before saving!")

# --- HELPERS ---
def crop_to_aspect(img, target_w, target_h):
    src_w, src_h = img.size
    target_aspect = target_w / target_h
    src_aspect = src_w / src_h

    if src_aspect > target_aspect:
        new_w = int(src_h * target_aspect)
        left = (src_w - new_w) / 2
        top = 0
        right = (src_w + new_w) / 2
        bottom = src_h
    else:
        new_h = int(src_w / target_aspect)
        left = 0
        top = (src_h - new_h) / 2
        right = src_w
        bottom = src_h + new_h

    cropped = img.crop((left, top, right, bottom))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

# --- FUNCTIONS ---
def compress_gif(input_img, quality, width, height, custom_size):
    img = Image.open(input_img)
    output_path = "temp_preview.gif"
    frames = []
    for frame in range(0, img.n_frames):
        img.seek(frame)
        current_frame = img.copy()
        if custom_size:
            current_frame = crop_to_aspect(current_frame, width, height)
        else:
            w_percent = (width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            current_frame = current_frame.resize((width, h_size), Image.Resampling.LANCZOS)
        frames.append(current_frame)
    frames[0].save(output_path, save_all=True, append_images=frames[1:], optimize=True, colors=quality, loop=0)
    return output_path

def images_to_gif(image_frames_list, duration, width, height, custom_size):
    frames = []
    for img in image_frames_list:
        if custom_size:
            resized_img = crop_to_aspect(img, width, height)
        else:
            w_percent = (width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            resized_img = img.resize((width, h_size), Image.Resampling.LANCZOS)
        frames.append(resized_img)
        
    output_path = "temp_preview.gif"
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=duration, loop=0)
    return output_path

def video_to_gif(video_bytes, fps, width, height, custom_size):
    with open("temp_video.mp4", "wb") as f:
        f.write(video_bytes.read())
    output_path = "video_preview_out.gif"
    if custom_size:
        vf_chain = f"fps={fps},crop='if(gte(iw/ih,{width}/{height}),ih*{width}/{height},iw)':'if(gte(iw/ih,{width}/{height}),ih,iw*{height}/{width})',scale={width}:{height}:flags=lanczos"
    else:
        vf_chain = f"fps={fps},scale={width}:-1:flags=lanczos"
    vf_chain += ",split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    ffmpeg_cmd = ['ffmpeg', '-y', '-i', 'temp_video.mp4', '-vf', vf_chain, output_path]
    subprocess.run(ffmpeg_cmd, check=True)
    return output_path

def show_size_guide(w, h):
    st.markdown(
        f"""
        <div style="background-color: #ffefe0; border: 2px dashed #ff9e42; border-radius: 8px;
        width: min(100%, {w}px); height: max(40px, min({h}px, 300px)); 
        display: flex; align-items: center; justify-content: center; color: #ff9e42; font-weight: bold; margin-bottom: 15px;">
        📐 Target Canvas Shape: {w} x {h}
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- UI TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ Compress GIF", "📸 Images to GIF", "🎬 Video to GIF"])

with tab1:
    st.header("Compress & Resize a GIF")
    uploaded_gif = st.file_uploader("Upload a GIF", type=["gif"], key="gif_comp")
    custom_size_1 = st.checkbox("Set custom Width and Height?", key="cs1")
    col1, col2 = st.columns(2)
    with col1:
        quality = st.slider("Quality (Colors)", 2, 256, 32, key="q_slide")
        gif_width = st.slider("Width (Pixels)", 100, 1200, 480, key="gw1")
    with col2:
        gif_height = st.slider("Height (Pixels)", 100, 1200, 480, key="gh1") if custom_size_1 else 480

    if uploaded_gif:
        if custom_size_1:
            show_size_guide(gif_width, gif_height)
        preview_file = compress_gif(uploaded_gif, quality, gif_width, gif_height, custom_size_1)
        st.subheader("👀 Live Edit Preview:")
        st.image(preview_file)
        with open(preview_file, "rb") as file:
            st.download_button("📥 Download GIF", data=file, file_name="baked_compressed.gif", key="dl_1")

with tab2:
    st.header("Convert Images into a GIF")
    uploaded_imgs = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_multi")
    
    # Initialize list to keep track of duplicated frames
    if 'frame_multipliers' not in st.session_state:
        st.session_state['frame_multipliers'] = {}

    if uploaded_imgs:
        st.write("---")
        st.write("📋 **Adjust Frame Repetitions:**")
        
        # Build final processing sequence based on user duplication inputs
        final_frames_list = []
        
        for i, img_file in enumerate(uploaded_imgs):
            file_id = f"{img_file.name}_{i}"
            if file_id not in st.session_state['frame_multipliers']:
                st.session_state['frame_multipliers'][file_id] = 1
                
            col_img, col_btn = st.columns([3, 1])
            with col_img:
                st.write(f"🖼️ `{img_file.name}` (Repeated: {st.session_state['frame_multipliers'][file_id]}x)")
            with col_btn:
                if st.button("➕ Duplicate", key=f"btn_{file_id}"):
                    st.session_state['frame_multipliers'][file_id] += 1
                    st.rerun()
            
            # Append the actual image object multiplied by the requested copies
            pil_obj = Image.open(img_file)
            for _ in range(st.session_state['frame_multipliers'][file_id]):
                final_frames_list.append(pil_obj)
                
        st.write("---")
        
        custom_size_2 = st.checkbox("Set custom Width and Height?", key="cs2")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Frame Speed (ms)", min_value=100, max_value=2000, value=300)
            img_width = st.slider("Output Width", 100, 1200, 480, key="iw2")
        with col2:
            img_height = st.slider("Output Height", 100, 1200, 480, key="ih2") if custom_size_2 else 480
            
        if custom_size_2:
            show_size_guide(img_width, img_height)
            
        preview_file = images_to_gif(final_frames_list, duration, img_width, img_height, custom_size_2)
        st.subheader("👀 Live Edit Preview:")
        st.image(preview_file)
        with open(preview_file, "rb") as file:
            st.download_button("📥 Download GIF", data=file, file_name="baked_image_animation.gif", key="dl_2")

with tab3:
    st.header("Convert Video into a GIF")
    uploaded_vid = st.file_uploader("Upload a video clip", type=["mp4", "mov", "avi"])
    if uploaded_vid:
        st.subheader("🎬 Your Uploaded Source Video:")
        st.video(uploaded_vid)
    custom_size_3 = st.checkbox("Set custom Width and Height?", key="cs3")
    col1, col2 = st.columns(2)
    with col1:
        fps = st.slider("Frames Per Second (FPS)", 5, 30, 12)
        vid_width = st.slider("GIF Width", 100, 1200, 480, key="vw3")
    with col2:
        vid_height = st.slider("GIF Height", 100, 1200, 480, key="vh3") if custom_size_3 else 480
        
    if uploaded_vid:
        if custom_size_3:
            show_size_guide(vid_width, vid_height)
        if st.button("🔄 Bake & Preview GIF Output"):
            try:
                preview_file = video_to_gif(uploaded_vid, fps, vid_width, vid_height, custom_size_3)
                st.session_state['baked_vid_path'] = preview_file
            except Exception as e:
                st.error("Error processing video.")
        if 'baked_vid_path' in st.session_state and os.path.exists(st.session_state['baked_vid_path']):
            st.subheader("👀 Final GIF Result Preview:")
            st.image(st.session_state['baked_vid_path'])
            with open(st.session_state['baked_vid_path'], "rb") as file:
                st.download_button("📥 Download GIF", data=file, file_name="baked_video_animation.gif", key="dl_3")
