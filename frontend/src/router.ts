import {
  createRouter,
  createWebHistory,
  type Router,
  type RouterHistory,
  type RouteRecordRaw,
} from 'vue-router'

import WorkbenchDesktop from './windows/WorkbenchDesktop.vue'

// Deep links only open windows (FRONTEND.md §6); window routes arrive with their windows.
// The root route is the bare Workbench screen.
const routes: RouteRecordRaw[] = [{ path: '/', name: 'workbench', component: WorkbenchDesktop }]

export function createWorkbenchRouter(history: RouterHistory = createWebHistory()): Router {
  return createRouter({ history, routes })
}
