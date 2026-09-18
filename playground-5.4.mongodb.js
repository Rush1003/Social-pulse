// ---- 5.4 AGGREGATE - Event type distribution in activity_logs ----
use('socialpulse');
db.getCollection('activity_logs').aggregate([
  { $group: { _id: "$event_type", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]);
