// result/eslint.config.js
import js from '@eslint/js';
import globals from 'globals';

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        // Add any other global variables your app uses, e.g., if you use Angular
        'angular': 'readonly',
        'io': 'readonly' // For socket.io.js
      },
    },
    rules: {
      // Your custom rules here
      'no-unused-vars': 'warn',
      'indent': ['error', 2],
      'linebreak-style': ['error', 'unix'],
      'quotes': ['error', 'single'],
      'semi': ['error', 'always'],
      // Potentially security-related rules for SAST
      'no-eval': 'error',
      'no-implied-eval': 'error',
      // etc.
    }
  }
];
