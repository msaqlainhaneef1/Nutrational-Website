import fs from 'fs';

const f = 'dist/restaurants/starbucks-nutrition-calculator/index.html';
const content = fs.readFileSync(f, 'utf8');

console.log('--- 0 to 500 chars ---');
console.log(content.substring(0, 500));

console.log('--- 100000 to 100500 chars ---');
console.log(content.substring(100000, 100500));

console.log('--- 1000000 to 1000500 chars ---');
console.log(content.substring(1000000, 1000500));

console.log('--- 3000000 to 3000500 chars ---');
console.log(content.substring(3000000, 3000500));
