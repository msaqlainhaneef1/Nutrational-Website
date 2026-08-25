import fs from 'fs';
import path from 'path';

const INDEXNOW_KEY = '8f7b2439c2d14b1897c4f44778be1a85';
const HOST = 'nutritionsolver.com';
const KEY_LOCATION = `https://${HOST}/${INDEXNOW_KEY}.txt`;

// Read dist directory or restaurant/calculator registries to compile the URL list
async function getUrlList() {
  const urls = [
    `https://${HOST}/`,
    `https://${HOST}/restaurants/`,
    `https://${HOST}/foods/`,
    `https://${HOST}/calculators/`,
    `https://${HOST}/about/`,
    `https://${HOST}/contact/`,
    `https://${HOST}/privacy/`,
    `https://${HOST}/terms/`,
    `https://${HOST}/search/`,
    `https://${HOST}/authors/`,
    `https://${HOST}/authors/sarah-jenkins/`,
    `https://${HOST}/editorial-policy/`,
    `https://${HOST}/disclaimer/`,
    `https://${HOST}/cookie-policy/`,
  ];

  // Add calculators
  const calcs = ['bmi', 'bmr', 'tdee', 'macro', 'calorie-deficit', 'ideal-weight', 'body-fat', 'water-intake', 'protein'];
  for (const c of calcs) {
    urls.push(`https://${HOST}/calculators/${c}/`);
  }

  // Add foods
  const foodsDir = path.resolve('src/data/foods');
  if (fs.existsSync(foodsDir)) {
    const foodFiles = fs.readdirSync(foodsDir).filter(f => f.endsWith('.json'));
    for (const f of foodFiles) {
      const slug = f.replace('.json', '');
      urls.push(`https://${HOST}/foods/${slug}/`);
    }
  }

  // Add restaurants
  const restDir = path.resolve('src/data/restaurants');
  if (fs.existsSync(restDir)) {
    const restFiles = fs.readdirSync(restDir).filter(f => f.endsWith('.json'));
    for (const f of restFiles) {
      const slug = f.replace('.json', '');
      urls.push(`https://${HOST}/restaurants/${slug}/`);
    }
  }

  return [...new Set(urls)];
}

async function submitIndexNow() {
  const urlList = await getUrlList();
  console.log(`Found ${urlList.length} canonical URLs to submit to IndexNow...`);

  const payload = {
    host: HOST,
    key: INDEXNOW_KEY,
    keyLocation: KEY_LOCATION,
    urlList: urlList,
  };

  try {
    const response = await fetch('https://api.indexnow.org/indexnow', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: JSON.stringify(payload),
    });

    console.log(`IndexNow Submission Status: ${response.status} ${response.statusText}`);
    if (response.status === 200 || response.status === 202) {
      console.log('Successfully submitted all URLs to IndexNow!');
    } else {
      const text = await response.text();
      console.log('IndexNow Response:', text);
    }
  } catch (err) {
    console.error('Error submitting to IndexNow:', err.message);
  }
}

submitIndexNow();
