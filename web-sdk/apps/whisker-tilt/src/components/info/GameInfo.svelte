<script lang="ts">
	import SymbolIcon from './SymbolIcon.svelte';
	import {
		RULES,
		KEY_AWARDS,
		MIN_CLUSTER,
		COIN_VALUES,
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

	const mode = (name: string) => BET_MODES.find((m) => m.name === name)!;
	const base = mode('base');
	const MODE_NAMES: Record<string, string> = {
		base: 'Base game',
		ante: 'Catnip (double chance)',
		feature: 'Paw Spins',
		bonus: 'Snow Day buy',
		super: 'Super Snow Day buy',
		mystery: "Mitten's Gift",
		max_or_nothing: 'Off the Shelf',
	};
	const giftTotal = RULES.mysteryGifts.reduce((sum, g) => sum + g.weight, 0);
	const capOdds = (cost: number, rtp: number) => Math.round(RULES.wincap / (cost * rtp));
	const range = (from: number, to: number) => (to >= 36 ? `${from}+` : from === to ? `${from}` : `${from}–${to}`);

	const scrollToPaytable = (node: HTMLElement) => {
		if (props.start === 'payTable') node.scrollIntoView({ block: 'start' });
	};
</script>

<article class="info" use:socialWording>
	<h1>Whisker Tilt</h1>

	<section>
		<p>
			A tiny winter village lives inside a glass snow box on a toyshop shelf, and Mitten the cat can't
			stop batting it. Every time a win clears out, the box turns a quarter and everything slides toward
			the new floor. Four Edge Keepers stand on the walls of the box and multiply every win that reaches
			them.
		</p>
	</section>

	<section>
		<h2>How to win</h2>
		<p>
			Cluster pays on a 6×6 board: {MIN_CLUSTER} or more of the same symbol connected horizontally or
			vertically win. Wins of different clusters are added together. There are no wild symbols.
		</p>
		<h3>Tilt Tumble</h3>
		<p>
			Winning symbols are removed, then Mitten turns the box a quarter turn clockwise: gravity changes from
			down to left, to up, to right and back to down. All symbols slide toward the new floor and new symbols
			fall in from the opposite wall. This repeats for as long as new clusters win. Every spin in the base
			game starts with gravity pointing down. The glowing wall is always the current floor.
		</p>
		<h3>Edge Keepers</h3>
		<p>
			Each wall has a keeper with a multiplier, starting at x0 (unlit). A winning cluster is multiplied by
			the sum of the keepers on every wall it touches; a cluster touching no lit keeper pays its normal
			amount. A corner cluster can touch two walls, a large cluster three or four.
		</p>
		<h3>Snowflake Coins</h3>
		<p>
			Coins carry a value ({COIN_VALUES.map((v) => formatX(v)).join(', ')}). They are not part of clusters.
			When a coin rests against the current floor wall, that wall's keeper takes it and adds its value, and
			the gap refills. Coins against other walls wait until the box turns their wall into the floor.
		</p>
		<h3>Snowstorm</h3>
		<p>
			Every fourth quarter turn completes a full turn of the box and starts a Snowstorm: every keeper's
			value doubles (up to x{RULES.keeperCap} each). In the base game the keepers and the turn count reset
			on every spin.
		</p>
	</section>

	<section>
		<h2>Snow Day (free spins)</h2>
		<p>
			{#each KEY_AWARDS as award, i}{i > 0 ? (i === KEY_AWARDS.length - 1 ? ' or ' : ', ') : ''}{award.keys}{/each}
			Wind-up Keys anywhere on the board at the end of a spin start Snow Day:
		</p>
		<table>
			<thead><tr><th>Wind-up Keys</th><th>Free spins</th></tr></thead>
			<tbody>
				{#each KEY_AWARDS as award}
					<tr><td>{award.keys}</td><td>{award.spins}</td></tr>
				{/each}
				<tr><td>{RULES.superTrigger}+</td><td>Super Snow Day, {RULES.superSpins} spins</td></tr>
			</tbody>
		</table>
		<p>
			During free spins the keepers, the gravity and the turn count are never reset. Before each free spin
			Mitten turns the box a quarter (this counts toward Snowstorms), so the floor wall changes every spin.
			{RULES.retriggerKeys} or more Wind-up Keys during free spins award {RULES.retriggerSpins} more spins,
			up to {RULES.maxFreeSpins} spins in total.
		</p>
		<h3>Super Snow Day</h3>
		<p>
			Played like Snow Day, but all four keepers start lit at x{RULES.superStartKeeper} and Snowflake Coins
			land more often.
		</p>
	</section>

	<section use:scrollToPaytable>
		<h2>Symbol payouts</h2>
		<p>Payouts are multiples of the total bet, for the size of the cluster.</p>
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
			<div class="pay-card">
				<SymbolIcon symbol="S" />
				<div><strong>Wind-up Key</strong> — scatter. Pays nothing by itself; starts and extends free spins.</div>
			</div>
			<div class="pay-card">
				<SymbolIcon symbol="C" />
				<div><strong>Snowflake Coin</strong> — banked by the keeper of the floor wall it rests against.</div>
			</div>
		</div>
	</section>

	<section>
		<h2>Bet modes and bonus buys</h2>
		<h3>Catnip (double chance)</h3>
		<p>
			Bet <strong>{mode('ante').cost}× the bet</strong> per spin and Snow Day triggers twice as often. Wins
			are calculated on the base bet. Catnip stays on until you switch it off.
		</p>
		<h3>Paw Spins</h3>
		<p>
			Bet <strong>{mode('feature').cost}× the bet</strong> per spin. Every Paw Spin starts with all four keepers
			lit at x{RULES.featureStartKeeper} and always wins. Wind-up Keys can still start free spins. Paw Spins stay
			on until you switch them off.
		</p>
		<h3>Snow Day buy</h3>
		<p>
			Buy Snow Day for <strong>{mode('bonus').cost}× the bet</strong>, starting with 4 or 5 Wind-up Keys. Bought
			rounds always pay something.
		</p>
		<h3>Super Snow Day buy</h3>
		<p>Buy Super Snow Day for <strong>{mode('super').cost}× the bet</strong>.</p>
		<h3>Mitten's Gift</h3>
		<p>
			For <strong>{mode('mystery').cost}× the bet</strong> Mitten knocks a present off the shelf. It opens to
			show the round before it starts:
		</p>
		<table>
			<thead><tr><th>Gift</th><th>Chance</th></tr></thead>
			<tbody>
				{#each RULES.mysteryGifts as gift}
					<tr>
						<td>{gift.kind === 'super' ? 'Super Snow Day' : 'Snow Day'}, {gift.spins} spins</td>
						<td>{Math.round((gift.weight / giftTotal) * 100)}%</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<h3>Off the Shelf (max or nothing)</h3>
		<p>
			For <strong>{mode('max_or_nothing').cost}× the bet</strong> Mitten pushes the box to the edge of the shelf
			and a Super Snow Day is played. Wins during this round are not paid: they crack the glass instead. If
			the round reaches the maximum win of {formatX(RULES.wincap)} the bet, the box shatters and pays
			{formatX(RULES.wincap)}; otherwise the round pays <strong>nothing</strong>. On average the box shatters
			about once in {capOdds(mode('max_or_nothing').cost, mode('max_or_nothing').rtp)} rounds.
		</p>
		<p>Buys and Paw Spins are not available while Catnip is on, and vice versa.</p>
	</section>

	<section>
		<h2>General rules</h2>
		<table>
			<thead><tr><th>Mode</th><th>Cost</th><th>RTP</th><th>Maximum win</th></tr></thead>
			<tbody>
				{#each BET_MODES as m}
					<tr>
						<td>{MODE_NAMES[m.name] ?? m.name}</td>
						<td>{formatX(m.cost)}</td>
						<td>{formatRtp(m.rtp)}</td>
						<td>{formatX(m.maxWin)}</td>
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
			<li><strong>Buy bonus</strong> — open the bonus menu: buy a bonus or switch Catnip or Paw Spins on.</li>
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
