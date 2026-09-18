// ---- 5.28 AGGREGATE - Author tenure: first post, last post, days active ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $group: {
      _id: "$author_id",
      first_post_at: { $min: "$created_at" },
      last_post_at: { $max: "$created_at" },
      total_posts: { $sum: 1 }
  }},
  { $project: {
      _id: 1,
      total_posts: 1,
      first_post_at: 1,
      last_post_at: 1,
      days_active: { $divide: [{ $subtract: ["$last_post_at", "$first_post_at"] }, 86400000] }
  }},
  { $sort: { days_active: -1 } },
  { $limit: 10 }
]);