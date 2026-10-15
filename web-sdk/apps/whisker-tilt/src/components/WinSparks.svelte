<!-- A one-shot burst of crystal sparks (ice blue / gold diamonds) around a
     winning symbol. Pixi objects are created once on mount and freed on unmount. -->
<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';

	import { SYMBOL_SIZE } from '../game/constants';

	type Props = { count?: number; duration?: number };
	const props: Props = $props();

	const COLOURS = [0x6fd6ff, 0x8fd3ff, 0xffd34d, 0x9fe6ff];
	const count = props.count ?? 10;
	const duration = props.duration ?? 650;

	const root = new PIXI.Container();
	getContextParent().addToParent(root);

	const sparks = Array.from({ length: count }, (_, i) => {
		const size = SYMBOL_SIZE * (0.04 + Math.random() * 0.035);
		const g = new PIXI.Graphics()
			.poly([0, -size * 1.6, size, 0, 0, size * 1.6, -size, 0])
			.fill(COLOURS[i % COLOURS.length]);
		g.blendMode = 'add';
		root.addChild(g);
		const angle = (i / count) * Math.PI * 2 + Math.random() * 0.5;
		const speed = SYMBOL_SIZE * (0.55 + Math.random() * 0.45);
		return { g, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed - SYMBOL_SIZE * 0.2, spin: (Math.random() - 0.5) * 8 };
	});

	const start = performance.now();
	let frame = requestAnimationFrame(function step(now) {
		const t = Math.min(1, (now - start) / duration);
		const secs = (now - start) / 1000;
		for (const s of sparks) {
			s.g.x = s.vx * secs * (1 - t * 0.4);
			s.g.y = s.vy * secs + SYMBOL_SIZE * 0.9 * secs * secs; // a little gravity
			s.g.rotation = s.spin * secs;
			s.g.alpha = 1 - t;
			s.g.scale.set(1 - t * 0.5);
		}
		if (t < 1) frame = requestAnimationFrame(step);
	});

	onDestroy(() => cancelAnimationFrame(frame));
</script>
