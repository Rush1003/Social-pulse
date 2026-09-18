// ---- 5.7 AGGREGATE - Daily post volume trend (last 30 days) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $match: { created_at: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) } } },
  { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      posts_created: { $sum: 1 }
  }},
  { $sort: { _id: 1 } }
]);