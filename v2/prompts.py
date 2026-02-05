"""
Centralized prompt templates for Claude API calls.

All prompts used for outfit and clothing analysis.
"""


OUTFIT_DESCRIPTION_PROMPT = """
Analyze this image and provide a detailed description of the clothing and gear worn by people in the photo.

Focus on VISUAL DETAILS (in order of importance):

1. BIB NUMBER (ABSOLUTE CRITICAL - UNIQUE IDENTIFIER):
   - Racing bib number (large number on chest/back)
   - Read the exact number carefully
   - This is THE MOST IMPORTANT identifier
   - If visible, note it clearly

2. EQUIPMENT BRANDING (CRITICAL - PRIMARY IDENTIFIER):
   - Helmet brand: SMITH, Giro, POC, Uvex, Salomon, etc.
   - Ski brand: HEAD, Rossignol, Atomic, Fischer, Völkl, K2, etc.
   - Boot brand: Lange, Salomon, Atomic, Rossignol, Tecnica, Nordica, Fischer, Head, Dalbello, etc.
   - Boot colors (often distinctive: white, black, red, blue, yellow)
   - Goggle brand visible
   - Suit/clothing brand logos
   - Pole brands if visible

2. HELMET/HEADGEAR (HIGHEST PRIORITY):
   - Helmet colors (be specific: metallic blue, matte black, fluorescent yellow, etc.)
   - Helmet patterns: stripes, graphics, logos, racing designs, solid color, multi-color blocks
   - Helmet design elements: color combinations, accent colors, decals, numbers
   - Visor color (clear, tinted, mirrored, colored)

3. CLOTHING PATTERNS:
   - Specific pattern types: stripes, graphics, logos, geometric, racing designs, solid
   - Pattern scale and placement
   - Pattern colors and contrast
   - Jersey/suit numbers or text

4. CLOTHING COLORS:
   - Primary colors (be specific: navy blue, burgundy, forest green, crimson, fluorescent orange, etc.)
   - Secondary colors and accent colors
   - Color blocking and combinations
   - Overall color scheme

5. SKI BOOTS (HIGHLY VISIBLE):
   - Boot brand and model if visible
   - Boot colors (primary and accent colors)
   - Boot design (racing style, buckle configuration)
   - Distinctive features or graphics

6. OTHER GEAR & CLOTHING ITEMS:
   - Type: racing suit, jersey, jacket, gloves, protective gear
   - Material appearance: leather, textile, mesh, reflective
   - Style: racing, casual, protective

If multiple people are present, describe the most prominent person's gear.

Provide a detailed paragraph emphasizing:
1. BIB NUMBER (if visible - read it carefully, this is critical!)
2. Helmet colors, patterns, and design (BE VERY SPECIFIC - most visible identifier)
3. SKI BOOT brand, colors, and design (VERY VISIBLE - often distinctive)
4. Clothing patterns and graphics (stripes, designs, etc.)
5. Primary and accent colors on all gear
6. EQUIPMENT BRANDS - helmet, skis, boots (read visible brand names as supporting info)
"""


DETECT_OUTFITS_PROMPT = """
Identify all people visible in this image and describe their gear and clothing.

For each person you detect, provide:
1. Position/location in the image (e.g., "center", "left side", "background right", etc.)
2. Detailed GEAR description emphasizing:

   BIB NUMBER (ABSOLUTE HIGHEST PRIORITY - UNIQUE IDENTIFIER):
   - Racing bib number (large number on chest or back)
   - READ THE EXACT NUMBER CAREFULLY
   - This is THE MOST CRITICAL piece of information
   - If not visible, note "no bib visible" or "bib number not readable"

   EQUIPMENT BRANDS (CRITICAL - READ ALL VISIBLE BRAND NAMES):
   - Helmet brand: SMITH, Giro, POC, Uvex, Salomon, etc.
   - Ski brand: HEAD, Rossignol, Atomic, Fischer, Völkl, K2, Dynastar, Blizzard, etc.
   - Boot brand: Lange, Salomon, Atomic, Rossignol, Tecnica, Nordica, Fischer, Head, Dalbello, Full Tilt, etc.
   - Goggle/visor brand
   - Clothing/suit brand logos
   - Pole brands
   - Any sponsor logos or team names

   HELMET/HEADGEAR (HIGHEST PRIORITY):
   - Helmet base color(s): be specific (metallic blue, matte black, fluorescent yellow, white, red, etc.)
   - Helmet patterns/graphics: stripes, racing designs, logos, sponsor graphics, color blocks, solid
   - Helmet accent colors and design elements
   - Visor characteristics: clear, tinted, mirrored, colored
   - Numbers, text, or distinctive markings on helmet

   CLOTHING PATTERNS:
   - Pattern types: stripes, graphics, logos, geometric, racing designs, numbers, solid
   - Pattern placement and scale
   - Pattern colors

   CLOTHING COLORS:
   - Primary colors on suit/jersey (be specific)
   - Secondary and accent colors
   - Color blocking patterns

   SKI BOOTS (HIGHLY VISIBLE AND DISTINCTIVE):
   - Boot brand and model if readable
   - Boot colors: primary color and accents (white, black, red, blue, yellow, etc.)
   - Boot style: racing boots are very distinctive
   - Buckle configuration and graphics
   - Boot condition and design features

   GEAR TYPE:
   - Racing suit, jersey, jacket, gloves, protective gear
   - Material type: leather, textile, mesh

Focus on BIB NUMBER FIRST (critical!), then helmet colors/patterns, then BOOT brand/colors (very visible!), then equipment brands, then clothing. DO NOT describe faces or facial features.

Format your response as a JSON array with this structure:
[
  {{
    "position": "description of location in image",
    "outfit_description": "detailed description with bib number, helmet, boots, brands, patterns, and colors...",
    "bib_number": "123" or null if not visible,
    "equipment_brands": ["BRAND1", "BRAND2", "..."],
    "boot_brand": "BRAND" or null if not visible,
    "boot_colors": ["color1", "color2", "..."],
    "helmet_colors": ["color1", "color2", "..."],
    "helmet_patterns": ["pattern description"],
    "patterns": ["clothing pattern1", "pattern2", "..."],
    "primary_colors": ["color1", "color2", "..."],
    "clothing_items": ["item1", "item2", "..."]
  }},
  ...
]

If no people are detected, return:
{{"outfits": []}}

Important: Return ONLY the JSON, no additional text or markdown formatting.
"""


COMPARE_OUTFITS_PROMPT = """
Compare these two gear descriptions and determine how similar they are.

Description 1:
{description1}

Description 2:
{description2}

ANALYSIS PRIORITIES (in order of importance):

0. BIB NUMBER MATCH (ABSOLUTE 100% CERTAINTY):
   - IF both descriptions have bib numbers AND they match → IMMEDIATE 1.0 score (100% same person)
   - IF bib numbers are different → IMMEDIATE 0.0 score (100% different people)
   - Bib numbers are UNIQUE identifiers - they override EVERYTHING else
   - Check for bib numbers FIRST before analyzing anything else

1. HELMET COLOR & PATTERN SIMILARITY (HIGHEST PRIORITY if no bib match - 30%):
   - Are the helmet colors the same or very similar?
   - Do the helmets have the same or similar patterns/graphics?
   - Are helmet design elements similar (stripes, logos, color blocks)?
   - Helmet appearance is THE MOST VISIBLE identifier
   - Different helmet colors/patterns = significant score reduction

2. SKI BOOT SIMILARITY (VERY HIGH PRIORITY - 25%):
   - Are the boot colors the same or very similar?
   - Same boot brand is a strong indicator
   - Boot color combinations (e.g., white with red accents)
   - Boots are HIGHLY VISIBLE and often distinctive
   - Different boot colors = significant score reduction

3. CLOTHING PATTERN SIMILARITY (HIGH PRIORITY - 25%):
   - Are the patterns on clothing the same or similar? (stripes, graphics, racing designs, solid)
   - Pattern type match on suits/jerseys
   - Graphics and logo placement
   - Horizontal stripes vs vertical stripes vs solid
   - If both solid with no pattern, that's a match for this category

4. CLOTHING COLOR SIMILARITY (MEDIUM PRIORITY - 15%):
   - Are the PRIMARY colors on suits/clothing similar?
   - Color combinations and blocking patterns
   - Accent colors
   - Overall color scheme

5. EQUIPMENT BRAND SIMILARITY (SUPPORTING EVIDENCE - 5%):
   - Do they use the SAME helmet brand? (SMITH = SMITH)
   - Do they use the SAME ski brand? (HEAD = HEAD)
   - Same brands = bonus points
   - Different brands = minor reduction
   - Brands are supporting evidence, not primary identifier

SCORING GUIDELINES (be generous with matching):
- 0.9-1.0: Nearly identical (same helmet colors/patterns, same suit colors/patterns)
- 0.7-0.9: Very similar (matching helmet colors with similar patterns OR same base helmet color)
- 0.5-0.7: Moderately similar (similar helmet colors even if patterns differ, OR similar overall color scheme)
- 0.3-0.5: Somewhat similar (some color overlap in helmet or suit)
- 0.0-0.3: Very different (completely different color schemes throughout)

MATCHING RULES (CRITICAL - CHECK BIB NUMBERS FIRST):
- SAME bib number = AUTOMATIC 1.0 (100% match - SAME PERSON, no further analysis needed)
- DIFFERENT bib numbers = AUTOMATIC 0.0 (different people, no further analysis needed)
- If NO bib numbers visible in either description, proceed with visual matching:
  - Same helmet colors + same boot colors + same suit patterns = score at least 0.9 (EXTREMELY STRONG visual match)
  - Same helmet colors + same boot colors = score at least 0.8 (VERY STRONG visual match)
  - Same helmet colors + similar boot colors + similar patterns = score at least 0.75
  - Same helmet colors OR same boot colors + similar suit patterns = score at least 0.7
  - Similar helmet colors + similar boot colors = score at least 0.65
  - Same helmet colors but different boot colors = score at least 0.6
  - Similar helmet colors + similar suit colors = score at least 0.55
  - Same color family + similar patterns = score at least 0.5
  - Same brands but different colors/patterns = score at least 0.4 (brands are bonus)
- Be LENIENT - err on the side of higher scores to enable clustering
- WEIGHT VISUAL APPEARANCE MORE THAN BRANDS
- Example: Bib #23 vs Bib #23 = 1.0 (guaranteed same person)
- Example: Bib #23 vs Bib #45 = 0.0 (guaranteed different people)
- Example: White helmet + white boots + blue striped suit vs White helmet + white boots + blue striped suit = 0.95 (near perfect visual match)
- Example: White helmet + white boots vs White helmet + white boots = 0.85 (very strong match)
- Example: White helmet + white boots vs White helmet + red boots = 0.7 (helmet matches, boots differ)
- Example: White helmet + blue suit vs White helmet + red suit = 0.65 (same helmet, different suit)
- Example: Blue helmet + blue boots vs Navy helmet + navy boots = 0.65 (similar shades)
- Example: SMITH helmet + different colors/boots = 0.4 (brand match but visual differs)

Provide a similarity score between 0.0 (completely different) and 1.0 (nearly identical).

Return your analysis as JSON with this exact structure:
{{
  "similarity": 0.0,
  "reasoning": "brief explanation - if bib numbers checked mention that FIRST, then helmet colors/patterns, then boot colors/brand, then suit patterns/colors, then other brands as supporting evidence"
}}

CRITICAL: If BOTH descriptions contain bib numbers:
- Same bib number → return {{"similarity": 1.0, "reasoning": "Same bib number #XX - definite match"}}
- Different bib numbers → return {{"similarity": 0.0, "reasoning": "Different bib numbers (#XX vs #YY) - different people"}}

Important: Return ONLY the JSON, no additional text or markdown formatting.
"""
