import os
import argparse
import subprocess
from PIL import Image

def compress_gif(input_path, output_path, quality=20):
    print(f"⚡ Compressing {input_path}...")
    with Image.open(input_path) as img:
        img.save(output_path, save_all=True, optimize=True, colors=quality)
    print(f"✅ Saved compressed GIF to: {output_path}\n")

def images_to_gif(image_folder, output_path, duration=500):
    print(f"📸 Converting images in '{image_folder}' to a GIF...")
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
    image_files = sorted([
        os.path.join(image_folder, f) for f in os.listdir(image_folder)
        if f.lower().endswith(valid_extensions)
    ])
    
    if not image_files:
        print("❌ Error: No valid images found in the folder!")
        return

    frames = [Image.open(img) for img in image_files]
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0
    )
    print(f"✅ Created GIF from images: {output_path}\n")

def video_to_gif(video_path, output_path, fps=12, width=480):
    print(f"🎬 Converting video {video_path} to GIF...")
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-vf', f'fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
        output_path
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"✅ Created GIF from video: {output_path}\n")
    except FileNotFoundError:
        print("❌ Error: FFmpeg is not installed or not in your system PATH.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ultimate GitHub GIF Tool")
    
    parser.add_argument("mode", choices=["compress", "img2gif", "vid2gif"], 
                        help="What do you want to do?")
    parser.add_argument("-i", "--input", required=True, 
                        help="Input file path or image folder path")
    parser.add_argument("-o", "--output", required=True, 
                        help="Output GIF file path")
    parser.add_argument("--quality", type=int, default=32, 
                        help="Compression quality (colors 2-256). Lower means smaller file. Default 32.")
    parser.add_argument("--duration", type=int, default=300, 
                        help="Duration per frame in milliseconds for img2gif. Default 300.")
    parser.add_argument("--fps", type=int, default=12, 
                        help="Frames per second for vid2gif. Default 12.")
    parser.add_argument("--width", type=int, default=480, 
                        help="Width of the output GIF for vid2gif. Default 480.")

    args = parser.parse_args()

    if args.mode == "compress":
        compress_gif(args.input, args.output, args.quality)
    elif args.mode == "img2gif":
        images_to_gif(args.input, args.output, args.duration)
    elif args.mode == "vid2gif":
        video_to_gif(args.input, args.output, args.fps, args.width)
