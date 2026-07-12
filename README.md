# NutriFlow

A privacy-first nutrition reference site covering 100 restaurant chains, 16,000+ menu items, and a growing library of whole foods. Built with Astro, Tailwind v4, and zero runtime trackers.

## What this is

- A static site (Astro SSG) that renders every page at build time.
- A restaurant nutrition database with 100 chains and full macro data per item.
- A whole foods reference with calories, macros, and key micronutrients.
- Three browser-side health calculators (BMI, BMR, TDEE).
- A small blog covering energy balance, label literacy, and macro basics.
- A build-time search index (Pagefind) that runs entirely in the browser.

## What this is not

- Not a tracker. No analytics cookies, no third-party scripts.
- Not a SaaS. No backend, no database, no signup.
- Not medical advice. Numbers are sourced from public restaurant disclosures and USDA reference data.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Framework | Astro 7 | Static output, islands architecture, fast builds |
| Styling | Tailwind v4 (CSS-first) | No JS runtime, design tokens in CSS `@theme` |
| Validation | Zod 4 | Build-time schema checks on every JSON file |
| Search | Pagefind 1 | Post-build static search index, lazy-loaded |
| Charts | Chart.js 4 | Lazy-loaded only on food detail pages |
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
    restaurants/            Restaurant schemas, services, components
    calculators/            BMI, BMR, TDEE logic and UI
    authors/                EEAT author widget
    shared/                 Cross-feature components and services
  layouts/Layout.astro      Master HTML shell
  pages/                    File-based routes (8 routes + 100 dynamic)
  styles/global.css         Tailwind v4 theme + glassmorphism utilities
scripts/
  sync-nutrition.ts         Optional OFF API importer (manual run)
```

## Commands

```sh
npm install           # install deps (node >= 22.12)
npm run dev           # local dev at localhost:4321
npm run build         # astro build + pagefind index
npm run preview       # preview the built site
```

## Adding data

### New restaurant

Drop a JSON file in `src/data/restaurants/<slug>.json` matching the `RestaurantSchema` in `src/features/restaurants/schemas/restaurant.ts`. The site picks it up automatically at build time.

### New whole food

Drop a JSON file in `src/data/foods/<slug>.json` matching the `FoodSchema` in `src/features/nutrition/schemas/food.ts`.

### New blog post

Create a Markdown file in `src/content/blog/<slug>.md` with the required frontmatter (title, description, pubDate, author, category).

## License

Source code is MIT. Nutrition data is sourced from public restaurant disclosures and USDA reference tables, used under fair use for educational reference.
