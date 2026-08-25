import fs from 'fs';

const content = fs.readFileSync('dist/restaurants/starbucks-nutrition-calculator/index.html', 'utf8');

const head = content.substring(0, content.indexOf('</head>'));
console.log(`HEAD size: ${(head.length / 1024).toFixed(1)} KB`);

const menuGridStart = content.indexOf('id="menu-items-grid"');
const menuGridEnd = content.indexOf('id="menu-empty-state"');
const menuGrid = content.substring(menuGridStart, menuGridEnd);
console.log(`Menu grid size: ${(menuGrid.length / 1024).toFixed(1)} KB`);

const rest = content.length - head.length - menuGrid.length;
console.log(`Rest of page size: ${(rest / 1024).toFixed(1)} KB`);
console.log(`Total: ${(content.length / 1024).toFixed(1)} KB`);
