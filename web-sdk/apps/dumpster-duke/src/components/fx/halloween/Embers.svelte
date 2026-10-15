<!-- Ghostly sparks drifting upwards (orange embers and green will-o'-the-wisps). -->
<script lang="ts">
	import { onDestroy } from 'svelte';
	import { Circle, Container } from 'pixi-svelte';

	import { createClock } from '../timeline.svelte';

	type Props = { width: number; height: number; count?: number };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const rand = (i: number, k: number) => {
		const v = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453;
		return v - Math.floor(v);
	};
	const sparks = Array.from({ length: props.count ?? 28 }, (_, i) => ({
		x: rand(i, 1),
		period: 6 + rand(i, 2) * 6,
		offset: rand(i, 3) * 12,
		size: 2 + rand(i, 4) * 4,
		green: rand(i, 5) > 0.65,
		sway: 10 + rand(i, 6) * 30,
	}));
</script>

<Container blendMode="add">
	{#each sparks as spark}
		{@const u = ((clock.seconds + spark.offset) % spark.period) / spark.period}
		<Circle
			x={spark.x * props.width + Math.sin(u * Math.PI * 4 + spark.offset) * spark.sway}
			y={props.height * (1.02 - u * 0.75)}
			diameter={spark.size * 2}
			anchor={0.5}
			backgroundColor={spark.green ? 0x7dff8a : 0xff9a2e}
			alpha={Math.sin(u * Math.PI) * 0.85}
		/>
	{/each}
</Container>
