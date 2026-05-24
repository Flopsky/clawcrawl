List every raster image URL that appears as an image in the markdown (markdown images, HTML img, or bare image URLs). Return only real image URLs; dedupe by URL.

Each entry in `images` must be an object with `url` (required), optional `alt`, and `source` (`markdown`, `html`, or `bare_url`). Do not return bare URL strings in the array.

Do not include SVG or SVGZ URLs (vector graphics, icons, logos ending in `.svg`). Those are left unchanged in the page and must not be described.
