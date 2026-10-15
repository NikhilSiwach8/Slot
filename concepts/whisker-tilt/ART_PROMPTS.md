# Whisker Tilt — ChatGPT art prompts

27 images: 10 symbols, 6 characters, 5 props, 6 backgrounds. Design: [CONCEPT.md](CONCEPT.md).

## Status

Cut into `art/whisker_tilt/raw/` by
`python art/whisker_tilt/slice_sheet.py art/whisker_tilt/source/{sheet_1,sheet_2,paw}.webp`
(preview: `python art/whisker_tilt/contact_sheet.py` → `art/whisker_tilt/contact_sheet.png`).

| Done (26) | Stand-in (1) |
|---|---|
| H1–H4, L1–L4, S, C, the four keepers (sheet 1); `box_frame`, `gift_closed`, `gift_open`, `crack_overlay`, `logo_plate` (sheet 2); `mitten_paw`; `mitten`; full-size `bg_base`, `bg_base_portrait`, `bg_snowday`, `bg_snowday_portrait`, `bg_super` | `bg_super_portrait`: for now the middle of `bg_super`, scaled to 1024×1536; the real one replaces it when its file arrives |

The backgrounds moved from the toyshop shelf to a snowy village by a frozen lake, with Mitten
sitting on the crates at the left. That reads as the village *inside* the snow box, so the
full-size versions should keep this look.

Fixed in code: sheet 1's checkerboard background is removed; its star was red like the round
bauble, so it's recoloured pine green; its red bauble's right edge was hidden behind the blue
one, so it's rebuilt from its mirror image. Frames are narrowed to the square board. The coin's
centre has a snowflake instead of being empty: the game prints its value on a small plaque over it.

## How to use

1. **Chat A (symbols, characters, props):** start a new ChatGPT chat, paste the **Style setup**
   first, then paste **one prompt per message** (1–21). Keeping it in one chat keeps the style
   consistent.
2. **Chat B (backgrounds):** start a second new chat for 22–27. Don't paste the style setup there:
   those prompts carry their own style.
3. Download each image as **PNG** and name it **exactly** as shown (e.g. `H1.png`).
4. Upload them all to **`art/whisker_tilt/raw/`** on branch **`claude/upbeat-newton-0yvrjr`**
   (on GitHub: switch to that branch → open `art/whisker_tilt/raw/` → *Add file* → *Upload files*
   → commit). Partial uploads are fine. Then tell Claude, who will run the finishing pass
   (trim, outline clean-up, sizing, sprite atlas).

**Fixes to reply with when something's off**

- Off-style: *"Redo it closer to the style setup: thicker uneven ink outlines, flatter gouache
  shading, less glossy, less 3D."*
- Background not transparent: *"Same image, transparent background PNG."*
- Text or numbers appeared: *"Same image with no text, letters or numbers anywhere."*
- Too busy for a small symbol: *"Simplify: bigger shapes, fewer details, it must read at 90 pixels."*

Free ChatGPT has a daily image limit, so this may take a few days. Do the symbols first (1–10):
they're the most important.

---

## Style setup (paste first in Chat A)

```
I'm making original art for my own slot game called "Whisker Tilt": a tiny winter village lives inside a square glass snow box on a toyshop shelf at midnight, and Mitten, the shop's mischievous ginger cat, keeps pawing the box and tipping it over. For every image I ask for in this chat, use this exact style:

Original hand-painted storybook illustration made as a slot-game asset. Chunky, rounded, readable silhouette with confident dark-brown ink outlines that vary in weight like a brush pen (thicker on the shadow side, tapering at the tips). Soft gouache shading in 2-3 tones with visible brush texture, one crisp white highlight, faint paper grain, small hand-made imperfections. Palette: warm toyshop colours (honey amber, cranberry red, pine green, gingerbread brown, gold) against cold snow-globe colours (ice blue, frosty white, soft lilac). Cosy, playful, a little mischievous, like a vintage Christmas toy come to life. Centered, the whole object visible with a little empty space around it, no text, no letters, no numbers, no border, no tile, no ground shadow, transparent background. It must NOT look like a 3D render, glossy AI art or stock vector art. No logos, no brands, no existing characters.

Reply "ready" and wait for my first image.
```

---

## Symbols (Chat A) — square 1024×1024, transparent

Each symbol needs a strong, unique silhouette and its own main colour, because players will read
it at about 90 pixels on a phone.

### 1. Golden Sleigh (top symbol) → `H1.png`

```
Symbol H1 — Golden Sleigh: a small ornate toy sleigh painted gold with cranberry-red velvet seats and curled runners, a few wrapped gifts piled in the back, a dusting of snow on top, little sparkles. Slightly grander than the other symbols. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 2. Gingerbread House → `H2.png`

```
Symbol H2 — Gingerbread House: a chunky little gingerbread house with thick white icing on the roof edges, gumdrop and candy-cane decorations, warm amber light glowing in the round window, snow on the roof. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 3. Nutcracker Guard → `H3.png`

```
Symbol H3 — Nutcracker Guard: a wooden toy nutcracker soldier, bust from the chest up, tall blue hat with a gold band, big white moustache, square jaw, cranberry-red jacket with gold buttons, a proud but slightly worried look (a cat is nearby). Square 1024×1024, transparent background PNG, same style as set up above.
```

### 4. Snowman → `H4.png`

```
Symbol H4 — Snowman: a round, cheerful snowman with a carrot nose, coal-button smile and a pine-green knitted scarf that has visible cat-claw snags and loose threads, one twig arm waving. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 5. Red Bauble (round) → `L1.png`

```
Symbol L1 — A round glass Christmas bauble in deep cranberry red, simple gold cap and loop on top, one swirl of frost pattern, a bright highlight. Simple and bold. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 6. Blue Bauble (teardrop) → `L2.png`

```
Symbol L2 — A teardrop-shaped glass Christmas bauble in ice blue, simple silver cap and loop on top, a few painted white snowflake dots, a bright highlight. Simple and bold, clearly teardrop-shaped. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 7. Green Bauble (star) → `L3.png`

```
Symbol L3 — A five-pointed star-shaped glass Christmas ornament in pine green, simple gold cap and loop on the top point, soft inner glow, a bright highlight. Simple and bold, clearly star-shaped. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 8. Gold Bell → `L4.png`

```
Symbol L4 — A small brass-gold jingle bell ornament with a tiny cranberry ribbon bow on top, clearly bell-shaped, a bright highlight. Simple and bold. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 9. Wind-up Key (scatter) → `S.png`

```
Symbol S — Scatter symbol: a big ornate brass wind-up key, the kind used to wind a music box, with a heart-shaped handle and swirly filigree, glowing with a soft lilac and gold aura, tiny musical sparkles and snowflakes around it. Iconic, with a slightly larger presence than the other symbols. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 10. Snowflake Coin (multiplier) → `C.png`

```
Symbol C — Snowflake Coin: a thick round gold coin with a frosted icy-blue rim and a six-pointed snowflake engraved around the edge, the CENTRE of the coin is completely flat and empty (a number will be printed there later), subtle shine. Front view, perfectly round. Square 1024×1024, transparent background PNG, same style as set up above.
```

---

## Characters (Chat A)

### 11. Mitten the cat → `mitten.png`

```
Character: Mitten, a fluffy ginger tabby cat with white socks, big round amber eyes, a mischievous grin and a raised paw, sitting and peering curiously at something in front of her. Full body, three-quarter view facing left. She will sit beside the game board in the background, so make her big and expressive. Portrait 1024×1536, transparent background PNG, same style as set up above.
```

### 11b. Mitten the cat, retry → `mitten.png`

Use this one: it matches the paw you already made (`mitten_paw.png`), so cat and paw look
like the same animal.

```
Character: a CAT named Mitten (an animal, NOT a glove or mitten). A fluffy smoky-grey house cat with cream-white fur on all four paws and her chest, pink toe beans, a red collar with a small gold jingle bell, pointed cat ears, long whiskers, big round amber eyes, a long fluffy grey tail and a mischievous grin. She sits upright with one front paw raised as if about to bat something. Full body, three-quarter view facing left. Portrait 1024×1536, transparent background PNG, same style as set up above.
```

### 12b. Mitten's paw, retry → `mitten_paw.png`

```
A CAT'S front paw (an animal paw, NOT a glove): a fluffy orange ginger tabby cat's foreleg with white fur on the paw and soft pink toe beans, coming down from the top edge of the image, claws slightly out, about to bat something below it. Only the paw and lower leg. Portrait 1024×1536, transparent background PNG, same style as set up above.
```

### 12. Mitten's paw → `mitten_paw.png`

```
Mitten's paw: a single big fluffy ginger cat paw with white sock fur and soft pink toe beans, reaching in from the top of the image toward the bottom, claws just slightly out, as if about to bat something. Only the paw and part of the foreleg, cut off at the top edge. Portrait 1024×1536, transparent background PNG, same style as set up above.
```

The four Edge Keepers stand on the four walls of the box, each holding a lantern. **The glass
pane of each lantern must be empty and flat:** their multiplier is printed there.

### 13. Skater (South wall keeper) → `keeper_south.png`

```
Character: a tiny toy-village ice skater, a round-cheeked kid in a cranberry-red coat, knitted hat with a pompom and ice skates, holding up a brass lantern with both hands. The lantern's glass pane is flat, empty and softly glowing warm amber (a number will be printed there later). Full body, front view, cheerful. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 14. Fisher (West wall keeper) → `keeper_west.png`

```
Character: a tiny toy-village ice fisher, a chubby old fellow with a bushy white beard, yellow raincoat and a fishing rod over one shoulder, holding up a brass lantern. The lantern's glass pane is flat, empty and softly glowing warm amber (a number will be printed there later). Full body, front view, friendly. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 15. Lamplighter (North wall keeper) → `keeper_north.png`

```
Character: a tiny toy-village lamplighter, a tall thin figure in a long pine-green coat and top hat, carrying a long lighting pole over one shoulder, holding up a brass lantern. The lantern's glass pane is flat, empty and softly glowing warm amber (a number will be printed there later). Full body, front view, dignified. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 16. Baker (East wall keeper) → `keeper_east.png`

```
Character: a tiny toy-village baker, a round jolly baker in a white apron and puffy chef's hat dusted with flour, a gingerbread biscuit tucked in the apron pocket, holding up a brass lantern. The lantern's glass pane is flat, empty and softly glowing warm amber (a number will be printed there later). Full body, front view, jolly. Square 1024×1024, transparent background PNG, same style as set up above.
```

---

## Props (Chat A)

### 17. Snow box frame → `box_frame.png`

```
Game board frame: a square glass snow box seen straight from the front, with a carved dark-wood frame, brass corner caps and a small brass wind-up keyhole on the wooden base at the bottom. The inside of the frame is completely EMPTY and transparent (the game board goes there), with only a faint frosty glass reflection streak in one corner and a little snow piled along the inside bottom edge. Frame border about 8% of the width. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 18. Mitten's Gift, closed → `gift_closed.png`

```
A wrapped present: a square gift box in cranberry-red paper with a pattern of tiny gold paw prints, a big lilac satin bow on top, slightly squashed and tilted as if a cat just knocked it off a shelf, a couple of snowflakes around it. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 19. Mitten's Gift, open → `gift_open.png`

```
The same wrapped present from the previous image, now with its lid popped off and floating above it, the bow undone, golden light and swirling snowflakes bursting out of the open box. Empty bright space above the box (text will go there later). Square 1024×1024, transparent background PNG, same style as set up above.
```

### 20. Cracked glass overlay (Off the Shelf) → `crack_overlay.png`

```
Overlay: thin white and pale-blue crack lines spreading across a pane of glass from the bottom-left corner, like a snow globe that has been knocked hard, with a few small chips and sparkles along the cracks. ONLY the cracks, nothing else: no glass colour, no background, no frame. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 21. Logo plate → `logo_plate.png`

```
Game title plate: a carved wooden toyshop sign with brass corners, hanging from two little red ribbons, a ginger cat tail curling around one side and a dusting of snow on top, the CENTRE of the sign is flat and completely empty (the title text will be added later). Wide, about 3:1. Landscape 1536×1024, transparent background PNG, same style as set up above.
```

---

## Backgrounds (start **Chat B**; don't paste the style setup)

Each background gets a landscape version (desktop) and a portrait version (phones). The game board
sits in the middle, so the centre must stay calm and slightly darker.

### 22. Base game, landscape → `bg_base.png`

```
Wide game background, original illustration: the inside of an old wooden toyshop at midnight, seen from the top shelf. Shelves of vintage toys (wooden trains, dolls, tin soldiers) fading into soft shadow, warm honey-amber lamplight on the left, cold blue moonlight and falling snow through a frosted window on the right. The centre is an empty, slightly darker area of shelf where a game board will sit. Hand-painted storybook gouache style with soft ink outlines and visible brush texture. No people, no cats, no text. Landscape 1536×1024, full-bleed, no transparency.
```

### 23. Base game, portrait → `bg_base_portrait.png`

```
The same midnight toyshop as the previous image, recomposed as a tall portrait view: shelves of vintage toys above and below, warm lamplight at the top, cold blue moonlight and snow from a window lower down, and an empty, slightly darker area of shelf in the middle where a game board will sit. Same hand-painted storybook gouache style. No people, no cats, no text. Portrait 1024×1536, full-bleed, no transparency.
```

### 24. Snow Day (free spins), landscape → `bg_snowday.png`

```
The same midnight toyshop, now during a magical indoor snowfall: thick fluffy snow drifting down everywhere, the toys on the shelves dusted white, warm fairy lights strung across the shelves, a cosy and joyful mood, ice-blue and lilac tones with warm gold lights. The centre stays empty and calm where a game board will sit. Hand-painted storybook gouache style with soft ink outlines and brush texture. No people, no cats, no text. Landscape 1536×1024, full-bleed, no transparency.
```

### 25. Snow Day, portrait → `bg_snowday_portrait.png`

```
The same magical indoor snowfall in the toyshop as the previous image, recomposed as a tall portrait view, with an empty calm area in the middle where a game board will sit. Same style. No people, no cats, no text. Portrait 1024×1536, full-bleed, no transparency.
```

### 26. Super Snow Day, landscape → `bg_super.png`

```
The same toyshop at the darkest hour of the night: the lamps are out, the scene is lit only by a rich golden glow pouring up from the centre of the shelf (where a game board will sit), deep indigo shadows, sparkling gold snow swirling in the air, and a pair of huge glowing amber cat eyes watching from the darkness in the upper background. Dramatic, magical, a little mysterious. Hand-painted storybook gouache style with brush texture. No text. Landscape 1536×1024, full-bleed, no transparency.
```

### 27. Super Snow Day, portrait → `bg_super_portrait.png`

```
The same golden, dark Super toyshop scene as the previous image, recomposed as a tall portrait view, with the glowing amber cat eyes near the top and the golden glow in the middle where a game board will sit. Same style. No text. Portrait 1024×1536, full-bleed, no transparency.
```

---

## Checklist

| # | File | # | File | # | File |
|---|---|---|---|---|---|
| 1 | `H1.png` | 10 | `C.png` | 19 | `gift_open.png` |
| 2 | `H2.png` | 11 | `mitten.png` | 20 | `crack_overlay.png` |
| 3 | `H3.png` | 12 | `mitten_paw.png` | 21 | `logo_plate.png` |
| 4 | `H4.png` | 13 | `keeper_south.png` | 22 | `bg_base.png` |
| 5 | `L1.png` | 14 | `keeper_west.png` | 23 | `bg_base_portrait.png` |
| 6 | `L2.png` | 15 | `keeper_north.png` | 24 | `bg_snowday.png` |
| 7 | `L3.png` | 16 | `keeper_east.png` | 25 | `bg_snowday_portrait.png` |
| 8 | `L4.png` | 17 | `box_frame.png` | 26 | `bg_super.png` |
| 9 | `S.png` | 18 | `gift_closed.png` | 27 | `bg_super_portrait.png` |

Not needed from ChatGPT: snow, sparkles, the Snowstorm whiteout, coin trails and the numbers in
coins and lanterns are made in code. Buttons and the bottom bar will be restyled from Dumpster
Duke's set; the Stake tile and cover art come later, once the logo is done.
