// ---- 5.2 AGGREGATE - Post count and average likes per author ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $group: {
      _id: "$author_id",
      post_count: { $sum: 1 },
      avg_likes: { $avg: "$like_count" },
      total_shares: { $sum: "$share_count" }
  }},
  { $sort: { post_count: -1 } },
  { $limit: 10 }
]);