import { dev } from 'astro';

async function start() {
  console.log('Initializing Astro Dev Server...');
  const server = await dev({
    root: process.cwd(),
    server: {
      host: '127.0.0.1',
      port: 4321,
    },
  });
  console.log('Astro Dev Server started on http://127.0.0.1:4321/');
}

start().catch((err) => {
  console.error('Error starting Astro server:', err);
  process.exit(1);
});
