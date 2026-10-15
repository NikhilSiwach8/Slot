<!-- Story helper: opens the buy-feature menu on a game background with a test balance. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { stateBet, stateConfig, stateModal } from 'state-shared';

	import { stateBonus } from 'components-ui-html/src/stateBonus.svelte';

	import ModalBuyFeature from '../components/buy/ModalBuyFeature.svelte';

	type Props = { modal: 'buyBonus' | 'buyBonusConfirm'; ante?: boolean; spinMode?: string; selected?: string };
	const props: Props = $props();
	const BG = new URL('../../assets/sprites/dukeBackgrounds/bg_base_landscape.webp', import.meta.url).href;

	onMount(() => {
		stateBet.balanceAmount = 1000;
		stateBet.betAmount = 1;
		stateConfig.betAmountOptions = [0.2, 0.5, 1, 2, 5, 10, 20, 50, 100];
		stateBet.activeBetModeKey = props.spinMode ?? (props.ante ? 'ANTE' : 'BASE');
		stateBonus.selectedBetModeKey = props.selected ?? 'BONUS';
		stateModal.modal = { name: props.modal };
	});
</script>

<div style="position: fixed; inset: 0; background: url({BG}) center / cover;"></div>
<ModalBuyFeature />
