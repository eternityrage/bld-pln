import os
import re
import json
import random
import requests
import datetime
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

PUBLISHED_FILE = 'published_videos.json'
YOUTUBE_STATE_FILE = 'youtube_publish_state.json'

# Allowed weekdays for YouTube: Monday (0), Wednesday (2), Friday (4), Sunday (6)
ALLOWED_YOUTUBE_WEEKDAYS = {0, 2, 4, 6}
WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}


# ==============================================================================
# ARCHITECTURAL & BUILDING PLANS KNOWLEDGE BASE
# ==============================================================================

ARCHITECTURAL_PLANS_DATABASE = {
    "isometric": {
        "category": "3D Isometric Floor Plan",
        "emoji": "📐✨",
        "focus": "3D cutaway visualization, spatial proportions, and seamless room-to-room circulation",
        "titles": [
            "Inside This Genius 3D Isometric Home Plan! 📐✨",
            "Next-Level 3D Floor Plan Visualization! 🏠🔥",
            "The Ultimate Isometric Cutaway Layout 📐🏡",
            "Watch This Blueprint Come to Life in 3D! 🏗️✨",
            "Is This the Most Satisfying Floor Plan Ever? 📐😍"
        ],
        "descriptions": [
            "Explore the perfect balance of aesthetic symmetry and spatial efficiency in this 3D isometric cutaway! From natural daylight pathways to seamless indoor-outdoor transitions, every square foot is masterfully engineered.\n\n🏡 Would you build this exact layout? Rate it 1-10 below!\n📐 Tag someone planning their dream home!\n\n#PlanViewLens #Architecture #FloorPlan #HouseDesign #BuildingPlans #Isometric #ArchitecturalDesign #InteriorDesign #3DDesign #HomeInspiration #Shorts #Reels",
            "Witness the flow of modern living! This 3D isometric perspective reveals how smart zoning and structural alignment maximize every square meter without sacrificing open space.\n\n💬 Drop your favorite room in this layout in the comments!\n👉 Follow @PlanViewLens for daily architectural inspiration and floor plans!\n\n#PlanViewLens #Architecture #FloorPlan #HouseDesign #BuildingPlans #Isometric #HomePlan #CivilEngineering #Construction #Shorts #Reels"
        ]
    },
    "floor_plan": {
        "category": "Architectural Floor Plan",
        "emoji": "🏠📐",
        "focus": "functional zoning, traffic flow efficiency, and modern spatial harmony",
        "titles": [
            "The Perfect Modern Floor Plan Breakdown! 🏠📐",
            "How to Design a Flawless Home Layout 🏡✨",
            "Smart Spatial Flow: Inside This Master Floor Plan 📐🔥",
            "Dream Home Floor Plan with Zero Wasted Space! 🏠💡",
            "Would You Live in This Modern Layout? 📐🤔"
        ],
        "descriptions": [
            "Notice the intuitive circulation and private-versus-communal zoning in this floor plan. By aligning service areas along structural cores, the living spaces remain airy, illuminated, and effortlessly functional.\n\n🏡 What's the one feature every dream home must have? Tell us below!\n📐 Tag a friend who loves architecture!\n\n#PlanViewLens #Architecture #FloorPlan #HouseDesign #BuildingPlans #CivilEngineering #ArchitecturalDesign #Construction #ModernHome #HomePlan #Shorts #Reels",
            "From entry vestibule to master sanctuary: see how circulation corridors are minimized to give you maximum usable living space. Clean lines, practical dimensions, and brilliant architectural design.\n\n💬 Rate this layout from 1 to 10 in the comments!\n👉 Follow @PlanViewLens for daily building designs!\n\n#PlanViewLens #Architecture #FloorPlan #HouseDesign #BuildingPlans #InteriorDesign #Blueprints #ConstructionLife #Shorts #Reels"
        ]
    },
    "architectural": {
        "category": "Architectural Blueprint & Design",
        "emoji": "🏛️📐",
        "focus": "structural elegance, architectural precision, and visionary blueprint design",
        "titles": [
            "From Blueprint to Masterpiece: Architectural Precision 🏛️✨",
            "Mastering Architectural Flow and Building Layouts 📐🔥",
            "The Art of Structural Blueprints Revealed! 🏛️📏",
            "Precision Engineering Meets Architectural Beauty 🏗️📐"
        ],
        "descriptions": [
            "Every landmark structure begins with an unwavering commitment to architectural precision. Observe how grid alignments, load paths, and aesthetic volumes coalesce into pure structural harmony.\n\n📐 Tag your favorite architect or engineer!\n💬 What's your architectural style: Modern Minimalist or Timeless Classic?\n\n#PlanViewLens #Architecture #Blueprints #BuildingPlans #CivilEngineering #ArchitecturalDesign #Construction #Engineering #Shorts #Reels",
            "Discover the intricate drafting and spatial planning behind this architectural concept. Built for durability, beauty, and elevated everyday living.\n\n🏡 Share this with anyone who appreciates great design!\n👉 Follow @PlanViewLens for daily architectural mastery!\n\n#PlanViewLens #Architecture #Blueprints #BuildingPlans #Architect #CivilEngineering #Construction #DesignInspiration #Shorts #Reels"
        ]
    },
    "villa": {
        "category": "Luxury Villa & Residence",
        "emoji": "🏡✨",
        "focus": "luxury living, expansive sightlines, and private courtyard integration",
        "titles": [
            "Inside This Modern Luxury Villa Blueprint! 🏡✨",
            "Luxury Living: The Ultimate Modern Villa Layout 🌴🏡",
            "Dream Villa Design with Breathtaking Spatial Flow 📐😍",
            "Architectural Luxury: Inside This Master Villa Plan 🏡🔥"
        ],
        "descriptions": [
            "This luxury villa layout combines expansive open-concept entertaining areas with secluded private suites. Large glazed facades invite natural light while preserving sanctuary privacy.\n\n🌴 Could you see yourself living in this villa? Let us know below!\n🏡 Tag someone who needs to see this dream home!\n\n#PlanViewLens #VillaDesign #Architecture #LuxuryHome #HouseDesign #FloorPlan #BuildingPlans #ModernVilla #Shorts #Reels"
        ]
    },
    "structural": {
        "category": "Structural Engineering & Construction",
        "emoji": "🏗️📐",
        "focus": "load-bearing columns, foundation integrity, and engineering mechanics",
        "titles": [
            "The Structural Engineering Behind Modern Architecture 🏗️📐",
            "Building Framework: How Modern Structures Stand Strong 🏗️💪",
            "Structural Integrity: The Hidden Science of Construction 📐⚙️"
        ],
        "descriptions": [
            "Before the finishes and furnishings, structural engineering defines the strength of every space. Notice the column grid distribution and shear wall placement ensuring lifetime stability.\n\n🏗️ Respect to the structural engineers who make bold architecture possible!\n💬 Comment your engineering discipline below!\n\n#PlanViewLens #CivilEngineering #StructuralEngineering #Construction #Architecture #BuildingPlans #Engineering #Shorts #Reels"
        ]
    }
}


def extract_video_subject(video_name: str) -> dict:
    """
    Identifies the architectural plan category and focus from filename.
    """
    clean_name = os.path.basename(video_name or "").lower()
    clean_name = re.sub(r'[_\-\.]', ' ', clean_name)

    for key, data in ARCHITECTURAL_PLANS_DATABASE.items():
        if key in clean_name:
            return data

    if "isometric" in clean_name:
        return ARCHITECTURAL_PLANS_DATABASE["isometric"]
    elif "floor" in clean_name or "plan" in clean_name:
        return ARCHITECTURAL_PLANS_DATABASE["floor_plan"]
    elif "architect" in clean_name:
        return ARCHITECTURAL_PLANS_DATABASE["architectural"]
    elif "villa" in clean_name or "house" in clean_name or "home" in clean_name:
        return ARCHITECTURAL_PLANS_DATABASE["villa"]
    elif "structur" in clean_name or "construct" in clean_name:
        return ARCHITECTURAL_PLANS_DATABASE["structural"]

    # General PlanView Lens default
    return {
        "category": "Modern Building Design & Floor Plan",
        "emoji": "📐🏡",
        "focus": "modern architectural design, space planning, and construction precision",
        "titles": [
            "Inside This Brilliant Architectural Floor Plan! 📐✨",
            "Smart Building Design & Modern Spatial Layout 🏡📐",
            "Where Engineering Precision Meets Architectural Art 🏗️✨",
            "The Ultimate Modern Living Layout Breakdown! 📐🔥"
        ],
        "descriptions": [
            "Explore the craftsmanship and intelligent space planning behind this modern architectural concept. From functional room transitions to balanced structural aesthetics, this layout is pure inspiration.\n\n🏡 Would you build this design? Drop a comment below!\n📐 Tag someone building or renovating their home!\n\n#PlanViewLens #Architecture #FloorPlan #HouseDesign #BuildingPlans #CivilEngineering #ArchitecturalDesign #Construction #Shorts #Reels"
        ]
    }


def generate_caption(video_name=None):
    """
    Generates a high-converting, matching title and description for PlanView Lens.
    """
    subject = extract_video_subject(video_name or "")
    category = subject.get("category", "Architectural Plan")
    focus = subject.get("focus", "modern building design and spatial efficiency")
    emoji = subject.get("emoji", "📐")

    fallback_titles = subject.get("titles") or [f"Modern Architectural Design Breakdown! {emoji}"]
    fallback_descriptions = subject.get("descriptions") or [
        f"Discover the spatial flow and engineering precision behind this {category.lower()}. Designed for seamless living and structural elegance.\n\n🏡 Would you build this? Comment below!\n\n#PlanViewLens #Architecture #FloorPlan #HouseDesign #BuildingPlans #Shorts #Reels"
    ]

    pollinations_key = os.environ.get('POLLINATIONS_API_KEY', '').strip()
    model = os.environ.get('AI_MODEL', 'gemini-fast').strip()

    if not pollinations_key:
        return random.choice(fallback_titles), random.choice(fallback_descriptions)

    vibes = [
        "informative, engaging, and professional architectural breakdown",
        "inspiring dream-home perspective focusing on modern spatial flow",
        "sharp engineering insight highlighting clever layout zoning"
    ]
    chosen_vibe = random.choice(vibes)

    prompt = (
        f"Write a compelling, professional title and engaging social media description for 'PlanView Lens' — "
        f"a page dedicated to architectural floor plans, building designs, blueprints, and construction.\n"
        f"Video Theme: {category} {emoji}.\n"
        f"Focus: {focus}.\n"
        f"Tone: {chosen_vibe}.\n\n"
        f"CRITICAL REQUIREMENTS:\n"
        f"1. TITLE: Extremely catchy hook under 70 characters with emoji (e.g. 'Inside This Genius 3D Home Plan! 📐✨').\n"
        f"2. DESCRIPTION: 3-4 professional, engaging sentences analyzing the design flow, room functionality, or architectural innovation.\n"
        f"3. CALL TO ACTION: Include an engaging question/CTA (e.g. 'Rate this layout 1-10 in the comments!', 'Tag someone designing their dream home!').\n"
        f"4. HASHTAGS: Include clean lowercase hashtags: #planviewlens #architecture #floorplan #housedesign #buildingplans #civilengineering #architecturaldesign #construction #interiordesign #shorts #reels.\n"
        f"5. OUTPUT FORMAT: Return ONLY a valid JSON object: {{\"title\": \"...\", \"description\": \"...\"}} without markdown backticks."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {pollinations_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "seed": random.randint(1, 999999)
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            raw_content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            clean_content = raw_content.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r'\{.*\}', clean_content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                gen_title = result.get("title", "").strip()
                gen_desc = result.get("description", "").strip()

                if gen_title and gen_desc:
                    if "#" not in gen_desc:
                        gen_desc = f"{gen_desc.rstrip()}\n\n#planviewlens #architecture #floorplan #housedesign #buildingplans #civilengineering #architecturaldesign #construction #interiordesign #shorts #reels"
                    print(f"✨ AI generated targeted caption for {category}!")
                    return gen_title, gen_desc
    except Exception as e:
        print(f"  [WARN] Pollinations caption generation notice: {e}")

    return random.choice(fallback_titles), random.choice(fallback_descriptions)


# ==============================================================================
# YOUTUBE PUBLISHING SCHEDULE (ALTERNATE DAYS & MAX ONCE A DAY)
# ==============================================================================

def load_published():
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_published(data):
    with open(PUBLISHED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def get_last_youtube_publish_date():
    """
    Finds the last date (datetime.date) on which a video was published to YouTube.
    First checks dedicated youtube_publish_state.json, then published_videos.json.
    """
    # 1. State file
    if os.path.exists(YOUTUBE_STATE_FILE):
        try:
            with open(YOUTUBE_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                d_str = state.get("last_published_date")
                if d_str:
                    return datetime.date.fromisoformat(d_str)
        except Exception as e:
            print(f"[youtube schedule] Notice reading {YOUTUBE_STATE_FILE}: {e}")

    # 2. published_videos.json
    published = load_published()
    for entry in reversed(published):
        yt_date_str = entry.get("youtube_published_at")
        results = entry.get("results", [])
        yt_success = any(r.get("platform") == "youtube" and r.get("status") == "success" for r in results)
        if yt_success and yt_date_str:
            try:
                return datetime.date.fromisoformat(yt_date_str[:10])
            except Exception:
                pass

    return None


def should_publish_to_youtube():
    """
    Strict YouTube Publishing Schedule for PlanView Lens:
    1. Publishes ONLY on Monday, Wednesday, Friday, and Sunday (4 times a week).
    2. Publishes at most ONCE per day on those allowed days.
    """
    today = datetime.datetime.now(datetime.timezone.utc).date()
    weekday = today.weekday()
    weekday_name = WEEKDAY_NAMES[weekday]

    # Check 1: Day of week constraint
    if weekday not in ALLOWED_YOUTUBE_WEEKDAYS:
        days_ahead = 1
        while (weekday + days_ahead) % 7 not in ALLOWED_YOUTUBE_WEEKDAYS:
            days_ahead += 1
        next_date = today + datetime.timedelta(days=days_ahead)
        next_day_name = WEEKDAY_NAMES[next_date.weekday()]
        return False, (
            f"Today is {weekday_name} ({today}). "
            f"Policy: YouTube publishes ONLY on Monday, Wednesday, Friday, and Sunday. "
            f"Next scheduled YouTube publish is {next_day_name} ({next_date})."
        )

    # Check 2: Max once a day constraint
    last_date = get_last_youtube_publish_date()
    if last_date is not None:
        if last_date == today:
            return False, f"YouTube has ALREADY published today ({weekday_name}, {today}). Policy: Maximum once a day on allowed days."
        if last_date > today:
            return False, f"Clock anomaly: Last YouTube publish recorded in future ({last_date}). Skipping YouTube upload."

    return True, f"Today is {weekday_name} ({today}) - scheduled YouTube publishing day! Ready to upload."


def record_youtube_publish(video_name, video_id=None):
    """Records the successful YouTube publication state."""
    today = datetime.datetime.now(datetime.timezone.utc).date()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    state = {
        "last_published_date": today.isoformat(),
        "last_published_at": now_iso,
        "last_video_name": video_name,
        "last_video_id": video_id or ""
    }
    try:
        with open(YOUTUBE_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)
        print(f"[youtube schedule] ✅ Recorded YouTube publish state for {today.isoformat()}")
    except Exception as e:
        print(f"[youtube schedule] ⚠️ Error saving {YOUTUBE_STATE_FILE}: {e}")


# ==============================================================================
# VIDEO SELECTION & MULTI-PLATFORM PUBLISHING
# ==============================================================================

def select_video(processed_videos, published):
    published_names = {p.get('filename') for p in published}
    unpublished = [v for v in processed_videos if os.path.basename(v) not in published_names]

    if unpublished:
        return random.choice(unpublished)

    # All published - weighted random from ALL processed videos
    if processed_videos:
        counts = {}
        for p in published:
            name = p.get('filename', '')
            counts[name] = counts.get(name, 0) + 1

        weights = []
        for v in processed_videos:
            name = os.path.basename(v)
            count = counts.get(name, 0)
            weight = max(1, 1000 // (3 ** min(count, 6)))
            weights.append(weight)

        chosen = random.choices(processed_videos, weights=weights, k=1)[0]
        return chosen

    return None


def publish(video_path, publish_to_facebook=True, publish_to_instagram=None, publish_to_youtube=True):
    results = []
    filename = os.path.basename(video_path)

    # Generate title and description matching the architectural video
    title, description = generate_caption(filename)
    combined_caption = f"{title}\n\n{description}" if title not in description else description

    print(f"\n[METADATA] Title: {title}")
    print(f"[METADATA] Description:\n{description}\n")

    # 1. Facebook Publishing (Reel & Story)
    if publish_to_facebook:
        from upload.upload_facebook import upload_reel, upload_story
        reel_result = upload_reel(video_path, caption=description, title=title)
        results.append(reel_result)

        story_result = upload_story(video_path)
        results.append(story_result)

    # 2. Instagram Publishing (Auto-detect if credentials configured)
    if publish_to_instagram is None:
        publish_to_instagram = bool(os.environ.get('INSTAGRAM_ACCOUNT_ID') or os.environ.get('IG_ACCOUNT_ID'))

    if publish_to_instagram:
        from upload.upload_instagram import upload_reel as ig_reel, upload_story as ig_story
        reel_result = ig_reel(video_path, caption=combined_caption, title=title)
        results.append(reel_result)

        story_result = ig_story(video_path)
        results.append(story_result)

    # 3. YouTube Shorts Publishing (Alternate Days & Max Once a Day)
    if publish_to_youtube:
        print("\n" + "-" * 40)
        print("🎬 CHECKING YOUTUBE PUBLISHING SCHEDULE (PlanView Lens)")
        print("-" * 40)
        yt_eligible, yt_reason = should_publish_to_youtube()

        if not yt_eligible:
            print(f"⏸️  YouTube Shorts SKIPPED: {yt_reason}")
            results.append({
                'status': 'skipped',
                'platform': 'youtube',
                'reason': yt_reason
            })
        else:
            print(f"✅ YouTube Shorts APPROVED: {yt_reason}")
            try:
                from upload.upload_to_youtube import upload_to_youtube

                # Title under 100 chars
                yt_title = title.strip()
                if "#Shorts" not in yt_title and "#shorts" not in yt_title:
                    if len(yt_title) + len(" #Shorts") <= 100:
                        yt_title = f"{yt_title} #Shorts"
                    else:
                        yt_title = yt_title[:91].rstrip() + " #Shorts"

                yt_tags = [
                    'planviewlens', 'architecture', 'floorplan', 'housedesign',
                    'buildingplans', 'civilengineering', 'architecturaldesign',
                    'construction', 'interiordesign', 'homeplan', 'shorts', 'fyp'
                ]

                yt_res = upload_to_youtube(
                    video_path=video_path,
                    title=yt_title,
                    description=description,
                    tags=yt_tags,
                    category_id='28'
                )

                if yt_res and yt_res.get('status') == 'success':
                    record_youtube_publish(filename, yt_res.get('id'))
                    results.append(yt_res)
                else:
                    err_msg = yt_res.get('error', 'Unknown error') if yt_res else 'Upload error'
                    print(f"❌ YouTube upload did not complete: {err_msg}")
                    results.append({
                        'status': 'failed',
                        'platform': 'youtube',
                        'error': err_msg
                    })
            except Exception as e:
                print(f"❌ YouTube upload failed with exception: {e}")
                results.append({
                    'status': 'failed',
                    'platform': 'youtube',
                    'error': str(e)
                })

    return results, title, description


def run_daily_publish(processed_videos):
    published = load_published()
    video = select_video(processed_videos, published)

    if not video:
        print("[INFO] No videos available to publish")
        return []

    filename = os.path.basename(video)
    print(f"\n[PUBLISH] Selected: {filename}")

    results, title, description = publish(
        video,
        publish_to_facebook=True,
        publish_to_instagram=None,
        publish_to_youtube=True
    )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    yt_success = any(r.get("platform") == "youtube" and r.get("status") == "success" for r in results)

    # Record full publication history
    entry = {
        'filename': filename,
        'title': title,
        'description': description,
        'published_at': now_iso,
        'youtube_published_at': now_iso if yt_success else None,
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
