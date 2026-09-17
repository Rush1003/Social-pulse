# SocialPulse — NoSQL Document Structures (MongoDB)

MongoDB stores the semi-structured, high-volume, evolving-shape data:
posts, comments, media metadata, and activity logs. Each collection
below is schema-flexible by design (MongoDB is schemaless), but the
project applies **JSON Schema validators** at the collection level to
keep a documented, enforced shape while still allowing optional /
nested fields to vary — the core reason NoSQL was chosen for this data.

`user_id` fields are intentionally kept as plain integers that map
back to `users.user_id` in PostgreSQL. This is the **only** link
between the two databases and is resolved at the application layer
(not via a foreign key, since MongoDB cannot enforce cross-database
referential integrity).

---

## 1. `posts`

```json
{
  "_id": ObjectId("665f1b2e8f1b2c1a2d3e4f01"),
  "post_id": "post_000123",
  "author_id": 42,
  "caption": "Sunset over the lake tonight 🌅",
  "hashtags": ["#sunset", "#nature", "#photography"],
  "media": [
    { "media_id": "media_000456", "type": "image", "position": 0 }
  ],
  "location": {
    "name": "Lake Geneva",
    "coordinates": { "lat": 46.4, "lng": 6.53 }
  },
  "visibility": "public",
  "like_count": 214,
  "comment_count": 18,
  "share_count": 5,
  "is_edited": false,
  "created_at": ISODate("2025-11-02T14:23:00Z"),
  "updated_at": ISODate("2025-11-02T14:23:00Z")
}
```

**Why NoSQL:** posts vary widely — a text-only post has no `media`
array, a check-in post has `location` but no hashtags, a poll post
would carry a completely different embedded structure. Forcing this
into fixed relational columns would mean dozens of nullable columns
or brittle joins across many tables.

---

## 2. `comments`

```json
{
  "_id": ObjectId("665f1c3f8f1b2c1a2d3e4f22"),
  "comment_id": "cmt_000789",
  "post_id": "post_000123",
  "author_id": 17,
  "parent_comment_id": null,
  "text": "This is stunning!",
  "mentions": [42],
  "like_count": 3,
  "is_edited": false,
  "created_at": ISODate("2025-11-02T15:01:12Z")
}
```

Threaded replies simply set `parent_comment_id` to a parent
`comment_id`, giving unlimited nesting depth without schema changes.

---

## 3. `media_metadata`

```json
{
  "_id": ObjectId("665f1d508f1b2c1a2d3e4f33"),
  "media_id": "media_000456",
  "owner_id": 42,
  "type": "image",
  "file": {
    "url": "https://cdn.socialpulse.io/media/000456.jpg",
    "size_bytes": 2482193,
    "format": "jpg"
  },
  "dimensions": { "width": 1920, "height": 1080 },
  "duration_seconds": null,
  "exif": {
    "camera_model": "iPhone 14 Pro",
    "taken_at": ISODate("2025-11-02T14:10:00Z")
  },
  "moderation": {
    "status": "approved",
    "flagged_reason": null,
    "reviewed_by": "auto-moderator-v2"
  },
  "created_at": ISODate("2025-11-02T14:20:00Z")
}
```

**Why NoSQL:** an image document has `dimensions` + `exif`; a video
document instead has `duration_seconds`, `resolution`, and
`thumbnail_url`. One collection cleanly holds both shapes.

---

## 4. `activity_logs`

```json
{
  "_id": ObjectId("665f1e618f1b2c1a2d3e4f44"),
  "log_id": "log_0012345",
  "user_id": 42,
  "event_type": "like_post",
  "target_type": "post",
  "target_id": "post_000123",
  "metadata": {
    "device": "android",
    "ip": "203.0.113.7",
    "app_version": "4.12.0"
  },
  "timestamp": ISODate("2025-11-02T14:25:03Z")
}
```

`event_type` drives what appears in `metadata` (a `login` event logs
IP/device; a `follow_user` event logs `target_user_id` instead) — a
textbook case for a flexible, append-only log store rather than a
rigid relational audit table.

---

## Indexing Strategy

| Collection | Index | Purpose |
|---|---|---|
| `posts` | `{ author_id: 1, created_at: -1 }` | fast "user's feed, newest first" |
| `posts` | `{ hashtags: 1 }` (multikey) | hashtag search/discovery |
| `posts` | `{ "location.coordinates": "2dsphere" }` | geo-queries near a point |
| `comments` | `{ post_id: 1, created_at: 1 }` | fetch a post's comment thread in order |
| `comments` | `{ parent_comment_id: 1 }` | fetch replies to a comment |
| `media_metadata` | `{ owner_id: 1 }` | a user's uploaded media |
| `media_metadata` | `{ "moderation.status": 1 }` | moderation queue lookups |
| `activity_logs` | `{ user_id: 1, timestamp: -1 }` | per-user activity history |
| `activity_logs` | `{ event_type: 1, timestamp: -1 }` | analytics by event type |
