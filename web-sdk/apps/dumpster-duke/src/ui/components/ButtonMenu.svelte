<script lang="ts">
	import type { ButtonProps } from 'components-pixi';
	import { stateUi } from 'state-shared';

	import UiButton from './UiButton.svelte';
	import { UI_BASE_SIZE } from '../constants';
	import { getContext } from '../context';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	// tall pill next to the BONUS card; toggles the menu popup (≡ / ✕)
	const sizes = { width: UI_BASE_SIZE * 0.55, height: UI_BASE_SIZE * 1.5 };

	const onpress = () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		stateUi.menuOpen = !stateUi.menuOpen;
	};
</script>

<UiButton {...props} {sizes} {onpress} icon={stateUi.menuOpen ? 'menuExit' : 'menu'} />
