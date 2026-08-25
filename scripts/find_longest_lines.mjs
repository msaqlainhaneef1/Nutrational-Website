import fs from 'fs';

const f = 'dist/restaurants/starbucks-nutrition-calculator/index.html';
const content = fs.readFileSync(f, 'utf8');
const lines = content.split('\n');

const lineLengths = lines.map((l, idx) => ({ idx, len: l.length, preview: l.substring(0, 100) }));
lineLengths.sort((a, b) => b.len - a.len);

console.log('Top 10 longest lines in Starbucks HTML:');
for (let i = 0; i < 10; i++) {
  console.log(`Line ${lineLengths[i].idx}: ${(lineLengths[i].len / 1024).toFixed(1)} KB -> ${lineLengths[i].preview}`);
}
