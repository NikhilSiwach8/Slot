<script lang="ts">
	import SymbolIcon from './SymbolIcon.svelte';
	import {
		SCATTER_AWARDS,
		RETRIGGER,
		MIN_CLUSTER,
		CAP_VALUES,
		SYMBOL_NAMES,
		PAYING_SYMBOLS,
		BET_MODES,
		getPayGroups,
		formatRtp,
		formatX,
	} from '../../game/rules';
	import { socialWording } from '../../game/social';

	type Props = { start?: 'rules' | 'payTable' };
	const props: Props = $props();

	const base = BET_MODES.find((mode) => mode.name === 'base')!;
	const ante = BET_MODES.find((mode) => mode.name === 'ante');
	const buy = BET_MODES.find((mode) => mode.buyBonus);
	const feature = BET_MODES.find((mode) => mode.name === 'feature');
	const superRaid = BET_MODES.find((mode) => mode.name === 'super');
	const mystery = BET_MODES.find((mode) => mode.name === 'mystery');
	const maxOrNothing = BET_MODES.find((mode) => mode.name === 'max');
	const MODE_NAMES: Record<string, string> = {
		base: 'Base game',
		ante: 'Double Chance',
		feature: 'Feature Spin',
		bonus: 'Bonus buy (Haunted Raid)',
		super: 'Super Bonus',
		mystery: 'Mystery Bonus',
		max: 'Max or Nothing',
	};
	const retrigger = RETRIGGER[0];
	const range = (from: number, to: number) => (to >= 30 ? `${from}+` : from === to ? `${from}` : `${from}–${to}`);

	const scrollToPaytable = (node: HTMLElement) => {
		if (props.start === 'payTable') node.scrollIntoView({ block: 'start' });
	};
</script>

<article class="info" use:socialWording>
	<h1>Dumpster Duke</h1>

	<section>
		<h2>About the game</h2>
		<p>
			The Dumpster Duke, a grinning, slime-dripping vampire dumpster, rules the junkyard after dark with his alley crew. Land
			{MIN_CLUSTER} or more matching symbols anywhere on the 6×5 screen to win, tumble for more wins,
			and lead the <strong>Haunted Raid</strong> to fill the Duke's <strong>Trick-or-Treat Bag</strong>.
		</p>
	</section>

	<section>
		<h2>Features</h2>
		<h3>Tumble</h3>
		<p>
			After every win the winning symbols are removed and the remaining symbols fall down. New
			symbols drop in from above. Tumbling continues until there are no new wins. All wins from one
			spin are added together.
		</p>
		<h3>Candy Caps</h3>
		<p>
			Candy Cap multipliers can land in the base game and the Haunted Raid and stay on screen
			while symbols tumble. In the base game, when a spin wins, the values of all Candy Caps on
			screen are added together and the total win of the spin is multiplied by that sum.
		</p>
		<h3>Haunted Raid (free spins)</h3>
		<p>
			{#each SCATTER_AWARDS as award, i}{i > 0 ? (i === SCATTER_AWARDS.length - 1 ? ' or ' : ', ') : ''}{award.scatters}{/each}
			Cursed Trash Cans anywhere trigger the Haunted Raid:
		</p>
		<table>
			<thead><tr><th>Cursed Trash Cans</th><th>Free spins</th></tr></thead>
			<tbody>
				{#each SCATTER_AWARDS as award}
					<tr><td>{award.scatters}</td><td>{award.spins}</td></tr>
				{/each}
			</tbody>
		</table>
		<p>
			The raid starts with an empty <strong>Trick-or-Treat Bag</strong>. When a free spin wins, every Candy Cap
			on screen is added to the Trick-or-Treat Bag and the win of that spin is multiplied by the whole Trick-or-Treat Bag
			total. The Trick-or-Treat Bag is never reset during the raid, so later wins are multiplied by everything
			collected so far, even when no new Candy Cap lands.
		</p>
		<p>
			{retrigger.scatters} or more Cursed Trash Cans during the raid award {retrigger.spins} more free
			spins.
		</p>
	</section>

	<section use:scrollToPaytable>
		<h2>Symbol payouts</h2>
		<p>Payouts are multiples of the total bet, for the number of matching symbols anywhere on screen.</p>
		<div class="paytable">
			{#each PAYING_SYMBOLS as symbol}
				<div class="pay-card">
					<SymbolIcon {symbol} />
					<div class="pays">
						<div class="name">{SYMBOL_NAMES[symbol]}</div>
						{#each getPayGroups(symbol) as group}
							<div class="pay-row">
								<span>{range(group.from, group.to)}</span><span>{formatX(group.pay)}</span>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</section>

	<section>
		<h2>Special symbols</h2>
		<div class="special">
			<SymbolIcon symbol="S" />
			<p>
				<strong>Cursed Trash Can</strong> — scatter. Pays nothing by itself; triggers and retriggers
				the Haunted Raid.
			</p>
		</div>
		<div class="special">
			<SymbolIcon symbol="M" />
			<p>
				<strong>Candy Cap</strong> — multiplier. Possible values:
				{CAP_VALUES.map((value) => formatX(value)).join(', ')}.
			</p>
		</div>
	</section>

	<section>
		<h2>How to win</h2>
		<p>
			Pay anywhere: {MIN_CLUSTER} or more of the same symbol anywhere on screen win. Symbols do not need
			to be adjacent or on a line. Each symbol pays once per tumble, for the total number of that
			symbol on screen; wins of different symbols are added together. There are no wild symbols.
		</p>
	</section>

	<section>
		<h2>Bonus buy</h2>
		{#if buy}
			<p>
				Buy the Haunted Raid for <strong>{buy.cost}× the bet</strong>. The bought round starts with
				4, 5 or 6 Cursed Trash Cans and is then played exactly like a triggered raid. Bought raids always pay something. RTP of the bonus buy: {formatRtp(buy.rtp)}. Maximum win:
				{formatX(buy.maxWin)} the bet.
			</p>
		{:else}
			<p>Not available in this game.</p>
		{/if}
	</section>

	{#if ante}
		<section>
			<h2>Double Chance</h2>
			<p>
				Switch on Double Chance in the bonus menu to bet <strong>{ante.cost}× the bet</strong> per spin. While
				it is on, the Haunted Raid triggers twice as often as in the base game. Base-game wins are a little
				less frequent to balance the extra raids. Wins are calculated on the base bet. RTP with
				Double Chance: {formatRtp(ante.rtp)}. Maximum win: {formatX(ante.maxWin)} the bet. Double Chance stays
				on until you switch it off; the bonus buy is not available while it is on.
			</p>
		</section>
	{/if}

	{#if feature}
		<section>
			<h2>Feature Spin</h2>
			<p>
				Switch on Feature Spin in the bonus menu to play at <strong>{feature.cost}× the bet</strong> per spin.
				Every spin lands 3 Cursed Trash Cans and at least one Candy Cap; one more Cursed Trash Can (landing
				in a tumble) starts the Haunted Raid. RTP: {formatRtp(feature.rtp)}. Maximum win: {formatX(feature.maxWin)}
				the bet. Feature Spin stays on until you switch it off.
			</p>
		</section>
	{/if}

	{#if superRaid || mystery || maxOrNothing}
		<section>
			<h2>More bonus buys</h2>
			{#if superRaid}
				<p>
					<strong>Super Bonus — {superRaid.cost}× the bet.</strong> A Haunted Raid where the Trick-or-Treat Bag starts at
					x10 and every free spin lands at least one Candy Cap. RTP: {formatRtp(superRaid.rtp)}. Maximum win:
					{formatX(superRaid.maxWin)} the bet.
				</p>
			{/if}
			{#if mystery}
				<p>
					<strong>Mystery Bonus — {mystery.cost}× the bet.</strong> A chest reveals the raid before it starts:
					5 to 25 free spins and a starting Trick-or-Treat Bag from x0 to x20, chosen at random. RTP:
					{formatRtp(mystery.rtp)}. Maximum win: {formatX(mystery.maxWin)} the bet.
				</p>
			{/if}
			{#if maxOrNothing}
				<p>
					<strong>Max or Nothing — {maxOrNothing.cost}× the bet.</strong> A single spin with no free spins.
					If the spin wins anything at all, the win is boosted straight to the maximum win of
					{formatX(maxOrNothing.maxWin)} the bet; if it does not win, it pays nothing. Cursed Trash Cans do not
					trigger the Haunted Raid on this spin. On average about
					1 in {(maxOrNothing.maxWin / (maxOrNothing.rtp * maxOrNothing.cost)).toFixed(1)} of these spins pays.
					RTP: {formatRtp(maxOrNothing.rtp)}.
				</p>
			{/if}
			<p>Bonus buys are not available while Double Chance or Feature Spin is on.</p>
		</section>
	{/if}

	<section>
		<h2>General rules</h2>
		<table>
			<thead><tr><th>Mode</th><th>Cost</th><th>RTP</th><th>Maximum win</th></tr></thead>
			<tbody>
				{#each BET_MODES as mode}
					<tr>
						<td>{MODE_NAMES[mode.name] ?? mode.name}</td>
						<td>{formatX(mode.cost)}</td>
						<td>{formatRtp(mode.rtp)}</td>
						<td>{formatX(mode.maxWin)}</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<p>
			The theoretical return to player of the game is {formatRtp(base.rtp)}. If a round reaches the
			maximum win of {formatX(base.maxWin)} the bet, the round ends immediately and the maximum win is
			paid. Each round is independent of previous rounds.
		</p>
	</section>

	<section>
		<h2>Additional information</h2>
		<ul>
			<li><strong>Bet</strong> (or the space bar) — play one round at the selected bet.</li>
			<li><strong>+ / −</strong> — change the bet. Available bet levels are set by the casino.</li>
			<li><strong>Auto spin</strong> — play several rounds automatically after you confirm the settings.</li>
			<li><strong>Turbo</strong> — faster animations; results are unchanged.</li>
			<li><strong>Buy bonus</strong> — open the bonus menu: buy a bonus, or switch Double Chance or Feature Spin on. While one of them is on, this button switches it off.</li>
			<li><strong>Menu</strong> — rules, paytable, sound and settings. Sound can be muted at any time.</li>
		</ul>
	</section>

	<section>
		<h2>Disclaimer</h2>
		<p class="disclaimer">
			Malfunction voids all wins and plays. A consistent internet connection is required. In the
			event of a disconnection, reload the game to finish any uncompleted rounds. The expected return
			is calculated over many plays. The game display is not representative of any physical device
			and is for illustrative purposes only. Winnings are settled according to the amount received
			from the Remote Game Server and not from events within the web browser. TM and © 2025 Stake
			Engine.
		</p>
	</section>

	<section>
		<h2>Credits</h2>
		<p class="disclaimer">
			Music: "Silly Intro" by Alexander Nakarada (serpentsoundstudios.com), licensed under Creative
			Commons Attribution 4.0 (CC BY 4.0).
		</p>
	</section>
</article>

<style>
	.info {
		max-width: 46rem;
		width: 100%;
		text-align: left;
		color: #fff6e6;
		font-family: Arial, Helvetica, sans-serif;
		line-height: 1.45;
		padding: 0 1rem 2rem;
		box-sizing: border-box;
	}
	h1 {
		text-align: center;
		color: #ffcf3a;
		margin: 0.5rem 0 1rem;
	}
	h2 {
		color: #ffcf3a;
		border-bottom: 2px solid rgba(255, 207, 58, 0.35);
		padding-bottom: 0.25rem;
		margin-top: 1.75rem;
	}
	h3 {
		color: #7fe3df;
		margin: 1rem 0 0.25rem;
	}
	table {
		border-collapse: collapse;
		margin: 0.5rem 0;
	}
	th,
	td {
		border: 1px solid rgba(255, 255, 255, 0.2);
		padding: 0.3rem 0.8rem;
		text-align: center;
	}
	.paytable {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr));
		gap: 0.75rem;
	}
	.pay-card {
		display: flex;
		gap: 0.75rem;
		align-items: center;
		background: rgba(255, 255, 255, 0.06);
		border-radius: 0.75rem;
		padding: 0.5rem 0.75rem;
	}
	.pays {
		flex: 1;
	}
	.name {
		font-weight: bold;
		margin-bottom: 0.2rem;
	}
	.pay-row {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		font-size: 0.95em;
	}
	.special {
		display: flex;
		gap: 1rem;
		align-items: center;
	}
	.disclaimer {
		font-size: 0.85em;
		opacity: 0.85;
	}
</style>
