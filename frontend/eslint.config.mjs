import { dirname } from 'path'
import { fileURLToPath } from 'url'
import { FlatCompat } from '@eslint/eslintrc'
import eslintConfigPrettier from 'eslint-config-prettier'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const compat = new FlatCompat({
  baseDirectory: __dirname,
})

const eslintConfig = [
  {
    ignores: [
      '**/node_modules/**',
      '**/.pnpm/**',
      '**/.next/**',
      '**/out/**',
      '**/build/**',
      '**/dist/**',
    ],
  },
  ...compat.extends('next/core-web-vitals'),
  {
    files: ['**/*.{js,jsx}'],
    rules: {
      eqeqeq: ['error', 'always'], // error on using == vs ===
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }], //ignores unused if beginning with _
      'jsx-a11y/alt-text': 'warn', // img alt text req
      'jsx-a11y/anchor-is-valid': 'error', //checks a tags validity
      'no-console': ['warn', { allow: ['warn', 'error'] }], // checks for console.log
      curly: 'error',
      'react/self-closing-comp': ['warn', { component: true, html: true }], //if no children
    },
  },
  eslintConfigPrettier,
]

export default eslintConfig
