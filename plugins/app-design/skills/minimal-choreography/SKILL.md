---
name: minimal-choreography
description: Enforce a minimal motion choreography for every page of a web app or site — one animated moment at most, motion only in response to gestures, reduced-motion fallback, an explicit list of what must not move — written as docs/choreographie/<page>.md before the page is created. Use whenever the user creates a new page, view, landing page or website, asks for animations, Framer Motion / Motion, page transitions, "make it feel alive", or wants a consistent motion system.
---

# Minimal choreography

A page earns motion; it does not get it by default. Before a page exists, its
choreography is decided and written down, then implemented with shared tokens.
This plugin ships the `choregraphe` agent (writes the sheet) and a
`PreToolUse` hook (refuses to create a page whose sheet is missing).

## Set up in a project

1. Copy `templates/choreographie-modele.md.stub` to
   `docs/choreographie/_modele.md` (strip `.stub`).
2. Optional `.claude/choreography.json`:
   `{"docs": "docs/choreographie", "ignore": ["sitemap"]}` — `ignore` lists
   page names that are not pages (feeds, XML views).
3. Add motion tokens to the CSS/JS: `short` 180 ms, `medium` 450 ms,
   `long` 1100 ms, `spring` `cubic-bezier(0.22, 1, 0.36, 1)`; one JS module
   that runs each page's single moment (e.g. a `data-entree` attribute on the
   header that settles in), muted under `prefers-reduced-motion`.
4. Add a CI test that every page has a complete sheet (the hook only guards
   Claude's writes).

## Page names (what the hook recognizes)

| File | Sheet |
|---|---|
| `resources/views/pages/home.blade.php` | `home.md` |
| `resources/views/articles/show.blade.php` | `articles-show.md` |
| `app/pricing/page.tsx` (Next.js) | `pricing.md` |
| `src/pages/blog/index.vue` / `.astro` / `.svelte` | `blog-index.md` |
| `public/kit.html` | `kit.md` |

Blade components, layouts, partials and mail views are not pages.

## Principles (why)

- One orchestrated moment lands; scattered fade-ups read as generated.
- Motion that answers an action explains what changed; motion for its own
  sake costs attention and battery.
- Reduced motion is not an afterthought: the page must be complete without
  any animation.

## Reference implementation

Missions Solidarité Liban (`joe17xe/Msl-website`): `docs/choreographie/`,
`resources/js/choregraphie.js`, `resources/js/carte.js`,
`tests/Feature/ChoregraphieTest.php`.
