// ---- 5.25 AGGREGATE - Content edit-rate: percentage of posts ever edited ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $group: {
      _id: null,
      total_posts: { $sum: 1 },
      edited_posts: { $sum: { $cond: ["$is_edited", 1, 0] } }
  }},
  { $project: {
      _id: 0,
      total_posts: 1,
      edited_posts: 1,
      edit_rate_pct: { $round: [{ $multiply: [{ $divide: ["$edited_posts", "$total_posts"] }, 100] }, 1] }
  }}
]);