// ---- 5.18 AGGREGATE - Top hashtag pairs used together (hashtag recommendation) ----
use('socialpulse');
db.getCollection('posts').aggregate([
  { $match: { "hashtags.1": { $exists: true } } },
  { $project: { hashtags: 1 } },
  { $unwind: "$hashtags" },
  { $group: { _id: "$_id", tags: { $push: "$hashtags" } } },
  { $project: {
      pairs: {
        $reduce: {
          input: { $range: [0, { $size: "$tags" }] },
          initialValue: [],
          in: {
            $concatArrays: [
              "$$value",
              { $map: {
                  input: { $range: [{ $add: ["$$this", 1] }, { $size: "$tags" }] },
                  as: "j",
                  in: { $concatArrays: [[{ $arrayElemAt: ["$tags", "$$this"] }],
                                          [{ $arrayElemAt: ["$tags", "$$j"] }]] }
              }}
            ]
          }
        }
      }
  }},
  { $unwind: "$pairs" },
  { $group: { _id: "$pairs", co_occurrences: { $sum: 1 } } },
  { $sort: { co_occurrences: -1 } },
  { $limit: 10 }
]);