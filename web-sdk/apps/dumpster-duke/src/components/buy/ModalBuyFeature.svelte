<!--
	Buy-feature menu in the Dumpster Duke art style (BONUS panel + card from the UI
	sheet). Replaces the template's buyBonus / buyBonusConfirm modals and lists only
	the game's real buy modes (see game/betModeMeta.ts).
-->
<script lang="ts">
	import '@fontsource/lilita-one/400.css';

	import { OnHotkey } from 'components-shared';
	import { stateBet, stateModal, stateMetaDerived } from 'state-shared';
	import { getContextEventEmitter } from 'utils-event-emitter';
	import { numberToCurrencyString } from 'utils-shared/amount';
	import BetMenuAmountToggle from 'components-ui-html/src/components/BetMenuAmountToggle.svelte';
	import { stateBonus, stateBonusDerived } from 'components-ui-html/src/stateBonus.svelte';
	import type { EmitterEventModal } from 'components-ui-html';

	const { eventEmitter } = getContextEventEmitter<EmitterEventModal>();

	// literal paths so Vite can resolve them
	const PANEL = new URL('../../../assets/ui/panel.webp', import.meta.url).href;
	const CARD = new URL('../../../assets/ui/card.webp', import.meta.url).href;
	const BACK = new URL('../../../assets/ui/btn_back.webp', import.meta.url).href;

	const buyList = $derived(stateMetaDerived.betModeMetaList().filter((mode) => mode.type === 'buy'));
	const open = $derived(stateModal.modal?.name === 'buyBonus' || stateModal.modal?.name === 'buyBonusConfirm');
	const confirming = $derived(stateModal.modal?.name === 'buyBonusConfirm');
	const selected = $derived(stateBonusDerived.selectedBetModeData());

	const price = (costMultiplier: number) => numberToCurrencyString(stateBet.betAmount * costMultiplier);
	const affordable = (costMultiplier: number) =>
		stateBet.betAmount > 0 && stateBet.balanceAmount >= stateBet.betAmount * costMultiplier;

	const close = () => (stateModal.modal = null);
	const choose = (mode: string) => {
		stateBonus.selectedBetModeKey = mode;
		eventEmitter.broadcast({ type: 'soundPressGeneral' });
		stateModal.modal = { name: 'buyBonusConfirm' };
	};
	const confirm = () => {
		stateBet.activeBetModeKey = stateBonus.selectedBetModeKey;
		eventEmitter.broadcast({ type: 'soundPressGeneral' });
		eventEmitter.broadcast({ type: 'bet' });
		stateModal.modal = null;
	};
</script>

{#if open}
	<OnHotkey hotkey="Escape" onpress={close} />
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="overlay" onclick={close}>
		<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
		<div class="panel" style="background-image: url({PANEL});" onclick={(event) => event.stopPropagation()}>
			<button class="close" aria-label="Close" onclick={close}></button>

			<div class="content">
				{#if !confirming}
					{#each buyList as mode}
						<div class="offer">
							<div class="card" style="background-image: url({CARD});"></div>
							<div class="details">
								<h2>{mode.text.title}</h2>
								<p>{mode.text.description}</p>
								<p class="small">{mode.text.dialog}</p>
								<div class="cost">
									<span class="label">COST</span>
									<span class="amount">{price(mode.costMultiplier)}</span>
									<span class="small">({mode.costMultiplier}x bet)</span>
								</div>
								<button class="gold" disabled={!affordable(mode.costMultiplier)} onclick={() => choose(mode.mode)}>
									{mode.text.button}
								</button>
								{#if !affordable(mode.costMultiplier)}
									<p class="small warn">Not enough balance for this bet.</p>
								{/if}
							</div>
						</div>
					{/each}
					<div class="bet">
						<BetMenuAmountToggle />
					</div>
				{:else}
					<div class="confirm">
						<h2>{selected.text.title}</h2>
						<p>Buy the {selected.text.title.toLowerCase()} for</p>
						<div class="amount big">{price(selected.costMultiplier)}</div>
						<p class="small">{selected.text.dialog}</p>
						<button class="gold" onclick={confirm}>CONFIRM</button>
						<button class="back" style="background-image: url({BACK});" aria-label="Back"
							onclick={() => (stateModal.modal = { name: 'buyBonus' })}></button>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	.overlay {
		position: fixed;
		inset: 0;
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(8, 4, 20, 0.72);
		font-family: 'Lilita One', 'Arial Black', sans-serif;
		color: #f6efe2;
	}
	/* panel art is 558 x 637; the inner dark area starts ~100px down and ~62px in */
	.panel {
		position: relative;
		width: min(92vw, 70vh * 558 / 637, 560px);
		aspect-ratio: 558 / 637;
		background-size: 100% 100%;
	}
	.close {
		position: absolute;
		top: 4%;
		right: 2.5%;
		width: 9%;
		aspect-ratio: 1;
		border: 0;
		border-radius: 50%;
		background: transparent;
		cursor: pointer;
	}
	.content {
		position: absolute;
		left: 12%;
		right: 15%;
		top: 17%;
		bottom: 10%;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}
	.offer {
		display: flex;
		gap: 0.75rem;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 12px;
		padding: 0.5rem;
	}
	.card {
		flex: 0 0 38%;
		aspect-ratio: 280 / 545;
		background-size: 100% 100%;
	}
	.details {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}
	h2 {
		margin: 0;
		color: #ffcf3a;
		font-weight: 400;
		font-size: 1.5rem;
		letter-spacing: 0.02em;
		text-shadow: 0 2px 0 #5a2a0a;
	}
	p {
		margin: 0;
		font-family: Arial, Helvetica, sans-serif;
		font-weight: 700;
		font-size: 0.8rem;
		line-height: 1.3;
	}
	.small {
		font-size: 0.7rem;
		opacity: 0.85;
	}
	.warn {
		color: #ff9a8a;
	}
	.cost {
		display: flex;
		align-items: baseline;
		gap: 0.4rem;
		margin-top: 0.2rem;
	}
	.label {
		color: #ffcf3a;
		font-size: 0.9rem;
	}
	.amount {
		font-size: 1.3rem;
	}
	.amount.big {
		font-size: 2.2rem;
		color: #ffcf3a;
		text-shadow: 0 3px 0 #5a2a0a;
	}
	button.gold {
		margin-top: 0.3rem;
		padding: 0.45rem 1.2rem;
		border: 3px solid #5a2a0a;
		border-radius: 12px;
		background: linear-gradient(#ffe066, #f39a1c);
		color: #4a1d06;
		font-family: inherit;
		font-size: 1.3rem;
		cursor: pointer;
		box-shadow: 0 4px 0 #5a2a0a, 0 0 18px rgba(255, 190, 60, 0.45);
	}
	button.gold:disabled {
		filter: grayscale(0.8) brightness(0.7);
		cursor: not-allowed;
	}
	.bet {
		margin-top: auto;
		font-size: 1.1rem;
	}
	.confirm {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 0.6rem;
		padding-top: 1rem;
	}
	button.back {
		width: 45%;
		aspect-ratio: 183 / 77;
		border: 0;
		background: transparent center / 100% 100% no-repeat;
		cursor: pointer;
	}
</style>
