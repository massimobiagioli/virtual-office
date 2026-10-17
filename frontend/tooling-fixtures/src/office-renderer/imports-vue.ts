// Negative lint fixture: office-renderer is a PixiJS adapter, no framework (FRONTEND.md §1.1).
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { createRouter } from 'vue-router'
import { reactive } from '@vue/reactivity'

export const framework = [ref, defineStore, createRouter, reactive]
