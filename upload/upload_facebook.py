import os
import requests
import json
import time

GRAPH_API_VERSION = 'v21.0'
GRAPH_URL = f'https://graph.facebook.com/{GRAPH_API_VERSION}'

def upload_reel(video_path, caption=""):
    page_token = os.environ.get('FB_PAGE_ACCESS_TOKEN', '')
    page_id = os.environ.get('FB_PAGE_ID', '')

    if not page_token or not page_id:
        print("[SKIP] Facebook credentials not set")
        return {'status': 'skipped', 'platform': 'facebook'}

    if not os.path.exists(video_path):
        print(f"[ERROR] Video not found: {video_path}")
        return {'status': 'failed', 'platform': 'facebook'}

    file_size = os.path.getsize(video_path)
    print(f"[FB] Uploading reel: {os.path.basename(video_path)} ({file_size / 1024 / 1024:.1f}MB)")

    # Step 1: Create video container
    init_url = f"{GRAPH_URL}/{page_id}/video_reels"
    init_data = {
        'upload_phase': 'start',
        'access_token': page_token
    }
    resp = requests.post(init_url, data=init_data)
    if resp.status_code != 200:
        print(f"  [ERROR] Init failed: {resp.text}")
        return {'status': 'failed', 'platform': 'facebook'}

    video_id = resp.json().get('video_id')
    upload_url = resp.json().get('upload_url')
    if not video_id or not upload_url:
        print(f"  [ERROR] No video_id or upload_url: {resp.json()}")
        return {'status': 'failed', 'platform': 'facebook'}

    print(f"  Container created: {video_id}")

    # Step 2: Transfer video bytes
    with open(video_path, 'rb') as f:
        video_data = f.read()

    transfer_headers = {
        'Authorization': f'OAuth {page_token}',
        'offset': '0',
        'file_size': str(file_size)
    }
    resp = requests.post(upload_url, headers=transfer_headers, data=video_data)
    if resp.status_code != 200:
        print(f"  [ERROR] Transfer failed: {resp.text}")
        return {'status': 'failed', 'platform': 'facebook'}

    print("  Video bytes transferred")

    # Step 3: Publish
    publish_url = f"{GRAPH_URL}/{page_id}/video_reels"
    publish_data = {
        'upload_phase': 'finish',
        'video_id': video_id,
        'access_token': page_token,
        'description': caption,
        'published': 'true'
    }
    resp = requests.post(publish_url, data=publish_data)
    if resp.status_code != 200:
        print(f"  [ERROR] Publish failed: {resp.text}")
        return {'status': 'failed', 'platform': 'facebook'}

    print(f"  Reel published: https://facebook.com/{page_id}/reels/{video_id}")
    return {'status': 'success', 'platform': 'facebook', 'video_id': video_id}


def upload_story(video_path):
    page_token = os.environ.get('FB_PAGE_ACCESS_TOKEN', '')
    page_id = os.environ.get('FB_PAGE_ID', '')

    if not page_token or not page_id:
        print("[SKIP] Facebook credentials not set")
        return {'status': 'skipped', 'platform': 'facebook_story'}

    if not os.path.exists(video_path):
        print(f"[ERROR] Video not found: {video_path}")
        return {'status': 'failed', 'platform': 'facebook_story'}

    file_size = os.path.getsize(video_path)
    print(f"[FB] Uploading story: {os.path.basename(video_path)} ({file_size / 1024 / 1024:.1f}MB)")

    # Step 1: Create story container
    init_url = f"{GRAPH_URL}/{page_id}/video_stories"
    init_data = {
        'upload_phase': 'start',
        'access_token': page_token
    }
    resp = requests.post(init_url, data=init_data)
    if resp.status_code != 200:
        print(f"  [ERROR] Story init failed: {resp.text}")
        return {'status': 'failed', 'platform': 'facebook_story'}

    video_id = resp.json().get('video_id')
    upload_url = resp.json().get('upload_url')
    if not video_id or not upload_url:
        print(f"  [ERROR] No story video_id: {resp.json()}")
        return {'status': 'failed', 'platform': 'facebook_story'}

    print(f"  Story container created: {video_id}")

    # Step 2: Transfer video bytes
    with open(video_path, 'rb') as f:
        video_data = f.read()

    transfer_headers = {
        'Authorization': f'OAuth {page_token}',
        'offset': '0',
        'file_size': str(file_size)
    }
    resp = requests.post(upload_url, headers=transfer_headers, data=video_data)
    if resp.status_code != 200:
        print(f"  [ERROR] Story transfer failed: {resp.text}")
        return {'status': 'failed', 'platform': 'facebook_story'}

    print("  Story bytes transferred")

    # Step 3: Publish story
    publish_url = f"{GRAPH_URL}/{page_id}/video_stories"
    publish_data = {
        'upload_phase': 'finish',
        'video_id': video_id,
        'access_token': page_token,
        'published': 'true'
    }
    resp = requests.post(publish_url, data=publish_data)
    if resp.status_code != 200:
        print(f"  [ERROR] Story publish failed: {resp.text}")
        return {'status': 'failed', 'platform': 'facebook_story'}

    print("  Story published")
    return {'status': 'success', 'platform': 'facebook_story'}
