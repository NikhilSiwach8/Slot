<script lang="ts" module>
	export type DukeSymbolInfo = {
		type: 'duke';
		assetKey: string;
		animation: 'idle' | 'land' | 'win' | 'explode' | 'taken';
		sizeRatios: { width: number; height: number };
		multiplier?: number;
	};

	// Duration (ms) of each one-shot animation; idle/taken loop and complete immediately.
	const DURATIONS = { land: 320, win: 1000, explode: 300 } as const;
</script>

<script lang="ts">
	import { onDestroy } from 'svelte';
	import { Container, Sprite, Text } from 'pixi-svelte';

	import { SYMBOL_SIZE } from '../game/constants';

	type Props = {
		x?: number;
		y?: number;
		symbolInfo: DukeSymbolInfo;
		oncomplete?: () => void;
		loop?: boolean;
	};

	const props: Props = $props();

	let elapsed = $state(0);
	let frame = 0;
	let completedFor: DukeSymbolInfo | undefined;

	const run = (info: DukeSymbolInfo) => {
		cancelAnimationFrame(frame);
		elapsed = 0;
		const duration = DURATIONS[info.animation as keyof typeof DURATIONS];
		if (!duration) {
			// Static states finish straight away, matching the template's sprite behaviour.
			props.oncomplete?.();
			return;
		}
		const start = performance.now();
		const tick = (now: number) => {
			elapsed = Math.min(1, (now - start) / duration);
			if (elapsed < 1) {
				frame = requestAnimationFrame(tick);
			} else if (props.loop) {
				run(info);
			} else if (completedFor !== info) {
				completedFor = info;
				props.oncomplete?.();
			}
		};
		frame = requestAnimationFrame(tick);
	};

	$effect(() => {
		run(props.symbolInfo);
	});

	onDestroy(() => cancelAnimationFrame(frame));

	// Hand-tuned cartoon motion: squash & stretch on land, double pulse + wiggle on win,
	// quick puff-out on explode.
	const transform = $derived.by(() => {
		const t = elapsed;
		switch (props.symbolInfo.animation) {
			case 'land': {
				const squash = Math.sin(t * Math.PI) * 0.18 * (1 - t);
				return { sx: 1 + squash, sy: 1 - squash, rot: 0, alpha: 1, dy: squash * SYMBOL_SIZE * 0.1 };
			}
			case 'win': {
				const pulse = Math.abs(Math.sin(t * Math.PI * 2)) * 0.16;
				const wiggle = Math.sin(t * Math.PI * 6) * 0.08 * (1 - t);
				return { sx: 1 + pulse, sy: 1 + pulse, rot: wiggle, alpha: 1, dy: 0 };
			}
			case 'explode': {
				const grow = 1 + t * 0.45;
				return { sx: grow, sy: grow, rot: t * 0.3, alpha: 1 - t, dy: 0 };
			}
			case 'taken':
				return { sx: 0.85, sy: 0.85, rot: 0, alpha: 0.45, dy: 0 };
			default:
				return { sx: 1, sy: 1, rot: 0, alpha: 1, dy: 0 };
		}
	});

	const width = $derived(SYMBOL_SIZE * props.symbolInfo.sizeRatios.width);
	const height = $derived(SYMBOL_SIZE * props.symbolInfo.sizeRatios.height);
</script>

<Container
	x={props.x ?? 0}
	y={(props.y ?? 0) + transform.dy}
	scale={{ x: transform.sx, y: transform.sy }}
	rotation={transform.rot}
	alpha={transform.alpha}
>
	<Sprite anchor={0.5} key={props.symbolInfo.assetKey} {width} {height} />
	{#if props.symbolInfo.multiplier !== undefined}
		<Text
			anchor={0.5}
			text={`${props.symbolInfo.multiplier}x`}
			style={{
				fontFamily: 'Arial Black, Arial, sans-serif',
				fontWeight: '900',
				fontSize: SYMBOL_SIZE * (props.symbolInfo.multiplier >= 100 ? 0.22 : 0.28),
				fill: '#fff6d8',
				stroke: { color: '#2d1914', width: SYMBOL_SIZE * 0.06 },
			}}
		/>
	{/if}
</Container>
