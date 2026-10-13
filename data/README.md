# Head's Up content database

`data/content.json` is the single source of truth for John Head's published LinkedIn content: newsletter editions now, feed posts later. The link page and every agent read it. Do not keep a second copy anywhere else.

## How to reach it

| Who | How |
|---|---|
| Cloud agent with the repo attached | `git clone --depth 1 https://github.com/johndavidhead/headsup-social-images` then read `data/content.json` |
| Anything with web access (read only) | `https://johndavidhead.github.io/headsup-social-images/data/content.json` or `https://raw.githubusercontent.com/johndavidhead/headsup-social-images/main/data/content.json` |
| Link page | `tools/build_links.py` reads it at build time |

Write only through `tools/content_db.py` (or its `load` / `upsert` / `save` functions), then run `python3 tools/content_db.py validate` and `python3 tools/build_links.py`, and commit `data/`, `media/` and `index.html` together.

## Layout

```
data/content.json          the database
data/bodies/<id>.md        full text of each record
media/linkedin/<id>/       images for each record: originals plus a 1100px "-web.jpg" copy
tools/content_db.py        import, upsert, validate, list, find, add-article
```

Images live in the repo because LinkedIn's CDN image URLs are signed and expire. `source_cdn_path` records where an image came from, without the signature.

## Top level

| Field | Contents |
|---|---|
| `schema_version` | `1` |
| `updated` | UTC timestamp of the last write |
| `owner` | `{name, profile_url}` |
| `newsletters` | `[{id, name, url}]`. Head's Up - Enterprise AI is `7463333308307869696` |
| `items` | Records, newest `published_date` first |

## Record (every type)

| Field | Contents |
|---|---|
| `id` | Stable unique key. Newsletter editions: `li-article-<LinkedIn pulse slug>`. Posts: `li-post-<activity id>` |
| `type` | `newsletter_edition` or `post` |
| `platform` | `linkedin` |
| `title` | Edition headline, or for a post its first line |
| `url` | Public LinkedIn URL |
| `published_date` | `YYYY-MM-DD` |
| `excerpt` | First substantive paragraph, up to 240 characters |
| `word_count` | Words in the body |
| `body_path` | Full text, `data/bodies/<id>.md` |
| `images` | List of image records (below); empty list if none |
| `tags` | Free list for topic labels (`ai`, `quantum`, ...) |
| `first_seen`, `last_scraped` | UTC timestamps |

## Newsletter edition fields

| Field | Contents |
|---|---|
| `edition_kind` | `issue` for the numbered bi-weekly issues, `article` for special editions published in the newsletter |
| `issue_no` | `"01"`, `"02"` ... for issues, `null` for articles |
| `newsletter_id` | Which newsletter it belongs to |

## Post fields

| Field | Contents |
|---|---|
| `activity_urn` | `urn:li:activity:<id>`. The id also encodes the post time |
| `post_kind` | `carousel` (document post), `image`, `article_share` (outside link with preview), `text`, `video` |
| `published_at` | UTC timestamp. `published_date` is the Chicago date |
| `links` | Outside URLs the post shares |
| `link_preview` | `{title, source}` of the shared link card, or `null` |
| `source_social_date` | The Head's Up social day (`YYYY-MM-DD`) when the post came from that pipeline. Its `images` then point at that day's carousel PNGs in this repo instead of a copy |
| `metrics` | `{reactions, comments, reposts, impressions, as_of}` at scrape time |

Reposts (with or without commentary) and shares of John's own newsletter editions are not stored as posts.

## Image record

| Field | Contents |
|---|---|
| `role` | `cover` for an edition's cover; for posts `image-1`, `image-2` ... in carousel order |
| `alt` | Alt text from LinkedIn, if any |
| `width`, `height`, `bytes`, `sha256` | Of the original |
| `path`, `url` | Original file in the repo and its raw GitHub URL |
| `web_path`, `web_url`, `web_width`, `web_height` | 1100px JPEG for pages |
| `source_cdn_path` | LinkedIn CDN path it was downloaded from, signature removed |

## Refreshing newsletter editions

LinkedIn's image CDN is not reachable from the cloud, so images come through John's logged-in Mac Chrome: scrape each edition (title, date, text, cover), download the covers as `headsup-cover-<slug>.jpg` plus a `headsup-newsletter-meta.json` list of `{slug, url, title, date ("September 17, 2026"), text, coverAlt, cover_cdn_path}`, then run `python3 tools/content_db.py import-newsletter <meta.json> <covers_dir>`. Upserts by `id`, so re-running is safe.

## Refreshing posts

From John's logged-in Mac Chrome, read `/voyager/api/identity/profileUpdatesV2?q=memberShareFeed` for his profile, download each post's images as `headsup-post-<activity id>-<role>.jpg` plus `headsup-posts-meta.json` (`{scraped_at, posts: [{activity_id, iso, kind, text, doc_title, link, metrics, images: [{role, width, height, alt, cdn_path, file}]}]}`), then run `python3 tools/content_db.py import-posts <meta.json> <images_dir>`. Upserts by `id`, so re-running refreshes metrics.

## Adding one article from pasted text

The `linkedin-article-social` skill uses two commands. `python3 tools/content_db.py find <linkedin url>` prints a stored item as JSON (exit 1 if missing); it matches by pulse slug, clean URL or activity id. `python3 tools/content_db.py add-article <url> <title> <YYYY-MM-DD> <text_file> [cover]` adds or updates `li-article-<slug>` with `source: "john_text"` and writes the body to `data/bodies/`. Then validate, rebuild the link page and commit.
