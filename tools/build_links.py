"""Build the Head's Up link page (index.html at the repo root).

data/links.json holds the profile, headshot and daily social post tiles. Newsletter issues and
articles come from data/content.json (the content database, see data/README.md); never list them
in links.json.

usage: python3 tools/build_links.py
Reads links/template.html, data/links.json and data/content.json, writes index.html. Every image path is
relative to the repo root, so the page works on johndavidhead.github.io/headsup-social-images/
and on a custom domain alike. Empty "url" fields fall back: posts to the LinkedIn profile,
issues to the newsletter page, articles to the profile.
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "data", "links.json")))
tpl = open(os.path.join(ROOT, "links", "template.html")).read()

def nice(d):
    if not d: return ""
    try:
        if len(d) == 7: return datetime.date.fromisoformat(d + "-01").strftime("%b %Y")
        x = datetime.date.fromisoformat(d); return x.strftime("%b ") + str(x.day) + x.strftime(", %Y")
    except ValueError:
        return d

prof = data["profile_url"]
posts = sorted(data["posts"], key=lambda p: p["date"], reverse=True)
for p in posts:
    p["date_iso"] = p["date"]; p["date"] = nice(p["date"]); p["url"] = p.get("url") or prof
content = json.load(open(os.path.join(ROOT, "data", "content.json")))
nlw = content["newsletters"][0]
eds = [i for i in content["items"] if i["type"] == "newsletter_edition" and i.get("newsletter_id") == nlw["id"]]
def card(i, **extra):
    img = next((im["web_path"] for im in i["images"] if im["role"] == "cover"), "")
    return dict(title=i["title"], date=nice(i["published_date"]), img=img, url=i.get("url") or nlw["url"], **extra)
issues = sorted([i for i in eds if i["edition_kind"] == "issue"], key=lambda i: i["published_date"], reverse=True)
nl = {"subscribe": nlw["url"], "issues": [card(i, no=i["issue_no"]) for i in issues]}
arts = sorted([i for i in eds if i["edition_kind"] == "article"], key=lambda i: i["published_date"], reverse=True)
arts = [card(a) for a in arts]

j = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
out = (tpl.replace("__POSTS__", j(posts)).replace("__NL__", j(nl)).replace("__ARTICLES__", j(arts))
          .replace("__HEADSHOT__", data["headshot"]))
open(os.path.join(ROOT, "index.html"), "w").write(out)
print("index.html:", len(posts), "posts,", len(issues), "issues,", len(arts), "articles")
