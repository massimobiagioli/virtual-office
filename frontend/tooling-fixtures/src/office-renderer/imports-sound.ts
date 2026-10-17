// Negative lint fixture: office-renderer may import @pixi/*, but never @pixi/sound (§14.10).
import { sound } from '@pixi/sound'
import beep from '../assets/beep.wav'

export const library = [sound, beep]
