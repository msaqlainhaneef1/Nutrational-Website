# Workspace Rules - Nutrition Platform Architecture Guidelines

The following rules apply to all code modifications, refactorings, and feature additions in this repository.

---

## 1. Page Responsibility (`src/pages`)
**Purpose:** SEO and routing configuration only.

**Allowed Operations:**
- Route parameter parsing and data collection.
- Loading data via feature services.
- Defining SEO Meta Titles, Descriptions, Canonical URLs, and Open Graph tags.
- Constructing page-specific JSON-LD schemas.
- Compositing layouts and passing props to main orchestrator components.

**Strictly Forbidden:**
- Inline CSS styling block tags.
- Direct database queries or API fetching logic.
- Calculation formulas, unit conversions, or scaling math.
- Long raw HTML structures.
- Duplicated utility functions.

**Target File Size:** 20 - 80 lines.

---

## 2. Layouts Responsibility (`src/layouts`)
Layouts (e.g. `Layout.astro`) are restricted to orchestrating the primary document tags:
- Base HTML wrapper (`<!doctype html>`, `<html lang="en">`).
- Metadata head content parsing (`<title>`, `<meta>`, link tags).
- Global headers, navigation bars, and footers.
- Base style imports and common scripts.

---

## 3. Modular Folder Allocation
All modules must be segregated by domain scope inside `src/features/` or global folders:
- **`src/features/`**: Code must be organized into feature subfolders (e.g., `nutrition/`, `calculators/`, `restaurants/`, `authors/`, `shared/`). Each feature folder holds its respective `components/`, `services/`, `schemas/`, and helper `utils/`.
- **`src/data/`**: Holds only static database files (JSON arrays or tables).
- **`src/content/`**: Holds markdown collections for articles or guides.

---

## 4. UI Components Rule
- Components must have a single responsibility and remain presentation-focused.
- Do not make direct HTTP fetch calls inside components.
- Components should not exceed 300 - 500 lines of code. Split complex items into smaller subcomponents.

---

## 5. JavaScript / TypeScript Segregation
- Business logic, calculators, utility helpers, and API endpoints must remain strictly inside dedicated TS files (`.ts`).
- Never duplicate code. Utility math or string formatting should go to helper services or the `utils/` directory.

---

## 6. AI Development Constraints
- Keep CSS modular. Keep page files thin.
- Lazy-load interactive components (e.g., charts, search UI, complex calculations) using client directives (`client:visible`, `client:idle`, etc.) to keep JavaScript bundles lightweight.
- Build search indexes at post-build step rather than runtime queries.
