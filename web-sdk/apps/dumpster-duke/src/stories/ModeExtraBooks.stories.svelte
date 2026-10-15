<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'MODE_EXTRA/book',
	});
</script>

<!-- Rounds from the Super Bonus, Mystery Bonus and Feature Spin modes. -->
<script lang="ts">
	import { StoryGameTemplate, StoryLocale, type TemplateArgs, templateArgs } from 'components-storybook';
	import { stateBet } from 'state-shared';

	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';
	import { playBet } from '../game/utils';
	import { reelSpin } from '../game/reelSpin/controller.svelte';
	import superBooks from './data/super_books';
	import mysteryBooks from './data/mystery_books';
	import featureBooks from './data/feature_books';

	setContext();

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const play = async (mode: string, book: any) => {
		stateBet.betAmount = 1;
		stateBet.activeBetModeKey = mode;
		reelSpin.start();
		await playBet({ ...book, state: book.events });
	};
</script>

{#snippet template(args: TemplateArgs<any>)}
	<StoryGameTemplate skipLoadingScreen={args.skipLoadingScreen} action={async () => await args.action?.(args.data)}>
		<StoryLocale lang="en">
			<Game />
		</StoryLocale>
	</StoryGameTemplate>
{/snippet}

<Story
	name="super bonus"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: async () => await play('SUPER', superBooks[1]) })}
	{template}
/>

<Story
	name="mystery bonus"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: async () => await play('MYSTERY', mysteryBooks[1]) })}
	{template}
/>

<Story
	name="feature spin"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await play('FEATURE', featureBooks.find((book) => book.payoutMultiplier > 0) ?? featureBooks[0]),
	})}
	{template}
/>
