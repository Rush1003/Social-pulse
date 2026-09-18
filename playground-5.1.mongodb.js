// ============================================================================
// SECTION 5: AGGREGATION PIPELINES
// ============================================================================

// ---- 5.1 AGGREGATE - Top 5 most-liked posts ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $sort: { like_count: -1 } },
  { $limit: 5 },
  { $project: { _id: 0, post_id: 1, author_id: 1, like_count: 1, comment_count: 1 } }
]);