import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_secrets():
    required = ['META_LONG_LIVED_ACCESS_TOKEN', 'FB_PAGE_ID', 'FB_PAGE_ACCESS_TOKEN', 'GOOGLE_SERVICE_ACCOUNT_KEY']
    optional = ['POLLINATIONS_API_KEY', 'INSTAGRAM_ACCOUNT_ID']

    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"[ERROR] Missing required secrets: {', '.join(missing)}")
        sys.exit(1)

    for k in optional:
        if not os.environ.get(k):
            print(f"[WARN] Optional secret not set: {k} (some features may be skipped)")

    print("[OK] All required secrets found")

def main():
    print("=" * 50)
    print("PlanView Lens - Auto Pipeline")
    print("=" * 50)

    # Step 1: Check secrets
    check_secrets()

    # Step 2: Fetch videos from Google Drive
    print("\n--- Step 1: Fetching videos from Google Drive ---")
    from google_drive_fetch import fetch_videos
    new_videos = fetch_videos()
    print(f"New videos downloaded: {len(new_videos)}")

    # Step 3: Process videos
    print("\n--- Step 2: Processing videos ---")
    from process_videos import process_all_videos
    processed = process_all_videos()
    print(f"Videos processed: {len(processed)}")

    # Step 4: Publish
    print("\n--- Step 3: Publishing to platforms ---")
    from daily_publisher import run_daily_publish
    results = run_daily_publish(processed)

    # Summary
    print("\n" + "=" * 50)
    print("Pipeline Summary:")
    print(f"  Videos fetched:  {len(new_videos)}")
    print(f"  Videos processed: {len(processed)}")
    print(f"  Publish results:  {len(results)}")
    for r in results:
        status = r.get('status', 'unknown')
        platform = r.get('platform', 'unknown')
        print(f"    {platform}: {status}")
    print("=" * 50)

if __name__ == '__main__':
    main()
