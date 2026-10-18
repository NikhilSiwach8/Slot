<script lang="ts">
	import { onMount, type Snippet } from 'svelte';
	import { GlobalStyle } from 'components-ui-html';
	import { Authenticate, LoadI18n } from 'components-shared';
	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';

	import messagesMap from '../i18n/messagesMap';
	import '../fonts.css';

	type Props = { children: Snippet };

	const props: Props = $props();

	// Stake Engine's intro (app.html, re-encoded from the template GIF by scripts/make_loader_webp.py)
	// stays up for one play of its 2 s animation after the image has loaded, then fades out.
	const INTRO_MS = 2000;
	onMount(() => {
		const intro = document.getElementById('stake-engine-intro');
		const img = intro?.querySelector('img');
		if (!intro || !img) return;
		const hide = () => {
			intro.style.opacity = '0';
			setTimeout(() => intro.remove(), 400);
		};
		const afterLoad = () => {
			const entry = performance.getEntriesByName(img.currentSrc || img.src)[0] as PerformanceResourceTiming | undefined;
			const loadedAt = entry?.responseEnd || performance.now();
			setTimeout(hide, Math.max(0, loadedAt + INTRO_MS - performance.now()));
		};
		if (img.complete && img.naturalWidth > 0) afterLoad();
		else {
			img.addEventListener('load', afterLoad, { once: true });
			img.addEventListener('error', hide, { once: true });
		}
	});

	setContext();
</script>

<GlobalStyle>
	<Authenticate>
		<LoadI18n {messagesMap}>
			<Game />
		</LoadI18n>
	</Authenticate>
</GlobalStyle>

{@render props.children()}