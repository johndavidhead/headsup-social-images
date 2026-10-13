"""Head's Up content database: data/content.json plus media/ and data/bodies/.

One record per published piece of LinkedIn content (newsletter editions today, feed posts
later). The link page (tools/build_links.py) and any cloud agent read data/content.json.
Images are stored in this repo because LinkedIn's signed CDN image URLs expire.

usage:
  python3 tools/content_db.py import-newsletter <meta.json> <covers_dir>
      Upsert newsletter editions scraped from LinkedIn (see data/README.md for the format).
  python3 tools/content_db.py import-posts <meta.json> <images_dir>
      Upsert feed posts scraped from John's activity feed. Reposts and newsletter shares are skipped.
  python3 tools/content_db.py validate
      Check every record against the rules in data/README.md and that every file exists.
  python3 tools/content_db.py list [type]
      Print one line per record, newest first.
  python3 tools/content_db.py find <linkedin url>
      Print the record for a LinkedIn article or post URL as JSON (exit 1 if it is not stored).
  python3 tools/content_db.py add-article <url> <title> <YYYY-MM-DD> <text_file> [cover_image]
      Upsert one newsletter special edition from its published URL and full text (used when the
      article came from John rather than a Mac Chrome import). A later import-newsletter of the
      same article replaces it, since both use the id li-article-<slug>.

Other scripts can `import content_db` and call load(), upsert(db, item), save(db).
"""
import datetime, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "content.json")
REPO = "johndavidhead/headsup-social-images"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
PAGES = "https://johndavidhead.github.io/headsup-social-images/"
NEWSLETTER = {
    "id": "7463333308307869696",
    "name": "Head's Up - Enterprise AI",
    "url": "https://www.linkedin.com/newsletters/head-s-up-enterprise-ai-7463333308307869696/",
}
TYPES = {"newsletter_edition", "post"}
WEB_W = 1100  # width of the web-size image the link page uses


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load():
    if not os.path.exists(DB_PATH):
        return {"schema_version": 1, "updated": now_iso(), "owner": {
            "name": "John Head", "profile_url": "https://www.linkedin.com/in/johndhead/"},
            "newsletters": [NEWSLETTER], "items": []}
    return json.load(open(DB_PATH))


def save(db):
    db["items"].sort(key=lambda i: (i["published_date"], i["id"]), reverse=True)
    db["updated"] = now_iso()
    with open(DB_PATH, "w") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        f.write("\n")


def upsert(db, item):
    """Insert or replace by id. Keeps first_seen from the existing record."""
    for k, old in enumerate(db["items"]):
        if old["id"] == item["id"]:
            item["first_seen"] = old.get("first_seen", item.get("first_seen"))
            db["items"][k] = item
            return "updated"
    db["items"].append(item)
    return "added"


def image_record(src_path, dest_dir, role, alt="", source_cdn_path=""):
    """Copy an image into media/, write a web-size JPEG beside it, return the image record."""
    from PIL import Image
    os.makedirs(os.path.join(ROOT, dest_dir), exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower() or ".jpg"
    orig_rel = f"{dest_dir}/{role}{ext}"
    data = open(src_path, "rb").read()
    open(os.path.join(ROOT, orig_rel), "wb").write(data)
    im = Image.open(src_path)
    w, h = im.size
    web_rel = f"{dest_dir}/{role}-web.jpg"
    web = im.convert("RGB")
    if w > WEB_W:
        web = web.resize((WEB_W, round(h * WEB_W / w)), Image.LANCZOS)
    web.save(os.path.join(ROOT, web_rel), "JPEG", quality=84, optimize=True, progressive=True)
    return {
        "role": role, "alt": alt, "width": w, "height": h, "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "path": orig_rel, "url": RAW + orig_rel,
        "web_path": web_rel, "web_url": RAW + web_rel, "web_width": web.size[0], "web_height": web.size[1],
        "source_cdn_path": source_cdn_path,
    }


SKIP = re.compile(r"^(volume \d|issue \d|what shipped, what broke|[—–\-_ ]+$|this is a .{0,12}bi-?\s?(weekly|monthly))", re.I)


def excerpt_of(text, limit=240):
    for para in [p.strip() for p in text.split("\n") if p.strip()]:
        if SKIP.match(para) or len(para) < 40:
            continue
        if len(para) <= limit:
            return para
        cut = para[:limit]
        end = max(cut.rfind(". "), cut.rfind("? "))
        return cut[:end + 1] if end > 80 else cut.rsplit(" ", 1)[0] + "..."
    return ""


def import_newsletter(meta_path, covers_dir):
    db = load()
    meta = json.load(open(meta_path))
    stamp = now_iso()
    for m in meta:
        slug = m["slug"]
        pub = datetime.datetime.strptime(m["date"], "%B %d, %Y").date().isoformat()
        head = m["text"][:200]
        mno = re.search(r"Issue (\d+)", head)
        iid = f"li-article-{slug}"
        body_rel = f"data/bodies/{iid}.md"
        os.makedirs(os.path.join(ROOT, "data", "bodies"), exist_ok=True)
        with open(os.path.join(ROOT, body_rel), "w") as f:
            f.write(f"# {m['title']}\n\n{pub} | {m['url']}\n\n{m['text'].strip()}\n")
        cover = os.path.join(covers_dir, f"headsup-cover-{slug}.jpg")
        images = [image_record(cover, f"media/linkedin/{iid}", "cover", m.get("coverAlt", ""),
                               m.get("cover_cdn_path", ""))] if os.path.exists(cover) else []
        item = {
            "id": iid,
            "type": "newsletter_edition",
            "edition_kind": "issue" if mno else "article",
            "issue_no": mno.group(1).zfill(2) if mno else None,
            "newsletter_id": NEWSLETTER["id"],
            "platform": "linkedin",
            "title": m["title"],
            "url": m["url"],
            "published_date": pub,
            "excerpt": excerpt_of(m["text"]),
            "word_count": len(m["text"].split()),
            "body_path": body_rel,
            "images": images,
            "tags": [],
            "first_seen": stamp,
            "last_scraped": stamp,
        }
        print(upsert(db, item), pub, m["title"])
    save(db)


def repo_image_record(rel, role, alt=""):
    """Image record for a file already in the repo (e.g. a Head's Up carousel slide)."""
    from PIL import Image
    full = os.path.join(ROOT, rel)
    data = open(full, "rb").read()
    w, h = Image.open(full).size
    return {"role": role, "alt": alt, "width": w, "height": h, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "path": rel, "url": RAW + rel,
            "web_path": rel, "web_url": RAW + rel, "web_width": w, "web_height": h, "source_cdn_path": ""}


def social_carousel(day):
    """Newest render of a Head's Up carousel for a social day, as repo paths in slide order."""
    import glob
    for d in sorted(glob.glob(os.path.join(ROOT, f"{day}-*"))):
        files = sorted(glob.glob(os.path.join(d, "*-carousel-[0-9].png")))
        if files:
            prefixes = sorted({os.path.basename(f).rsplit("-carousel-", 1)[0] for f in files})
            newest = [f for f in files if os.path.basename(f).startswith(prefixes[-1] + "-carousel-")]
            return [os.path.relpath(f, ROOT) for f in newest]
    return []


def title_of(text, limit=110):
    first = text.strip().split("\n")[0]
    m = re.match(r"(.+?[.?!])(\s|$)", first)
    t = m.group(1) if m else first
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "..."


def import_posts(meta_path, images_dir):
    """Upsert LinkedIn feed posts scraped from John's activity feed (see data/README.md)."""
    from zoneinfo import ZoneInfo
    db = load()
    meta = json.load(open(meta_path))
    stamp = now_iso()
    for p in meta["posts"]:
        if p["kind"] in ("repost", "newsletter_share"):
            continue
        act = p["activity_id"]
        iid = f"li-post-{act}"
        at = datetime.datetime.fromisoformat(p["iso"].replace("Z", "+00:00"))
        local = at.astimezone(ZoneInfo("America/Chicago"))
        pub = local.date().isoformat()
        text = p["text"].strip()
        title = p.get("doc_title") or title_of(text)
        url = f"https://www.linkedin.com/feed/update/urn:li:activity:{act}/"
        body_rel = f"data/bodies/{iid}.md"
        os.makedirs(os.path.join(ROOT, "data", "bodies"), exist_ok=True)
        with open(os.path.join(ROOT, body_rel), "w") as f:
            f.write(f"# {title}\n\n{pub} | {url}\n\n{text}\n")
        images, social_day = [], None
        if p["kind"] == "carousel":
            slides = social_carousel(pub)
            if slides:
                social_day = pub
                images = [repo_image_record(s, f"slide-{k}") for k, s in enumerate(slides, 1)]
        if not images:
            for im in p["images"]:
                src = os.path.join(images_dir, im["file"])
                if os.path.exists(src):
                    images.append(image_record(src, f"media/linkedin/{iid}", im["role"], im.get("alt", ""),
                                               im.get("cdn_path", "")))
        link = p.get("link") or None
        item = {
            "id": iid,
            "type": "post",
            "post_kind": {"link_share": "article_share"}.get(p["kind"], p["kind"]),
            "activity_urn": f"urn:li:activity:{act}",
            "platform": "linkedin",
            "title": title,
            "url": url,
            "published_date": pub,
            "published_at": at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "excerpt": excerpt_of(text),
            "word_count": len(text.split()),
            "body_path": body_rel,
            "images": images,
            "links": [link["url"]] if link and link.get("url") else [],
            "link_preview": {"title": link.get("title", ""), "source": link.get("subtitle", "")} if link else None,
            "source_social_date": social_day,
            "metrics": dict(p["metrics"], as_of=meta.get("scraped_at", stamp)[:10]) if p.get("metrics") else None,
            "tags": [],
            "first_seen": stamp,
            "last_scraped": stamp,
        }
        print(upsert(db, item), pub, item["post_kind"], len(images), "img", title[:60])
    save(db)


def slug_of(url):
    """LinkedIn pulse slug from an article URL, e.g. accountable-ai-you-cannot-see-john-head-qrctc."""
    m = re.search(r"linkedin\.com/pulse/([^/?#]+)", url or "")
    return m.group(1).strip("/") if m else ""


def find(url):
    """Stored record for a LinkedIn article or post URL, or None."""
    db = load()
    slug = slug_of(url)
    clean = (url or "").split("?")[0].rstrip("/")
    act = re.search(r"(activity|ugcPost|share)[:%3A]+(\d+)", url or "")
    for i in db["items"]:
        if slug and i["id"] == f"li-article-{slug}":
            return i
        if i.get("url", "").split("?")[0].rstrip("/") == clean:
            return i
        if act and act.group(2) in (i.get("activity_urn", "") + i.get("url", "")):
            return i
    return None


def add_article(url, title, pub, text_file, cover=None):
    slug = slug_of(url)
    if not slug:
        sys.exit("not a linkedin.com/pulse/ article URL: " + url)
    datetime.date.fromisoformat(pub)
    db = load()
    text = open(text_file).read().strip()
    iid = f"li-article-{slug}"
    body_rel = f"data/bodies/{iid}.md"
    os.makedirs(os.path.join(ROOT, "data", "bodies"), exist_ok=True)
    with open(os.path.join(ROOT, body_rel), "w") as f:
        f.write(f"# {title}\n\n{pub} | https://www.linkedin.com/pulse/{slug}/\n\n{text}\n")
    images = [image_record(cover, f"media/linkedin/{iid}", "cover")] if cover and os.path.exists(cover) else []
    stamp = now_iso()
    item = {
        "id": iid, "type": "newsletter_edition", "edition_kind": "article", "issue_no": None,
        "newsletter_id": NEWSLETTER["id"], "platform": "linkedin", "title": title,
        "url": f"https://www.linkedin.com/pulse/{slug}/", "published_date": pub,
        "excerpt": excerpt_of(text), "word_count": len(text.split()), "body_path": body_rel,
        "images": images, "tags": [], "first_seen": stamp, "last_scraped": stamp,
        "source": "john_text",
    }
    print(upsert(db, item), pub, title)
    save(db)


def validate():
    db = load()
    errs, ids = [], set()
    for i in db["items"]:
        where = i.get("id", "?")
        for k in ("id", "type", "platform", "title", "url", "published_date", "images"):
            if k not in i:
                errs.append(f"{where}: missing {k}")
        if i.get("id") in ids:
            errs.append(f"{where}: duplicate id")
        ids.add(i.get("id"))
        if i.get("type") not in TYPES:
            errs.append(f"{where}: unknown type {i.get('type')}")
        try:
            datetime.date.fromisoformat(i.get("published_date", ""))
        except ValueError:
            errs.append(f"{where}: bad published_date")
        for p in [i.get("body_path")] + [x for im in i.get("images", []) for x in (im.get("path"), im.get("web_path"))]:
            if p and not os.path.exists(os.path.join(ROOT, p)):
                errs.append(f"{where}: missing file {p}")
    print("\n".join(errs) or f"OK: {len(db['items'])} records")
    return not errs


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "import-newsletter":
        import_newsletter(sys.argv[2], sys.argv[3])
    elif cmd == "import-posts":
        import_posts(sys.argv[2], sys.argv[3])
    elif cmd == "validate":
        sys.exit(0 if validate() else 1)
    elif cmd == "list":
        t = sys.argv[2] if len(sys.argv) > 2 else None
        for i in load()["items"]:
            if not t or i["type"] == t:
                print(i["published_date"], i["type"], i.get("issue_no") or "", i["title"], len(i["images"]), "img")
    elif cmd == "find":
        rec = find(sys.argv[2])
        if not rec:
            sys.exit(1)
        print(json.dumps(rec, ensure_ascii=False, indent=2))
    elif cmd == "add-article":
        add_article(*sys.argv[2:7])
    else:
        print(__doc__)
