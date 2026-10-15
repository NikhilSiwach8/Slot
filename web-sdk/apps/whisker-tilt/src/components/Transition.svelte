<script lang="ts" module>
	export type EmitterEventTransition = { type: 'transition' };
</script>

<script lang="ts">
	import { waitForResolve } from 'utils-shared/wait';

	import TransitionAnimation from './TransitionAnimation.svelte';
	import { getContext } from '../game/context';

	const context = getContext();

	let transitioning = $state(false);
	let opening = $state(false);
	let oncomplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		transition: async () => {
			transitioning = true;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

{#if transitioning}
	<TransitionAnimation
		oncomplete={() => {
			// covered: let the scene switch underneath, then open the curtain
			oncomplete();
			transitioning = false;
			opening = true;
		}}
	/>
{/if}

{#if opening}
	<TransitionAnimation opening oncomplete={() => (opening = false)} />
{/if}
