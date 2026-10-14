<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { Container } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import { SYMBOL_SIZE } from '../game/constants';
	import { createTween01, type Tween01 } from './fx/timeline.svelte';

	type Props = {
		width: number;
		amount: number;
		animate: boolean;
		oncomplete: () => void;
	};

	const props: Props = $props();
	const amount = new Tween(0);
	let burst = $state<Tween01 | null>(null);

	// counts up to each new amount; the final multiplied amount bursts in
	$effect(() => {
		const target = props.amount;
		if (props.animate) {
			const pop = createTween01(500);
			burst = pop;
			amount.set(target, { duration: 350 });
			pop.done.then(() => props.oncomplete());
		} else {
			amount.set(target).then(() => props.oncomplete());
		}
	});
</script>

<Container scale={burst ? 1 + 0.35 * Math.sin(burst.t * Math.PI) : 1}>
	<ResponsiveBitmapText
		anchor={0.5}
		style={{ fontFamily: 'gold', fontSize: 0.5 * SYMBOL_SIZE }}
		text={bookEventAmountToCurrencyString(amount.current)}
		maxWidth={props.width * 0.9}
	/>
</Container>
