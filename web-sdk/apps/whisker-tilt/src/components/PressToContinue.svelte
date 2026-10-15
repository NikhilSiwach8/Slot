<script lang="ts">
	import { onDestroy } from 'svelte';
	import { MainContainer, OnPressFullScreen } from 'components-layout';
	import { OnHotkey } from 'components-shared';
	import { BitmapText } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { createClock } from './fx/timeline.svelte';

	type Props = {
		onpress: () => void;
	};

	const props: Props = $props();
	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());
</script>

<MainContainer alignVertical="bottom">
	<BitmapText
		anchor={{ x: 0.5, y: 1 }}
		x={context.stateLayoutDerived.mainLayout().width * 0.5}
		y={context.stateLayoutDerived.mainLayout().height - 40}
		alpha={0.65 + 0.35 * Math.sin(clock.seconds * 4)}
		text="PRESS ANYWHERE TO CONTINUE"
		style={{ fontFamily: 'gold', fontSize: 56 }}
	/>
</MainContainer>
<OnHotkey hotkey="Space" onpress={() => props.onpress()} />
<OnPressFullScreen onpress={() => props.onpress()} />
