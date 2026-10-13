# Head's Up social images

Public image host for Head's Up social posts. Postiz pulls each image from its raw.githubusercontent.com link.

- `YYYY-MM-DD-<topic>/` holds one day's images: six carousel slides and one single card, 1080 x 1350.
- `tools/render_ds.py` renders those images from the John David Head design system. The design tokens, styles and Source Serif 4 fonts are read from the design system at run time and are not stored here. `tools/fonts/` holds only the Caveat script font used on Saturdays.

## Link page (GitHub Pages)

The repo root is also John's Head's Up link page, served by GitHub Pages at https://johndavidhead.github.io/headsup-social-images/.

- `data/content.json` is the content database: every newsletter issue and special edition, with full text in `data/bodies/` and images in `media/`. LinkedIn posts go here too. Schema and access in `data/README.md`.
- `data/links.json` holds only the profile, headshot and daily post tiles. Never edit `index.html`.
- `links/template.html` is the page design (Head's Up layer, cream). `links/assets/` holds the headshot.
- `python3 tools/build_links.py` rebuilds `index.html` from the template, `links.json` and `content.json`. Commit them together.
- Daily post tiles reuse the cover image from that day's folder. An empty post `url` falls back to John's LinkedIn profile.
- `.nojekyll` makes GitHub serve the files as they are. If a custom domain is added later, GitHub writes a `CNAME` file here; never delete it.
