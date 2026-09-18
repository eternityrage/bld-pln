import os
import json
import random
import requests

PUBLISHED_FILE = 'published_videos.json'

def load_published():
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE, 'r') as f:
            return json.load(f)
    return []

def save_published(data):
    with open(PUBLISHED_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_caption():
    pollinations_key = os.environ.get('POLLINATIONS_API_KEY', '')
    if not pollinations_key:
        return get_fallback_caption()

    prompt = (
        "Generate a short engaging social media caption for a construction/building plans page. "
        "The video shows architectural plans, building designs, or construction process. "
        "Include relevant hashtags. Keep it under 200 characters. "
        "Make it engaging and professional."
    )

    try:
        resp = requests.post(
            'https://text.pollinations.ai/',
            json={
                'messages': [{'role': 'user', 'content': prompt}],
                'model': 'openai',
                'seed': random.randint(1, 999999)
            },
            headers={'Authorization': f'Bearer {pollinations_key}'},
            timeout=30
        )
        if resp.status_code == 200:
            caption = resp.text.strip()
            if len(caption) > 200:
                caption = caption[:197] + '...'
            return caption
    except Exception as e:
        print(f"  [WARN] Pollinations failed: {e}")

    return get_fallback_caption()

def get_fallback_caption():
    captions = [
        "Building dreams one plan at a time #architecture #construction #buildingplans",
        "Every great structure starts with a great plan #blueprints #engineering",
        "Transforming visions into reality #architecturaldesign #construction",
        "Precision in every detail #buildingdesign #floorplan",
        "Where engineering meets artistry #architecture #constructionlife",
        "From blueprint to reality #buildingplans #construction",
        "Design. Build. Inspire. #architect #construction #building",
        "The foundation of greatness #architecture #engineering #design"
    ]
    return random.choice(captions)

def select_video(processed_videos, published):
    published_names = {p.get('filename') for p in published}
    unpublished = [v for v in processed_videos if os.path.basename(v) not in published_names]

    if unpublished:
        return random.choice(unpublished)

    # Repost: weighted random from already published
    if published:
        counts = {}
        for p in published:
            name = p.get('filename', '')
            counts[name] = counts.get(name, 0) + 1

        weights = [1000 // (3 ** min(counts.get(v, 0), 6)) for v in [p.get('filename') for p in published]]
        chosen = random.choices(published, weights=weights, k=1)[0]
        video_path = os.path.join('Processed_Videos', chosen['filename'])
        if os.path.exists(video_path):
            return video_path

    return None

def publish(video_path, publish_to_facebook=True, publish_to_instagram=False):
    results = []

    if publish_to_facebook:
        from upload.upload_facebook import upload_reel, upload_story
        caption = generate_caption()
        print(f"\n[CAPTION] {caption}")

        reel_result = upload_reel(video_path, caption)
        results.append(reel_result)

        story_result = upload_story(video_path)
        results.append(story_result)

    if publish_to_instagram:
        from upload.upload_instagram import upload_reel as ig_reel, upload_story as ig_story
        caption = generate_caption()
        print(f"\n[IG CAPTION] {caption}")

        reel_result = ig_reel(video_path, caption)
        results.append(reel_result)

        story_result = ig_story(video_path)
        results.append(story_result)

    return results

def run_daily_publish(processed_videos):
    published = load_published()
    video = select_video(processed_videos, published)

    if not video:
        print("[INFO] No videos available to publish")
        return []

    filename = os.path.basename(video)
    print(f"\n[PUBLISH] {filename}")

    results = publish(video, publish_to_facebook=True, publish_to_instagram=False)

    # Record
    entry = {
        'filename': filename,
        'results': results
    }
    published.append(entry)
    save_published(published)

    return results

if __name__ == '__main__':
    import glob
    processed = glob.glob('Processed_Videos/*.mp4') + glob.glob('Processed_Videos/*.mov')
    results = run_daily_publish(processed)
    print(f"\nPublish results: {len(results)} platforms")
