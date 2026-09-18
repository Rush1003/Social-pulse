// ---- 5.22 AGGREGATE - Top 10 most-commented posts (raw discussion volume) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $sort: { comment_count: -1 } },
  { $limit: 10 },
  { $project: { _id: 0, post_id: 1, author_id: 1, comment_count: 1, like_count: 1 } }
]);