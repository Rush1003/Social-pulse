// ============================================================================
// SECTION 4: DELETE
// ============================================================================

// ---- 4.1 DELETE - Remove a single comment ----
use('socialpulse');
db.getCollection('comments').deleteOne({ comment_id: "cmt_000999" });

// ---- 4.2 DELETE - Purge activity logs older than 1 year (retention policy) ----
use('socialpulse');
const cutoff1 = new Date();
cutoff1.setDate(cutoff1.getDate() - 365);
db.getCollection('activity_logs').deleteMany({ timestamp: { $lt: cutoff1 } });

// ---- 4.3 DELETE - Remove a post and its dependent comments (manual cascade) ----
use('socialpulse');
db.getCollection('comments').deleteMany({ post_id: "post_000999" });
db.getCollection('posts').deleteOne({ post_id: "post_000999" });

// ---- 4.4 DELETE - Purge old flagged media metadata past the review window ----
use('socialpulse');
const cutoff2 = new Date();
cutoff2.setDate(cutoff2.getDate() - 90);
db.getCollection('media_metadata').deleteMany(
  { "moderation.status": "flagged", created_at: { $lt: cutoff2 } }
);