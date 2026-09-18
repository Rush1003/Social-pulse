// ---- 5.26 AGGREGATE - Average time-to-first-comment per post (engagement speed) ----
use('socialpulse');
db.getCollection('comments').aggregate([
  { $sort: { created_at: 1 } },
  { $group: { _id: "$post_id", first_comment_at: { $first: "$created_at" } } },
  { $lookup: {
      from: "posts",
      localField: "_id",
      foreignField: "post_id",
      as: "post"
  }},
  { $unwind: "$post" },
  { $project: {
      post_id: "$_id",
      _id: 0,
      minutes_to_first_comment: {
        $divide: [{ $subtract: ["$first_comment_at", "$post.created_at"] }, 60000]
      }
  }},
  { $group: { _id: null, avg_minutes_to_first_comment: { $avg: "$minutes_to_first_comment" } } }
]);