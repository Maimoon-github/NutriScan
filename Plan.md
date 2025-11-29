I’ll quickly scan the repo to map APIs, services, and current gaps.

Research NutriScan backend and API surface

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/nutriscan/settings.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/nutriscan/urls.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/urls.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/views.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/serializers.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/models.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/services/ocr.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/services/pipeline.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/api_contract.json)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/test_api.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/requirements.txt)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/manage.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/README.md)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/Pseudocode.md)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/scripts/init_pinecone.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/scripts/ingest_regulations.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/admin.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/backend_logic.py)

Read [](file:///c%3A/Users/CreativePC/Documents/vscode/NutriScan/analyzer/apps.py)

Here’s a concise, actionable plan to move the frontend forward, based on the repo and spec you shared.

## Plan: Frontend MVP For NutriScan

Build a mobile-first MVP focused on the scan-to-answer flow, integrating with the existing `/api/v1/scan/` endpoint. Use Flutter for the user app (per product spec), and optionally add a lightweight React + Vite web console for QA/admin. Keep costs near zero using community/free tiers and ship a thin UI that cleanly renders the contract the backend already enforces (Traffic Light, Why, Citations, Better Swaps). Defer auth and advanced features to Phase 2.

### Steps
1. Finalize API contract and dev config
2. Choose frontend track(s) and scaffold projects
3. Implement Scan flow and API integration
4. Build Results UI (Traffic Light + Explainers)
5. Add polish: loading, errors, retries, i18n
6. Ship a QA web console (optional but fast win)

### Further Considerations
1. Auth strategy and rate-limit: add JWT in Phase 2
2. Real AI toggle: make “mock vs. live” selectable for demos
3. Accessibility and Urdu/RTL: verify early for layout issues

— — —

**1) What to do next, why it matters, and how to do it**

- Finalize API Contract
  - What: Lock request/response for `/api/v1/scan/`; fix api_contract.json filename typo; document fields the UI must render.
  - Why: Prevent breaking UI; align fields like `traffic_light`, `why`, `citations`, `better_swaps`, `ingredients`, `allergens`, `ocr_confidence`, `latency_ms`.
  - How: Validate the serializer contract in serializers.py; rename the JSON contract file to match; add 2–3 example responses (success/partial/unreadable).

- Pick Frontend Track(s)
  - What: Primary mobile app in Flutter (per spec). Optional React + Vite web console for internal testing.
  - Why: Flutter delivers Android/iOS fast; React console accelerates QA without building mobile every time.
  - How:
    - Flutter: Use `camera` (or `image_picker`) for capture, `dio` for upload, `riverpod` for state, `go_router` for navigation, `intl` for i18n.
    - React: Vite + React + TypeScript; `tailwindcss` for styling, `@tanstack/react-query` for API, `react-hook-form` + `zod` for upload/validation.

- Implement Scan Flow (MVP)
  - What: Camera/gallery capture → multipart POST `/api/v1/scan/` → show result.
  - Why: Core value prop; use backend fallbacks to ensure consistent demos even without live OCR/LLM/RAG.
  - How: POST `file` (image) and optional `profile` JSON string; bound size to ≤10MB; handle 400 (validation) and 500 (pipeline mismatch) gracefully.

- Results UI (Traffic Light + Why)
  - What: Render `traffic_light` badge, `summary`, `issues`, `ingredients`, `allergens`, `regulatory_flags`, `citations`, `better_swaps`.
  - Why: Delivers the “Is it safe?” moment with clear, explainable reasoning and alternatives.
  - How: Components:
    - TrafficLightBadge (Green/Yellow/Red based on `status`/`traffic_light`)
    - WhyAccordion (expandable explainers with `citations`)
    - IngredientList + AllergenChips
    - BetterSwapsList with price/health hints (textual for now)
    - Meta panel: `ocr_confidence`, `latency_ms`

- UX Polish & Resilience
  - What: Loading skeletons, progress bar on upload, retries, offline copy, Urdu/RTL layout, accessibility color contrast.
  - Why: Feels fast, inclusive, and reliable on low-end phones and flaky networks.
  - How: Show skeleton while uploading; expose “Try again” and “Use sample image” paths; add i18n keys for English/Urdu; verify contrasts for the red/green palette.

- Optional: Web QA Console
  - What: Simple drag-and-drop uploader to the same endpoint; render the same contract.
  - Why: Validate backend and content quickly; easy shareable demos.
  - How: One page: Dropzone → POST → Results panel using the same field mapping as mobile.

— — —

**2) Technology recommendations (efficient or free)**

- Mobile App (Primary)
  - Flutter: fastest to meet spec; single codebase Android/iOS; strong camera and i18n support.
  - Libraries: `camera` or `image_picker` (capture), `dio` (HTTP), `riverpod` (state), `go_router` (nav), `intl` (i18n), `freezed` (models).

- Web Console (Optional/QC)
  - React + Vite + TypeScript: fast dev, great DX.
  - Tailwind CSS: speed up UI; pair with Headless UI or `shadcn/ui` for ready components.
  - Data libs: `@tanstack/react-query` (fetch/cache), `react-hook-form` + `zod` (validation), `axios` (HTTP).
  - PWA readiness: free “installable” demo later.

- Backend (Keep as-is for now)
  - Django + DRF: already implemented and contract-enforced. Add `djangorestframework-simplejwt` in Phase 2 if auth is needed.
  - CORS: leave open in dev; tighten in prod via `django-cors-headers`.

- AI/Infra (Free or near-free paths)
  - LLM: Local `ollama` model.
  - Vector DB: Skip for MVP; use mocked RAG (already supported). Later: Pinecone free tier.
  - Analytics/Errors: PostHog Community (product analytics), Sentry free (crash/reporting).
  - CI/CD: GitHub Actions.

— — —

**3) Actionable, prioritized steps**

- Phase 0: Align Contracts (0.5 day)
  - Confirm `/api/v1/scan/` inputs/outputs; fix the JSON contract filename; add sample responses.
  - Ensure CORS dev domains include your local/mobile IP.

- Phase 1: Flutter App Scaffold (1–2 days)
  - Create app shell with `Home`, `Scan`, `Result` routes; wire `riverpod` and `go_router`.
  - Add camera/gallery capture; limit image size; store last result locally for quick re-open.

- Phase 2: API Integration + UI (2–3 days)
  - Implement multipart POST; parse response; map to UI components; display Traffic Light, Why, Citations, Better Swaps.
  - Add loaders, retries, and a “Use sample image” pathway for demos.

- Phase 3: i18n + Accessibility (1–2 days)
  - Add English/Urdu localization; verify RTL layouts; adjust color contrast for status badges.

- Phase 4: Web QA Console (Optional, 1 day)
  - Vite + React + Tailwind; single-page uploader; render same fields; share with stakeholders for quick validation.

- Phase 5: Hardening (Later)
  - Add JWT auth (DRF SimpleJWT), rate limit, and telemetry; toggle “live vs. mock” AI mode; prepare store assets.

— — —

If you’d like, I can draft the concrete Flutter screen structure and state/data models next, or alternatively scaffold a minimal React + Vite QA console. Which track do you want to start with first?