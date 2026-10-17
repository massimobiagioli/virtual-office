import {
  createMemoryHistory,
  createRouter,
  createWebHistory,
  type Router,
  type RouteRecordRaw,
} from 'vue-router'

// Deep links only open windows (FRONTEND.md §6); window routes arrive with their windows.
// The root route is the bare Workbench screen, so its view renders nothing.
const routes: RouteRecordRaw[] = [
  { path: '/', name: 'workbench', component: { name: 'WorkbenchDesktop', render: () => null } },
]

export type WorkbenchHistory = 'web' | 'memory'

export function createWorkbenchRouter(history: WorkbenchHistory = 'web'): Router {
  return createRouter({
    history: history === 'web' ? createWebHistory() : createMemoryHistory(),
    routes,
  })
}
