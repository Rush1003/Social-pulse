"""
SocialPulse - MongoDB functional queries
CRUD, retrieval, and aggregation pipeline demonstrations.

Run against real MongoDB:      python3 queries.py
Run against local mongita:     USE_MONGITA=1 python3 queries.py
"""
import os
from datetime import datetime, timedelta
from pprint import pprint

USE_MONGITA = os.environ.get("USE_MONGITA") == "1"

if USE_MONGITA:
    from mongita import MongitaClientDisk
    client = MongitaClientDisk("/home/claude/social-pulse/nosql/mongita_store")
else:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")

db = client["socialpulse"]

def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# =====================================================================
# SECTION 1: CREATE
# =====================================================================
banner("1.1 CREATE - Insert a new post")
new_post = {
    "post_id": "post_000999",
    "author_id": 1,
    "caption": "Testing the SocialPulse NoSQL layer!",
    "hashtags": ["#test", "#coding"],
    "media": [],
    "location": None,
    "visibility": "public",
    "like_count": 0,
    "comment_count": 0,
    "share_count": 0,
    "is_edited": False,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}
result = db["posts"].insert_one(new_post)
print("Inserted post with _id:", result.inserted_id)

banner("1.2 CREATE - Insert a comment on that post")
new_comment = {
    "comment_id": "cmt_000999",
    "post_id": "post_000999",
    "author_id": 2,
    "parent_comment_id": None,
    "text": "Nice work!",
    "mentions": [],
    "like_count": 0,
    "is_edited": False,
    "created_at": datetime.utcnow(),
}
db["comments"].insert_one(new_comment)
db["posts"].update_one({"post_id": "post_000999"}, {"$inc": {"comment_count": 1}})
print("Comment inserted and post comment_count incremented.")


# =====================================================================
# SECTION 2: READ / RETRIEVAL
# =====================================================================
banner("2.1 READ - Fetch a single post by post_id")
pprint(db["posts"].find_one({"post_id": "post_000999"}))

banner("2.2 READ - A user's feed: latest 5 public posts by author_id")
cursor = db["posts"].find(
    {"author_id": 1, "visibility": "public"}
).sort("created_at", -1).limit(5)
for doc in cursor:
    print(doc["post_id"], "-", doc["caption"][:50])

banner("2.3 READ - All top-level comments on a post, oldest first")
cursor = db["comments"].find(
    {"post_id": "post_000001", "parent_comment_id": None}
).sort("created_at", 1)
for doc in cursor:
    print(doc["comment_id"], "-", doc["text"])

banner("2.4 READ - Posts tagged with a specific hashtag")
cursor = db["posts"].find({"hashtags": "#sunset"}).limit(5)
for doc in cursor:
    print(doc["post_id"], doc["hashtags"])

banner("2.5 READ - Media pending moderation review")
cursor = db["media_metadata"].find({"moderation.status": "pending"}).limit(5)
for doc in cursor:
    print(doc["media_id"], doc["type"], doc["moderation"]["status"])

banner("2.6 READ - Recent activity log for a specific user")
cursor = db["activity_logs"].find({"user_id": 1}).sort("timestamp", -1).limit(5)
for doc in cursor:
    print(doc["log_id"], doc["event_type"], doc["timestamp"])

banner("2.7 READ - Search posts by keyword in caption (case-insensitive)")
cursor = db["posts"].find(
    {"caption": {"$regex": "beach", "$options": "i"}}
).limit(5)
for doc in cursor:
    print(doc["post_id"], "-", doc["caption"][:60])

banner("2.8 READ - Posts that carry a geo-location (map/near-me view)")
cursor = db["posts"].find({"location": {"$ne": None}}).limit(5)
for doc in cursor:
    print(doc["post_id"], doc.get("location"))


# =====================================================================
# SECTION 3: UPDATE
# =====================================================================
banner("3.1 UPDATE - Edit a post's caption")
db["posts"].update_one(
    {"post_id": "post_000999"},
    {"$set": {"caption": "Testing the SocialPulse NoSQL layer! (edited)",
              "is_edited": True, "updated_at": datetime.utcnow()}}
)
print("Post caption updated.")

banner("3.2 UPDATE - Like a post (atomic increment)")
db["posts"].update_one({"post_id": "post_000999"}, {"$inc": {"like_count": 1}})
print("like_count incremented.")

banner("3.3 UPDATE - Approve a flagged media item")
db["media_metadata"].update_many(
    {"moderation.status": "pending"},
    {"$set": {"moderation.status": "approved", "moderation.reviewed_by": "manual-review-team"}}
)
print("Pending media items approved.")

banner("3.4 UPDATE - Add a hashtag to a post without duplicating it")
try:
    # $addToSet is standard MongoDB syntax; the lightweight `mongita`
    # engine used for local demoing has a smaller operator set and
    # falls back to $push here (harmless for this single-run demo).
    db["posts"].update_one(
        {"post_id": "post_000999"},
        {"$addToSet": {"hashtags": "#mongodb"}}
    )
    print("Hashtag added via $addToSet.")
except Exception:
    db["posts"].update_one(
        {"post_id": "post_000999"},
        {"$push": {"hashtags": "#mongodb"}}
    )
    print("Hashtag added via $push (mongita fallback; use $addToSet on real MongoDB).")

banner("3.5 UPDATE - Soft-delete a post (flag instead of hard delete)")
db["posts"].update_one(
    {"post_id": "post_000002"},
    {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
)
print("Post soft-deleted (is_deleted flag set; document kept for audit/undo).")

banner("3.6 UPDATE - Increment share_count when a post is shared")
db["posts"].update_one({"post_id": "post_000003"}, {"$inc": {"share_count": 1}})
print("share_count incremented.")


# =====================================================================
# SECTION 4: DELETE
# =====================================================================
banner("4.1 DELETE - Remove a single comment")
db["comments"].delete_one({"comment_id": "cmt_000999"})
print("Comment deleted.")

banner("4.2 DELETE - Purge activity logs older than 1 year (retention policy)")
cutoff = datetime.utcnow() - timedelta(days=365)
result = db["activity_logs"].delete_many({"timestamp": {"$lt": cutoff}})
print(f"Deleted {result.deleted_count} old log entries.")

banner("4.3 DELETE - Remove a post and its dependent comments (manual cascade)")
db["comments"].delete_many({"post_id": "post_000999"})
db["posts"].delete_one({"post_id": "post_000999"})
print("Post and its comments removed.")

banner("4.4 DELETE - Purge old flagged media metadata past the review window")
cutoff = datetime.utcnow() - timedelta(days=90)
result = db["media_metadata"].delete_many(
    {"moderation.status": "flagged", "created_at": {"$lt": cutoff}}
)
print(f"Deleted {result.deleted_count} flagged media items.")


# =====================================================================
# SECTION 5: AGGREGATION PIPELINES
# =====================================================================
banner("5.1 AGGREGATE - Top 5 most-liked posts")
pipeline = [
    {"$sort": {"like_count": -1}},
    {"$limit": 5},
    {"$project": {"_id": 0, "post_id": 1, "author_id": 1, "like_count": 1, "comment_count": 1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.2 AGGREGATE - Post count and average likes per author")
pipeline = [
    {"$group": {
        "_id": "$author_id",
        "post_count": {"$sum": 1},
        "avg_likes": {"$avg": "$like_count"},
        "total_shares": {"$sum": "$share_count"},
    }},
    {"$sort": {"post_count": -1}},
    {"$limit": 10},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.3 AGGREGATE - Most-used hashtags platform-wide")
pipeline = [
    {"$unwind": "$hashtags"},
    {"$group": {"_id": "$hashtags", "usage_count": {"$sum": 1}}},
    {"$sort": {"usage_count": -1}},
    {"$limit": 10},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.4 AGGREGATE - Event type distribution in activity_logs")
pipeline = [
    {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]
for doc in db["activity_logs"].aggregate(pipeline):
    print(doc)

banner("5.5 AGGREGATE - Media storage usage by type (image vs video)")
pipeline = [
    {"$group": {
        "_id": "$type",
        "count": {"$sum": 1},
        "total_bytes": {"$sum": "$file.size_bytes"},
        "avg_bytes": {"$avg": "$file.size_bytes"},
    }},
]
for doc in db["media_metadata"].aggregate(pipeline):
    print(doc)

banner("5.6 AGGREGATE - Posts joined with their comment authors ($lookup)")
pipeline = [
    {"$match": {"comment_count": {"$gt": 0}}},
    {"$limit": 3},
    {"$lookup": {
        "from": "comments",
        "localField": "post_id",
        "foreignField": "post_id",
        "as": "post_comments",
    }},
    {"$project": {"_id": 0, "post_id": 1, "comment_count": 1,
                  "sample_comment": {"$arrayElemAt": ["$post_comments.text", 0]}}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.7 AGGREGATE - Daily post volume trend (last 30 days)")
pipeline = [
    {"$match": {"created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}}},
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
        "posts_created": {"$sum": 1},
    }},
    {"$sort": {"_id": 1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.8 AGGREGATE - Top 10 most active users by total activity events")
pipeline = [
    {"$group": {"_id": "$user_id", "event_count": {"$sum": 1}}},
    {"$sort": {"event_count": -1}},
    {"$limit": 10},
]
for doc in db["activity_logs"].aggregate(pipeline):
    print(doc)

banner("5.9 AGGREGATE - Weighted virality score (likes + 2*comments + 3*shares)")
pipeline = [
    {"$addFields": {
        "virality_score": {
            "$add": [
                "$like_count",
                {"$multiply": ["$comment_count", 2]},
                {"$multiply": ["$share_count", 3]},
            ]
        }
    }},
    {"$sort": {"virality_score": -1}},
    {"$limit": 10},
    {"$project": {"_id": 0, "post_id": 1, "like_count": 1, "comment_count": 1,
                  "share_count": 1, "virality_score": 1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.10 AGGREGATE - Visibility distribution across all posts (%)")
pipeline = [
    {"$group": {"_id": "$visibility", "count": {"$sum": 1}}},
    {"$group": {"_id": None, "breakdown": {"$push": {"visibility": "$_id", "count": "$count"}},
                "total": {"$sum": "$count"}}},
    {"$unwind": "$breakdown"},
    {"$project": {
        "_id": 0,
        "visibility": "$breakdown.visibility",
        "count": "$breakdown.count",
        "percentage": {"$round": [{"$multiply": [{"$divide": ["$breakdown.count", "$total"]}, 100]}, 1]},
    }},
    {"$sort": {"count": -1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.11 AGGREGATE - Average caption length grouped by visibility")
pipeline = [
    {"$project": {"visibility": 1, "caption_len": {"$strLenCP": "$caption"}}},
    {"$group": {"_id": "$visibility", "avg_caption_length": {"$avg": "$caption_len"}}},
    {"$sort": {"avg_caption_length": -1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.12 AGGREGATE - Engagement gap: posts with zero comments")
pipeline = [
    {"$match": {"comment_count": 0}},
    {"$count": "posts_with_no_comments"},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.13 AGGREGATE - Most discussed but least liked posts (comment:like ratio)")
pipeline = [
    {"$match": {"like_count": {"$gt": 0}}},
    {"$addFields": {"discuss_ratio": {"$divide": ["$comment_count", "$like_count"]}}},
    {"$sort": {"discuss_ratio": -1}},
    {"$limit": 5},
    {"$project": {"_id": 0, "post_id": 1, "like_count": 1, "comment_count": 1, "discuss_ratio": 1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.14 AGGREGATE - Peak posting hour of day (platform traffic pattern)")
pipeline = [
    {"$group": {"_id": {"$hour": "$created_at"}, "posts_count": {"$sum": 1}}},
    {"$sort": {"posts_count": -1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.15 AGGREGATE - Threaded vs top-level comment ratio")
pipeline = [
    {"$group": {
        "_id": {"$cond": [{"$eq": ["$parent_comment_id", None]}, "top_level", "threaded_reply"]},
        "count": {"$sum": 1},
    }},
]
for doc in db["comments"].aggregate(pipeline):
    print(doc)

banner("5.16 AGGREGATE - Media storage growth by upload day")
pipeline = [
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
        "items_uploaded": {"$sum": 1},
        "bytes_uploaded": {"$sum": "$file.size_bytes"},
    }},
    {"$sort": {"_id": 1}},
]
for doc in db["media_metadata"].aggregate(pipeline):
    print(doc)

banner("5.17 AGGREGATE - Moderation status crosstab by media type")
pipeline = [
    {"$group": {
        "_id": {"type": "$type", "status": "$moderation.status"},
        "count": {"$sum": 1},
    }},
    {"$sort": {"_id.type": 1, "_id.status": 1}},
]
for doc in db["media_metadata"].aggregate(pipeline):
    print(doc)

banner("5.18 AGGREGATE - Top hashtag pairs used together (hashtag recommendation)")
pipeline = [
    {"$match": {"hashtags.1": {"$exists": True}}},
    {"$project": {"hashtags": 1}},
    {"$unwind": "$hashtags"},
    {"$group": {"_id": "$_id", "tags": {"$push": "$hashtags"}}},
    {"$project": {
        "pairs": {
            "$reduce": {
                "input": {"$range": [0, {"$size": "$tags"}]},
                "initialValue": [],
                "in": {
                    "$concatArrays": [
                        "$$value",
                        {"$map": {
                            "input": {"$range": [{"$add": ["$$this", 1]}, {"$size": "$tags"}]},
                            "as": "j",
                            "in": {"$concatArrays": [[{"$arrayElemAt": ["$tags", "$$this"]}],
                                                      [{"$arrayElemAt": ["$tags", "$$j"]}]]},
                        }},
                    ]
                },
            }
        }
    }},
    {"$unwind": "$pairs"},
    {"$group": {"_id": "$pairs", "co_occurrences": {"$sum": 1}}},
    {"$sort": {"co_occurrences": -1}},
    {"$limit": 10},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.19 AGGREGATE - Single-call admin dashboard ($facet: 3 metrics at once)")
pipeline = [
    {"$facet": {
        "top_liked_posts": [
            {"$sort": {"like_count": -1}},
            {"$limit": 3},
            {"$project": {"_id": 0, "post_id": 1, "like_count": 1}},
        ],
        "visibility_breakdown": [
            {"$group": {"_id": "$visibility", "count": {"$sum": 1}}},
        ],
        "avg_engagement": [
            {"$group": {
                "_id": None,
                "avg_likes": {"$avg": "$like_count"},
                "avg_comments": {"$avg": "$comment_count"},
                "avg_shares": {"$avg": "$share_count"},
            }},
        ],
    }},
]
for doc in db["posts"].aggregate(pipeline):
    pprint(doc)

banner("5.20 AGGREGATE - Bucket posts into engagement tiers ($bucket)")
pipeline = [
    {"$bucket": {
        "groupBy": "$like_count",
        "boundaries": [0, 10, 50, 200, 100000],
        "default": "other",
        "output": {"post_count": {"$sum": 1}, "avg_comments": {"$avg": "$comment_count"}},
    }},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.21 AGGREGATE - Weekly active users (WAU) trend from activity_logs")
pipeline = [
    {"$group": {
        "_id": {"year": {"$isoWeekYear": "$timestamp"}, "week": {"$isoWeek": "$timestamp"}},
        "active_users": {"$addToSet": "$user_id"},
    }},
    {"$project": {"_id": 1, "active_user_count": {"$size": "$active_users"}}},
    {"$sort": {"_id.year": 1, "_id.week": 1}},
]
for doc in db["activity_logs"].aggregate(pipeline):
    print(doc)

banner("5.22 AGGREGATE - Top 10 most-commented posts (raw discussion volume)")
pipeline = [
    {"$sort": {"comment_count": -1}},
    {"$limit": 10},
    {"$project": {"_id": 0, "post_id": 1, "author_id": 1, "comment_count": 1, "like_count": 1}},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.23 AGGREGATE - Self-engagement detector: authors commenting on their own posts")
pipeline = [
    {"$lookup": {
        "from": "posts",
        "localField": "post_id",
        "foreignField": "post_id",
        "as": "post",
    }},
    {"$unwind": "$post"},
    {"$match": {"$expr": {"$eq": ["$author_id", "$post.author_id"]}}},
    {"$group": {"_id": "$author_id", "self_comment_count": {"$sum": 1}}},
    {"$sort": {"self_comment_count": -1}},
    {"$limit": 10},
]
for doc in db["comments"].aggregate(pipeline):
    print(doc)

banner("5.24 AGGREGATE - Average comment length per post (discussion quality/depth)")
pipeline = [
    {"$project": {"post_id": 1, "text_len": {"$strLenCP": "$text"}}},
    {"$group": {"_id": "$post_id", "avg_comment_length": {"$avg": "$text_len"}, "n_comments": {"$sum": 1}}},
    {"$match": {"n_comments": {"$gte": 2}}},
    {"$sort": {"avg_comment_length": -1}},
    {"$limit": 10},
]
for doc in db["comments"].aggregate(pipeline):
    print(doc)

banner("5.25 AGGREGATE - Content edit-rate: percentage of posts ever edited")
pipeline = [
    {"$group": {
        "_id": None,
        "total_posts": {"$sum": 1},
        "edited_posts": {"$sum": {"$cond": ["$is_edited", 1, 0]}},
    }},
    {"$project": {
        "_id": 0,
        "total_posts": 1,
        "edited_posts": 1,
        "edit_rate_pct": {"$round": [{"$multiply": [{"$divide": ["$edited_posts", "$total_posts"]}, 100]}, 1]},
    }},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.26 AGGREGATE - Average time-to-first-comment per post (engagement speed)")
pipeline = [
    {"$sort": {"created_at": 1}},
    {"$group": {"_id": "$post_id", "first_comment_at": {"$first": "$created_at"}}},
    {"$lookup": {
        "from": "posts",
        "localField": "_id",
        "foreignField": "post_id",
        "as": "post",
    }},
    {"$unwind": "$post"},
    {"$project": {
        "post_id": "$_id",
        "_id": 0,
        "minutes_to_first_comment": {
            "$divide": [{"$subtract": ["$first_comment_at", "$post.created_at"]}, 60000]
        },
    }},
    {"$group": {"_id": None, "avg_minutes_to_first_comment": {"$avg": "$minutes_to_first_comment"}}},
]
for doc in db["comments"].aggregate(pipeline):
    print(doc)

banner("5.27 AGGREGATE - Media orientation breakdown (portrait/landscape/square)")
pipeline = [
    {"$project": {
        "orientation": {
            "$switch": {
                "branches": [
                    {"case": {"$gt": ["$dimensions.width", "$dimensions.height"]}, "then": "landscape"},
                    {"case": {"$lt": ["$dimensions.width", "$dimensions.height"]}, "then": "portrait"},
                ],
                "default": "square",
            }
        }
    }},
    {"$group": {"_id": "$orientation", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]
for doc in db["media_metadata"].aggregate(pipeline):
    print(doc)

banner("5.28 AGGREGATE - Author tenure: first post, last post, days active")
pipeline = [
    {"$group": {
        "_id": "$author_id",
        "first_post_at": {"$min": "$created_at"},
        "last_post_at": {"$max": "$created_at"},
        "total_posts": {"$sum": 1},
    }},
    {"$project": {
        "_id": 1,
        "total_posts": 1,
        "first_post_at": 1,
        "last_post_at": 1,
        "days_active": {"$divide": [{"$subtract": ["$last_post_at", "$first_post_at"]}, 86400000]},
    }},
    {"$sort": {"days_active": -1}},
    {"$limit": 10},
]
for doc in db["posts"].aggregate(pipeline):
    print(doc)

banner("5.29 AGGREGATE - Most-followed users leaderboard (from follow_user events)")
pipeline = [
    {"$match": {"event_type": "follow_user"}},
    {"$group": {"_id": "$target_id", "new_follows": {"$sum": 1}}},
    {"$sort": {"new_follows": -1}},
    {"$limit": 10},
]
for doc in db["activity_logs"].aggregate(pipeline):
    print(doc)

banner("5.30 AGGREGATE - Engagement by device type (cross-collection: view events -> post likes)")
pipeline = [
    {"$match": {"event_type": "view_post", "target_id": {"$ne": None}}},
    {"$lookup": {
        "from": "posts",
        "localField": "target_id",
        "foreignField": "post_id",
        "as": "post",
    }},
    {"$unwind": "$post"},
    {"$group": {
        "_id": "$metadata.device",
        "views": {"$sum": 1},
        "avg_like_count_of_viewed_posts": {"$avg": "$post.like_count"},
    }},
    {"$sort": {"views": -1}},
]
for doc in db["activity_logs"].aggregate(pipeline):
    print(doc)
