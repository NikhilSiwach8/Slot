<!--
	Same as components-ui-html's <Modals>, but with our own rules/paytable screen and
	buy-feature menu in place of the template's empty "ADD YOUR GAME RULES" placeholders.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';

	import ModalError from 'components-ui-html/src/components/ModalError.svelte';
	import ModalBetMenu from 'components-ui-html/src/components/ModalBetMenu.svelte';
	import ModalAutoSpin from 'components-ui-html/src/components/ModalAutoSpin.svelte';
	import ModalAutoSpinMessage from 'components-ui-html/src/components/ModalAutoSpinMessage.svelte';
	import ModalSettings from 'components-ui-html/src/components/ModalSettings.svelte';

	import ModalGameInfo from './info/ModalGameInfo.svelte';
	import ModalBuyFeature from './buy/ModalBuyFeature.svelte';
	import MenuPopup from './MenuPopup.svelte';

	type Props = { version: Snippet };
	const props: Props = $props();
</script>

<ModalError />
<ModalBetMenu />
<MenuPopup />
<ModalBuyFeature />
<ModalAutoSpin />
<ModalAutoSpinMessage />
<ModalGameInfo version={props.version} />
<ModalSettings />

<style lang="scss">
	:global(html) {
		font-size: 16px;
		@media screen and (max-width: 500px) {
			font-size: 50%;
		}
	}
</style>
