// ---- 5.10 AGGREGATE - Visibility distribution across all posts (%) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $group: { _id: "$visibility", count: { $sum: 1 } } },
  { $group: {
      _id: null,
      breakdown: { $push: { visibility: "$_id", count: "$count" } },
      total: { $sum: "$count" }
  }},
  { $unwind: "$breakdown" },
  { $project: {
      _id: 0,
      visibility: "$breakdown.visibility",
      count: "$breakdown.count",
      percentage: { $round: [{ $multiply: [{ $divide: ["$breakdown.count", "$total"] }, 100] }, 1] }
  }},
  { $sort: { count: -1 } }
]);