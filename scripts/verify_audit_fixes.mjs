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
console.log(`Analyzing ${htmlFiles.length} generated HTML pages in dist/...\n`);

let maxSizeBytes = 0;
let maxFile = '';
let totalLargePages = 0;
let schemaCount = 0;
let schemaErrors = 0;
let slashlessLinks = 0;

for (const f of htmlFiles) {
  const stat = fs.statSync(f);
  if (stat.size > maxSizeBytes) {
    maxSizeBytes = stat.size;
    maxFile = f;
  }
  if (stat.size > 2 * 1024 * 1024) {
    totalLargePages++;
    console.error(`[ERROR] File exceeds 2MB: ${f} (${(stat.size / 1024 / 1024).toFixed(2)} MB)`);
  }

  const content = fs.readFileSync(f, 'utf8');

  // Check Schema
  const schemaMatches = content.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g);
  if (schemaMatches) {
    for (const sm of schemaMatches) {
      schemaCount++;
      const jsonStr = sm.replace(/<script type="application\/ld\+json">/, '').replace(/<\/script>/, '');
      try {
        const parsed = JSON.parse(jsonStr);
        // Check for disallowed @type: "Restaurant" without local business fields
        if (parsed['@type'] === 'Restaurant' || (Array.isArray(parsed['@graph']) && parsed['@graph'].some(x => x['@type'] === 'Restaurant'))) {
          schemaErrors++;
          console.error(`[SCHEMA ERROR] Disallowed Restaurant type on: ${f}`);
        }
      } catch (e) {
        schemaErrors++;
        console.error(`[JSON ERROR] Malformed JSON-LD in ${f}: ${e.message}`);
      }
    }
  }

  // Check for internal links with missing trailing slash (e.g. href="/restaurants/subway" or href="/calculators/bmi")
  const linkMatches = content.match(/href="\/([a-zA-Z0-9_\-\/]+)"/g);
  if (linkMatches) {
    for (const lm of linkMatches) {
      const url = lm.replace(/^href="/, '').replace(/"$/, '');
      if (!url.endsWith('/') && !url.includes('.') && !url.includes('#') && !url.includes('?')) {
        slashlessLinks++;
        // console.warn(`[SLASHLESS LINK] ${url} in ${f}`);
      }
    }
  }
}

console.log('=== AUDIT VERIFICATION SUMMARY ===');
console.log(`Total HTML Pages: ${htmlFiles.length}`);
console.log(`Largest Page: ${maxFile} (${(maxSizeBytes / 1024).toFixed(1)} KB)`);
console.log(`Pages > 2 MB (Googlebot limit): ${totalLargePages} (Target: 0)`);
console.log(`Schema.org script tags checked: ${schemaCount}`);
console.log(`Schema / Rich Result errors: ${schemaErrors} (Target: 0)`);
console.log(`Slashless internal links detected: ${slashlessLinks} (Target: 0)`);

if (totalLargePages === 0 && schemaErrors === 0 && slashlessLinks === 0) {
  console.log('\n>>> SUCCESS: ALL AUDIT ISSUES FULLY RESOLVED! <<<');
} else {
  console.log('\n>>> SOME ISSUES REQUIRE FURTHER REFINEMENT <<<');
}
