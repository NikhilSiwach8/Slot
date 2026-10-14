<script lang="ts">
	import { Rectangle } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { SECOND } from 'constants-shared/time';

	import CoverImage from './CoverImage.svelte';
	import { getContext } from '../game/context';

	const context = getContext();
	const showBaseBackground = $derived(context.stateGame.gameType === 'basegame');
	const showFeatureBackground = $derived(context.stateGame.gameType === 'freeSpins');
</script>

<Rectangle {...context.stateLayoutDerived.canvasSizes()} backgroundColor={0x000000} zIndex={-3} />

<FadeContainer show={showBaseBackground} duration={SECOND} zIndex={-2}>
	<CoverImage name="bg_base" />
</FadeContainer>

<!-- Midnight Raid: the same tunnel, graded darker and more purple -->
<FadeContainer show={showFeatureBackground} duration={SECOND} zIndex={-1}>
	<CoverImage name="bg_raid" />
</FadeContainer>
