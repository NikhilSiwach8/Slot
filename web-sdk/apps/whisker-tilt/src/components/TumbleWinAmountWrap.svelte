<script lang="ts">
	import type { Snippet } from 'svelte';

	import { Container } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';

	import { getContext } from '../game/context';
	import { FRAME } from '../game/constants';

	type Props = {
		show: boolean;
		children: Snippet;
	};

	const props: Props = $props();
	const context = getContext();

	const layout = $derived(context.stateGameDerived.boardLayout());
	const boxHalf = $derived((FRAME.size * layout.scale) / 2);

	// beside the snow box on wide screens, under it when the layout is stacked
	const position = $derived(
		context.stateLayoutDerived.isStacked()
			? { x: layout.x, y: layout.y + boxHalf + 40 }
			: { x: layout.x + boxHalf + 190, y: layout.y - layout.height * 0.25 },
	);
	const scale = $derived(context.stateLayoutDerived.isStacked() ? 1.2 : 1);
</script>

<FadeContainer show={props.show}>
	<Container {...position} {scale}>
		{@render props.children()}
	</Container>
</FadeContainer>
