// ---- 5.20 AGGREGATE - Bucket posts into engagement tiers ($bucket) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $bucket: {
      groupBy: "$like_count",
      boundaries: [0, 10, 50, 200, 100000],
      default: "other",
      output: { post_count: { $sum: 1 }, avg_comments: { $avg: "$comment_count" } }
  }}
]);