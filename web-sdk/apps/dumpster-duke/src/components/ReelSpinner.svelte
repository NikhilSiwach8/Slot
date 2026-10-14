<!--
	Draws the spinning reels. Imperative Pixi for speed: a fixed pool of sprites per
	reel is created once and only repositioned/re-textured each frame (no objects are
	created or destroyed while spinning). Each reel has a hard rectangular mask and a
	vertical-only blur that scales with its speed. Motion comes from game/reelSpin.
-->
<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { getContextApp, getContextParent } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, SYMBOL_INFO_MAP, BOARD_DIMENSIONS } from '../game/constants';
	import { getSymbolX } from '../game/utils';
	import { reels, reelSpin, stateReelSpin } from '../game/reelSpin/controller.svelte';
	import type { TapeSymbol } from '../game/reelSpin/reelMotion';

	const context = getContext();
	const app = getContextApp();
	const parent = getContextParent();

	const SLOTS = 8; // window rows (5) + partial rows above/below + spare
	const ROWS = BOARD_DIMENSIONS.y;
	const LAND_SQUASH_MS = 160;
	const FLASH_MS = 220;

	type Slot = { root: PIXI.Container; sprite: PIXI.Sprite; value: PIXI.BitmapText; size: number };
	type ReelView = {
		outer: PIXI.Container;
		inner: PIXI.Container;
		blur: PIXI.BlurFilter;
		slots: Slot[];
		flash: PIXI.Graphics;
		landedAt: number;
	};

	const root = new PIXI.Container();
	root.visible = false;
	parent.addToParent(root); // also destroys it (and the pooled sprites) on unmount

	const texture = (key: string) =>
		(app.stateApp.loadedAssets?.[key] as PIXI.Texture | undefined) ?? PIXI.Texture.EMPTY;

	const symbolLook = (symbol: TapeSymbol) => {
		const key = symbol.multiplier !== undefined ? `M_${symbol.multiplier}` : symbol.name;
		const info = (SYMBOL_INFO_MAP[key] ?? SYMBOL_INFO_MAP.L4).static;
		return { texture: texture(info.assetKey), size: SYMBOL_SIZE * info.sizeRatios.width };
	};

	const views: ReelView[] = reels.map((_, reelIndex) => {
		const outer = new PIXI.Container();
		const x = getSymbolX(reelIndex);
		const mask = new PIXI.Graphics().rect(x - SYMBOL_SIZE / 2, 0, SYMBOL_SIZE, SYMBOL_SIZE * ROWS).fill(0xffffff);
		outer.addChild(mask);
		outer.mask = mask;

		const inner = new PIXI.Container();
		const blur = new PIXI.BlurFilter({ strengthX: 0, strengthY: 0, quality: 3 });
		inner.filters = [blur];
		outer.addChild(inner);

		const slots: Slot[] = Array.from({ length: SLOTS }, () => {
			const slotRoot = new PIXI.Container();
			slotRoot.x = x;
			const sprite = new PIXI.Sprite();
			sprite.anchor.set(0.5);
			const value = new PIXI.BitmapText({ text: '', style: { fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.26 } });
			value.anchor.set(0.5);
			value.y = -SYMBOL_SIZE * 0.05;
			slotRoot.addChild(sprite, value);
			inner.addChild(slotRoot);
			return { root: slotRoot, sprite, value, size: 0 };
		});

		// landing impact: a soft gold flash over the reel
		const flash = new PIXI.Graphics()
			.rect(x - SYMBOL_SIZE / 2, 0, SYMBOL_SIZE, SYMBOL_SIZE * ROWS)
			.fill({ color: 0xffd36a, alpha: 1 });
		flash.alpha = 0;
		flash.blendMode = 'add';
		outer.addChild(flash);

		root.addChild(outer);
		return { outer, inner, blur, slots, flash, landedAt: -Infinity };
	});

	const draw = (now: number) => {
		const c = reelSpin.config();
		const spacing = SYMBOL_SIZE * c.symbolSpacing;
		reels.forEach((reel, reelIndex) => {
			const view = views[reelIndex];
			const speed = reel.speedRatio();
			view.blur.strengthY = c.motionBlurAmount * speed;
			view.blur.enabled = speed > 0.05; // skip the filter pass when nearly still
			const stretch = 1 + c.speedStretch * speed;
			const sinceLand = now - view.landedAt;
			const squash = sinceLand < LAND_SQUASH_MS ? Math.sin((sinceLand / LAND_SQUASH_MS) * Math.PI) * 0.08 : 0;
			view.flash.alpha = sinceLand < FLASH_MS ? 0.28 * (1 - sinceLand / FLASH_MS) : 0;

			const indices = reel.visibleIndices();
			view.slots.forEach((slot, k) => {
				const index = indices[k];
				if (index === undefined) {
					slot.root.visible = false;
					return;
				}
				const symbol = reel.symbolAt(index);
				const look = symbolLook(symbol);
				if (slot.sprite.texture !== look.texture) slot.sprite.texture = look.texture;
				slot.size = look.size;
				slot.root.visible = true;
				slot.root.y = (index + reel.scroll + 0.5) * spacing;
				slot.sprite.width = look.size * (1 + squash * 0.6);
				slot.sprite.height = look.size * stretch * (1 - squash);
				const text = symbol.multiplier !== undefined ? `${symbol.multiplier}x` : '';
				if (slot.value.text !== text) slot.value.text = text;
			});
		});
	};

	const tick = () => {
		reelSpin.updateShake(performance.now());
		if (!stateReelSpin.active) {
			if (root.visible) root.visible = false;
			return;
		}
		const now = performance.now();
		const landed = reelSpin.update(now);
		for (const reelIndex of landed) views[reelIndex].landedAt = now;
		// stay visible on the frame the spin hands over, so there is no blank frame
		root.visible = true;
		draw(now);
	};

	$effect(() => {
		const ticker = app.stateApp.pixiApplication?.ticker;
		if (!ticker) return;
		ticker.add(tick);
		return () => ticker.remove(tick);
	});

	context.eventEmitter.subscribeOnMount({
		stopButtonClick: () => reelSpin.hurry(),
	});

</script>
