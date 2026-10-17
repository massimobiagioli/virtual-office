// Negative lint fixture: no audio, ever (Constitution §14.10, FRONTEND.md §8.6).
import { sound } from '@pixi/sound'

export const beep = new Audio('beep.wav')
export const context = new AudioContext()
export const library = sound
