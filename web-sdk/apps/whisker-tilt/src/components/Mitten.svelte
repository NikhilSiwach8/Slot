<script lang="ts" module>
	export type EmitterEventMitten = { type: 'mittenBat'; gravity: string };
</script>

<!-- Mitten sits beside the snow box (wide layouts) and bats it with her paw on every tilt. -->
<script lang="ts">
	import { onDestroy } from 'svelte';
	import { Container, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { FRAME } from '../game/constants';
	import { animate, easeOutCubic } from '../game/tiltBoard.svelte';
	import { createClock } from './fx/timeline.svelte';

	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const layout = $derived(context.stateGameDerived.boardLayout());
	const main = $derived(context.stateLayoutDerived.mainLayout());
	const wide = $derived(['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType()));
	const boxHalf = $derived((FRAME.size * layout.scale) / 2);

	// paw: 0 = out of view, 1 = touching the box's top-right corner
	let reach = $state(0);
	let swipe = $state(0);

	context.eventEmitter.subscribeOnMount({
		mittenBat: async () => {
			await animate(170, (t) => (reach = easeOutCubic(t)));
			await animate(110, (t) => (swipe = Math.sin(t * Math.PI)));
			await animate(200, (t) => (reach = 1 - easeOutCubic(t)));
			swipe = 0;
		},
	});

	const PAW = { w: 344 * 0.6, h: 512 * 0.6 };
	const pawFrom = $derived({ x: main.width + PAW.h, y: -PAW.h });
	const pawTo = $derived({ x: layout.x + boxHalf * 0.55, y: layout.y - boxHalf * 0.75 });
</script>

{#if wide}
	<!-- Mitten, breathing gently, to the left of the box -->
	<Sprite
		key="mitten"
		anchor={{ x: 0.5, y: 1 }}
		x={Math.max(150, layout.x - boxHalf - 130)}
		y={main.height * 0.92}
		width={234}
		height={330 * (1 + Math.sin(clock.seconds * 1.6) * 0.012)}
	/>
{/if}

{#if reach > 0}
	<Container
		x={pawFrom.x + (pawTo.x - pawFrom.x) * reach}
		y={pawFrom.y + (pawTo.y - pawFrom.y) * reach}
		rotation={-2.45 + swipe * 0.35}
	>
		<Sprite key="mitten_paw" anchor={{ x: 0.5, y: 0.2 }} width={PAW.w} height={PAW.h} />
	</Container>
{/if}
