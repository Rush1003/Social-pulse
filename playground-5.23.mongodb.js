// ---- 5.23 AGGREGATE - Self-engagement detector: authors commenting on their own posts ----
use('socialpulse');
db.getCollection('comments').aggregate([
  { $lookup: {
      from: "posts",
      localField: "post_id",
      foreignField: "post_id",
      as: "post"
  }},
  { $unwind: "$post" },
  { $match: { $expr: { $eq: ["$author_id", "$post.author_id"] } } },
  { $group: { _id: "$author_id", self_comment_count: { $sum: 1 } } },
  { $sort: { self_comment_count: -1 } },
  { $limit: 10 }
]);