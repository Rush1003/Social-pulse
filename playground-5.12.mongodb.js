// ---- 5.12 AGGREGATE - Engagement gap: posts with zero comments ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $match: { comment_count: 0 } },
  { $count: "posts_with_no_comments" }
]);