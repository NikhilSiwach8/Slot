<!--
	Bonus menu in the Dumpster Duke art style (BONUS panel + card from the UI sheet).
	Replaces the template's buyBonus / buyBonusConfirm modals. Lists the game's real
	modes (game/betModeMeta.ts): the Midnight Raid buy and the Double Chance (ante) switch.

	Everything is sized in container-query units of the panel (cqw), so the layout
	keeps the same proportions inside the panel art at every viewport size.
-->
<script lang="ts">
	import '@fontsource/lilita-one/400.css';

	import { OnHotkey, OptionsToggle } from 'components-shared';
	import { stateBet, stateConfig, stateModal, stateMetaDerived, stateBetDerived } from 'state-shared';
	import { getContextEventEmitter } from 'utils-event-emitter';
	import { numberToCurrencyString } from 'utils-shared/amount';
	import { stateBonus, stateBonusDerived } from 'components-ui-html/src/stateBonus.svelte';
	import type { EmitterEventModal } from 'components-ui-html';

	import { socialWording } from '../../game/social';

	const { eventEmitter } = getContextEventEmitter<EmitterEventModal>();

	// literal paths so Vite can resolve them
	const PANEL = new URL('../../../assets/ui/panel.webp', import.meta.url).href;
	const CARD = new URL('../../../assets/ui/card.webp', import.meta.url).href;
	const BACK = new URL('../../../assets/ui/btn_back.webp', import.meta.url).href;

	const modes = $derived(stateMetaDerived.betModeMetaList());
	const buyList = $derived(modes.filter((mode) => mode.type === 'buy'));
	const anteList = $derived(modes.filter((mode) => mode.type === 'activate'));
	const open = $derived(stateModal.modal?.name === 'buyBonus' || stateModal.modal?.name === 'buyBonusConfirm');
	const confirming = $derived(stateModal.modal?.name === 'buyBonusConfirm');
	const selected = $derived(stateBonusDerived.selectedBetModeData());
	const anteOn = $derived(stateBetDerived.activeBetMode()?.type === 'activate');

	const price = (costMultiplier: number) => numberToCurrencyString(stateBet.betAmount * costMultiplier);
	const affordable = (costMultiplier: number) =>
		stateBet.betAmount > 0 && stateBet.balanceAmount >= stateBet.betAmount * costMultiplier;

	const press = () => eventEmitter.broadcast({ type: 'soundPressGeneral' });
	const close = () => (stateModal.modal = null);
	const choose = (mode: string) => {
		stateBonus.selectedBetModeKey = mode;
		press();
		stateModal.modal = { name: 'buyBonusConfirm' };
	};
	const confirm = () => {
		stateBet.activeBetModeKey = stateBonus.selectedBetModeKey;
		press();
		eventEmitter.broadcast({ type: 'bet' });
		stateModal.modal = null;
	};
	const toggleAnte = (mode: string) => {
		press();
		stateBet.activeBetModeKey = anteOn ? 'BASE' : mode;
		if (!anteOn) close();
	};
</script>

{#if open}
	<OnHotkey hotkey="Escape" onpress={close} />
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="overlay" onclick={close}>
		<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
		<div class="panel" style="background-image: url({PANEL});" onclick={(event) => event.stopPropagation()}>
			<button class="close" aria-label="Close" onclick={close}></button>

			<div class="content" use:socialWording>
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
									<span class="small">{mode.costMultiplier}x bet</span>
								</div>
								<button
									class="gold"
									disabled={anteOn || !affordable(mode.costMultiplier)}
									onclick={() => choose(mode.mode)}
								>
									{anteOn ? 'DOUBLE CHANCE IS ON' : mode.text.button}
								</button>
								{#if !anteOn && !affordable(mode.costMultiplier)}
									<p class="small warn">Not enough balance for this bet.</p>
								{/if}
							</div>
						</div>
					{/each}

					{#each anteList as mode}
						<div class="offer ante" class:on={anteOn}>
							<div class="badge" aria-hidden="true"><span>2×</span><small>CHANCE</small></div>
							<div class="details">
								<h2>{mode.text.title}</h2>
								<p>{mode.text.description}</p>
								<p class="small">{mode.text.dialog}</p>
								<div class="cost">
									<span class="label">SPIN</span>
									<span class="amount">{price(mode.costMultiplier)}</span>
									<span class="small">{mode.costMultiplier}x bet</span>
								</div>
								<button class="gold" class:off={anteOn} onclick={() => toggleAnte(mode.mode)}>
									{anteOn ? 'SWITCH OFF' : mode.text.button}
								</button>
							</div>
						</div>
					{/each}

					<OptionsToggle
						value={stateBet.betAmount}
						options={stateConfig.betAmountOptions}
						onchange={(value) => {
							stateBet.betAmount = value;
							press();
						}}
					>
						{#snippet children({ disabledDown, disabledUp, toggleDown, toggleUp })}
							<div class="bet">
								<span class="label">BET</span>
								<button class="step" disabled={disabledDown} onclick={toggleDown} aria-label="Lower bet">−</button>
								<span class="amount">{numberToCurrencyString(stateBet.betAmount)}</span>
								<button class="step" disabled={disabledUp} onclick={toggleUp} aria-label="Raise bet">+</button>
							</div>
						{/snippet}
					</OptionsToggle>
				{:else}
					<div class="confirm">
						<h2>{selected.text.title}</h2>
						<p>Buy the {selected.text.title.toLowerCase()} for</p>
						<div class="amount big">{price(selected.costMultiplier)}</div>
						<p class="small">{selected.text.dialog}</p>
						<button class="gold wide" onclick={confirm}>CONFIRM</button>
						<button
							class="back"
							style="background-image: url({BACK});"
							aria-label="Back"
							onclick={() => (stateModal.modal = { name: 'buyBonus' })}
						></button>
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
	/* panel art is 558 x 637; its dark inner window spans x 42-510 and y 88-592,
	   and the lantern hangs over the right edge between y 100 and 260 */
	.panel {
		position: relative;
		width: min(94vw, 86vh * 558 / 637, 600px);
		aspect-ratio: 558 / 637;
		background-size: 100% 100%;
		container-type: inline-size;
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
		left: 10%;
		right: 11.5%;
		top: 15%;
		bottom: 8%;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		justify-content: safe center;
		gap: 1.6cqw;
		scrollbar-width: thin;
	}
	.offer {
		display: flex;
		align-items: stretch;
		gap: 2.6cqw;
		padding: 1.5cqw 2.2cqw;
		border-radius: 3cqw;
		background: rgba(255, 255, 255, 0.05);
		box-shadow: inset 0 0 0 0.35cqw rgba(255, 207, 58, 0.18);
	}
	.offer.ante.on {
		box-shadow: inset 0 0 0 0.5cqw #ffcf3a, 0 0 4cqw rgba(255, 190, 60, 0.35);
	}
	.card {
		flex: 0 0 21%;
		aspect-ratio: 280 / 545;
		background-size: 100% 100%;
		align-self: center;
	}
	.badge {
		flex: 0 0 21%;
		align-self: center;
		aspect-ratio: 1;
		border-radius: 50%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: radial-gradient(circle at 35% 30%, #ffe680, #f4a21e 55%, #9a4a0a);
		box-shadow: 0 0 0 0.8cqw #5a2a0a, 0 0 5cqw rgba(255, 190, 60, 0.45);
		color: #4a1d06;
		line-height: 1;
	}
	.badge span {
		font-size: 8cqw;
	}
	.badge small {
		font-size: 2.4cqw;
	}
	.details {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 0.9cqw;
	}
	h2 {
		margin: 0;
		color: #ffcf3a;
		font-weight: 400;
		font-size: 5cqw;
		line-height: 1.05;
		letter-spacing: 0.02em;
		text-shadow: 0 0.4cqw 0 #5a2a0a;
	}
	p {
		margin: 0;
		font-family: Arial, Helvetica, sans-serif;
		font-weight: 700;
		font-size: 2.8cqw;
		line-height: 1.25;
	}
	.small {
		font-size: 2.6cqw;
		opacity: 0.85;
		white-space: nowrap;
	}
	p.small {
		white-space: normal;
	}
	.warn {
		color: #ff9a8a;
	}
	.cost {
		display: flex;
		align-items: baseline;
		flex-wrap: nowrap;
		gap: 1.5cqw;
	}
	.label {
		color: #ffcf3a;
		font-size: 3.4cqw;
	}
	.amount {
		font-size: 4.6cqw;
		white-space: nowrap;
	}
	.amount.big {
		font-size: 9cqw;
		color: #ffcf3a;
		text-shadow: 0 0.6cqw 0 #5a2a0a;
	}
	button.gold {
		width: 100%;
		padding: 0.9cqw 0;
		border: 0.6cqw solid #5a2a0a;
		border-radius: 2.4cqw;
		background: linear-gradient(#ffe066, #f39a1c);
		color: #4a1d06;
		font-family: inherit;
		font-size: 4.2cqw;
		cursor: pointer;
		box-shadow: 0 0.8cqw 0 #5a2a0a, 0 0 3cqw rgba(255, 190, 60, 0.45);
	}
	button.gold.off {
		background: linear-gradient(#d9d0e8, #9c8fb5);
	}
	button.gold.wide {
		width: 70%;
	}
	button.gold:disabled {
		filter: grayscale(0.8) brightness(0.7);
		cursor: not-allowed;
	}
	.bet {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 3cqw;
	}
	.bet .amount {
		min-width: 22cqw;
		text-align: center;
	}
	button.step {
		width: 8cqw;
		aspect-ratio: 1;
		border: 0.5cqw solid #5a2a0a;
		border-radius: 50%;
		background: linear-gradient(#ffe066, #f39a1c);
		color: #4a1d06;
		font-family: inherit;
		font-size: 6cqw;
		line-height: 1;
		cursor: pointer;
	}
	button.step:disabled {
		filter: grayscale(0.8) brightness(0.6);
		cursor: not-allowed;
	}
	.confirm {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 2.4cqw;
	}
	.confirm p {
		font-size: 3.4cqw;
	}
	button.back {
		width: 40%;
		aspect-ratio: 183 / 77;
		border: 0;
		background: transparent center / 100% 100% no-repeat;
		cursor: pointer;
	}
</style>
