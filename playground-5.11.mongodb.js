// ---- 5.11 AGGREGATE - Average caption length grouped by visibility ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $project: { visibility: 1, caption_len: { $strLenCP: "$caption" } } },
  { $group: { _id: "$visibility", avg_caption_length: { $avg: "$caption_len" } } },
  { $sort: { avg_caption_length: -1 } }
]);