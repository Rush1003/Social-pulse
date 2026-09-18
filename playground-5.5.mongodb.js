// ---- 5.5 AGGREGATE - Media storage usage by type (image vs video) ----
use('socialpulse');
db.getCollection('media_metadata').aggregate([
  { $group: {
      _id: "$type",
      count: { $sum: 1 },
      total_bytes: { $sum: "$file.size_bytes" },
      avg_bytes: { $avg: "$file.size_bytes" }
  }}
]);