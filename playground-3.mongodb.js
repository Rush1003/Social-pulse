use('socialpulse');


// ============================================================================
// SECTION 3: UPDATE
// ============================================================================

// ---- 3.1 UPDATE - Edit a post's caption ----
use('socialpulse');
db.getCollection('posts').updateOne(
  { post_id: "post_000999" },
  { $set: {
      caption: "Testing the SocialPulse NoSQL layer! (edited)",
      is_edited: true,
      updated_at: new Date()
  }}
);

// ---- 3.2 UPDATE - Like a post (atomic increment) ----
use('socialpulse');
db.getCollection('posts').updateOne(
  { post_id: "post_000999" },
  { $inc: { like_count: 1 } }
);

// ---- 3.3 UPDATE - Approve a flagged/pending media item ----
use('socialpulse');
db.getCollection('media_metadata').updateMany(
  { "moderation.status": "pending" },
  { $set: {
      "moderation.status": "approved",
      "moderation.reviewed_by": "manual-review-team"
  }}
);

// ---- 3.4 UPDATE - Add a hashtag to a post without duplicating it ----
use('socialpulse');
db.getCollection('posts').updateOne(
  { post_id: "post_000999" },
  { $addToSet: { hashtags: "#mongodb" } }
);

// ---- 3.5 UPDATE - Soft-delete a post (flag instead of hard delete) ----
use('socialpulse');
db.getCollection('posts').updateOne(
  { post_id: "post_000002" },
  { $set: { is_deleted: true, updated_at: new Date() } }
);

// ---- 3.6 UPDATE - Increment share_count when a post is shared ----
use('socialpulse');
db.getCollection('posts').updateOne(
  { post_id: "post_000003" },
  { $inc: { share_count: 1 } }
);