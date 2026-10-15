<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'MODE_BASE/book',
	});
</script>

<script lang="ts">
	import {
		StoryGameTemplate,
		StoryLocale,
		type TemplateArgs,
		templateArgs,
	} from 'components-storybook';
	import { randomInteger } from 'utils-shared/random';

	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';
	import { playBet } from '../game/utils';
	import books from './data/base_books';
	import { reelSpin } from '../game/reelSpin/controller.svelte';

	
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

<Story
	name="random"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const index = randomInteger({ min: 0, max: books.length - 1 });
			const data = books[index];
			console.log('Running a book at index', index);
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>

<!-- Like a real bet: the reels launch on press, the result arrives ~300 ms later (network),
     and a round with several tumbles is played. Used to check timings for idle gaps. -->
<Story
	name="tumbles with network delay"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const tumbles = (book: (typeof books)[number]) => book.events.filter((event) => event.type === 'tumbleBoard').length;
			const data = [...books].sort((a, b) => tumbles(b) - tumbles(a))[0];
			reelSpin.start();
			await new Promise((resolve) => setTimeout(resolve, 300));
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>
