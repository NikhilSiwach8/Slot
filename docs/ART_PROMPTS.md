# Dumpster Duke — ChatGPT art prompts

How to use (free ChatGPT):

1. Use **one chat** for all the symbols, so ChatGPT keeps the style consistent. Paste the **Style setup** message first.
2. Then paste one symbol prompt per message. If one comes out off-style, reply: *"Redo it closer to the style setup: thicker uneven ink outlines, flatter cel shading, less glossy."*
3. Download each image as PNG and save it with the exact file name shown (e.g. `H1.png`).
4. Upload the files to the repo folder `art/raw/` (on GitHub: open the folder on branch `claude/inspiring-ritchie-6rsodv` → Add file → Upload files). Then tell Claude, who will run the finishing pass.

Tips: if the background isn't transparent, ask *"same image, transparent background PNG"*. Backgrounds should be wide (landscape).

---

## Style setup (paste first)

```
I'm making original art for my own slot game called "Dumpster Duke" (a raccoon king who rules a junkyard at night). For every image I ask for in this chat, use this exact style:

Original hand-drawn cartoon slot-game symbol. Chunky, bold silhouette with thick dark-brown ink outlines whose weight varies like a real brush pen (thicker on shadow side, tapering at tips). Flat cel shading in 2-3 tones painted with a slightly textured gouache brush, one hard white highlight, subtle hand-made imperfections: tiny wobble in lines, uneven colour fill near edges, faint paper grain. Saturated night-time palette: teal, purple, neon pink, acid green and warm gold. Expressive, mischievous, comedic. Centered, full object visible, no text, no border, no tile, transparent background. Must NOT look like 3D render, glossy AI art or stock vector; should look like an illustrator's finished game asset. No logos or existing characters.

Reply "ready" and wait for my first symbol.
```

### 1. The Dumpster Duke → save as `H1.png`

```
Symbol H1 — The Dumpster Duke: a pompous fat raccoon king with a crown made of bent bottle caps, a tin-foil cape, a gold chain, one eyebrow raised, toothy smug grin, holding a half-eaten donut like a sceptre. Bust portrait. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 2. Possum Bruiser → save as `H2.png`

```
Symbol H2 — Possum Bruiser: a tough grey possum bodyguard with a dented traffic-cone helmet, a sticking-plaster on the nose, cracking knuckles, sly squint. Bust portrait. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 3. Bling Pigeon → save as `H3.png`

```
Symbol H3 — Bling Pigeon: a strutting city pigeon wearing oversized gold sunglasses and a chunky gold chain, chest puffed out, iridescent purple-green neck feathers. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 4. Golden Pizza Slice → save as `H4.png`

```
Symbol H4 — Golden Pizza Slice: a single gooey pizza slice that glows gold like treasure, cheese stretching, pepperoni coins, little sparkles. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 5. Soda Can → save as `L1.png`

```
Symbol L1 — A dented neon-pink soda can with a bent ring pull, fizz droplets popping out. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 6. Fish Bone → save as `L2.png`

```
Symbol L2 — A cartoon fish skeleton (fish bone) in pale aqua with a cheeky stitched-x eye. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 7. Banana Peel → save as `L3.png`

```
Symbol L3 — A bright yellow banana peel splayed open, slightly bruised, with comic shine. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 8. Apple Core → save as `L4.png`

```
Symbol L4 — A chewed acid-green apple core with two seeds and a single leaf. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 9. Golden Trash Can (scatter) → save as `S.png`

```
Symbol S — Scatter symbol: a battered golden trash can with its lid popping open, gold coins and light beams bursting out, glowing aura. Iconic and slightly larger presence than other symbols. Square 1024×1024, transparent background PNG, same style as set up above.
```

### 10. Bottle Cap (multiplier) → save as `M.png`

```
Symbol M — Multiplier symbol: a big shiny bottle cap in red and gold with crimped edges, empty flat centre where a number will be printed later, sparkling rim. Square 1024×1024, transparent background PNG, same style as set up above.
```

---

## Backgrounds (start a **new chat** for these; do NOT paste the style setup — these prompts carry their own style)

### 11. Base game background → save as `bg_base.png`

```
Wide 16:9 game background, original illustration: a back-alley junkyard kingdom at night, stacked garbage bags and broken furniture forming a throne-like hill, neon signs (no readable text) in pink and green, puddles reflecting lights, string lights, a fat moon. Painterly hand-drawn cartoon style with thick ink outlines and visible brush texture; slightly darker in the centre where the reels sit. No characters, no text. Landscape 1536×1024, full-bleed, no transparency.
```

### 12. Free spins background → save as `bg_raid.png`

```
Same junkyard alley at midnight during a raid: purple and pink searchlights, flying trash, glowing gold spilling from bins, dramatic and energetic. Painterly hand-drawn cartoon style with thick ink outlines and brush texture. No characters, no text. Landscape 1536×1024, full-bleed, no transparency.
```

### 13. Logo plate → save as `logo_plate.png`

```
Ornate game-title plate made of a rusty sheet-metal sign with bottle-cap rivets, neon tube trim and a tiny bottle-cap crown on top, empty centre for title text. Hand-drawn cartoon style, transparent background. Square-ish, transparent background PNG.
```
