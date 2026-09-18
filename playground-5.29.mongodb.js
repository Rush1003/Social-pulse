// ---- 5.29 AGGREGATE - Most-followed users leaderboard (from follow_user events) ----
use('socialpulse');
db.getCollection('activity_logs').aggregate([
  { $match: { event_type: "follow_user" } },
  { $group: { _id: "$target_id", new_follows: { $sum: 1 } } },
  { $sort: { new_follows: -1 } },
  { $limit: 10 }
]);