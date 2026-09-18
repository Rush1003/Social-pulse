// ---- 5.8 AGGREGATE - Top 10 most active users by total activity events ----
use('socialpulse');
db.getCollection('activity_logs').aggregate([
  { $group: { _id: "$user_id", event_count: { $sum: 1 } } },
  { $sort: { event_count: -1 } },
  { $limit: 10 }
]);