import { dev } from 'astro';

async function start() {
  console.log('Starting Astro dev server via JS API...');
  try {
    const server = await dev({
      server: {
        host: '0.0.0.0',
        port: 4321
      }
    });
    console.log('Astro dev server is ready at http://localhost:4321');
  } catch (err) {
    console.error('Failed to start Astro dev server:', err);
    process.exit(1);
  }
}

start();
