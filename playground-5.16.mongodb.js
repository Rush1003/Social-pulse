// ---- 5.16 AGGREGATE - Media storage growth by upload day ----
use('socialpulse');
db.getCollection('media_metadata').aggregate([
  { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      items_uploaded: { $sum: 1 },
      bytes_uploaded: { $sum: "$file.size_bytes" }
  }},
  { $sort: { _id: 1 } }
]);