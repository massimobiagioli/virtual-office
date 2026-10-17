// Negative lint fixture: shared/ is plain TypeScript, no Vue (FRONTEND.md §1, §1.1).
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { createRouter } from 'vue-router'

export const framework = [ref, defineStore, createRouter]
