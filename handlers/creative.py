"""
Creative handlers — write ads, landers, VSLs using proven frameworks.

Slash commands:
    /ad       — Write a UGC-style ad script (A.D.A.P.T. framework)
    /lander   — Write a landing page
    /vsl      — Write a VSL script
    /hooks    — Generate 10 hooks for a product/angle
    /kb-status — Show what's loaded in the knowledge base
"""

import logging
import os

from slack_bolt import App

import knowledge_base
from claude_client import creative_request

logger = logging.getLogger(__name__)

def _load_framework_file(filename: str) -> str:
    """Load a framework file from the knowledge/frameworks/ directory."""
    path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "frameworks", filename)
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return ""


def _load_copy_quality_rules() -> str:
    """Load the copy quality rules that get injected into ALL creative prompts."""
    rules = _load_framework_file("copy-quality-rules.md")
    if rules:
        return f"\n\n## COPY QUALITY RULES (MANDATORY — self-audit before delivering):\n{rules}"
    return ""


COPY_QUALITY_RULES = _load_copy_quality_rules()

# ─── System prompts per creative type ────────────────────

def _build_ad_system():
    """Build the AD system prompt. Uses the skill file + adapt framework.
    Total ~27k chars / ~7k tokens — focused and precise."""
    skill = _load_framework_file("yapper-ads-skill.md")
    adapt = _load_framework_file("adapt-framework.md")

    parts = [
        "You are an elite direct-response copywriter for Roly Poly Digital, "
        "specializing in UGC-style video ad scripts ('yapper ads').\n\n"
        "You MUST follow these frameworks precisely. Every script must be 1:30-3:00 minutes "
        "of spoken word. Sound like a REAL PERSON — not a copywriter.\n\n"
    ]
    if skill:
        parts.append(skill)
    if adapt:
        parts.append("\n\n## DETAILED A.D.A.P.T. SECTION REFERENCE:\n" + adapt)

    return "".join(parts) + COPY_QUALITY_RULES

AD_SYSTEM = _build_ad_system()

LANDER_SYSTEM = """You are an elite direct-response copywriter specializing in high-converting landing pages.

## LANDING PAGE STRUCTURE:
1. **Hero Section**: Headline (big promise), subheadline (mechanism or proof), CTA button, hero image/video
2. **Problem Agitation**: Name their pain. Layer it: surface → emotional → deep. Make them feel understood.
3. **Root Cause**: Reframe WHY the problem exists. "It's not your fault — here's what's really going on..."
4. **Solution Introduction**: Introduce the product as the breakthrough. Explain the mechanism simply.
5. **Social Proof Block**: Testimonials, star ratings, before/afters, press logos, number of customers
6. **How It Works**: 3-step simplification. Make it feel effortless.
7. **Benefits Stack**: 5-7 benefits, each with a headline + short description. Feature → benefit → emotional outcome.
8. **More Social Proof**: Longer testimonials, video reviews, expert endorsements
9. **Offer Section**: Price anchoring, value stack, per-day cost breakdown, bonuses
10. **Guarantee**: Risk reversal. Frame as confidence, not desperation.
11. **FAQ**: Handle top 5-7 objections disguised as questions.
12. **Final CTA**: Urgency + scarcity + restate the transformation promise.

## WRITING RULES:
- Write in second person ("you") throughout.
- Headlines should be benefit-driven, not feature-driven.
- Every section should answer: "why should I keep reading?"
- Use specificity: numbers, timeframes, real details.
- Match the reader's awareness level (problem-aware needs more education, product-aware needs more proof).
- Mobile-first: short paragraphs, scannable, lots of whitespace.

## OUTPUT FORMAT:
Output the full landing page copy, section by section, with:
- [SECTION NAME] headers
- Suggested headline + body copy for each section
- [CTA BUTTON: text] callouts
- [IMAGE/VIDEO: description] notes for the designer
- [TESTIMONIAL PLACEHOLDER] markers
""" + COPY_QUALITY_RULES

VSL_SYSTEM = """You are an elite direct-response copywriter specializing in Video Sales Letters (VSLs).

## THE VSL ARC:
HOOK (0-15s) → PRESENTER INTRO (15-30s) → THE PROBLEM (30s-1:30)
→ ROOT CAUSE REVELATION (1:30-3:00) → WHY OLD SOLUTIONS FAIL (3:00-4:00)
→ THE DISCOVERY/BREAKTHROUGH (4:00-5:00) → HOW IT WORKS (5:00-6:30)
→ PROOF STACK (6:30-8:00) → THE OFFER (8:00-9:30)
→ GUARANTEE (9:30-10:00) → URGENCY + CTA (10:00-10:30)

## VSL GOLDEN RULES:
1. Root cause is king — reframe WHY the problem exists.
2. The presenter IS the product — build their character first.
3. Education = persuasion — teach them something, they'll trust you.
4. Attack old solutions before introducing yours.
5. Mechanism must be simple enough for a 10-year-old.
6. Stack proof: studies + experts + testimonials + numbers.
7. The offer is a SECTION, not a sentence — price anchor, value stack, bonuses, guarantee.
8. Urgency must feel real and specific.
9. Pattern interrupts every 30-45 seconds.
10. CTA is a command: "Tap the button below this video NOW."

## VSL TYPES:
- Inventor/Founder Story (default)
- Scientific Discovery (health/supplement)
- Personal Struggle to Solution (everyman arc)
- Exposé/Conspiracy ("what THEY don't want you to know")
- Quiz Funnel VSL (personalized results → recommendation)

## OUTPUT FORMAT:
PRODUCT: [Name]
TARGET AVATAR: [Desire-first description]
VSL TYPE: [Template]
PRESENTER: [Who + credentials]
ROOT CAUSE ANGLE: [The hidden "why"]
BIG DOMINO: [One belief that makes objections irrelevant]
ESTIMATED LENGTH: [Minutes]

[Full script with section labels and timestamps]
[VISUAL/B-ROLL NOTES in brackets]
[ON-SCREEN TEXT callouts where relevant]
""" + COPY_QUALITY_RULES

HOOKS_SYSTEM = """You are an elite direct-response copywriter. Generate 10 scroll-stopping hooks.

## HOOK FORMULAS:
1. Reversal: "[Trusted thing] might actually be [causing problem]"
2. Age + Transformation: "[Age], been using [product] for [time], honest thoughts"
3. Authority + Pattern: "As a [profession], [frustrating pattern] was driving me crazy"
4. Shock Value: "Someone [dramatic reaction] because [outrageous claim]"
5. Before/After Visual: "Watch what happens to [demographic] using [product] for [timeframe]"
6. Catalyst Hook: "Because of [EXTERNAL EVENT], [DEMOGRAPHIC] can now [BENEFIT]"
7. Fight-Me Statement: "[Bold polarizing assertion]"
8. Target Callout: "[Specific demographic], stop scrolling"
9. Credibility Flash: "I'm a [profession] and I've never seen anything like this"
10. Story Tease: "You guys got to hang with me on this one"

For each hook, output:
- The hook text (exactly as it would be spoken/shown)
- Which formula it uses
- Why it works for this specific product/audience

Generate hooks across DIFFERENT formulas — don't repeat the same type.
""" + COPY_QUALITY_RULES


def register(app: App):
    """Register all creative slash commands."""

    @app.command("/ad")
    def handle_ad(ack, command, respond):
        """Write a UGC-style ad script using the A.D.A.P.T. framework."""
        ack()
        brief = command.get("text", "").strip()
        if not brief:
            respond(
                "Usage: `/ad <brief>`\n\n"
                "Example: `/ad UGC script for our collagen powder, targeting women 35-55 "
                "who are frustrated with aging skin, for Facebook`"
            )
            return

        respond("Writing your ad script... this takes 30-60 seconds.")
        context = knowledge_base.load_for_creative()
        result = creative_request(AD_SYSTEM, context, brief)
        respond(text=result)

    @app.command("/lander")
    def handle_lander(ack, command, respond):
        """Write landing page copy."""
        ack()
        brief = command.get("text", "").strip()
        if not brief:
            respond(
                "Usage: `/lander <brief>`\n\n"
                "Example: `/lander landing page for our teeth whitening kit, "
                "targeting young professionals, focus on speed and convenience`"
            )
            return

        respond("Writing your landing page copy... this takes 60-90 seconds.")
        context = knowledge_base.load_for_creative()
        result = creative_request(LANDER_SYSTEM, context, brief)
        respond(text=result)

    @app.command("/vsl")
    def handle_vsl(ack, command, respond):
        """Write a VSL script."""
        ack()
        brief = command.get("text", "").strip()
        if not brief:
            respond(
                "Usage: `/vsl <brief>`\n\n"
                "Example: `/vsl 5-minute VSL for our joint supplement, "
                "founder story angle, targeting men 50+ with knee pain`"
            )
            return

        respond("Writing your VSL script... this takes 60-120 seconds.")
        context = knowledge_base.load_for_creative()
        result = creative_request(VSL_SYSTEM, context, brief)
        respond(text=result)

    @app.command("/hooks")
    def handle_hooks(ack, command, respond):
        """Generate 10 hooks for a product/angle."""
        ack()
        brief = command.get("text", "").strip()
        if not brief:
            respond(
                "Usage: `/hooks <product and angle>`\n\n"
                "Example: `/hooks collagen powder for women 40+, "
                "angle: their current skincare is actually making things worse`"
            )
            return

        respond("Generating hooks...")
        context = knowledge_base.load_for_creative()
        result = creative_request(HOOKS_SYSTEM, context, brief)
        respond(text=result)

    @app.command("/kb-status")
    def handle_kb_status(ack, respond):
        """Show what's loaded in the knowledge base."""
        ack()
        files = knowledge_base.list_files()
        lines = [f"*Knowledge Base Status*\n"]

        for section, filenames in files.items():
            icon = ":white_check_mark:" if filenames else ":x:"
            title = knowledge_base.SECTIONS[section]
            lines.append(f"{icon} *{title}* (`knowledge/{section}/`)")
            if filenames:
                for f in filenames:
                    lines.append(f"    • `{f}`")
            else:
                lines.append(f"    _No files yet — add .txt or .md files here_")
            lines.append("")

        lines.append(
            "_Tip: Add files to the `knowledge/` folder and restart the bot. "
            "All creative commands automatically pull from these docs._"
        )
        respond(text="\n".join(lines))
