# Head's Up social images

Public image host for Head's Up social posts. Postiz pulls each image from its raw.githubusercontent.com link.

- `YYYY-MM-DD-<topic>/` holds one day's images: six carousel slides and one single card, 1080 x 1350.
- `tools/render_ds.py` renders those images from the John David Head design system. The design tokens, styles and Source Serif 4 fonts are read from the design system at run time and are not stored here. `tools/fonts/` holds only the Caveat script font used on Saturdays.

## Link page (GitHub Pages)

The repo root is also John's Head's Up link page, served by GitHub Pages at https://johndavidhead.github.io/headsup-social-images/.

- `data/links.json` holds the content: daily posts, newsletter issues and special editions. Edit this file, never `index.html`.
- `links/template.html` is the page design (Head's Up layer, cream). `links/assets/` holds the headshot and newsletter and article images.
- `python3 tools/build_links.py` rebuilds `index.html` from the two. Commit both.
- Daily post tiles reuse the cover image from that day's folder. An empty `url` falls back to John's LinkedIn profile (posts and articles) or the newsletter page (issues).
- `.nojekyll` makes GitHub serve the files as they are. If a custom domain is added later, GitHub writes a `CNAME` file here; never delete it.
