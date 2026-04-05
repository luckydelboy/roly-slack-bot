---
name: advertorial
description: "Build high-converting advertorial landing pages (story-style, listicle, or editorial blog format) as complete, deploy-ready HTML files. Use this skill whenever the user asks to create an advertorial, build a landing page, write a story-style ad page, create a native ad landing page, make an editorial-style sales page, build an advertorial funnel page, or anything related to creating long-form advertorial content for paid traffic. Also trigger when the user mentions advertorial, landing page for ads, story page, personal story ad, blog-style ad, native ad page, editorial ad, beauty advertorial, health advertorial, supplement advertorial, or presell page. If the user asks to 'build a page' for a product or client, this is almost certainly the right skill."
---

# Advertorial Landing Page Builder

You build high-converting advertorial landing pages — personal story / editorial blog-style HTML pages that look like native content, not ads. These pages are designed to be the bridge between a paid ad and a product page, warming the reader through story, mechanism, and proof before they click through to buy.

**Before writing anything**, read the reference files:
- `references/copy-frameworks.md` — The Three Core Tests, mechanism types, awareness levels, pain layering, emotional state matching, gender-specific rules, bottom-up writing, catalyst hooks
- `references/html-template-guide.md` — HTML structure, CSS patterns, design system, and layout options for each advertorial format

## What You Need From the User

Before building an advertorial, gather this information (ask if not provided):

1. **Product/Brand**: What's the product? Price? Key ingredients/features? Product page URL?
2. **Target audience**: Who are we writing for? Gender, age range, key pain points, emotional state (beaten down and skeptical, or motivated and ready)?
3. **Core angle/hook**: What's the story angle? (e.g., "failed prescriptions," "doctor's secret," "accidental discovery"). If they have research docs or a brief, read those first.
4. **Awareness level**: Is the audience problem-unaware, problem-aware, or solution-aware? (Default to problem-aware if unclear)
5. **Advertorial format**: Which style?
   - **Personal Story** (default — first-person narrative, most versatile)
   - **Authority Confession** (professional confesses they were wrong, discovers product through a patient/client — high credibility for health/supplement)
   - **Editorial/Journal** (third-person, news-style, higher authority feel)
   - **Listicle** (numbered reasons/discoveries, fast-paced, high engagement)
6. **Product images**: URLs for product shots, before/after images, lifestyle images, ingredient images. If not provided, ask or look on their website.
7. **CTA destination**: Where does the buy button link to? (product page URL, checkout link, etc.)
8. **Any research/brief docs**: Google Drive docs, PDFs, or notes with market research, pain banks, personas, angles.

## The Advertorial Copywriting Process

Follow this order. Do NOT start writing the opening hook first — build from the mechanism outward.

### Step 1: Build the Mechanism

Every advertorial needs a core mechanism — the "reason why" that makes everything else click. Read `references/copy-frameworks.md` for the full framework. In short:

**Unique Problem Mechanism (UPM)**: Reframe WHY the problem exists in a way the audience hasn't heard before. This is your "big idea."
- Research what the audience currently believes causes their problem
- Find the gap or missing piece in their understanding
- Create a new explanation that shifts blame away from them and toward a system, process, or hidden cause
- Example: "Your scalp isn't diseased — it's starving. Medical treatments suppress symptoms but never feed the microbiome that actually controls flare-ups."

**The Big Domino**: What single belief, if accepted, makes every objection irrelevant? Build the entire advertorial to push this one domino over.

### Step 2: Map the Pain Stack

Document three layers of pain using the audience's actual language (from reviews, forums, research docs):

1. **Surface pain**: The obvious symptom ("my scalp flakes constantly")
2. **Life impact pain**: How it affects daily life ("I haven't worn a dark shirt in three years")
3. **Deepest pain**: The shame/fear underneath ("I'm terrified my partner finds me disgusting")

The pain stack IS your credibility. If you describe their experience so precisely they think "how does this person know my life?" — they'll trust everything that follows. This is the Credibility Transfer Principle.

### Step 3: Structure the Page (Bottom-Up)

Write in this order, then arrange into final page layout:

1. **Mechanism section** — the "revelation" or discovery
2. **Proof elements** — testimonials, stats, before/after, ingredient science
3. **CTA and offer** — what they do next
4. **Personal story / hero's journey** — the narrator's discovery arc
5. **Problem agitation** — pain stack, failed solutions
6. **Opening hook / headline** — write this LAST, once you know exactly what the page delivers

### Step 4: Apply the Three Core Tests

Before finalizing, every key sentence must pass:

1. **Can I visualize it?** — Use concrete, sensory language. Not "effective treatment" but "the flakes stopped falling onto my black sweater by day four."
2. **Can I falsify it?** — Make provable claims. Not "amazing results" but "87% of users saw visible improvement within 2 weeks."
3. **Can nobody else say this?** — The copy should be uniquely true to THIS product. If a competitor could sign their name to it, rewrite it.

### Step 5: Match Emotional State and Gender

**Low-energy, skeptical markets** (chronic health, debt, weight loss for women):
- Empathize first: "It's not your fault"
- Shift blame to external systems/forces
- Position the product as "fighting back" against those forces
- Softer CTAs: "See if it works for you" not "Buy now"

**High-energy, motivated markets** (fitness, business growth, luxury):
- Challenge and push: "You know you're capable of more"
- Status/exclusivity framing
- Strong, direct CTAs

**Selling to women** (validation-first approach):
- Start with validation: "You've already tried everything — that takes real strength"
- Never imply they're broken, stupid, or failing
- Third-person problem framing: "Women who deal with this often find..."
- Use "free gifts" not "free bonuses"; supportive not aggressive language
- Include testimonials from similar women; address fears about judgment

**Selling to men**:
- Direct confrontation and challenge
- Data, process, logic, systematic approaches
- Status and exclusivity appeal

## HTML Output Requirements

The output is always a single, self-contained HTML file with all CSS inline (no external stylesheets except Google Fonts). Read `references/html-template-guide.md` for the full design system, but the key principles are:

**Design philosophy**: The page should look like an editorial blog post or health journal article — NOT a sales page. Readers should feel like they stumbled onto a genuine personal story or journalistic piece. The selling happens through story and mechanism, not through flashy design.

**Required elements**:
- Top bar with category labels (e.g., "WELLNESS - SKINCARE - HONEST REVIEWS")
- Site header with a publication-style name (e.g., "The Scalp Health Journal")
- Navigation links for editorial feel (e.g., PSORIASIS | ECZEMA | REVIEWS | TREATMENTS)
- Article headline (story-driven, curiosity-driven, or revelation-driven)
- Author byline with date and read time
- Before/after image pair near the top (if available)
- Personal story body copy using short paragraphs (2-3 sentences max)
- Pull quotes / callout boxes for key mechanism revelations
- Product image integration (at least 2-3 product shots throughout)
- Stats/proof bar (e.g., "12,847 5-star reviews | 97% would recommend | 60-day guarantee")
- Testimonial cards (2-3 minimum, mechanism-anchored — not generic "it works!")
- Multiple CTAs (minimum 2 — one mid-page, one at bottom) styled as editorial buttons
- Mobile-responsive design
- Sticky CTA button on mobile

**Image handling**: Use the product image URLs the user provides. If they give a website URL, help them find image URLs from the site's CDN (Shopify sites use `cdn/shop/files/` or `cdn/shop/products/` patterns). Never use placeholder images — if no images are available, note this and suggest the user provide them.

**Typography**: Serif body font (Lora, Georgia) for editorial feel. Sans-serif (Inter) for UI elements, nav, stats. This creates the "real article" feeling that makes advertorials convert.

## Copy Quality Standards

Apply these checks to every advertorial before delivering:

- **The Zoom-In Test**: Read every abstract phrase and ask "What do I actually mean?" Replace vague language with specific, visual details.
- **The Competitor Test**: Could a competing product sign their name to this copy? If yes, rewrite until it's uniquely true to this product.
- **The Two-Second Test**: Show any key line to someone for two seconds. If they don't "get it," rewrite.
- **The Paragraph Burrito Test**: Each paragraph should hold together as a unit — if you can remove a sentence and it still works, that sentence shouldn't be there.
- **Kaplan's Law**: "Any words that aren't working for you are working against you." Cut ruthlessly.
- **8th-grade reading level**: Short words over fancy synonyms. Short sentences mixed with occasional longer ones for rhythm. Eliminate adverbs; use strong verbs and concrete nouns.

## Deployment

After building the HTML file, help the user get it live:
- If they have a GitHub account, create a repo and push the file
- Connect to Vercel for instant deployment (GitHub → Vercel auto-deploy)
- Any future edits to the HTML in GitHub will auto-redeploy
- They can add a custom domain through Vercel if needed

## Proven Advertorial Tactics (From Real Examples)

These are specific techniques observed in high-performing advertorial pages. Integrate them where they fit naturally:

### Authority Confession Angle
Instead of a customer telling their story, use a professional (doctor, dermatologist, trainer, nutritionist) who CONFESSES they were doing it wrong. "I'm a board-certified [credential] with [X] years of experience... and I was getting it wrong." This is powerful because the authority figure takes the blame — it shifts blame away from the reader while building massive credibility. The professional's story of discovering the product through a patient creates a natural mechanism reveal.

### Scarcity Close
End with genuine-feeling scarcity: the product is "made in small batches," "sells out often," and "was out of stock for nearly four weeks when I tried to reorder." Then frame the CTA as "check availability" rather than "buy now." This works because it positions clicking the button as checking IF they can still get it, not committing to a purchase. Much lower friction.

### Bundle Offer Framing
When the product has multi-buy offers, present them simply in the close section: "Buy 2, get 1 free / Buy 3, get 2 free." Frame the multi-buy as the "smartest way to order" for daily-use products. Add: "Not only do you save the most, but you'll also have enough on hand if they sell out again." This stacks the scarcity angle with the practical logic of buying more.

### Facebook Comment Screenshots as Social Proof
Screenshots of real Facebook comments (with profile pictures, names, timestamps, like/react counts) feel more authentic than styled testimonial cards to audiences who spend time on Facebook. Use these alongside or instead of polished testimonial cards, especially for older demographics or products targeting Facebook-heavy audiences. The key is they should look like genuine unfiltered reactions, not curated marketing.

### Fake Sidebar / "Similar Articles"
Many advertorials include a sidebar with "similar articles" linking to unrelated content (sports, lifestyle) to mimic real news sites. This is a common pattern, but use it carefully — irrelevant sidebar content (cycling articles on a health page) can actually break the illusion. If using a sidebar, make the "related articles" topically relevant to the niche. Or better: skip the sidebar entirely and use a clean single-column layout that looks like a quality editorial blog (which is what we do by default).

### The Patient/Case Study Vehicle
Instead of first-person ("my scalp was terrible"), the story follows a specific named person: "It started with one patient: a woman named Sarah." The doctor/narrator watches Sarah's transformation from the outside. This creates emotional distance that actually increases credibility — the narrator isn't selling their own experience, they're reporting what they observed. Works especially well for health/supplement products where "doctor recommends" carries weight.

## Catalyst Hook Integration

When relevant (time-sensitive angles, regulatory changes, seasonal hooks), integrate catalyst hooks into the advertorial opening:

**Structure**: "Because of [external catalyst] + [qualifier] + [benefit]"
- Legal/regulatory: "Because of a new FDA guideline..."
- Seasonal: "Because enrollment just opened for 2025..."
- Technological: "Because of a breakthrough in [science]..."

These combat "claim resistance" by providing an external reason WHY the opportunity exists now.
