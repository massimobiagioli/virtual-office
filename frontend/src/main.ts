import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { createWorkbenchRouter } from './router'

createApp(App).use(createPinia()).use(createWorkbenchRouter()).mount('#app')
