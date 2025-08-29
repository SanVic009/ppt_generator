import { Moon, Sun } from 'lucide-react'
import { useDarkMode } from '../context/DarkModeContext'

export function DarkModeToggle() {
  const { isDark, toggleDarkMode } = useDarkMode()

  return (
    <button
      onClick={toggleDarkMode}
      className="flex items-center space-x-2 bg-white/10 backdrop-blur-md rounded-full px-4 py-2 border border-white/20 hover:bg-white/20 transition-all duration-200"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? (
        <>
          <Sun className="h-5 w-5 text-yellow-400" />
          <span className="text-white font-medium text-sm hidden sm:inline">Light</span>
        </>
      ) : (
        <>
          <Moon className="h-5 w-5 text-blue-200" />
          <span className="text-white font-medium text-sm hidden sm:inline">Dark</span>
        </>
      )}
    </button>
  )
}
