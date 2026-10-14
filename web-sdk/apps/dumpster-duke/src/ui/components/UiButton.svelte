<script lang="ts" module>
	import type { ButtonIcon } from '../types';
	import type { ArtName } from './UiArt.svelte';

	// Art for each button; buttons without their own icon use the blank round button
	// with a short label in the game font.
	const ICON_ART: Record<ButtonIcon, { art: ArtName; label?: string }> = {
		decrease: { art: 'bar_minus' },
		increase: { art: 'bar_plus' },
		menu: { art: 'btn_menu' },
		turbo: { art: 'btn_turbo' },
		autoSpin: { art: 'btn_blank', label: 'AUTO' },
		payTable: { art: 'btn_blank', label: 'PAYS' },
		info: { art: 'btn_info' },
		settings: { art: 'btn_blank', label: 'SET' },
		soundOn: { art: 'btn_blank', label: 'SOUND' },
		soundOff: { art: 'btn_blank', label: 'MUTED' },
		menuExit: { art: 'btn_back' },
	};
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import { BitmapText, Container } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';

	import UiArt from './UiArt.svelte';

	type Props = Omit<ButtonProps, 'children'> & {
		icon: ButtonIcon;
		sizes: { width: number; height: number };
		active?: boolean;
		children?: Snippet;
		variant?: 'dark' | 'light';
	};

	const { icon, active, variant: _variant, children: childrenFromParent, ...buttonProps }: Props = $props();
	const look = $derived(ICON_ART[icon]);
	const size = $derived(buttonProps.sizes.width);
	const wide = $derived(look.art === 'btn_info' || look.art === 'btn_back');
</script>

<Button {...buttonProps}>
	{#snippet children({ center, hovered, pressed })}
		<Container
			{...center}
			scale={pressed ? 0.93 : hovered && !buttonProps.disabled ? 1.05 : 1}
			alpha={buttonProps.disabled ? 0.45 : 1}
		>
			{#if active}
				<!-- "on" state (turbo, auto spin): a warm glow behind the button -->
				<UiArt name={look.art} width={size * 1.18} height={size * 1.18} tint={0xffc23a} alpha={0.55} />
			{/if}
			<UiArt name={look.art} width={wide ? size * 1.6 : size} height={size} />
			{#if look.label}
				<BitmapText
					anchor={0.5}
					text={look.label}
					style={{ fontFamily: 'gold', fontSize: size * (look.label.length > 4 ? 0.17 : 0.22) }}
				/>
			{/if}
		</Container>

		{@render childrenFromParent?.()}
	{/snippet}
</Button>
