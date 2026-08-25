import fs from 'fs';

const content = fs.readFileSync('dist/restaurants/starbucks-nutrition-calculator/index.html', 'utf8');
const cardStart = content.indexOf('class="menu-item-card mic"');
const cardEnd = content.indexOf('class="menu-item-card mic"', cardStart + 1);

console.log('Sample Card Length:', cardEnd - cardStart);
console.log('Sample Card Markup:\n', content.substring(cardStart - 5, cardEnd));
