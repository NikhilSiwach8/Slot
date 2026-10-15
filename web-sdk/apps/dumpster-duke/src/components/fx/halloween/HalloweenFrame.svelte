<!-- Halloween dressing for the reel house: jack-o'-lanterns sitting on the top corners and
     cobwebs (with a dangling spider) hanging off the outside of the frame. -->
<script lang="ts">
	import { Container } from 'pixi-svelte';

	import { getContext } from '../../../game/context';
	import { SYMBOL_SIZE } from '../../../game/constants';
	import JackOLantern from './JackOLantern.svelte';
	import Cobweb from './Cobweb.svelte';

	const context = getContext();
	const board = $derived(context.stateGameDerived.boardLayout());
	// outer edge of the frame drawn by BoardFrame (PAD 0.1 + BORDER 0.16 symbol sizes)
	const edge = SYMBOL_SIZE * 0.26;
	const hw = $derived(board.width / 2 + edge);
	const hh = $derived(board.height / 2 + edge);
</script>

<Container x={board.x} y={board.y}>
	<!-- cobwebs hang outside the frame so they never cover a symbol -->
	<Container x={-hw} y={-hh + 10} scale={{ x: -1, y: 1 }}>
		<Cobweb size={SYMBOL_SIZE * 1.1} spider />
	</Container>
	<Container x={hw} y={-hh + 10}>
		<Cobweb size={SYMBOL_SIZE * 0.9} />
	</Container>
	<Container x={-hw} y={hh - 10} scale={{ x: -1, y: -1 }}>
		<Cobweb size={SYMBOL_SIZE * 0.8} />
	</Container>

	<!-- pumpkins on the frame -->
	<JackOLantern x={-hw + SYMBOL_SIZE * 0.55} y={-hh - SYMBOL_SIZE * 0.22} size={SYMBOL_SIZE * 1.05} seed={1} rotation={-0.12} />
	<!-- the top-right corner is where the Treat Bag counter sits in the raid, so this one perches lower on the side -->
	<JackOLantern x={hw + SYMBOL_SIZE * 0.38} y={-hh + SYMBOL_SIZE * 1.55} size={SYMBOL_SIZE * 0.8} seed={4} rotation={0.1} />
	<JackOLantern x={hw + SYMBOL_SIZE * 0.05} y={hh - SYMBOL_SIZE * 0.05} size={SYMBOL_SIZE * 0.7} seed={7} rotation={0.05} />
</Container>
