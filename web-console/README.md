# NutriScan Web Console

Internal QA console for testing the NutriScan API without building the mobile app.

## Features

- 📤 Drag-and-drop image upload
- 🚦 Traffic light safety indicator  
- 🔍 Detailed ingredient analysis
- ⚠️ Allergen alerts
- 📚 Regulatory citations
- 💡 Better product alternatives
- ⚡ Real-time API integration

## Tech Stack

- **Framework**: Vite + React + TypeScript
- **Styling**: Tailwind CSS
- **Data Fetching**: @tanstack/react-query
- **HTTP Client**: Axios
- **Form Validation**: react-hook-form + zod

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Configuration

Create a `.env` file:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Usage

1. Ensure Django backend is running at `http://127.0.0.1:8000`
2. Start the dev server: `npm run dev`
3. Open `http://localhost:5173`
4. Upload a food label image
5. View instant analysis results

## API Contract

Matches the backend `/api/v1/scan/` endpoint specification in `../api_contract.json`.

**Request:**
- `file`: Image file (JPG, PNG, WEBP, max 10MB)
- `user_profile` (optional): JSON with age_months, region, dietary_restrictions

**Response:**
- `traffic_light`: Safety status (green/yellow/red)
- `parsed_ingredients`: Ingredient list with risk levels
- `allergen_alerts`: Detected allergens with severity
- `why`: Explanation with citations
- `better_swaps`: Alternative product recommendations
- `ocr_confidence`, `latency_ms`: Metadata

## Development

This console is for **internal testing only**. The primary user-facing app is built with Flutter.

---

## React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
