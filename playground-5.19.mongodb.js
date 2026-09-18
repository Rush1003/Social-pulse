// ---- 5.19 AGGREGATE - Single-call admin dashboard ($facet: 3 metrics at once) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $facet: {
      top_liked_posts: [
        { $sort: { like_count: -1 } },
        { $limit: 3 },
        { $project: { _id: 0, post_id: 1, like_count: 1 } }
      ],
      visibility_breakdown: [
        { $group: { _id: "$visibility", count: { $sum: 1 } } }
      ],
      avg_engagement: [
        { $group: {
            _id: null,
            avg_likes: { $avg: "$like_count" },
            avg_comments: { $avg: "$comment_count" },
            avg_shares: { $avg: "$share_count" }
        }}
      ]
  }}
]);