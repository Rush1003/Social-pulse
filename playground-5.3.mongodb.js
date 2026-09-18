// ---- 5.3 AGGREGATE - Most-used hashtags platform-wide ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $unwind: "$hashtags" },
  { $group: { _id: "$hashtags", usage_count: { $sum: 1 } } },
  { $sort: { usage_count: -1 } },
  { $limit: 10 }
]);