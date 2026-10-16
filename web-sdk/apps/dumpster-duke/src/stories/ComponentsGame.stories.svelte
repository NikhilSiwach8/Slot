<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'COMPONENTS/<Game>',
	});
</script>

<script lang="ts">
	import {
		StoryLocale,
		StoryGameTemplate,
		type TemplateArgs,
		templateArgs,
	} from 'components-storybook';

	import { stateGameDerived } from '../game/stateGame.svelte';
	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';
	import { eventEmitter } from '../game/eventEmitter';
	import { stateBet } from 'state-shared';
	import { winLevelMap } from '../game/winLevelMap';

	
	setContext();
</script>

{#snippet template(args: TemplateArgs<any>)}
	<StoryGameTemplate
		skipLoadingScreen={args.skipLoadingScreen}
		action={async () => {
			await args.action?.(args.data);
		}}
	>
		<StoryLocale lang="en">
			<Game />
		</StoryLocale>
	</StoryGameTemplate>
{/snippet}

<Story name="component (loadingScreen)">
	<StoryLocale lang="en">
		<Game />
	</StoryLocale>
</Story>

<Story
	name="preSpin"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			await stateGameDerived.enhancedBoard.preSpin({});
		},
	})}
	{template}
/>

<Story
	name="emitterEvent: boardHide"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			eventEmitter.broadcast({ type: 'boardHide' });
		},
	})}
	{template}
/>

<Story
	name="double chance on"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			stateBet.activeBetModeKey = 'ANTE';
		},
	})}
	{template}
/>

<Story
	name="mystery reveal"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			await eventEmitter.broadcastAsync({ type: 'mysteryReveal', spins: 15, lootBag: 8 });
		},
	})}
	{template}
/>

<Story
	name="splash: haunted raid"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.activeBetModeKey = 'BASE';
			eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
			await eventEmitter.broadcastAsync({ type: 'freeSpinIntroUpdate', totalFreeSpins: 12 });
		},
	})}
	{template}
/>

<Story
	name="splash: super bonus"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.activeBetModeKey = 'SUPER';
			eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
			await eventEmitter.broadcastAsync({ type: 'freeSpinIntroUpdate', totalFreeSpins: 12 });
		},
	})}
	{template}
/>

<Story
	name="splash: mystery bonus"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.activeBetModeKey = 'MYSTERY';
			eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
			await eventEmitter.broadcastAsync({ type: 'freeSpinIntroUpdate', totalFreeSpins: 12 });
		},
	})}
	{template}
/>

<Story
	name="splash: raid complete"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			eventEmitter.broadcast({ type: 'freeSpinOutroShow' });
			await eventEmitter.broadcastAsync({ type: 'freeSpinOutroCountUp', amount: 1254300000, winLevelData: winLevelMap[6] });
		},
	})}
	{template}
/>

<Story
	name="max multiplier total"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			eventEmitter.broadcast({ type: 'multiplierTotalShow' });
			eventEmitter.broadcast({ type: 'multiplierTotalUpdate', totalMultiplier: 25000 });
		},
	})}
	{template}
/>

<Story
	name="win: good"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			eventEmitter.broadcast({ type: 'winShow' });
			await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: 800, winLevelData: winLevelMap[5] });
		},
	})}
	{template}
/>

<Story
	name="win: big"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			eventEmitter.broadcast({ type: 'winShow' });
			await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: 2000, winLevelData: winLevelMap[6] });
		},
	})}
	{template}
/>

<Story
	name="win: super"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			eventEmitter.broadcast({ type: 'winShow' });
			await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: 4000, winLevelData: winLevelMap[7] });
		},
	})}
	{template}
/>

<Story
	name="win: mega"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			eventEmitter.broadcast({ type: 'winShow' });
			await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: 7500, winLevelData: winLevelMap[8] });
		},
	})}
	{template}
/>

<Story
	name="win: epic"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			eventEmitter.broadcast({ type: 'winShow' });
			await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: 15000, winLevelData: winLevelMap[9] });
		},
	})}
	{template}
/>

<Story
	name="win: max"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			stateBet.betAmount = 1;
			eventEmitter.broadcast({ type: 'winShow' });
			await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: 1000000, winLevelData: winLevelMap[10] });
		},
	})}
	{template}
/>
