use('socialpulse');


// ============================================================================
// SECTION 2: READ / RETRIEVAL
// ============================================================================

// ---- 2.1 READ - Fetch a single post by post_id ----
db.getCollection('posts').findOne({ post_id: "post_000999" });

// ---- 2.2 READ - A user's feed: latest 5 public posts by author_id ----
db.getCollection('posts').find(
  { author_id: 1, visibility: "public" }
).sort({ created_at: -1 }).limit(5);

// ---- 2.3 READ - All top-level comments on a post, oldest first ----
db.getCollection('comments').find(
  { post_id: "post_000999", parent_comment_id: null }
).sort({ created_at: 1 });

// ---- 2.4 READ - Posts tagged with a specific hashtag ----
use('socialpulse');
db.getCollection('posts').find({ hashtags: "#sunset" }).limit(5);

// ---- 2.5 READ - Media pending moderation review ----
use('socialpulse');
db.getCollection('media_metadata').find({ "moderation.status": "pending" }).limit(5);

// ---- 2.6 READ - Recent activity log for a specific user ----
use('socialpulse');
db.getCollection('activity_logs').find({ user_id: 1 }).sort({ timestamp: -1 }).limit(5);

// ---- 2.7 READ - Search posts by keyword in caption (case-insensitive) ----
use('socialpulse');
db.getCollection('posts').find(
  { caption: { $regex: "body", $options: "i" } }
).limit(5);

// ---- 2.8 READ - Posts that carry a geo-location (map/near-me view) ----
use('socialpulse');
db.getCollection('posts').find({ location: { $ne: null } }).limit(5);