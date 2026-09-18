// ---- 5.9 AGGREGATE - Weighted virality score (likes + 2*comments + 3*shares) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $addFields: {
      virality_score: {
        $add: [
          "$like_count",
          { $multiply: ["$comment_count", 2] },
          { $multiply: ["$share_count", 3] }
        ]
      }
  }},
  { $sort: { virality_score: -1 } },
  { $limit: 10 },
  { $project: { _id: 0, post_id: 1, like_count: 1, comment_count: 1, share_count: 1, virality_score: 1 } }
]);