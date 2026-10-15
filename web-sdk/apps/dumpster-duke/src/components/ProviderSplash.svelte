<script lang="ts" module>
	// The intro screen waits for this to finish, so its animations start when it is seen.
	export const stateSplash = $state({ visible: true });
</script>

<!--
	Provider splash and loading window: the NYXHILX logo on black with a glowing loading bar.
	Stays up while the game loads, and for at least MIN_MS so the logo is always seen, then
	fades out into the intro ("press anywhere to continue") screen.
-->
<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { fade } from 'svelte/transition';

	import { getContext } from '../game/context';
	import { staticAsset } from '../game/staticAsset';

	const MIN_MS = 2600;
	const LOGO = staticAsset('provider/nyxhilx_logo.webp');

	const context = getContext();
	let elapsed = $state(0);
	let timer: ReturnType<typeof setInterval> | undefined;
	onMount(() => {
		const start = performance.now();
		timer = setInterval(() => (elapsed = performance.now() - start), 100);
	});
	onDestroy(() => clearInterval(timer));

	// show the bar moving even when loading is instant
	const progress = $derived(
		Math.min(context.stateApp.loaded ? 100 : context.stateApp.loadingProgress, (elapsed / MIN_MS) * 100),
	);
	$effect(() => {
		if (context.stateApp.loaded && elapsed >= MIN_MS) {
			stateSplash.visible = false;
			clearInterval(timer);
		}
	});
</script>

{#if stateSplash.visible}
	<div class="splash" out:fade={{ duration: 600 }}>
		<img src={LOGO} alt="Nyxhilx" />
		<div class="bar" role="progressbar" aria-valuenow={Math.round(progress)} aria-valuemin="0" aria-valuemax="100">
			<div class="fill" style="width: {progress}%"></div>
		</div>
		<div class="label">LOADING {Math.round(progress)}%</div>
	</div>
{/if}

<style>
	.splash {
		position: fixed;
		inset: 0;
		z-index: 2000;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: min(2.4vh, 1.6vw);
		background: #020408; /* the logo artwork's own black, so the image edge never shows */
	}
	img {
		width: min(78vw, 110vh);
		max-height: 62vh;
		object-fit: contain;
		/* fade the picture's edges into the page */
		-webkit-mask-image: radial-gradient(ellipse 50% 50% at 50% 50%, #000 70%, transparent 100%);
		mask-image: radial-gradient(ellipse 50% 50% at 50% 50%, #000 70%, transparent 100%);
		animation: breathe 3.2s ease-in-out infinite;
	}
	@keyframes breathe {
		0%,
		100% {
			filter: brightness(0.95);
			transform: scale(1);
		}
		50% {
			filter: brightness(1.18);
			transform: scale(1.015);
		}
	}
	.bar {
		width: min(46vw, 60vh);
		height: max(5px, 0.8vh);
		border-radius: 999px;
		background: rgba(140, 170, 230, 0.14);
		box-shadow: inset 0 0 0 1px rgba(170, 195, 255, 0.25);
		overflow: hidden;
	}
	.fill {
		height: 100%;
		border-radius: inherit;
		background: linear-gradient(90deg, #4f7dff, #cfe0ff, #8fb1ff);
		box-shadow: 0 0 1.4vh rgba(120, 165, 255, 0.8);
		transition: width 0.15s linear;
	}
	.label {
		font-family: Georgia, 'Times New Roman', serif;
		letter-spacing: 0.35em;
		font-size: max(10px, min(1.6vh, 1.1vw));
		color: #b9c8ec;
	}
</style>
