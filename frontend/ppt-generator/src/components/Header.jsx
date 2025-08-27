import { Presentation, Sparkles, Zap } from 'lucide-react'

export function Header() {
  return (
    <header className="glass-effect border-b border-white/20 shadow-xl relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -right-1/2 w-96 h-96 bg-gradient-to-br from-blue-400/20 to-purple-600/20 rounded-full blur-3xl floating-animation"></div>
        <div className="absolute -bottom-1/2 -left-1/2 w-96 h-96 bg-gradient-to-tr from-purple-400/20 to-pink-600/20 rounded-full blur-3xl floating-animation" style={{animationDelay: '3s'}}></div>
      </div>
      
      <div className="container mx-auto px-6 py-6 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-75"></div>
              <div className="relative p-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl">
                <Presentation className="h-8 w-8 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">AI Presentation Generator</h1>
              <p className="text-white/80 text-sm font-medium">Create stunning presentations with artificial intelligence</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-md rounded-full px-4 py-2 border border-white/20">
              <Zap className="h-5 w-5 text-yellow-400" />
              <span className="text-white font-medium text-sm">Powered by AI</span>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-white/70">
              <Sparkles className="h-5 w-5 animate-pulse" />
              <span className="text-sm font-medium">v2.0</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
