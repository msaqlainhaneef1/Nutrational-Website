import fs from 'fs';
import path from 'path';

function walkDir(dir) {
  let files = [];
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) {
      files = files.concat(walkDir(filePath));
    } else if (file.endsWith('.html')) {
      files.push(filePath);
    }
  }
  return files;
}

const htmlFiles = walkDir('dist');
for (const f of htmlFiles) {
  const content = fs.readFileSync(f, 'utf8');
  const linkMatches = content.match(/href="\/([a-zA-Z0-9_\-\/]+)"/g);
  if (linkMatches) {
    for (const lm of linkMatches) {
      const url = lm.replace(/^href="/, '').replace(/"$/, '');
      if (!url.endsWith('/') && !url.includes('.') && !url.includes('#') && !url.includes('?')) {
        console.log(`Found slashless link: ${url} in file: ${f}`);
      }
    }
  }
}
