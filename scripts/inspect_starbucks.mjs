import fs from 'fs';

const f = 'dist/restaurants/starbucks-nutrition-calculator/index.html';
const content = fs.readFileSync(f, 'utf8');
console.log(`Total Length: ${(content.length / 1024).toFixed(1)} KB`);

// Find largest blocks
const scriptTags = content.match(/<script[\s\S]*?<\/script>/g) || [];
for (let i = 0; i < scriptTags.length; i++) {
  console.log(`Script ${i}: ${(scriptTags[i].length / 1024).toFixed(1)} KB (Start: ${scriptTags[i].substring(0, 80).replace(/\n/g, ' ')})`);
}

const lines = content.split('\n');
console.log(`Total lines: ${lines.length}`);
