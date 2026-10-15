// Offline demo RGS: answers the game's /wallet and /bet requests in the page,
// drawing rounds from window.__DEMO_BOOKS__ (sampled from the real books by weight).
// Play money only. Not part of the Stake release build.
(() => {
	const M = 1000000;
	const BOOKS = window.__DEMO_BOOKS__;
	const COST = window.__DEMO_COSTS__ || { base: 1, bonus: 100 };
	// ?demoBook=<mode>:<id> plays that book on the next round of that mode (testing)
	const forced = new URLSearchParams(location.search).get('demoBook');
	let balance = 1000 * M;
	let round = null;

	const json = (body) => new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } });
	const bal = () => ({ amount: balance, currency: 'USD' });
	const levels = [0.1, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.6, 2, 2.4, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 50, 100].map((v) => Math.round(v * M));

	const handlers = {
		'/wallet/authenticate': () => ({
			balance: bal(),
			config: {
				betLevels: levels,
				defaultBetLevel: M,
				betModes: {},
				jurisdiction: {
					socialCasino: false, disabledFullscreen: false, disabledTurbo: false, disabledSuperTurbo: false,
					disabledAutoplay: false, disabledSlamstop: false, disabledSpacebar: false, disabledBuyFeature: false,
					displayNetPosition: false, displayRTP: false, displaySessionTimer: false, minimumRoundDuration: 0,
				},
			},
		}),
		'/wallet/play': (req) => {
			const mode = String(req.mode || 'base').toLowerCase();
			const set = BOOKS[mode] || BOOKS.base;
			const cost = req.amount * (COST[mode] || 1);
			if (cost > balance) {
				balance = 1000 * M; // demo top-up instead of an error
			}
			balance -= cost;
			let id = set.picks[Math.floor(Math.random() * set.picks.length)];
			if (forced && forced.startsWith(`${mode}:`) && set.books[forced.split(':')[1]]) id = forced.split(':')[1];
			const book = set.books[id];
			const payoutMultiplier = book.p / 100;
			round = { roundID: Date.now(), amount: req.amount, payout: Math.round(req.amount * payoutMultiplier), payoutMultiplier, active: payoutMultiplier > 0, mode: req.mode, event: null, state: book.e };
			return { balance: bal(), round };
		},
		'/wallet/end-round': () => {
			if (round) balance += round.payout;
			round = null;
			return { balance: bal() };
		},
		'/bet/event': (req) => ({ event: req.event }),
	};

	const realFetch = window.fetch.bind(window);
	window.fetch = async (input, init) => {
		const url = typeof input === 'string' ? input : input.url;
		const path = Object.keys(handlers).find((p) => url.includes(p));
		if (!path) return realFetch(input, init);
		const body = init && init.body ? JSON.parse(init.body) : {};
		return json(handlers[path](body));
	};
})();
