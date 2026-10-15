<script lang="ts">
	import { Rectangle } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { SECOND } from 'constants-shared/time';

	import CoverImage from './CoverImage.svelte';
	import { getContext } from '../game/context';

	const context = getContext();
	// reveal events set gameType to the math's name ('freegame'), the trigger handler to 'freeSpins'
	const inFreeSpins = $derived(context.stateGame.gameType !== 'basegame');
	const scene = $derived(
		!inFreeSpins ? 'base' : context.stateGame.freeSpinKind === 'super' ? 'super' : 'snowday',
	);
</script>

<Rectangle {...context.stateLayoutDerived.canvasSizes()} backgroundColor={0x000000} zIndex={-4} />

<!-- dusk by the frozen lake -->
<FadeContainer show={scene === 'base'} duration={SECOND} zIndex={-3}>
	<CoverImage name="bg_base" />
</FadeContainer>

<!-- Snow Day: the skating rink under falling snow -->
<FadeContainer show={scene === 'snowday'} duration={SECOND} zIndex={-2}>
	<CoverImage name="bg_snowday" />
</FadeContainer>

<!-- Super Snow Day: night and the aurora -->
<FadeContainer show={scene === 'super'} duration={SECOND} zIndex={-1}>
	<CoverImage name="bg_super" />
</FadeContainer>
