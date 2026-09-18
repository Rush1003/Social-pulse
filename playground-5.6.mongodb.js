// ---- 5.6 AGGREGATE - Posts joined with their comment authors ($lookup) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $match: { comment_count: { $gt: 0 } } },
  { $limit: 3 },
  { $lookup: {
      from: "comments",
      localField: "post_id",
      foreignField: "post_id",
      as: "post_comments"
  }},
  { $project: {
      _id: 0,
      post_id: 1,
      comment_count: 1,
      sample_comment: { $arrayElemAt: ["$post_comments.text", 0] }
  }}
]);