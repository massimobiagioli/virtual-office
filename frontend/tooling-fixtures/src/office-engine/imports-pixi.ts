// Negative lint fixture (US-01.06 AC3): only office-renderer may import pixi.js (FRONTEND.md §1.1).
import { Application } from 'pixi.js'

export const application = new Application()
