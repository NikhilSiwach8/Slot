<!-- Distant lightning: every 18-30 s the whole screen flickers twice with a cold light. -->
<script lang="ts">
	import { onDestroy } from 'svelte';
	import { Rectangle } from 'pixi-svelte';

	import { createClock } from '../timeline.svelte';

	type Props = { width: number; height: number };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const PERIOD = 23;
	const flash = $derived.by(() => {
		const cycle = Math.floor(clock.seconds / PERIOD);
		const t = (clock.seconds % PERIOD) - (6 + ((cycle * 7) % 11)); // vary the moment each cycle
		if (t < 0 || t > 0.6) return 0;
		const a = Math.max(0, 1 - Math.abs(t - 0.05) / 0.07);
		const b = Math.max(0, 1 - Math.abs(t - 0.28) / 0.18);
		return Math.max(a * 0.22, b * 0.16);
	});
</script>

{#if flash > 0}
	<Rectangle width={props.width} height={props.height} backgroundColor={0xd8d4ff} alpha={flash} blendMode="add" />
{/if}
