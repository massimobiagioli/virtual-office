// Negative lint fixture: office-renderer may import @pixi/*, but never @pixi/sound (§14.10).
import { sound } from '@pixi/sound'

export const library = sound
