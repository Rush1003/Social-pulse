// ---- 5.30 AGGREGATE - Engagement by device type (cross-collection: view events -> post likes) ----
use('socialpulse');
db.getCollection('activity_logs').aggregate([
  { $match: { event_type: "view_post", target_id: { $ne: null } } },
  { $lookup: {
      from: "posts",
      localField: "target_id",
      foreignField: "post_id",
      as: "post"
  }},
  { $unwind: "$post" },
  { $group: {
      _id: "$metadata.device",
      views: { $sum: 1 },
      avg_like_count_of_viewed_posts: { $avg: "$post.like_count" }
  }},
  { $sort: { views: -1 } }
]);