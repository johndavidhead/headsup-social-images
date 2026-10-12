# Head's Up social images

Public image host for Head's Up social posts. Postiz pulls each image from its raw.githubusercontent.com link.

- `YYYY-MM-DD-<topic>/` holds one day's images: six carousel slides and one single card, 1080 x 1350.
- `tools/render_ds.py` renders those images from the John David Head design system. The design tokens, styles and Source Serif 4 fonts are read from the design system at run time and are not stored here. `tools/fonts/` holds only the Caveat script font used on Saturdays.
