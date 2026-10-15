// Stake.us (social casino) wording. When the game is launched with social=true,
// restricted phrases must not appear anywhere in the UI or rules.
import { stateUrlDerived } from 'state-shared';

// Longest phrases first so "bonus buy" wins over "buy", "total bet" over "bet", etc.
const REPLACEMENTS: [string, string][] = [
	['be awarded to player\'s accounts', 'appear in player\'s accounts'],
	['place your bets', 'come and play'],
	['at the cost of', 'for'],
	['cost of', 'can be played for'],
	['win feature', 'play feature'],
	['loss streak', 'miss streak'],
	['loss limit', 'stop limit'],
	['bonus buy', 'bonus'],
	['buy bonus', 'get bonus'],
	['pay table', 'win table'],
	['paytable', 'win table'],
	['pays out', 'win'],
	['paid out', 'won'],
	['pay out', 'win'],
	['total bet', 'total play'],
	['bet/s', 'play/s'],
	['betting', 'playing'],
	['bets', 'plays'],
	['bet', 'play'],
	['bought', 'instantly triggered'],
	['purchase', 'play'],
	['buy', 'play'],
	['cash', 'coins'],
	['credit', 'coins'],
	['currency', 'token'],
	['deposit', 'get coins'],
	['gamble', 'play'],
	['money', 'coins'],
	['paid', 'won'],
	['payouts', 'wins'],
	['payout', 'win'],
	['payer', 'winner'],
	['pays', 'wins'],
	['pay', 'win'],
	['profit', 'net gain'],
	['rebet', 'respin'],
	['stake', 'play amount'],
	['wager', 'play'],
	['withdraw', 'redeem'],
];

const escape = (text: string) => text.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
const PATTERN = new RegExp(`\\b(${REPLACEMENTS.map(([from]) => escape(from)).join('|')})\\b`, 'gi');
const LOOKUP = new Map(REPLACEMENTS.map(([from, to]) => [from.toLowerCase(), to]));

const matchCase = (source: string, replacement: string) => {
	if (source === source.toUpperCase()) return replacement.toUpperCase();
	if (source[0] === source[0].toUpperCase()) return replacement[0].toUpperCase() + replacement.slice(1);
	return replacement;
};

// The SDK reads launch parameters through SvelteKit's page state; also check the
// window URL directly (same launch URL in production, and works in Storybook).
export const isSocial = () =>
	stateUrlDerived.social() ||
	(typeof location !== 'undefined' && new URLSearchParams(location.search).get('social') === 'true');

/** Apply social-casino wording to a string (no-op outside social mode). */
export const socialText = (text: string) =>
	isSocial()
		? text.replace(PATTERN, (match, _word, offset: number, whole: string) =>
				// "Stake Engine" is the platform's name (legal disclaimer), not the word "stake"
				/^stake$/i.test(match) && /^\s+Engine/.test(whole.slice(offset + match.length))
					? match
					: matchCase(match, LOOKUP.get(match.toLowerCase()) ?? match),
			)
		: text;

/** Svelte action: keep every text node inside an element in social wording. */
export const socialWording = (node: HTMLElement) => {
	if (!isSocial()) return;
	const apply = () => {
		const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
		for (let text = walker.nextNode(); text; text = walker.nextNode()) {
			const next = socialText(text.nodeValue ?? '');
			if (next !== text.nodeValue) text.nodeValue = next;
		}
	};
	apply();
	const observer = new MutationObserver(apply);
	observer.observe(node, { subtree: true, childList: true, characterData: true });
	return { destroy: () => observer.disconnect() };
};
