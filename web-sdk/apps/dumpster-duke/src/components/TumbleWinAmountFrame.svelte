<script lang="ts">
	import type { Snippet } from 'svelte';

	import { BitmapText, Container, type Sizes } from 'pixi-svelte';

	import Plaque from './fx/Plaque.svelte';
	import { SYMBOL_SIZE } from '../game/constants';

	type Props = {
		children: Snippet<[{ frameSizes: Sizes }]>;
	};

	const props: Props = $props();

	const TITLE_HEIGHT = SYMBOL_SIZE * 0.28;
	const PANEL_SIZES = { width: SYMBOL_SIZE * 2.9, height: SYMBOL_SIZE * 0.75 };
</script>

<Plaque {...PANEL_SIZES} />
<Container y={-PANEL_SIZES.height * 0.5 - TITLE_HEIGHT * 0.15}>
	<Plaque width={TITLE_HEIGHT * 4.4} height={TITLE_HEIGHT * 1.15} />
	<BitmapText anchor={0.5} text="TUMBLE WIN" style={{ fontFamily: 'gold', fontSize: TITLE_HEIGHT * 0.55 }} />
</Container>
{@render props.children({ frameSizes: PANEL_SIZES })}
