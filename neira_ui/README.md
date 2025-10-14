# NEIRA UI - Web Components Version

Simple, no-build web interface for NEIRA rowing data.

## Testing Locally

Start a local web server:

```bash
# Using Python 3
python3 -m http.server 8000

# Or using Python 2
python -m SimpleHTTPServer 8000

# Or using Node.js (if you have npx)
npx http-server -p 8000
```

Then open http://localhost:8000 in your browser.

## Structure

```
neira_ui/
├── index.html              # Home page
├── css/
│   ├── styles.css          # Global styles
│   └── page-layout.css     # Layout component styles
├── js/
│   ├── components/
│   │   └── page-layout.js  # Page layout web component
│   ├── utils/
│   │   ├── router.js       # Routing utilities
│   │   └── csv-parser.js   # CSV parsing utilities
│   └── pages/
│       └── home.js         # Home page logic
└── static/                 # Symlink to neira_ui_svelte/static
    ├── dot/                # Generated graph visualizations
    └── tables/             # Generated comparison tables
```

## Current Status

**Phase 1-3 Complete:**
- ✅ Directory structure
- ✅ Shared utilities (router, CSV parser)
- ✅ Page layout web component
- ✅ Home page

**Not Yet Implemented:**
- Ranking page with reorderable list
- Seeding tool
- Modal dialog component

## Development Notes

- Uses ES modules (type="module")
- Uses Shadow DOM for component encapsulation
- No build step required
- Works with modern browsers only
