// ---- 5.17 AGGREGATE - Moderation status crosstab by media type ----
use('socialpulse');
db.getCollection('media_metadata').aggregate([
  { $group: {
      _id: { type: "$type", status: "$moderation.status" },
      count: { $sum: 1 }
  }},
  { $sort: { "_id.type": 1, "_id.status": 1 } }
]);