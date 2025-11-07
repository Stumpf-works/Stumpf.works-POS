import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Plugin } from '@/types/plugins'

interface PluginState {
  // Active plugins
  activePlugins: string[]
  availablePlugins: Plugin[]

  // Plugin settings per plugin
  pluginSettings: Record<string, any>

  // Loading states
  isLoading: boolean
  error: string | null

  // Actions
  setActivePlugins: (plugins: string[]) => void
  setAvailablePlugins: (plugins: Plugin[]) => void
  setPluginSettings: (pluginName: string, settings: any) => void
  isPluginActive: (pluginName: string) => boolean
  getPluginSettings: (pluginName: string) => any
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const initialState = {
  activePlugins: [],
  availablePlugins: [],
  pluginSettings: {},
  isLoading: false,
  error: null,
}

export const usePluginStore = create<PluginState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setActivePlugins: (plugins) => set({ activePlugins: plugins }),

      setAvailablePlugins: (plugins) => set({ availablePlugins: plugins }),

      setPluginSettings: (pluginName, settings) =>
        set((state) => ({
          pluginSettings: { ...state.pluginSettings, [pluginName]: settings },
        })),

      isPluginActive: (pluginName) => {
        return get().activePlugins.includes(pluginName)
      },

      getPluginSettings: (pluginName) => {
        return get().pluginSettings[pluginName] || {}
      },

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      reset: () => set(initialState),
    }),
    {
      name: 'plugin-storage',
      partialize: (state) => ({
        pluginSettings: state.pluginSettings,
      }),
    }
  )
)
