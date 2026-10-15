<!--
	Bonus menu ("BONUS GAMES"): one card per real mode (game/betModeMeta.ts) in a row,
	like a feature-buy shop. Each card has a header picture, a volatility meter, the price
	at the current bet and a button: BUY for the bonus buys (Haunted Raid, Super Bonus,
	Mystery Bonus, Max or Nothing; they ask for confirmation first) and ACTIVATE / ON for
	the spin modes that stay on (Double Chance, Feature Spin). Tapping the picture shows
	the mode's description. Underneath: balance, and the bet with ‹ › arrows and a slider.

	Sizes use a card unit (--cw = 1/100 of a card's width) so the layout scales with the
	panel: 6 cards in a row on wide screens, 3 x 2 on narrow ones.
-->
<script lang="ts">
	import '@fontsource/lilita-one/400.css';

	import { OnHotkey } from 'components-shared';
	import { stateBet, stateConfig, stateModal, stateMetaDerived, stateBetDerived } from 'state-shared';
	import { getContextEventEmitter } from 'utils-event-emitter';
	import { numberToCurrencyString } from 'utils-shared/amount';
	import { stateBonus, stateBonusDerived } from 'components-ui-html/src/stateBonus.svelte';
	import type { EmitterEventModal } from 'components-ui-html';

	import { socialWording } from '../../game/social';

	const { eventEmitter } = getContextEventEmitter<EmitterEventModal>();

	// literal paths so Vite can resolve them
	const ICON_CAN = new URL('../../../assets/ui/icon_s.webp', import.meta.url).href;
	const ICON_CAP = new URL('../../../assets/ui/icon_m.webp', import.meta.url).href;
	const ICON_DUKE = new URL('../../../assets/ui/icon_h1.webp', import.meta.url).href;

	type Look = { images: string[]; badge?: string; text?: string; sky: string; volatility: number };
	const LOOK: Record<string, Look> = {
		ANTE: { images: [ICON_CAN, ICON_CAN], badge: '2×', sky: '#6a3fb5, #2b1450', volatility: 2 },
		FEATURE: { images: [ICON_CAN, ICON_CAN, ICON_CAN], badge: 'CAP', sky: '#7b3f9e, #2b1450', volatility: 3 },
		BONUS: { images: [ICON_CAN], sky: '#b8641c, #3b1648', volatility: 3 },
		SUPER: { images: [ICON_CAP], badge: 'x10', sky: '#c23a5c, #3b1648', volatility: 3 },
		MYSTERY: { images: [], text: '?', sky: '#2f7a8f, #1d1033', volatility: 4 },
		MAX: { images: [ICON_DUKE], badge: 'MAX', sky: '#d1a21c, #4a1d06', volatility: 5 },
	};
	const ORDER = ['ANTE', 'FEATURE', 'BONUS', 'SUPER', 'MYSTERY', 'MAX'];

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
	const betOptions = $derived(stateConfig.betAmountOptions);
	const betIndex = $derived(Math.max(0, betOptions.indexOf(stateBet.betAmount)));

	const price = (costMultiplier: number) => numberToCurrencyString(stateBet.betAmount * costMultiplier);
	const affordable = (costMultiplier: number) =>
		stateBet.betAmount > 0 && stateBet.balanceAmount >= stateBet.betAmount * costMultiplier;
	const isOn = (mode: string) => spinModeOn && activeMode?.mode === mode;

	const press = () => eventEmitter.broadcast({ type: 'soundPressGeneral' });
	const close = () => (stateModal.modal = null);
	const setBet = (index: number) => {
		const value = betOptions[Math.max(0, Math.min(betOptions.length - 1, index))];
		if (value !== undefined && value !== stateBet.betAmount) {
			stateBet.betAmount = value;
			press();
		}
	};
	const showDetail = (mode: string) => {
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
	const toggleSpinMode = (mode: string) => {
		press();
		stateBet.activeBetModeKey = isOn(mode) ? 'BASE' : mode;
		close();
	};
</script>

{#snippet art(mode: string, big = false)}
	{@const look = LOOK[mode] ?? { images: [], text: '★', sky: '#6a3fb5, #2b1450', volatility: 3 }}
	<div class="art" class:big style="--sky: {look.sky}">
		<div class="rays"></div>
		<div class="stack">
			{#each look.images as image, i}
				<img src={image} alt="" style="--i: {i - (look.images.length - 1) / 2}" />
			{/each}
			{#if look.text}<span class="mark">{look.text}</span>{/if}
		</div>
		{#if look.badge}<b class="badge">{look.badge}</b>{/if}
	</div>
{/snippet}

{#snippet meter(mode: string)}
	{@const level = LOOK[mode]?.volatility ?? 3}
	<div class="meter">
		<span>VOLATILITY</span>
		<span class="bar">
			{#each [1, 2, 3, 4, 5] as step}<i class:lit={step <= level} class:hot={level >= 5}></i>{/each}
		</span>
	</div>
{/snippet}

{#if open}
	<OnHotkey hotkey="Escape" onpress={close} />
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="overlay" onclick={close}>
		<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
		<div class="panel" onclick={(event) => event.stopPropagation()} use:socialWording>
			<div class="inner">
			<header>
				<h1>BONUS GAMES</h1>
				<button class="close" aria-label="Close" onclick={close}>✕</button>
			</header>

			{#if !detail}
				<div class="cards">
					{#each modes as mode}
						{@const on = isOn(mode.mode)}
						{@const blocked = mode.type === 'buy' && spinModeOn}
						<div class="card" class:on class:blocked>
							<button class="pic" onclick={() => showDetail(mode.mode)} aria-label="About {mode.text.title}">
								<span class="title">{mode.text.title}</span>
								{@render art(mode.mode)}
							</button>
							<div class="foot">
								{@render meter(mode.mode)}
								<div class="price">
									{price(mode.costMultiplier)}{#if mode.type === 'activate'}<small>/spin</small>{/if}
								</div>
								{#if mode.type === 'activate'}
									<button class="act" class:on onclick={() => toggleSpinMode(mode.mode)}>
										{on ? 'ON' : 'ACTIVATE'}
									</button>
								{:else}
									<button
										class="buy"
										disabled={blocked || !affordable(mode.costMultiplier)}
										onclick={() => showDetail(mode.mode)}
									>
										BUY
									</button>
								{/if}
							</div>
						</div>
					{/each}
				</div>

				<div class="wallet">
					<div class="stat">
						<span class="tag">BALANCE</span>
						<span class="value">{numberToCurrencyString(stateBet.balanceAmount)}</span>
					</div>
					<button class="chev" disabled={betIndex <= 0} onclick={() => setBet(betIndex - 1)} aria-label="Lower bet">‹</button>
					<div class="stat">
						<span class="tag">BET</span>
						<span class="value">{numberToCurrencyString(stateBet.betAmount)}</span>
					</div>
					<button
						class="chev"
						disabled={betIndex >= betOptions.length - 1}
						onclick={() => setBet(betIndex + 1)}
						aria-label="Raise bet">›</button
					>
					<input
						class="slider"
						type="range"
						min="0"
						max={Math.max(0, betOptions.length - 1)}
						value={betIndex}
						style="--fill: {betOptions.length > 1 ? (betIndex / (betOptions.length - 1)) * 100 : 0}%"
						oninput={(event) => setBet(Number((event.target as HTMLInputElement).value))}
						aria-label="Bet"
					/>
				</div>
			{:else}
				{@const spinMode = selected.type === 'activate'}
				<div class="detail">
					{@render art(selected.mode, true)}
					<div class="text">
						<h2>{selected.text.title}</h2>
						<p>{selected.text.description}</p>
						{@render meter(selected.mode)}
						<p class="small">{selected.text.dialog}</p>
						<div class="price big">
							{price(selected.costMultiplier)}{#if spinMode}<small> per spin</small>{/if}
						</div>
						<p class="small">
							{selected.costMultiplier}x the bet{spinMode ? ', stays on until you switch it off' : ''}
						</p>
						<div class="actions">
							<button class="back" onclick={() => (stateModal.modal = { name: 'buyBonus' })}>BACK</button>
							{#if spinMode}
								<button class="act" class:on={isOn(selected.mode)} onclick={() => toggleSpinMode(selected.mode)}>
									{isOn(selected.mode) ? 'SWITCH OFF' : 'ACTIVATE'}
								</button>
							{:else}
								<button
									class="buy"
									disabled={spinModeOn || !affordable(selected.costMultiplier)}
									onclick={buy}
								>
									CONFIRM BUY
								</button>
							{/if}
						</div>
						{#if !spinMode && spinModeOn}
							<p class="small warn">Switch off {activeMode?.text.title} to buy.</p>
						{:else if !spinMode && !affordable(selected.costMultiplier)}
							<p class="small warn">Not enough balance for this bet.</p>
						{/if}
					</div>
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
		background: rgba(8, 4, 20, 0.75);
		font-family: 'Lilita One', 'Arial Black', sans-serif;
		color: #f6efe2;
	}
	/* the panel is the size container; everything inside is measured in --u, one
	   hundredth of a card's width (6 cards per row, or 3 on tall screens) */
	.panel {
		container-type: inline-size;
		position: relative;
		width: min(96vw, 1320px, 170vh);
		max-height: 96vh;
		overflow-y: auto;
		box-sizing: border-box;
		border-radius: 18px;
		background: linear-gradient(#2a1745, #170b2a);
		border: 4px solid #f2b33d;
		box-shadow: 0 0 0 3px #2a1208, 0 10px 40px rgba(0, 0, 0, 0.7);
		scrollbar-width: thin;
	}
	.inner {
		--cw: calc(100cqw / 6.9);
		--u: calc(var(--cw) / 100);
		padding: calc(var(--u) * 14) calc(var(--u) * 16);
	}
	@media (max-aspect-ratio: 1/1) {
		.panel {
			width: min(96vw, 600px);
		}
		.inner {
			--cw: calc(100cqw / 3.45);
		}
	}
	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: calc(var(--u) * 12);
	}
	h1 {
		margin: 0;
		font-weight: 400;
		font-size: calc(var(--u) * 26);
		color: #ffcf3a;
		text-shadow: 0 calc(var(--u) * 2.5) 0 #5a2a0a;
		border-bottom: calc(var(--u) * 3) solid #c23a8a;
		padding-bottom: calc(var(--u) * 2);
	}
	.close {
		width: calc(var(--u) * 34);
		height: calc(var(--u) * 34);
		border-radius: 50%;
		border: calc(var(--u) * 2.5) solid #f2b33d;
		background: #1d1033;
		color: #ffcf3a;
		font-size: calc(var(--u) * 16);
		cursor: pointer;
	}
	.cards {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: calc(var(--u) * 10);
	}
	@media (max-aspect-ratio: 1/1) {
		.cards {
			grid-template-columns: repeat(3, 1fr);
		}
	}
	.card {
		display: flex;
		flex-direction: column;
		border-radius: calc(var(--u) * 10);
		border: calc(var(--u) * 3) solid #f2b33d;
		background: #120822;
		overflow: hidden;
		box-shadow: 0 calc(var(--u) * 4) 0 #2a1208;
		transition: transform 0.12s;
	}
	.card:hover {
		transform: translateY(calc(var(--u) * -3));
	}
	.card.on {
		border-color: #ffe27a;
		box-shadow: 0 0 calc(var(--u) * 14) rgba(255, 190, 60, 0.6), 0 calc(var(--u) * 4) 0 #2a1208;
	}
	.card.blocked {
		filter: grayscale(0.7) brightness(0.7);
	}
	.pic {
		position: relative;
		padding: 0;
		border: 0;
		background: none;
		color: inherit;
		font-family: inherit;
		cursor: pointer;
	}
	.title {
		position: absolute;
		z-index: 2;
		top: calc(var(--u) * 5);
		left: 0;
		right: 0;
		font-size: calc(var(--u) * 12.5);
		line-height: 1;
		text-shadow: 0 calc(var(--u) * 1.5) 0 #2a1208, 0 0 calc(var(--u) * 4) #000;
	}
	.art {
		position: relative;
		aspect-ratio: 1 / 0.82;
		overflow: hidden;
		background: radial-gradient(circle at 50% 60%, var(--sky));
		border-bottom: calc(var(--u) * 3) solid #f2b33d;
	}
	.art.big {
		width: 100%;
		border: calc(var(--u) * 3) solid #f2b33d;
		border-radius: calc(var(--u) * 10);
	}
	.rays {
		position: absolute;
		inset: -50%;
		background: repeating-conic-gradient(rgba(255, 220, 120, 0.16) 0 8deg, transparent 8deg 22deg);
		animation: spin 18s linear infinite;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	.stack {
		position: absolute;
		inset: 18% 0 0 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.stack img {
		position: absolute;
		width: 52%;
		transform: translateX(calc(var(--i) * 46%)) rotate(calc(var(--i) * 10deg)) scale(calc(1 - (var(--i) * var(--i)) * 0.12));
		filter: drop-shadow(0 calc(var(--u) * 3) calc(var(--u) * 3) rgba(0, 0, 0, 0.55));
	}
	.mark {
		font-size: calc(var(--u) * 58);
		color: #ffcf3a;
		text-shadow: 0 calc(var(--u) * 4) 0 #5a2a0a, 0 0 calc(var(--u) * 20) rgba(255, 207, 58, 0.6);
	}
	.badge {
		position: absolute;
		left: calc(var(--u) * 6);
		bottom: calc(var(--u) * 6);
		padding: calc(var(--u) * 1) calc(var(--u) * 6);
		border-radius: calc(var(--u) * 6);
		background: #c23a8a;
		color: #fff;
		font-weight: 400;
		font-size: calc(var(--u) * 13);
		box-shadow: 0 calc(var(--u) * 2) 0 #4a0d2e;
	}
	.foot {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: calc(var(--u) * 5);
		padding: calc(var(--u) * 7) calc(var(--u) * 8) calc(var(--u) * 9);
	}
	.meter {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		font-family: Arial, Helvetica, sans-serif;
		font-weight: 700;
		gap: calc(var(--u) * 4);
		font-size: calc(var(--u) * 6.5);
		letter-spacing: 0.06em;
		color: #c9bde0;
	}
	.text .meter {
		width: fit-content;
		gap: calc(var(--u) * 8);
		font-size: calc(var(--u) * 9);
	}
	.bar {
		display: flex;
		gap: calc(var(--u) * 1.5);
		padding: calc(var(--u) * 2);
		border-radius: calc(var(--u) * 6);
		border: calc(var(--u) * 1.5) solid #c9bde0;
	}
	.bar i {
		width: calc(var(--u) * 7);
		height: calc(var(--u) * 6);
		border-radius: calc(var(--u) * 1.5);
		background: #2c1d44;
	}
	.bar i.lit {
		background: #f4a21e;
	}
	.bar i.lit.hot {
		background: #ff4d5e;
	}
	.price {
		font-size: calc(var(--u) * 19);
		white-space: nowrap;
	}
	.price small {
		font-size: calc(var(--u) * 9);
		opacity: 0.8;
	}
	.price.big {
		font-size: calc(var(--u) * 28);
		color: #ffcf3a;
		text-shadow: 0 calc(var(--u) * 2.5) 0 #5a2a0a;
	}
	button.buy,
	button.act,
	button.back {
		width: 100%;
		padding: calc(var(--u) * 6) 0;
		border-radius: calc(var(--u) * 7);
		font-family: inherit;
		font-size: calc(var(--u) * 14);
		cursor: pointer;
	}
	button.buy {
		border: calc(var(--u) * 2.5) solid #5a2a0a;
		background: linear-gradient(#ffe066, #f39a1c);
		color: #4a1d06;
		box-shadow: 0 calc(var(--u) * 3) 0 #5a2a0a;
	}
	button.act {
		border: calc(var(--u) * 2.5) solid #2a0f4a;
		background: linear-gradient(#b48cff, #7a3fe0);
		color: #fff;
		box-shadow: 0 calc(var(--u) * 3) 0 #2a0f4a;
	}
	button.act.on {
		background: linear-gradient(#ffe27a, #f4a21e);
		color: #4a1d06;
		border-color: #5a2a0a;
	}
	button.back {
		border: calc(var(--u) * 2.5) solid #f2b33d;
		background: #1d1033;
		color: #ffcf3a;
	}
	button:disabled {
		filter: grayscale(0.85) brightness(0.65);
		cursor: not-allowed;
	}
	.wallet {
		display: grid;
		grid-template-columns: auto auto auto auto;
		grid-template-areas: 'bal down bet up' 'slider slider slider slider';
		align-items: center;
		justify-content: center;
		column-gap: calc(var(--u) * 16);
		row-gap: calc(var(--u) * 8);
		width: fit-content;
		margin: calc(var(--u) * 14) auto 0;
		padding: calc(var(--u) * 10) calc(var(--u) * 24);
		border-radius: calc(var(--u) * 12);
		border: calc(var(--u) * 3) solid #f2b33d;
		background: #120822;
	}
	.wallet .stat:first-child {
		grid-area: bal;
		margin-right: calc(var(--u) * 20);
	}
	.stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: calc(var(--u) * 3);
	}
	.tag {
		padding: calc(var(--u) * 1.5) calc(var(--u) * 10);
		border-radius: calc(var(--u) * 5);
		border: calc(var(--u) * 1.5) solid #f2b33d;
		background: #1d1033;
		color: #ffcf3a;
		font-size: calc(var(--u) * 11);
	}
	.value {
		font-size: calc(var(--u) * 20);
	}
	.chev {
		border: 0;
		background: none;
		color: #ffcf3a;
		font-family: Arial, Helvetica, sans-serif;
		font-weight: 900;
		font-size: calc(var(--u) * 42);
		line-height: 1;
		cursor: pointer;
		text-shadow: 0 calc(var(--u) * 2) 0 #5a2a0a;
	}
	.slider {
		grid-area: slider;
		width: 100%;
		height: calc(var(--u) * 8);
		appearance: none;
		border-radius: calc(var(--u) * 6);
		background: linear-gradient(90deg, #c23a8a, #ff6fb5) 0 / var(--fill, 0%) 100% no-repeat, #2c1d44;
		cursor: pointer;
	}
	.slider::-webkit-slider-thumb {
		appearance: none;
		width: calc(var(--u) * 18);
		height: calc(var(--u) * 18);
		border-radius: 50%;
		background: #fff3c4;
		border: calc(var(--u) * 3) solid #5a2a0a;
	}
	.slider::-moz-range-thumb {
		width: calc(var(--u) * 14);
		height: calc(var(--u) * 14);
		border-radius: 50%;
		background: #fff3c4;
		border: calc(var(--u) * 3) solid #5a2a0a;
	}
	.detail {
		display: grid;
		grid-template-columns: 1fr 1.4fr;
		gap: calc(var(--u) * 20);
		align-items: center;
		max-width: calc(var(--cw) * 4.4);
		margin: 0 auto;
	}
	@media (max-aspect-ratio: 1/1) {
		.detail {
			grid-template-columns: 1fr;
			max-width: none;
		}
	}
	.text {
		display: flex;
		flex-direction: column;
		gap: calc(var(--u) * 8);
		text-align: left;
	}
	h2 {
		margin: 0;
		font-weight: 400;
		font-size: calc(var(--u) * 26);
		color: #ffcf3a;
		text-shadow: 0 calc(var(--u) * 2.5) 0 #5a2a0a;
	}
	p {
		margin: 0;
		font-family: Arial, Helvetica, sans-serif;
		font-weight: 700;
		font-size: calc(var(--u) * 12);
		line-height: 1.35;
	}
	.small {
		font-size: calc(var(--u) * 10);
		opacity: 0.85;
	}
	.warn {
		color: #ff9a8a;
		opacity: 1;
	}
	.actions {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: calc(var(--u) * 10);
	}
</style>
