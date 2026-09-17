"""
SocialPulse - MongoDB seed data generator

This script is written against the standard `pymongo` API and will run
unmodified against a real local/Atlas MongoDB instance. For local
grading/demo without a MongoDB server installed, set USE_MOCK=1 to
run against `mongomock` (an in-memory, pymongo-compatible engine,
including aggregation pipeline support) instead -- useful only for
verifying the logic, not a replacement for MongoDB in production.

Usage (real MongoDB):
    python3 seed_data.py

Usage (no local MongoDB server available):
    USE_MOCK=1 python3 seed_data.py
"""
import os
import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()
Faker.seed(7)
random.seed(7)

USE_MOCK = os.environ.get("USE_MOCK") == "1"

if USE_MOCK:
    import mongomock
    client = mongomock.MongoClient()
else:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")

db = client["socialpulse"]

NUM_USERS = 120          # mirrors SQL users (author_id / user_id map to users.user_id)
NUM_POSTS = 150
NUM_MEDIA = 110
COMMENTS_PER_POST_MAX = 6
NUM_LOGS = 300

EVENT_TYPES = ["like_post", "comment_post", "follow_user", "login", "share_post", "view_post"]
DEVICE_TYPES = ["ios", "android", "web", "desktop"]

# ---------------------------------------------------------------- reset --
for coll in ["posts", "comments", "media_metadata", "activity_logs"]:
    db[coll].delete_many({})

# --------------------------------------------------------- media_metadata --
media_docs = []
for i in range(1, NUM_MEDIA + 1):
    media_id = f"media_{i:06d}"
    mtype = random.choices(["image", "video"], weights=[80, 20])[0]
    owner_id = random.randint(1, NUM_USERS)
    created_at = fake.date_time_between(start_date="-2y", end_date="now")
    doc = {
        "media_id": media_id,
        "owner_id": owner_id,
        "type": mtype,
        "file": {
            "url": f"https://cdn.socialpulse.io/media/{media_id}.{'mp4' if mtype=='video' else 'jpg'}",
            "size_bytes": random.randint(80_000, 8_000_000),
            "format": "mp4" if mtype == "video" else random.choice(["jpg", "png"]),
        },
        "dimensions": {"width": random.choice([1080, 1920, 720]), "height": random.choice([1080, 1350, 1280])},
        "duration_seconds": random.randint(3, 60) if mtype == "video" else None,
        "exif": {
            "camera_model": fake.random_element(["iPhone 14 Pro", "iPhone 15", "Pixel 8", "Galaxy S23", None]),
            "taken_at": created_at,
        } if mtype == "image" else None,
        "moderation": {
            "status": random.choices(["approved", "pending", "flagged"], weights=[85, 10, 5])[0],
            "flagged_reason": None,
            "reviewed_by": "auto-moderator-v2",
        },
        "created_at": created_at,
    }
    media_docs.append(doc)
db["media_metadata"].insert_many(media_docs)

# -------------------------------------------------------------------- posts --
HASHTAG_POOL = ["#travel", "#food", "#photography", "#nature", "#music", "#fitness",
                "#art", "#tech", "#fashion", "#sunset", "#coding", "#pets"]

post_docs = []
post_ids = []
for i in range(1, NUM_POSTS + 1):
    post_id = f"post_{i:06d}"
    post_ids.append(post_id)
    author_id = random.randint(1, NUM_USERS)
    created_at = fake.date_time_between(start_date="-2y", end_date="now")
    has_media = random.random() < 0.7
    attached_media = []
    if has_media and media_docs:
        chosen = random.sample(media_docs, k=min(random.randint(1, 3), len(media_docs)))
        attached_media = [{"media_id": m["media_id"], "type": m["type"], "position": idx}
                           for idx, m in enumerate(chosen)]
    doc = {
        "post_id": post_id,
        "author_id": author_id,
        "caption": fake.sentence(nb_words=12),
        "hashtags": random.sample(HASHTAG_POOL, k=random.randint(0, 4)),
        "media": attached_media,
        "location": {
            "name": fake.city(),
            "coordinates": {"lat": float(fake.latitude()), "lng": float(fake.longitude())},
        } if random.random() < 0.4 else None,
        "visibility": random.choices(["public", "followers", "private"], weights=[75, 20, 5])[0],
        "like_count": random.randint(0, 500),
        "comment_count": 0,  # updated after comments are generated
        "share_count": random.randint(0, 50),
        "is_edited": random.random() < 0.1,
        "created_at": created_at,
        "updated_at": created_at,
    }
    post_docs.append(doc)
db["posts"].insert_many(post_docs)

# ----------------------------------------------------------------- comments --
comment_docs = []
comment_counter = 1
post_comment_counts = {p: 0 for p in post_ids}
for post in post_docs:
    n_comments = random.randint(0, COMMENTS_PER_POST_MAX)
    thread_ids = []
    for _ in range(n_comments):
        comment_id = f"cmt_{comment_counter:06d}"
        comment_counter += 1
        parent = random.choice(thread_ids) if thread_ids and random.random() < 0.3 else None
        created_at = post["created_at"] + timedelta(minutes=random.randint(1, 10000))
        comment_docs.append({
            "comment_id": comment_id,
            "post_id": post["post_id"],
            "author_id": random.randint(1, NUM_USERS),
            "parent_comment_id": parent,
            "text": fake.sentence(nb_words=8),
            "mentions": random.sample(range(1, NUM_USERS + 1), k=random.choice([0, 0, 1])),
            "like_count": random.randint(0, 40),
            "is_edited": False,
            "created_at": created_at,
        })
        thread_ids.append(comment_id)
        post_comment_counts[post["post_id"]] += 1

if comment_docs:
    db["comments"].insert_many(comment_docs)

# backfill comment_count on posts
for pid, count in post_comment_counts.items():
    db["posts"].update_one({"post_id": pid}, {"$set": {"comment_count": count}})

# ------------------------------------------------------------- activity_logs --
log_docs = []
for i in range(1, NUM_LOGS + 1):
    event = random.choice(EVENT_TYPES)
    user_id = random.randint(1, NUM_USERS)
    ts = fake.date_time_between(start_date="-1y", end_date="now")
    target_type, target_id = None, None
    if event in ("like_post", "comment_post", "share_post", "view_post") and post_docs:
        target_type = "post"
        target_id = random.choice(post_docs)["post_id"]
    elif event == "follow_user":
        target_type = "user"
        target_id = random.randint(1, NUM_USERS)

    log_docs.append({
        "log_id": f"log_{i:07d}",
        "user_id": user_id,
        "event_type": event,
        "target_type": target_type,
        "target_id": target_id,
        "metadata": {
            "device": random.choice(DEVICE_TYPES),
            "ip": fake.ipv4_public(),
            "app_version": f"{random.randint(3,5)}.{random.randint(0,20)}.0",
        },
        "timestamp": ts,
    })
db["activity_logs"].insert_many(log_docs)

print(f"posts: {db['posts'].count_documents({})}")
print(f"comments: {db['comments'].count_documents({})}")
print(f"media_metadata: {db['media_metadata'].count_documents({})}")
print(f"activity_logs: {db['activity_logs'].count_documents({})}")
