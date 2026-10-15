<!-- Gold crown coins (from the UI art) bursting up and raining down. A fixed pool
     of sprites is created once; coins respawn at the top while `active`. -->
<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextApp, getContextParent } from 'pixi-svelte';

	type Props = { width: number; height: number; count?: number; active: boolean; size?: number };
	const props: Props = $props();

	const app = getContextApp();
	const root = new PIXI.Container();
	getContextParent().addToParent(root);

	const texture = (app.stateApp.loadedAssets?.['ui_icon_bonus.png'] as PIXI.Texture) ?? PIXI.Texture.EMPTY;
	const size = props.size ?? 70;
	const coins = Array.from({ length: props.count ?? 40 }, () => {
		const sprite = new PIXI.Sprite(texture);
		sprite.anchor.set(0.5);
		sprite.width = sprite.height = size;
		root.addChild(sprite);
		return { sprite, x: 0, y: 0, vx: 0, vy: 0, spin: 0, phase: 0, alive: false };
	});

	const spawn = (coin: (typeof coins)[number], burst: boolean) => {
		coin.alive = true;
		coin.x = (Math.random() - 0.5) * props.width;
		coin.y = burst ? props.height * 0.15 : -props.height / 2 - size;
		coin.vx = (Math.random() - 0.5) * (burst ? 900 : 120);
		coin.vy = burst ? -700 - Math.random() * 700 : Math.random() * 200;
		coin.spin = 6 + Math.random() * 8;
		coin.phase = Math.random() * Math.PI * 2;
	};
	coins.forEach((coin) => spawn(coin, true));

	let last = performance.now();
	let frame = requestAnimationFrame(function step(now) {
		const dt = Math.min(0.05, (now - last) / 1000);
		last = now;
		for (const coin of coins) {
			if (!coin.alive) continue;
			coin.vy += 1500 * dt;
			coin.x += coin.vx * dt;
			coin.y += coin.vy * dt;
			coin.phase += coin.spin * dt;
			coin.sprite.x = coin.x;
			coin.sprite.y = coin.y;
			coin.sprite.scale.x = Math.cos(coin.phase) * (size / texture.width); // flipping coin
			coin.sprite.visible = true;
			if (coin.y > props.height / 2 + size) {
				if (props.active) spawn(coin, false);
				else {
					coin.alive = false;
					coin.sprite.visible = false;
				}
			}
		}
		frame = requestAnimationFrame(step);
	});

	onDestroy(() => cancelAnimationFrame(frame));
</script>
