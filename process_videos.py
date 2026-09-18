import os
import subprocess
import glob

def process_video(input_path, output_dir='Processed_Videos'):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, filename)

    if os.path.exists(output_path):
        print(f"[SKIP] Already processed: {filename}")
        return output_path

    print(f"[PROCESS] {filename}...")

    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,unsharp=3:3:0.8',
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart',
        '-t', '60',
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  Processed: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"  Error processing {filename}: {e.stderr}")
        return None

def process_all_videos():
    videos = glob.glob('Videos/*.mp4') + glob.glob('Videos/*.mov') + glob.glob('Videos/*.avi')
    if not videos:
        print("[INFO] No videos to process")
        return []

    processed = []
    for v in videos:
        result = process_video(v)
        if result:
            processed.append(result)

    return processed

if __name__ == '__main__':
    processed = process_all_videos()
    print(f"\nTotal videos processed: {len(processed)}")
