// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://wangjagom.github.io',
  base: '/sap-notes',
  trailingSlash: 'always',
  build: { format: 'directory' },
  integrations: [mdx(), react()],
  devToolbar: { enabled: false },
});
