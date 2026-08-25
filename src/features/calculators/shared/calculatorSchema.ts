import type { CalculatorMeta } from './registry';

export interface FAQItem {
  q: string;
  a: string;
}

export function createCalculatorSchema(
  meta: CalculatorMeta,
  siteUrl: string,
  faqs?: FAQItem[]
) {
  const cleanSite = siteUrl.replace(/\/$/, '');
  const canonicalUrl = `${cleanSite}/calculators/${meta.slug}/`;

  const webAppSchema = {
    "@type": "WebApplication",
    "@id": `${canonicalUrl}#app`,
    "url": canonicalUrl,
    "name": meta.name,
    "description": meta.description,
    "applicationCategory": "HealthApplication",
    "operatingSystem": "All",
    "browserRequirements": "Requires JavaScript. Requires HTML5.",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };

  const breadcrumbSchema = {
    "@type": "BreadcrumbList",
    "@id": `${canonicalUrl}#breadcrumb`,
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": `${cleanSite}/`
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "Calculators",
        "item": `${cleanSite}/calculators/`
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": meta.shortName || meta.name,
        "item": canonicalUrl
      }
    ]
  };

  const schemas: any[] = [webAppSchema, breadcrumbSchema];

  if (faqs && faqs.length > 0) {
    schemas.push({
      "@type": "FAQPage",
      "@id": `${canonicalUrl}#faq`,
      "mainEntity": faqs.map((faq) => ({
        "@type": "Question",
        "name": faq.q,
        "acceptedAnswer": {
          "@type": "Answer",
          "text": faq.a
        }
      }))
    });
  }

  return schemas;
}
