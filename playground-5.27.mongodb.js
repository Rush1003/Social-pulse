// ---- 5.27 AGGREGATE - Media orientation breakdown (portrait/landscape/square) ----
use('socialpulse');
db.getCollection('media_metadata').aggregate([
  { $project: {
      orientation: {
        $switch: {
          branches: [
            { case: { $gt: ["$dimensions.width", "$dimensions.height"] }, then: "landscape" },
            { case: { $lt: ["$dimensions.width", "$dimensions.height"] }, then: "portrait" }
          ],
          default: "square"
        }
      }
  }},
  { $group: { _id: "$orientation", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]);