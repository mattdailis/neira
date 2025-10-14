# Plan: Add Race Listing Pages

## Current Jinja2 Structure

The `neira_ui_jinja` version generates:

1. **Home page** (`/2025/index.html`)
   - Links to each boat category (Girls 1st Fours, etc.)

2. **Category pages** (`/2025/fours/girls/1/index.html`)
   - Lists all races for that specific boat chronologically
   - Shows results for each race date
   - Links to graph visualization
   - Links to individual race details

3. **Individual race pages** (`/2025/ABCD1234.html`)
   - Full details of a single regatta
   - All heats from that race
   - Link to row2k

4. **Founders Day page** (`/2025/founders-day.html`)
   - Special formatting for Founders Day results

## What We Need to Build

### Phase A: Data Loading

**Create:** `js/utils/race-data.js`

```javascript
// Fetch and parse race data from data/2_reviewed/
async function loadRaceData() {
  // Returns structure:
  // {
  //   "fours": {
  //     "girls": {
  //       "1": [{ date, results, url }, ...]
  //     }
  //   }
  // }
}

async function loadRaceDetail(raceId) {
  // Fetch specific race JSON: /data/2_reviewed/{raceId}.json
}
```

**Challenge:** The Python script reads from `data/2_reviewed/` which isn't in `static/`. We need to either:
- **Option 1:** Copy reviewed data to `static/data/` during build
- **Option 2:** Generate JSON index files during Python build
- **Option 3:** Have Python generate the HTML (not pure web components)

**Recommended:** Option 2 - Generate JSON manifests

### Phase B: Category Page

**Create:** `category.html`

URL: `/category.html?class=fours&gender=girls&varsity=1`

**Components needed:**
- Fetch race data for that category
- Display chronologically
- Format results with monospace font
- Link to row2k for each result

**Example:**
```
Girls Fours: 1V

[Graph visualization link]

Saturday, May 17, 2025
┌──────────────────────┬─────────┐
│ Groton               │ 5:23.4  │
│ Brooks               │ 5:28.1  │
│ Nobles               │ 5:31.2  │
└──────────────────────┴─────────┘
[Link to full race details]

Saturday, May 10, 2025
...
```

### Phase C: Race Detail Page

**Create:** `race.html`

URL: `/race.html?id=ABCD1234`

**Shows:**
- Regatta name
- Date
- Link to row2k
- Comment (with distance/conditions)
- All heats from that race

### Phase D: Update Home Page

Update `index.html` to link to category pages instead of static dot files:

```html
<a href="category.html?class=fours&gender=girls&varsity=1">First Boat</a>
```

Keep the direct dot links as secondary:
```html
<a href="category.html?class=fours&gender=girls&varsity=1">First Boat</a>
(<a href="static/dot/girls1fours.html">graph</a>)
```

## Implementation Strategy

### Option 1: Python + JSON (Hybrid - Recommended)

**Python generates:**
- Race manifest JSONs during `neira apply-corrections`
- Structure: `static/data/races-manifest.json`

```json
{
  "fours": {
    "girls": {
      "1": [
        {
          "date": "2025-05-17",
          "displayDate": "Saturday, May 17, 2025",
          "races": [
            {
              "raceId": "ABCD1234",
              "results": [
                {"school": "Groton", "time": "5:23.4"},
                {"school": "Brooks", "time": "5:28.1"}
              ],
              "url": "https://www.row2k.com/...",
              "distance": 1500
            }
          ]
        }
      ]
    }
  }
}
```

**Web components:**
- Fetch and display manifest data
- No build step on the JS side

**Pros:**
- No build step for JS/HTML
- Data is pre-organized by Python
- Leverages existing Python logic

**Cons:**
- Requires updating Python pipeline

### Option 2: Pure Client-Side (No Python Changes)

**Fetch all race JSONs:**
- Read `static/data/2_reviewed/` directory listing (if available)
- Or: Create a simple `races-index.json` by hand once

**Pros:**
- No Python changes needed

**Cons:**
- Can't easily list directory contents from browser
- Would need manual index file

### Option 3: Pre-generate HTML (Like Jinja2)

Keep using Python to generate full HTML, but:
- Use simpler templates
- Match our minimal CSS style
- Skip web components

**Pros:**
- Works exactly like current Jinja2 version

**Cons:**
- Not web components
- Defeats the "no build" goal

## Recommendation

**Hybrid Approach (Option 1):**

1. **Extend Python pipeline** to generate race manifests:
   ```python
   # In neira/main.py or new command
   @cli.command()
   def generate_ui_data():
       # Read from data/2_reviewed
       # Generate static/data/races-manifest.json
   ```

2. **Build web components pages** to consume the manifest

3. **Keep it simple:** Start with just category pages, skip individual race detail pages initially

## Next Steps

Would you like me to:

**A)** Implement the Python manifest generation?
**B)** Build the category page web component (assuming manifest exists)?
**C)** Start with a simpler approach (manually create a races index)?
**D)** Something else?
