// ---- 5.21 AGGREGATE - Weekly active users (WAU) trend from activity_logs ----
use('socialpulse');
db.getCollection('activity_logs').aggregate([
  { $group: {
      _id: { year: { $isoWeekYear: "$timestamp" }, week: { $isoWeek: "$timestamp" } },
      active_users: { $addToSet: "$user_id" }
  }},
  { $project: { _id: 1, active_user_count: { $size: "$active_users" } } },
  { $sort: { "_id.year": 1, "_id.week": 1 } }
]);