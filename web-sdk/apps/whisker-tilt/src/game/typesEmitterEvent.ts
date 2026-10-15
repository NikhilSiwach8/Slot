import type { EmitterEventTumbleWinAmount } from '../components/TumbleWinAmount.svelte';
import type { EmitterEventFreeSpinIntro } from '../components/FreeSpinIntro.svelte';
import type { EmitterEventFreeSpinCounter } from '../components/FreeSpinCounter.svelte';
import type { EmitterEventFreeSpinOutro } from '../components/FreeSpinOutro.svelte';
import type { EmitterEventWin } from '../components/Win.svelte';
import type { EmitterEventSound } from '../components/Sound.svelte';
import type { EmitterEventTransition } from '../components/Transition.svelte';
import type { EmitterEventMitten } from '../components/Mitten.svelte';
import type { EmitterEventMysteryGift } from '../components/MysteryGift.svelte';
import type { EmitterEventWinLabels } from '../components/WinLabels.svelte';
import type { EmitterEventShelf } from '../components/ShelfResult.svelte';

export type EmitterEventGame =
	| { type: 'boardFrameGlowShow' }
	| { type: 'boardFrameGlowHide' }
	| EmitterEventTumbleWinAmount
	| EmitterEventWin
	| EmitterEventFreeSpinIntro
	| EmitterEventFreeSpinCounter
	| EmitterEventFreeSpinOutro
	| EmitterEventSound
	| EmitterEventTransition
	| EmitterEventMitten
	| EmitterEventMysteryGift
	| EmitterEventWinLabels
	| EmitterEventShelf;
