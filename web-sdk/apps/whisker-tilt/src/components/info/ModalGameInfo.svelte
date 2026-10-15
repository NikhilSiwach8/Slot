<script lang="ts">
	import type { Snippet } from 'svelte';

	import { Popup } from 'components-shared';
	import { zIndex } from 'constants-shared/zIndex';
	import { stateModal } from 'state-shared';

	import GameInfo from './GameInfo.svelte';

	type Props = { version: Snippet };
	const props: Props = $props();

	const open = $derived(stateModal.modal?.name === 'gameRules' || stateModal.modal?.name === 'payTable');
</script>

{#if open}
	<Popup zIndex={zIndex.modal} onclose={() => (stateModal.modal = null)}>
		<div class="scroll">
			<GameInfo start={stateModal.modal?.name === 'payTable' ? 'payTable' : 'rules'} />
			{@render props.version()}
		</div>
	</Popup>
{/if}

<style>
	.scroll {
		max-height: 90vh;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
</style>
