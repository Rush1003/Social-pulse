// ---- 5.13 AGGREGATE - Most discussed but least liked posts (comment:like ratio) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $match: { like_count: { $gt: 0 } } },
  { $addFields: { discuss_ratio: { $divide: ["$comment_count", "$like_count"] } } },
  { $sort: { discuss_ratio: -1 } },
  { $limit: 5 },
  { $project: { _id: 0, post_id: 1, like_count: 1, comment_count: 1, discuss_ratio: 1 } }
]);