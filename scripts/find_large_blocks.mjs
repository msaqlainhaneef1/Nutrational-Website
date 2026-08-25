import fs from 'fs';

const f = 'dist/restaurants/starbucks-nutrition-calculator/index.html';
const content = fs.readFileSync(f, 'utf8');

// Find all tags in line 0
let pos = 0;
while (pos < content.length && pos < 5000000) {
  const nextScript = content.indexOf('<script', pos);
  const nextStyle = content.indexOf('<style', pos);
  const nextDiv = content.indexOf('<div', pos);
  
  const minPos = Math.min(
    nextScript === -1 ? Infinity : nextScript,
    nextStyle === -1 ? Infinity : nextStyle,
    nextDiv === -1 ? Infinity : nextDiv
  );
  
  if (minPos === Infinity) break;
  
  const tagEnd = content.indexOf('>', minPos);
  const tagHeader = content.substring(minPos, Math.min(tagEnd + 1, minPos + 120));
  
  let blockEnd = -1;
  if (minPos === nextScript) blockEnd = content.indexOf('</script>', minPos);
  else if (minPos === nextStyle) blockEnd = content.indexOf('</style>', minPos);
  else blockEnd = content.indexOf('</div>', minPos);
  
  const blockLength = blockEnd !== -1 ? blockEnd - minPos : 0;
  if (blockLength > 50000) {
    console.log(`LARGE BLOCK at ${minPos} (${(blockLength / 1024).toFixed(1)} KB): ${tagHeader.replace(/\n/g, ' ')}`);
  }
  
  pos = minPos + Math.max(1, blockLength);
}
