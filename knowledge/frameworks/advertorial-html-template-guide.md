# HTML Template Guide — Advertorial Reference

This file defines the HTML structure, CSS patterns, design system, and layout options for each advertorial format. Every advertorial is a single, self-contained HTML file with all CSS inline (no external stylesheets except Google Fonts).

---

## Design Philosophy

The page should look like an editorial blog post or health journal article — **NOT a sales page**. Readers should feel like they stumbled onto a genuine personal story or journalistic piece. The selling happens through story and mechanism, not through flashy design.

**Key principles:**
- Clean, readable typography with generous white space
- Serif body font for editorial authenticity
- No flashy colors, no countdown timers, no pop-ups
- Images should feel editorial (lifestyle, candid) not commercial (product-on-white)
- The layout should pass the "screenshot test" — if someone took a screenshot and posted it, it should look like a real article

---

## Required Page Elements

Every advertorial must include these elements. The order can vary by format, but all must be present.

### 1. Top Category Bar
A thin bar at the very top with category labels that reinforce the editorial feel.

```html
<div style="background: #f8f8f8; border-bottom: 1px solid #e0e0e0; padding: 8px 0; text-align: center; font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 2px; color: #888;">
  WELLNESS &bull; SKINCARE &bull; HONEST REVIEWS
</div>
```

Customize categories to match the niche: `PET HEALTH`, `JOINT CARE`, `NUTRITION`, `FITNESS`, etc.

### 2. Site Header (Publication Name)
A publication-style name that sells the editorial illusion. This should match whatever domain you'll deploy to.

```html
<header style="text-align: center; padding: 20px 0; border-bottom: 1px solid #e0e0e0;">
  <h1 style="font-family: 'Lora', Georgia, serif; font-size: 28px; font-weight: 700; color: #1a1a1a; margin: 0; letter-spacing: -0.5px;">
    The Scalp Health Journal
  </h1>
</header>
```

**Naming conventions by niche:**
- Pet: "The Canine Wellness Journal," "Pet Health Daily," "The Dog Owner's Guide"
- Skin: "The Skin Health Journal," "Clear Skin Daily," "The Derma Review"
- Supplements: "The Wellness Review," "Natural Health Journal," "The Supplement Insider"
- Fitness: "The Fitness Journal," "Active Living Review," "The Training Post"

### 3. Navigation Bar
Fake nav links that reinforce the niche. These don't need to link anywhere — they're set dressing.

```html
<nav style="text-align: center; padding: 12px 0; border-bottom: 1px solid #eee; font-family: 'Inter', sans-serif; font-size: 13px;">
  <a href="#" style="color: #555; text-decoration: none; margin: 0 15px;">PSORIASIS</a>
  <a href="#" style="color: #555; text-decoration: none; margin: 0 15px;">ECZEMA</a>
  <a href="#" style="color: #555; text-decoration: none; margin: 0 15px;">REVIEWS</a>
  <a href="#" style="color: #555; text-decoration: none; margin: 0 15px;">TREATMENTS</a>
</nav>
```

### 4. Article Headline
Story-driven, curiosity-driven, or revelation-driven. NOT a sales headline.

```html
<h1 style="font-family: 'Lora', Georgia, serif; font-size: 32px; line-height: 1.3; color: #1a1a1a; margin: 30px auto 15px; max-width: 680px; padding: 0 20px;">
  I Was Ready to Give Up on My Scalp — Then a Dermatologist Friend Told Me Something That Changed Everything
</h1>
```

**Headline styles by format:**
- **Personal Story:** "I Was Ready to Give Up on [Problem] — Then [Discovery]"
- **Authority Confession:** "I'm a [Credential] With [X] Years of Experience — And I Was Getting It Wrong"
- **Editorial:** "[Number] [Demographic] Are Discovering [Mechanism] — Here's What [Experts] Say"
- **Listicle:** "[Number] Reasons Why [Common Approach] Isn't Working (And What [Experts] Recommend Instead)"

### 5. Author Byline
Reinforces editorial feel. Include a date and read time.

```html
<div style="font-family: 'Inter', sans-serif; font-size: 13px; color: #888; max-width: 680px; margin: 0 auto 25px; padding: 0 20px;">
  By <span style="color: #333; font-weight: 500;">Sarah Mitchell</span> &nbsp;|&nbsp; March 18, 2026 &nbsp;|&nbsp; 6 min read
</div>
```

### 6. Hero Image
A lifestyle/editorial image near the top. NOT a product shot — this should feel like a blog post image.

```html
<div style="max-width: 720px; margin: 0 auto 30px; padding: 0 20px;">
  <img src="[IMAGE_URL]" alt="[Descriptive alt text]" style="width: 100%; border-radius: 8px; display: block;">
  <p style="font-family: 'Inter', sans-serif; font-size: 12px; color: #999; margin-top: 8px; text-align: center;">
    [Optional caption — e.g., "Bailey before we found the solution"]
  </p>
</div>
```

### 7. Body Copy
Short paragraphs (2-3 sentences max). Serif font. Generous line height. Single-column, max-width constrained.

```html
<div style="max-width: 680px; margin: 0 auto; padding: 0 20px; font-family: 'Lora', Georgia, serif; font-size: 18px; line-height: 1.8; color: #333;">
  <p>The day I found Bailey standing over my grandmother's shredded photo album was the day I almost gave up.</p>
  <p>I'd only been gone two hours. Two hours at the grocery store. And somehow, in that time, he'd pulled the album off the shelf, torn through the cover, and scattered thirty years of memories across the living room floor.</p>
</div>
```

### 8. Pull Quotes / Callout Boxes
Use these to highlight key mechanism revelations or powerful statements. They break up long text and draw the eye to your most important claims.

```html
<div style="max-width: 620px; margin: 30px auto; padding: 25px 30px; background: #f9f7f4; border-left: 4px solid #c8a87c; border-radius: 0 8px 8px 0;">
  <p style="font-family: 'Lora', Georgia, serif; font-size: 20px; line-height: 1.6; color: #2a2a2a; margin: 0; font-style: italic;">
    "It's not a behavior problem — it's a chemistry problem. When cortisol stays elevated, the brain is stuck in fight-or-flight even when there's no threat."
  </p>
  <p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #888; margin: 10px 0 0;">
    — Dr. Amanda Chen, Veterinary Behaviorist
  </p>
</div>
```

**Alternative style — stat callout:**
```html
<div style="max-width: 620px; margin: 30px auto; padding: 20px 30px; background: linear-gradient(135deg, #f0f7f0, #e8f4e8); border-radius: 8px; text-align: center;">
  <p style="font-family: 'Inter', sans-serif; font-size: 36px; font-weight: 700; color: #2d6a2d; margin: 0;">87%</p>
  <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #555; margin: 5px 0 0;">
    of dogs showed reduced anxiety behaviors within 14 days
  </p>
</div>
```

### 9. Product Image Integration
Introduce product shots naturally within the story — NOT as hero images. They should feel like the narrator is showing you what they bought.

```html
<div style="max-width: 500px; margin: 30px auto; padding: 0 20px; text-align: center;">
  <img src="[PRODUCT_IMAGE_URL]" alt="[Product name]" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
</div>
```

Include at least 2-3 product images throughout the page:
- One when the narrator first discovers/receives the product
- One in the proof/ingredients section
- One near the CTA

### 10. Stats/Proof Bar
A horizontal bar of key metrics. Positioned after the mechanism reveal and before the detailed proof section.

```html
<div style="max-width: 720px; margin: 40px auto; padding: 25px 20px; background: #fafafa; border-radius: 12px; display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center;">
  <div style="padding: 10px 15px;">
    <div style="font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 700; color: #1a1a1a;">12,847</div>
    <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #888; margin-top: 4px;">5-Star Reviews</div>
  </div>
  <div style="padding: 10px 15px;">
    <div style="font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 700; color: #1a1a1a;">97%</div>
    <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #888; margin-top: 4px;">Would Recommend</div>
  </div>
  <div style="padding: 10px 15px;">
    <div style="font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 700; color: #1a1a1a;">60-Day</div>
    <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #888; margin-top: 4px;">Money-Back Guarantee</div>
  </div>
</div>
```

### 11. Testimonial Cards
Minimum 2-3 testimonials. They should be **mechanism-anchored** — referencing the specific mechanism from the advertorial, not generic "it works!" quotes.

```html
<div style="max-width: 680px; margin: 30px auto; padding: 0 20px;">
  <!-- Testimonial Card -->
  <div style="background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <div style="display: flex; align-items: center; margin-bottom: 15px;">
      <div style="width: 45px; height: 45px; border-radius: 50%; background: #e8d5c0; display: flex; align-items: center; justify-content: center; font-family: 'Inter', sans-serif; font-weight: 600; color: #8b6f47; font-size: 18px;">
        M
      </div>
      <div style="margin-left: 12px;">
        <div style="font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px; color: #333;">Michelle R.</div>
        <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #888;">Verified Buyer &bull; Phoenix, AZ</div>
      </div>
      <div style="margin-left: auto; color: #f4b942; font-size: 16px;">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
    </div>
    <p style="font-family: 'Lora', Georgia, serif; font-size: 16px; line-height: 1.7; color: #444; margin: 0;">
      "By the end of week two, I came home and nothing was destroyed. I actually cried. After a year of coming home to chaos, I'd forgotten what a peaceful house felt like."
    </p>
  </div>
</div>
```

### 12. CTA Buttons
Minimum 2 CTAs — one mid-page, one at the bottom. Styled as editorial buttons, not aggressive sales buttons. Soft, curiosity-driven language.

```html
<div style="max-width: 680px; margin: 40px auto; text-align: center; padding: 0 20px;">
  <a href="[PRODUCT_URL]" style="display: inline-block; background: #2d6a2d; color: #fff; font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 600; padding: 16px 40px; border-radius: 8px; text-decoration: none; transition: background 0.2s;">
    Check If It's Still In Stock →
  </a>
  <p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #888; margin-top: 12px;">
    Free shipping &bull; 60-day money-back guarantee
  </p>
</div>
```

**CTA text options by tone:**
- Soft/skeptical market: "Check If It's Still Available" / "See If It Works For You"
- Medium confidence: "Try It Risk-Free" / "Get Yours Before They Sell Out"
- Direct/motivated market: "Get Yours Now" / "Order Today"

### 13. Sticky Mobile CTA
A fixed button at the bottom of the screen on mobile devices.

```html
<!-- Sticky Mobile CTA -->
<div style="display: none; position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 12px 20px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 1000; text-align: center;" id="sticky-cta">
  <a href="[PRODUCT_URL]" style="display: block; background: #2d6a2d; color: #fff; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; padding: 14px; border-radius: 8px; text-decoration: none;">
    Check Availability →
  </a>
</div>

<script>
// Show sticky CTA on mobile after scrolling past first CTA
if (window.innerWidth <= 768) {
  document.getElementById('sticky-cta').style.display = 'block';
  // Add padding to body so content isn't hidden behind sticky CTA
  document.body.style.paddingBottom = '80px';
}
</script>
```

### 14. Comparison Table (Optional but Recommended)
For products competing in crowded markets. Keep it simple — your product vs. "everyone else."

```html
<div style="max-width: 620px; margin: 40px auto; padding: 0 20px; overflow-x: auto;">
  <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 14px;">
    <thead>
      <tr>
        <th style="text-align: left; padding: 12px 15px; border-bottom: 2px solid #333; font-size: 13px; color: #888;"></th>
        <th style="text-align: center; padding: 12px 15px; border-bottom: 2px solid #2d6a2d; color: #2d6a2d; font-weight: 700;">[Product Name]</th>
        <th style="text-align: center; padding: 12px 15px; border-bottom: 2px solid #ddd; color: #888; font-weight: 500;">Everyone Else</th>
      </tr>
    </thead>
    <tbody>
      <tr style="background: #fafafa;">
        <td style="padding: 12px 15px; border-bottom: 1px solid #eee;">Active Ingredients</td>
        <td style="padding: 12px 15px; border-bottom: 1px solid #eee; text-align: center; font-weight: 600; color: #2d6a2d;">330mg</td>
        <td style="padding: 12px 15px; border-bottom: 1px solid #eee; text-align: center; color: #999;">150-250mg</td>
      </tr>
      <!-- Add more rows -->
    </tbody>
  </table>
</div>
```

### 15. Footer with Disclosure
Every advertorial needs a clear disclosure at the bottom.

```html
<footer style="max-width: 680px; margin: 60px auto 40px; padding: 30px 20px; border-top: 1px solid #eee; font-family: 'Inter', sans-serif; font-size: 12px; color: #aaa; line-height: 1.6;">
  <p><strong>Disclosure:</strong> This article contains affiliate links. If you click a link and make a purchase, we may receive a commission at no additional cost to you. Individual results may vary. This content is not intended as medical advice.</p>
  <p style="margin-top: 10px;">&copy; 2026 [Publication Name]. All rights reserved.</p>
</footer>
```

---

## Typography System

### Fonts (Google Fonts — import in `<head>`):

```html
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Usage:
| Element | Font | Weight | Size | Color |
|---|---|---|---|---|
| Body copy | Lora (serif) | 400 | 18px | #333 |
| Body bold | Lora (serif) | 600 | 18px | #1a1a1a |
| Headline | Lora (serif) | 700 | 32px | #1a1a1a |
| Subheading | Inter (sans) | 600 | 22px | #1a1a1a |
| Nav / UI | Inter (sans) | 500 | 13px | #555 |
| Stats numbers | Inter (sans) | 700 | 24-36px | #1a1a1a |
| Captions | Inter (sans) | 400 | 12-13px | #888 |
| CTA buttons | Inter (sans) | 600 | 15-16px | #fff |
| Byline | Inter (sans) | 400 | 13px | #888 |
| Pull quotes | Lora (serif italic) | 400 | 20px | #2a2a2a |

### Line Heights:
- Body copy: 1.8 (generous — editorial feel)
- Headlines: 1.3
- UI elements: 1.4

---

## Color System

Use muted, editorial colors. Avoid bright reds, oranges, or anything that screams "advertisement."

### Base Palette:
| Role | Color | Usage |
|---|---|---|
| Text primary | #1a1a1a | Headlines, strong emphasis |
| Text body | #333333 | Body copy |
| Text secondary | #555555 | Nav links, subtext |
| Text muted | #888888 | Bylines, captions, timestamps |
| Background | #ffffff | Page background |
| Background alt | #fafafa | Stats bar, section backgrounds |
| Background warm | #f9f7f4 | Pull quote boxes, callouts |
| Border | #e0e0e0 | Dividers, cards |
| Border light | #eeeeee | Subtle separators |

### Accent Colors (choose ONE per advertorial):
| Niche | Accent | CTA Background | Callout Border |
|---|---|---|---|
| Health/Wellness | Green | #2d6a2d | #4a9a4a |
| Beauty/Skin | Rose | #8b4560 | #c07090 |
| Pet Health | Warm green | #3a7a3a | #5aaa5a |
| Fitness | Blue | #2a5a8a | #4a8aba |
| Supplements | Teal | #2a7a7a | #4aaaaa |
| Weight Loss | Sage | #5a8a5a | #7aba7a |
| Luxury | Gold/Warm | #8b6f47 | #c8a87c |

---

## Layout Options by Format

### Personal Story Layout (Default)
Single-column, linear narrative. The reader scrolls through a story from beginning to end.

```
┌─────────────────────────────────┐
│         Category Bar            │
│         Site Header             │
│         Navigation              │
├─────────────────────────────────┤
│         Headline                │
│         Byline                  │
│         Hero Image              │
│                                 │
│         Opening story...        │
│         Pain agitation...       │
│                                 │
│       ┌─ Pull Quote ──┐        │
│       │  Mechanism     │        │
│       └────────────────┘        │
│                                 │
│         Mechanism reveal...     │
│         Product Image           │
│         Discovery story...      │
│                                 │
│    ═══ Mid-Page CTA ═══        │
│                                 │
│       ┌─ Stats Bar ───┐        │
│       │  Numbers       │        │
│       └────────────────┘        │
│                                 │
│         Proof section...        │
│         Testimonial Cards       │
│         Product Images          │
│                                 │
│       ┌─ Comparison ──┐        │
│       │  Table         │        │
│       └────────────────┘        │
│                                 │
│         Scarcity close...       │
│                                 │
│    ═══ Final CTA ═══           │
│                                 │
│         Footer/Disclosure       │
└─────────────────────────────────┘
│     Sticky Mobile CTA           │
```

### Authority Confession Layout
Same structure as Personal Story, but opens with the authority figure's credentials before the confession.

**Key differences:**
- Headline format: "I'm a [Credential] — And I Was Getting It Wrong"
- Byline includes title: "Dr. Amanda Chen, DVM, Board-Certified Veterinary Behaviorist"
- Hero image can be the authority figure (stock photo or AI-generated)
- Story follows a patient/client, not the authority figure directly
- Pull quotes attributed to the authority figure carry extra weight

### Editorial/Journal Layout
Third-person, news-style. More formal tone, more data, less personal emotion.

**Key differences:**
- Headline is journalistic: "[Number] [People] Are Discovering [Thing] — Here's What Experts Say"
- No first-person narrative — uses "researchers found," "experts say," "users report"
- More pull quotes from named experts
- Heavier on stats and clinical data
- Can include a "Key Takeaways" box near the top (like a news article summary)

```html
<!-- Key Takeaways Box (Editorial format only) -->
<div style="max-width: 620px; margin: 25px auto 35px; padding: 20px 25px; background: #f0f4f8; border-radius: 8px; border: 1px solid #d0d8e0;">
  <p style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #555; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px;">Key Takeaways</p>
  <ul style="font-family: 'Inter', sans-serif; font-size: 14px; line-height: 1.7; color: #444; margin: 0; padding-left: 20px;">
    <li>Key point one</li>
    <li>Key point two</li>
    <li>Key point three</li>
  </ul>
</div>
```

### Listicle Layout
Numbered sections with fast pacing. Each section is a mini-story or discovery.

**Key differences:**
- Headline: "[Number] Reasons Why [Approach] Isn't Working (And What Actually Does)"
- Body organized into numbered sections with subheadings
- Each section is shorter (3-5 paragraphs max)
- Can reveal the product at different points depending on the angle
- More visual breaks between sections

---

## Responsive Design

All advertorials must be mobile-responsive. Key breakpoints:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
  /* Base styles are mobile-first */
  body {
    margin: 0;
    padding: 0;
    background: #fff;
    -webkit-font-smoothing: antialiased;
  }

  /* Images */
  img {
    max-width: 100%;
    height: auto;
  }

  /* Stats bar wraps on mobile */
  @media (max-width: 600px) {
    .stats-bar {
      flex-direction: column;
      gap: 15px;
    }

    /* Slightly smaller body text on mobile */
    .body-copy {
      font-size: 16px;
    }

    /* Full-width CTA buttons on mobile */
    .cta-button {
      display: block;
      width: 100%;
    }

    /* Headline sizing */
    .headline {
      font-size: 26px;
    }
  }
</style>
```

### Mobile-Specific Considerations:
- Body padding: 16-20px on mobile
- Font size: 16px minimum for body (prevents iOS zoom)
- Touch targets: CTA buttons minimum 48px height
- Images: Always `max-width: 100%`
- Tables: Add `overflow-x: auto` wrapper for comparison tables
- Sticky CTA: Only show on screens ≤768px wide
- Add `padding-bottom: 80px` to body when sticky CTA is active

---

## Image Handling

### Product Images
Use the product image URLs the brand provides. For Shopify sites, images are typically at:
- `cdn.shopify.com/s/files/...`
- `[store].com/cdn/shop/files/[filename]`
- `[store].com/cdn/shop/products/[filename]`

### Lifestyle/Story Images
Options for sourcing:
- Brand-provided lifestyle shots
- AI-generated images (via nanobanana or similar) — host these or embed as base64
- Stock photos (use sparingly — they can break the editorial illusion)

### Image Best Practices:
- Always include descriptive `alt` text
- Use `border-radius: 8px` for soft, editorial feel
- Add subtle `box-shadow` to product shots: `0 4px 15px rgba(0,0,0,0.1)`
- Image captions in Inter, 12px, #999
- Hero images: full content width (720px max)
- Product shots: 400-500px max width, centered
- Before/after pairs: side by side on desktop, stacked on mobile

### AI-Generated Image Integration:
When using AI-generated images (from nanobanana or similar tools):
- Save generated images and host them (GitHub, Cloudinary, or Vercel) — DON'T embed as base64 in the HTML (causes file bloat and API errors)
- If base64 is the only option, keep images under 500KB
- Use JPEG format for photographs, PNG for graphics with transparency

---

## Page Template (Full Boilerplate)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Headline] — [Publication Name]</title>
  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #fff; -webkit-font-smoothing: antialiased; }
    img { max-width: 100%; height: auto; display: block; }
    a { color: inherit; }
    @media (max-width: 600px) {
      .hide-mobile { display: none !important; }
      .show-mobile { display: block !important; }
    }
    @media (min-width: 601px) {
      .show-mobile { display: none !important; }
    }
  </style>
</head>
<body>

  <!-- Category Bar -->
  <!-- Site Header -->
  <!-- Navigation -->
  <!-- Headline -->
  <!-- Byline -->
  <!-- Hero Image -->
  <!-- Body Copy Sections -->
  <!-- Pull Quotes -->
  <!-- Product Images -->
  <!-- Mid-Page CTA -->
  <!-- Stats Bar -->
  <!-- Testimonials -->
  <!-- Comparison Table -->
  <!-- Final CTA -->
  <!-- Footer -->
  <!-- Sticky Mobile CTA -->

</body>
</html>
```

---

## Deployment Notes

### GitHub + Vercel (Recommended):
1. Create a repo with the HTML file as `index.html`
2. Connect to Vercel — auto-deploys on push
3. Add custom domain through Vercel dashboard
4. Future edits auto-redeploy

### Domain Strategy:
- Buy a domain that matches the publication name on the page
- e.g., `caninewellnessjournal.com` for "The Canine Wellness Journal"
- This reinforces the editorial illusion when the reader checks the URL bar
- .com is best for paid traffic credibility
