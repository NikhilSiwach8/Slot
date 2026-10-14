<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';
	import { stateModal, stateBet, stateBetDerived } from 'state-shared';

	import UiArt from './UiArt.svelte';
	import { UI_BASE_SIZE } from '../constants';
	import { getContext } from '../context';
	import { i18nDerived } from '../i18n/i18nDerived';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const { stateXstateDerived, eventEmitter } = getContext();
	const sizes = { width: UI_BASE_SIZE, height: UI_BASE_SIZE };
	const disabled = $derived(!stateXstateDerived.isIdle());
	const active = $derived(stateBetDerived.activeBetMode()?.type === 'activate');

	const openModal = () => (stateModal.modal = { name: 'buyBonus' });
	const disableActiveBetMode = () => (stateBet.activeBetModeKey = 'BASE');
	const onpress = () => {
		eventEmitter.broadcast({ type: 'soundPressGeneral' });

		if (active) {
			disableActiveBetMode();
		} else {
			openModal();
		}
	};

	const getState = (value: {
		active: boolean;
		disabled: boolean;
		hovered: boolean;
		pressed: boolean;
	}) => {
		if (value.disabled) return 'disabled' as const;
		if (value.pressed) return 'pressed' as const;
		if (value.hovered) return 'hovered' as const;
		if (value.active) return 'active' as const;
		return 'default' as const;
	};
</script>

<Button {...props} {sizes} {disabled} {onpress}>
	{#snippet children({ center, hovered, pressed })}
		{@const state = getState({ active, disabled, hovered, pressed })}
		<Container
			{...center}
			scale={pressed ? 0.93 : hovered && !disabled ? 1.05 : 1}
			alpha={disabled ? 0.45 : 1}
		>
			<UiArt name="icon_cart" width={sizes.width} height={sizes.height * 0.8} y={-sizes.height * 0.08} />
			<BitmapText
				anchor={0.5}
				y={sizes.height * 0.4}
				text={(state === 'active' ? i18nDerived.disable() : i18nDerived.buyBonus()).toUpperCase()}
				style={{ fontFamily: 'gold', fontSize: sizes.width * 0.16 }}
			/>
		</Container>
	{/snippet}
</Button>
