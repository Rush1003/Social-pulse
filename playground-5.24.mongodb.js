// ---- 5.24 AGGREGATE - Average comment length per post (discussion quality/depth) ----
use('socialpulse');
db.getCollection('comments').aggregate([
  { $project: { post_id: 1, text_len: { $strLenCP: "$text" } } },
  { $group: { _id: "$post_id", avg_comment_length: { $avg: "$text_len" }, n_comments: { $sum: 1 } } },
  { $match: { n_comments: { $gte: 2 } } },
  { $sort: { avg_comment_length: -1 } },
  { $limit: 10 }
]);