use('socialpulse');


// ============================================================================
// SECTION 1: CREATE
// ============================================================================

// ---- 1.1 CREATE - Insert a new post ----
db.getCollection('posts').insertOne({
  post_id: "post_000999",
  author_id: 1,
  caption: "Testing the SocialPulse NoSQL layer!",
  hashtags: ["#test", "#coding"],
  media: [],
  location: null,
  visibility: "public",
  like_count: 0,
  comment_count: 0,
  share_count: 0,
  is_edited: false,
  created_at: new Date(),
  updated_at: new Date()
});

// ---- 1.2 CREATE - Insert a comment on that post ----
db.getCollection('comments').insertOne({
  comment_id: "cmt_000999",
  post_id: "post_000999",
  author_id: 2,
  parent_comment_id: null,
  text: "Nice work!",
  mentions: [],
  like_count: 0,
  is_edited: false,
  created_at: new Date()
});
db.getCollection('posts').updateOne(
  { post_id: "post_000999" },
  { $inc: { comment_count: 1 } }
);