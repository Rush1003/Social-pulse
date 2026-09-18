// ---- 5.15 AGGREGATE - Threaded vs top-level comment ratio ----
use('socialpulse');
db.getCollection('comments').aggregate([
  { $group: {
      _id: { $cond: [{ $eq: ["$parent_comment_id", null] }, "top_level", "threaded_reply"] },
      count: { $sum: 1 }
  }}
]);