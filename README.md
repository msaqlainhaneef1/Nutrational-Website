# Nutrition Solver

A privacy-first nutrition reference covering 100 restaurant chains, 16,000+ menu items, whole food nutrition data, and a full library of health calculators. Built with Astro. No tracking, no signup, no fluff.

Inspired by the breadth and integration of macroandmeals.com, rebuilt from scratch with a privacy-first architecture suitable for shared static hosting (Hostinger, Netlify, Cloudflare Pages, Vercel, GitHub Pages).

## What this is

- A static site (Astro SSG) that renders every page at build time.
- A restaurant nutrition database with 100 chains and 16,000+ menu items.
- A whole foods reference with calories, macros, and key micronutrients.
- Nine browser-side health calculators (BMI, BMR, TDEE, macro, calorie deficit, ideal weight, body fat, water intake, protein).
- A meal builder with localStorage persistence, shareable links, and a combined FDA nutrition label view.
- An auto meal generator (constraint solver) on every restaurant page.
- A small blog covering energy balance, label literacy, and macro basics.
- A build-time search index (Pagefind) that runs entirely in the browser.

## What this is not

- Not a tracker. No analytics cookies, no third party scripts.
- Not a SaaS. No backend, no database, no signup.
- Not medical advice. Numbers are sourced from public restaurant disclosures and USDA reference data.

## Brand identity

The Nutrition Solver brand is built around a leaf-and-checkmark icon that combines nutrition (the leaf) with solving and verification (the checkmark). The icon is rendered as an SVG favicon and a reusable `BrandLogo.astro` component that draws the same icon inline at three sizes (sm, md, lg). The color palette is emerald-and-teal on a near-black surface, designed for dark mode first and accented with a custom mesh gradient background.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Framework | Astro 7 | Static output, islands architecture, fast builds |
| Styling | Tailwind v4 (CSS-first) | No JS runtime, design tokens in CSS `@theme` |
| Validation | Zod 4 | Build-time schema checks on every JSON file |
| Search | Pagefind 1 | Post-build static search index, lazy-loaded |
| Charts | Chart.js 4 | Lazy-loaded only on food detail pages |
| Sitemap | @astrojs/sitemap | Auto-generated sitemap-index.xml |
| Icons | lucide-astro | Tree-shaken SVG icons, zero runtime |

## Project structure

```
src/
  content/blog/             Markdown blog posts (Astro Content Collections)
  content.config.ts         Blog collection schema
  data/
    foods/*.json            Whole food nutrition data (curated)
    restaurants/*.json      Restaurant menu data (100 chains, 16k items)
  features/
    nutrition/              Food schemas, services, components
    restaurants/            Restaurant schemas, services, components, meal generator
    calculators/            BMI, BMR, TDEE, macro, calorie deficit, ideal weight, body fat, water, protein
    authors/                EEAT author widget
    shared/                 Cross-feature components including BrandLogo and MealBuilder
  layouts/Layout.astro      Master HTML shell with mega-menu, scroll progress, back to top, cookie banner
  pages/                    File-based routes
  styles/global.css         Tailwind v4 theme + glassmorphism utilities + prose-invert typography
public/
  .htaccess                 Hostinger/Apache/LiteSpeed config (HTTPS, gzip, cache, security headers)
  favicon.svg               Custom leaf-and-checkmark icon (gradient emerald/teal)
  manifest.json             PWA-style manifest
  robots.txt                Crawler directives
  llms.txt                  AI discoverability manifest
scripts/
  sync-nutrition.ts         Optional Open Food Facts API importer (manual run)
```

## Calculators (9 tools)

| Tool | Slug | Purpose |
|---|---|---|
| BMI | `/calculators/bmi` | Body Mass Index from height and weight |
| BMR | `/calculators/bmr` | Basal Metabolic Rate (Mifflin-St Jeor) |
| TDEE | `/calculators/tdee` | Total Daily Energy Expenditure |
| Macro | `/calculators/macro` | Protein/carb/fat split by goal and diet approach |
| Calorie deficit | `/calculators/calorie-deficit` | Weight loss timeline projector |
| Ideal weight | `/calculators/ideal-weight` | Devine, Robinson, Miller, Hamwi formulas |
| Body fat | `/calculators/body-fat` | U.S. Navy circumference method |
| Water intake | `/calculators/water-intake` | Daily hydration target |
| Protein | `/calculators/protein` | Daily protein target by goal and activity |

## Commands

```sh
npm install           # install deps (node >= 22.12)
npm run dev           # local dev at localhost:4321
npm run build         # astro build + pagefind index
npm run preview       # preview the built site
```

## Deploying to Hostinger shared hosting

1. Run `npm install && npm run build` locally (Node 22+ required on your machine, not the server).
2. Upload the contents of the `dist/` folder to `public_html/` via File Manager or FTP.
3. The included `.htaccess` file handles HTTPS redirect, gzip compression, browser caching, security headers, and 404 routing. No additional setup needed.
4. Visit your domain. The site should load instantly.

The build produces approximately 3,000 files totaling 45 MB. The largest single file is the Starbucks restaurant page at ~3.9 MB of HTML.

## Adding data

### New restaurant

Drop a JSON file in `src/data/restaurants/<slug>.json` matching the `RestaurantSchema` in `src/features/restaurants/schemas/restaurant.ts`. The site picks it up automatically at build time.

### New whole food

Drop a JSON file in `src/data/foods/<slug>.json` matching the `FoodSchema` in `src/features/nutrition/schemas/food.ts`.

### New calculator

1. Add the logic file at `src/features/calculators/<slug>/<slug>.ts`.
2. Add the calculator widget component at `src/features/calculators/<slug>/<Name>Calculator.astro`.
3. Add the page at `src/pages/calculators/<slug>.astro`.
4. Register the calculator in `src/features/calculators/shared/registry.ts`.

### New blog post

Create a Markdown file in `src/content/blog/<slug>.md` with the required frontmatter (title, description, pubDate, author, category).

## License

Source code is MIT. Nutrition data is sourced from public restaurant disclosures and USDA reference tables, used under fair use for educational reference.
