import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: 5173,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
        '/output': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
        '/assets': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
        '/reddit-api': {
          target: 'https://www.reddit.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/reddit-api/, ''),
          secure: false,
          headers: {
            'User-Agent': 'web:reddit-shorts-studio:v1.0 (by /u/any-meaning5473)'
          }
        },
        // OAuth token endpoint (www.reddit.com/api/v1/access_token)
        '/reddit-oauth': {
          target: 'https://www.reddit.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/reddit-oauth/, ''),
          secure: false,
          headers: {
            'User-Agent': 'web:reddit-shorts-studio:v1.0 (by /u/any-meaning5473)'
          }
        },
        // Authenticated data endpoint (oauth.reddit.com)
        '/reddit-data': {
          target: 'https://oauth.reddit.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/reddit-data/, ''),
          secure: false,
          headers: {
            'User-Agent': 'web:reddit-shorts-studio:v1.0 (by /u/any-meaning5473)'
          }
        }
      },
    },
    plugins: [react()],
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY ?? ''),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY ?? ''),
      'process.env.REDDIT_CLIENT_ID': JSON.stringify(env.REDDIT_CLIENT_ID ?? ''),
      'process.env.REDDIT_CLIENT_SECRET': JSON.stringify(env.REDDIT_CLIENT_SECRET ?? '')
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    }
  };
});
