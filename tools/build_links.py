"""Build the Head's Up link page (index.html at the repo root) from data/links.json.

usage: python3 tools/build_links.py
Reads links/template.html and data/links.json, writes index.html. Every image path is
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
nlw = data["newsletter"]
issues = sorted(nlw["issues"], key=lambda i: i["date"], reverse=True)
nl = {"subscribe": nlw["url"], "issues": [dict(i, date=nice(i["date"]), url=i.get("url") or nlw["url"]) for i in issues]}
arts = sorted(data["articles"], key=lambda a: a["date"], reverse=True)
arts = [dict(a, date=nice(a["date"]), url=a.get("url") or prof) for a in arts]

j = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
out = (tpl.replace("__POSTS__", j(posts)).replace("__NL__", j(nl)).replace("__ARTICLES__", j(arts))
          .replace("__HEADSHOT__", data["headshot"]))
open(os.path.join(ROOT, "index.html"), "w").write(out)
print("index.html:", len(posts), "posts,", len(issues), "issues,", len(arts), "articles")
