// ---- 5.14 AGGREGATE - Peak posting hour of day (platform traffic pattern) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $group: { _id: { $hour: "$created_at" }, posts_count: { $sum: 1 } } },
  { $sort: { posts_count: -1 } }
]);