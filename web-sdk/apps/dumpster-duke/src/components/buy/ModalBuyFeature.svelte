<!--
	Bonus menu in the Dumpster Duke art style (BONUS panel from the UI sheet).
	Replaces the template's buyBonus / buyBonusConfirm modals.

	Menu: a grid of tiles, one per real mode (game/betModeMeta.ts): the bonus buys
	(Midnight Raid, Super Bonus, Mystery Bonus, Max or Nothing) and the spin modes that
	stay on (Double Chance, Feature Spin), plus a bet stepper. Tapping a tile opens its
	detail screen, where the player buys the bonus or switches the spin mode on/off.

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
	const BACK = new URL('../../../assets/ui/btn_back.webp', import.meta.url).href;
	const ICON_CAN = new URL('../../../assets/ui/icon_s.webp', import.meta.url).href;
	const ICON_CAP = new URL('../../../assets/ui/icon_m.webp', import.meta.url).href;
	const ICON_DUKE = new URL('../../../assets/ui/icon_h1.webp', import.meta.url).href;

	type Icon = { image?: string; text?: string; tag?: string };
	const ICONS: Record<string, Icon> = {
		BONUS: { image: ICON_CAN },
		SUPER: { image: ICON_CAP, tag: 'x10' },
		MYSTERY: { text: '?' },
		MAX: { image: ICON_DUKE, tag: 'MAX' },
		ANTE: { text: '2×' },
		FEATURE: { image: ICON_CAN, tag: '3' },
	};
	const ORDER = ['BONUS', 'SUPER', 'MYSTERY', 'MAX', 'ANTE', 'FEATURE'];

	const modes = $derived(
		stateMetaDerived
			.betModeMetaList()
			.filter((mode) => mode.type !== 'default')
			.sort((a, b) => ORDER.indexOf(a.mode) - ORDER.indexOf(b.mode)),
	);
	const open = $derived(stateModal.modal?.name === 'buyBonus' || stateModal.modal?.name === 'buyBonusConfirm');
	const detail = $derived(stateModal.modal?.name === 'buyBonusConfirm');
	const selected = $derived(stateBonusDerived.selectedBetModeData());
	const activeMode = $derived(stateBetDerived.activeBetMode());
	const spinModeOn = $derived(activeMode?.type === 'activate');

	const price = (costMultiplier: number) => numberToCurrencyString(stateBet.betAmount * costMultiplier);
	const affordable = (costMultiplier: number) =>
		stateBet.betAmount > 0 && stateBet.balanceAmount >= stateBet.betAmount * costMultiplier;
	const isOn = (mode: string) => spinModeOn && activeMode?.mode === mode;

	const press = () => eventEmitter.broadcast({ type: 'soundPressGeneral' });
	const close = () => (stateModal.modal = null);
	const openDetail = (mode: string) => {
		stateBonus.selectedBetModeKey = mode;
		press();
		stateModal.modal = { name: 'buyBonusConfirm' };
	};
	const buy = () => {
		stateBet.activeBetModeKey = stateBonus.selectedBetModeKey;
		press();
		eventEmitter.broadcast({ type: 'bet' });
		stateModal.modal = null;
	};
	const toggleSpinMode = () => {
		press();
		const mode = stateBonus.selectedBetModeKey;
		stateBet.activeBetModeKey = isOn(mode) ? 'BASE' : mode;
		close();
	};
</script>

{#snippet icon(mode: string)}
	{@const art = ICONS[mode] ?? { text: '★' }}
	<div class="icon" class:coin={!art.image}>
		{#if art.image}
			<img src={art.image} alt="" />
		{:else}
			<span>{art.text}</span>
		{/if}
		{#if art.tag}<b class="tag">{art.tag}</b>{/if}
	</div>
{/snippet}

{#if open}
	<OnHotkey hotkey="Escape" onpress={close} />
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="overlay" onclick={close}>
		<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
		<div class="panel" style="background-image: url({PANEL});" onclick={(event) => event.stopPropagation()}>
			<button class="close" aria-label="Close" onclick={close}></button>

			<div class="content" use:socialWording>
				{#if !detail}
					<div class="grid">
						{#each modes as mode}
							{@const on = isOn(mode.mode)}
							{@const blocked = mode.type === 'buy' && spinModeOn}
							<button
								class="tile"
								class:on
								class:spin={mode.type === 'activate'}
								disabled={blocked}
								onclick={() => openDetail(mode.mode)}
							>
								{@render icon(mode.mode)}
								<span class="info">
									<span class="title">{mode.text.title}</span>
									<span class="price">
										{price(mode.costMultiplier)}{#if mode.type === 'activate'}<small> /spin</small>{/if}
									</span>
									<span class="state">
										{#if on}ON{:else if blocked}{activeMode?.text.title} IS ON{:else}{mode.costMultiplier}x bet{/if}
									</span>
								</span>
							</button>
						{/each}
					</div>

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
					{@const spinMode = selected.type === 'activate'}
					<div class="detail">
						{@render icon(selected.mode)}
						<h2>{selected.text.title}</h2>
						<p>{selected.text.description}</p>
						<p class="small">{selected.text.dialog}</p>
						<div class="amount big">
							{price(selected.costMultiplier)}{#if spinMode}<small> per spin</small>{/if}
						</div>
						<p class="small">{selected.costMultiplier}x the bet{spinMode ? ', stays on until you switch it off' : ''}</p>
						{#if spinMode}
							<button class="gold wide" class:off={isOn(selected.mode)} onclick={toggleSpinMode}>
								{isOn(selected.mode) ? 'SWITCH OFF' : 'ACTIVATE'}
							</button>
						{:else}
							<button class="gold wide" disabled={!affordable(selected.costMultiplier)} onclick={buy}>BUY</button>
							{#if !affordable(selected.costMultiplier)}
								<p class="small warn">Not enough balance for this bet.</p>
							{/if}
						{/if}
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
		gap: 2.4cqw;
		scrollbar-width: thin;
	}
	.grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2cqw;
	}
	.tile {
		display: flex;
		align-items: center;
		gap: 1.8cqw;
		padding: 1.6cqw;
		border: 0;
		border-radius: 2.6cqw;
		background: rgba(255, 255, 255, 0.06);
		box-shadow: inset 0 0 0 0.35cqw rgba(255, 207, 58, 0.22);
		color: inherit;
		font-family: inherit;
		text-align: left;
		cursor: pointer;
		transition: transform 0.12s, background 0.12s;
	}
	.tile:hover:not(:disabled) {
		transform: translateY(-0.4cqw);
		background: rgba(255, 207, 58, 0.12);
	}
	.tile.spin {
		background: rgba(140, 90, 255, 0.1);
	}
	.tile.on {
		box-shadow: inset 0 0 0 0.5cqw #ffcf3a, 0 0 3cqw rgba(255, 190, 60, 0.4);
	}
	.tile:disabled {
		filter: grayscale(0.7) brightness(0.7);
		cursor: not-allowed;
	}
	.icon {
		position: relative;
		flex: 0 0 13cqw;
		aspect-ratio: 1;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.icon img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		filter: drop-shadow(0 0.5cqw 0.6cqw rgba(0, 0, 0, 0.5));
	}
	.icon.coin {
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #ffe680, #f4a21e 55%, #9a4a0a);
		box-shadow: 0 0 0 0.6cqw #5a2a0a, 0 0 3cqw rgba(255, 190, 60, 0.4);
		color: #4a1d06;
		font-size: 6.5cqw;
		line-height: 1;
	}
	.tag {
		position: absolute;
		right: -1cqw;
		bottom: -0.6cqw;
		padding: 0.2cqw 1cqw;
		border-radius: 1.4cqw;
		background: #5a2a0a;
		color: #ffcf3a;
		font-weight: 400;
		font-size: 2.6cqw;
	}
	.info {
		display: flex;
		flex-direction: column;
		min-width: 0;
		gap: 0.3cqw;
	}
	.title {
		color: #ffcf3a;
		font-size: 3.6cqw;
		line-height: 1.05;
		text-shadow: 0 0.3cqw 0 #5a2a0a;
	}
	.price {
		font-size: 4.2cqw;
		white-space: nowrap;
	}
	.price small {
		font-size: 2.4cqw;
		opacity: 0.8;
	}
	.state {
		font-family: Arial, Helvetica, sans-serif;
		font-weight: 700;
		font-size: 2.2cqw;
		opacity: 0.85;
	}
	.tile.on .state {
		color: #ffcf3a;
		opacity: 1;
	}
	h2 {
		margin: 0;
		color: #ffcf3a;
		font-weight: 400;
		font-size: 6.4cqw;
		line-height: 1.05;
		letter-spacing: 0.02em;
		text-shadow: 0 0.5cqw 0 #5a2a0a;
	}
	p {
		margin: 0;
		font-family: Arial, Helvetica, sans-serif;
		font-weight: 700;
		font-size: 3.2cqw;
		line-height: 1.3;
	}
	.small {
		font-size: 2.6cqw;
		opacity: 0.85;
	}
	.warn {
		color: #ff9a8a;
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
		font-size: 8.5cqw;
		color: #ffcf3a;
		text-shadow: 0 0.6cqw 0 #5a2a0a;
	}
	.amount.big small {
		font-size: 3.4cqw;
		color: #f6efe2;
		text-shadow: none;
	}
	button.gold {
		padding: 1.2cqw 0;
		border: 0.6cqw solid #5a2a0a;
		border-radius: 2.4cqw;
		background: linear-gradient(#ffe066, #f39a1c);
		color: #4a1d06;
		font-family: inherit;
		font-size: 4.8cqw;
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
	.detail {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 1.8cqw;
	}
	.detail .icon {
		flex: none;
		width: 18cqw;
	}
	.detail .icon.coin {
		font-size: 9cqw;
	}
	button.back {
		width: 34%;
		aspect-ratio: 183 / 77;
		border: 0;
		background: transparent center / 100% 100% no-repeat;
		cursor: pointer;
	}
</style>
