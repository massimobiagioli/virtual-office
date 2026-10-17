// Negative lint fixture: no audio, ever (Constitution §14.10, FRONTEND.md §8.6). One line per
// banned name, so that every entry of the lint config is proven on its own (ADR-0009).
import { sound } from '@pixi/sound'
import { filters } from '@pixi/sound/filters'
import { Howl } from 'howler'
import * as Tone from 'tone'

export const libraries = [sound, filters, Howl, Tone]
export const element = new Audio('beep.wav')
export const context = new AudioContext()
export const offline = new OfflineAudioContext(1, 1, 44100)
export const legacy = new webkitAudioContext()
export const voice = speechSynthesis
export const utterance = new SpeechSynthesisUtterance('beep')
export const audioElement = HTMLAudioElement
export const viaWindow = new window.Audio()
export const viaGlobalThis = new globalThis.AudioContext()
export const viaSelf = self.speechSynthesis
export const created = document.createElement('audio')
