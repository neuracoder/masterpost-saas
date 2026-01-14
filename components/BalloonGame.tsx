'use client'
import { useEffect, useRef, useState, useCallback } from 'react'

type GameState = 'initial' | 'playing' | 'completed'

interface BalloonGameProps {
  isPlaying: boolean
  imagesProcessed: number
  totalImages: number
  onExit: () => void
}

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  life: number
}

export default function BalloonGame({
  isPlaying,
  imagesProcessed,
  totalImages,
  onExit
}: BalloonGameProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [gameState, setGameState] = useState<GameState>('initial')
  const [score, setScore] = useState(0)
  const animationFrameRef = useRef<number>(0)

  const gameStateRef = useRef({
    balloon: {
      x: 170,
      y: 340,
      size: 40,
      velocity: 0,
      rotation: 0,
      ropeSwing: 0,
      ropeVelocity: 0
    },
    obstacles: [] as Array<{
      x: number
      y: number
      type: 'drone' | 'mine' | 'cloud'
      rotation: number
      rotationSpeed: number
      wobble: number
      lateralOffset: number
      lightningTimer: number
    }>,
    ascendingLines: [] as Array<{ x: number; y: number; speed: number }>,
    clouds: [] as Array<{ x: number; y: number; speed: number; size: number }>,
    mountains: [] as Array<{ x: number; height: number; width: number }>,
    particles: [] as Particle[],
    windGusts: [] as Array<{ x: number; y: number; direction: 'left' | 'right'; opacity: number; life: number }>,
    windForce: 0,
    gameOver: false,
    score: 0,
    mouseX: 170,
    keyboardX: 0,
    isExploding: false,
    isInfiniteMode: false
  })

  // Get sky color based on progress (day/night cycle)
  const getSkyGradient = (ctx: CanvasRenderingContext2D, progress: number) => {
    const gradient = ctx.createLinearGradient(0, 0, 0, 425)

    if (progress < 0.33) {
      // Day - Blue sky
      gradient.addColorStop(0, '#87CEEB')
      gradient.addColorStop(1, '#B0E0E6')
    } else if (progress < 0.66) {
      // Sunset - Orange/Purple
      gradient.addColorStop(0, '#FF6B6B')
      gradient.addColorStop(0.5, '#FFB347')
      gradient.addColorStop(1, '#C06C84')
    } else {
      // Night - Dark blue
      gradient.addColorStop(0, '#1a1a2e')
      gradient.addColorStop(1, '#16213e')
    }

    return gradient
  }

  // Manual restart function with proper cleanup
  const handleManualRestart = useCallback(() => {
    const state = gameStateRef.current

    // Cancel any ongoing animation
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = 0
    }

    // Reset all game state
    state.gameOver = false
    state.isExploding = false
    state.balloon = {
      x: 170,
      y: 340,
      size: 40,
      velocity: 0,
      rotation: 0,
      ropeSwing: 0,
      ropeVelocity: 0
    }
    state.obstacles = []
    state.particles = []
    state.ascendingLines = []
    state.windGusts = []
    state.windForce = 0
    state.score = 0
    state.keyboardX = 0
    // Enable infinite mode when manually restarting
    if (imagesProcessed >= totalImages && totalImages > 0) {
      state.isInfiniteMode = true
    }

    // Reset clouds
    state.clouds = []
    const canvas = canvasRef.current
    if (canvas) {
      for (let i = 0; i < 7; i++) {
        state.clouds.push({
          x: Math.random() * canvas.width,
          y: Math.random() * 300,
          speed: 0.3 + Math.random() * 0.4,
          size: 20 + Math.random() * 20
        })
      }

      // Reset ascending lines
      for (let i = 0; i < 10; i++) {
        state.ascendingLines.push({
          x: (canvas.width / 10) * i,
          y: Math.random() * canvas.height,
          speed: 2 + Math.random() * 1.5
        })
      }
    }

    // Reset score display
    setScore(0)
  }, [imagesProcessed, totalImages])

  // Reset game when modal opens
  useEffect(() => {
    if (isPlaying) {
      // Reset infinite mode when starting fresh
      if (gameStateRef.current) {
        gameStateRef.current.isInfiniteMode = false
      }
      setGameState('initial')
      setScore(0)
    }
  }, [isPlaying])

  // Detect processing completion
  useEffect(() => {
    if (imagesProcessed >= totalImages &&
      totalImages > 0 &&
      gameState === 'playing' &&
      !gameStateRef.current.isInfiniteMode) {
      setTimeout(() => {
        setGameState('completed')
      }, 1500)
    }
  }, [imagesProcessed, totalImages, gameState])

  // ESC key listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && gameState === 'completed') {
        onExit()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [gameState, onExit])

  // Main game loop
  useEffect(() => {
    if (!isPlaying || gameState !== 'playing' || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = 340
    canvas.height = 425

    const state = gameStateRef.current

    // Keyboard controls
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') state.keyboardX = -1
      if (e.key === 'ArrowRight') state.keyboardX = 1
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') state.keyboardX = 0
    }

    // Mouse controls
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      state.mouseX = e.clientX - rect.left
    }

    // Touch controls
    const handleTouchMove = (e: TouchEvent) => {
      e.preventDefault()
      const rect = canvas.getBoundingClientRect()
      state.mouseX = e.touches[0].clientX - rect.left
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    canvas.addEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('touchmove', handleTouchMove, { passive: false })

    // Initialize environment
    state.clouds = []
    for (let i = 0; i < 7; i++) {
      state.clouds.push({
        x: Math.random() * canvas.width,
        y: Math.random() * 300,
        speed: 0.3 + Math.random() * 0.4,
        size: 20 + Math.random() * 20
      })
    }

    // Initialize mountains for parallax
    state.mountains = []
    for (let i = 0; i < 5; i++) {
      state.mountains.push({
        x: i * 100,
        height: 100 + Math.random() * 100,
        width: 80 + Math.random() * 60
      })
    }

    // Initialize ascending lines
    state.ascendingLines = []
    for (let i = 0; i < 10; i++) {
      state.ascendingLines.push({
        x: (canvas.width / 10) * i,
        y: Math.random() * canvas.height,
        speed: 2 + Math.random() * 1.5
      })
    }

    let lastObstacleTime = Date.now()
    let lastWindTime = Date.now()
    let lastTime = Date.now()

    // Modular functions
    const updatePhysics = (deltaTime: number) => {
      // Check completion
      if (imagesProcessed >= totalImages && totalImages > 0 && !state.isInfiniteMode) {
        setGameState('completed')
        return false
      }

      if (state.gameOver || state.isExploding) return true

      // Balloon movement (with wind force applied)
      if (state.keyboardX !== 0) {
        state.balloon.x += state.keyboardX * 5 + state.windForce
      } else {
        const targetX = state.mouseX
        state.balloon.x += (targetX - state.balloon.x) * 0.1 + state.windForce
      }

      // Decay wind force
      state.windForce *= 0.92

      // Keep in bounds
      state.balloon.x = Math.max(state.balloon.size / 2, Math.min(canvas.width - state.balloon.size / 2, state.balloon.x))

      // Balloon float physics
      state.balloon.velocity -= 0.3
      state.balloon.y += state.balloon.velocity

      // Lower area constraint
      if (state.balloon.y < 255) {
        state.balloon.y = 255
        state.balloon.velocity = 0
      }
      if (state.balloon.y > canvas.height - state.balloon.size) {
        state.balloon.y = canvas.height - state.balloon.size
        state.balloon.velocity = -2
      }

      // Rope swing physics (pendulum)
      const swingForce = state.keyboardX * 0.02 || (state.mouseX - state.balloon.x) * 0.0005
      state.balloon.ropeVelocity += swingForce
      state.balloon.ropeVelocity *= 0.95 // Damping
      state.balloon.ropeSwing += state.balloon.ropeVelocity
      state.balloon.ropeSwing *= 0.98

      // Rotation based on movement
      state.balloon.rotation = state.balloon.ropeSwing * 0.5

      // Update particles
      state.particles = state.particles.filter(p => {
        p.x += p.vx
        p.y += p.vy
        p.vy += 0.5 // Gravity
        p.life -= deltaTime * 0.001
        return p.life > 0
      })

      // Update ascending lines
      state.ascendingLines.forEach((line: { x: number; y: number; speed: number }) => {
        line.y += line.speed
        if (line.y > canvas.height) {
          line.y = -10
        }
      })

      // Update wind gusts
      state.windGusts = state.windGusts.filter((gust: { x: number; y: number; direction: 'left' | 'right'; opacity: number; life: number }) => {
        gust.x += gust.direction === 'right' ? 15 : -15
        gust.life -= deltaTime * 0.001
        gust.opacity = gust.life
        return gust.life > 0 && gust.x > -100 && gust.x < canvas.width + 100
      })

      // Move obstacles
      state.obstacles.forEach(obs => {
        obs.y += 3
        obs.rotation += obs.rotationSpeed
        obs.lightningTimer += deltaTime

        // Drone wobble
        if (obs.type === 'drone') {
          obs.wobble += 0.1
          obs.lateralOffset = Math.sin(obs.wobble) * 10
        }
      })

      // Remove off-screen obstacles
      state.obstacles = state.obstacles.filter(obs => obs.y < canvas.height + 20)

      // Create new obstacles - MORE FREQUENT AND CENTERED
      const now = Date.now()
      if (now - lastObstacleTime > 400) { // Reduced to 400ms for ~3x difficulty
        const rand = Math.random()
        let type: 'drone' | 'mine' | 'cloud'
        if (rand < 0.33) type = 'drone'
        else if (rand < 0.66) type = 'mine'
        else type = 'cloud'

        // 70% spawn in CENTER zone, 30% in sides
        let xPosition: number
        if (Math.random() < 0.7) {
          // CENTER zone (middle 50% of screen)
          const centerStart = canvas.width * 0.25
          const centerWidth = canvas.width * 0.5
          xPosition = centerStart + Math.random() * centerWidth
        } else {
          // SIDES (left 25% or right 25%)
          if (Math.random() < 0.5) {
            // Left side
            xPosition = Math.random() * (canvas.width * 0.25)
          } else {
            // Right side
            xPosition = canvas.width * 0.75 + Math.random() * (canvas.width * 0.25)
          }
        }

        state.obstacles.push({
          x: xPosition,
          y: -20,
          type,
          rotation: 0,
          rotationSpeed: type === 'mine' ? 0.05 : 0,
          wobble: 0,
          lateralOffset: 0,
          lightningTimer: 0
        })
        lastObstacleTime = now
      }

      // Create wind gusts (every 8-15 seconds - MORE SPORADIC)
      if (now - lastWindTime > 8000 + Math.random() * 7000) {
        const direction = Math.random() < 0.5 ? 'left' : 'right'
        const startX = direction === 'right' ? -80 : canvas.width + 80
        const windY = state.balloon.y + (Math.random() - 0.5) * 100

        // Create wind tornado/swirl effect with multiple particles
        for (let i = 0; i < 12; i++) {
          const angle = (Math.PI * 2 * i) / 12
          const radius = 30 + Math.random() * 20
          state.windGusts.push({
            x: startX + Math.cos(angle) * radius,
            y: windY + Math.sin(angle) * radius,
            direction,
            opacity: 1,
            life: 1
          })
        }

        // Apply strong force to balloon
        state.windForce = direction === 'right' ? 15 : -15
        lastWindTime = now
      }

      // Collision detection
      state.obstacles.forEach(obs => {
        const distance = Math.sqrt(
          Math.pow(state.balloon.x - (obs.x + obs.lateralOffset), 2) +
          Math.pow(state.balloon.y - obs.y, 2)
        )

        if (distance < state.balloon.size / 2 + 15) {
          state.isExploding = true
          state.gameOver = true

          // Create explosion particles
          for (let i = 0; i < 15; i++) {
            const angle = (Math.PI * 2 * i) / 15
            state.particles.push({
              x: state.balloon.x,
              y: state.balloon.y,
              vx: Math.cos(angle) * (3 + Math.random() * 2),
              vy: Math.sin(angle) * (3 + Math.random() * 2) - 2,
              life: 1
            })
          }

          setTimeout(() => {
            if (imagesProcessed >= totalImages && totalImages > 0) {
              setGameState('completed')
              return
            }

            // Auto restart
            state.isExploding = false
            state.gameOver = false
            state.balloon = { x: 170, y: 340, size: 40, velocity: 0, rotation: 0, ropeSwing: 0, ropeVelocity: 0 }
            state.obstacles = []
            state.particles = []
            state.ascendingLines = []
            for (let i = 0; i < 10; i++) {
              state.ascendingLines.push({
                x: (canvas.width / 10) * i,
                y: Math.random() * canvas.height,
                speed: 2 + Math.random() * 1.5
              })
            }
            state.score = 0
            setScore(0)
          }, 1500)
        }
      })

      // Increment score
      if (!state.gameOver) {
        state.score += 1
        if (state.score % 10 === 0) {
          setScore(Math.floor(state.score / 10))
        }
      }

      return true
    }

    const drawScene = () => {
      const progress = totalImages > 0 ? imagesProcessed / totalImages : 0

      // Sky gradient
      ctx.fillStyle = getSkyGradient(ctx, progress) as any
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Ascending vertical lines (balloon rising effect)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)'
      ctx.lineWidth = 1
      state.ascendingLines.forEach((line: { x: number; y: number; speed: number }) => {
        ctx.beginPath()
        ctx.moveTo(line.x, line.y)
        ctx.lineTo(line.x, line.y + 30)
        ctx.stroke()
      })

      // Parallax mountains
      ctx.fillStyle = progress > 0.66 ? 'rgba(20, 20, 40, 0.5)' : 'rgba(100, 100, 150, 0.3)'
      state.mountains.forEach(mountain => {
        ctx.beginPath()
        ctx.moveTo(mountain.x, canvas.height)
        ctx.lineTo(mountain.x + mountain.width / 2, canvas.height - mountain.height)
        ctx.lineTo(mountain.x + mountain.width, canvas.height)
        ctx.closePath()
        ctx.fill()
      })

      // Clouds
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)'
      state.clouds.forEach(cloud => {
        ctx.beginPath()
        ctx.arc(cloud.x, cloud.y, cloud.size, 0, Math.PI * 2)
        ctx.arc(cloud.x + cloud.size * 0.8, cloud.y - cloud.size * 0.3, cloud.size * 0.9, 0, Math.PI * 2)
        ctx.arc(cloud.x + cloud.size * 1.6, cloud.y, cloud.size, 0, Math.PI * 2)
        ctx.fill()

        cloud.y += cloud.speed
        if (cloud.y > canvas.height + 50) {
          cloud.y = -50
          cloud.x = Math.random() * canvas.width
        }
      })

      // Draw wind tornado/swirl
      state.windGusts.forEach((gust: { x: number; y: number; direction: 'left' | 'right'; opacity: number; life: number }, index: number) => {
        // Curved wind lines forming a spiral
        ctx.strokeStyle = `rgba(180, 220, 255, ${gust.opacity * 0.7})`
        ctx.lineWidth = 4
        ctx.lineCap = 'round'
        ctx.beginPath()

        const angle = (index / 12) * Math.PI * 2 + (Date.now() * 0.005)
        const spiralRadius = 25
        const spiralX = Math.cos(angle) * spiralRadius
        const spiralY = Math.sin(angle) * spiralRadius

        ctx.moveTo(gust.x, gust.y)
        ctx.quadraticCurveTo(
          gust.x + spiralX * 0.5,
          gust.y + spiralY * 0.5,
          gust.x + spiralX,
          gust.y + spiralY
        )
        ctx.stroke()

        // Add small circles for more visual effect
        ctx.fillStyle = `rgba(200, 230, 255, ${gust.opacity * 0.5})`
        ctx.beginPath()
        ctx.arc(gust.x, gust.y, 3, 0, Math.PI * 2)
        ctx.fill()
      })

      // Draw obstacles
      state.obstacles.forEach(obs => {
        ctx.save()
        ctx.translate(obs.x + obs.lateralOffset, obs.y)

        // Add glow effect
        ctx.shadowBlur = 10
        ctx.shadowColor = 'rgba(255, 100, 100, 0.5)'

        if (obs.type === 'drone') {
          // Technological drone
          ctx.fillStyle = '#444'
          ctx.fillRect(-15, -8, 30, 16) // Body
          ctx.strokeStyle = '#666'
          ctx.lineWidth = 2
          ctx.strokeRect(-15, -8, 30, 16)

          // Rotating propellers
          ctx.save()
          ctx.translate(-12, 0)
          ctx.rotate(obs.rotation * 10)
          ctx.strokeStyle = '#888'
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(-8, 0)
          ctx.lineTo(8, 0)
          ctx.stroke()
          ctx.restore()

          ctx.save()
          ctx.translate(12, 0)
          ctx.rotate(obs.rotation * 10)
          ctx.strokeStyle = '#888'
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(-8, 0)
          ctx.lineTo(8, 0)
          ctx.stroke()
          ctx.restore()

          // Blinking red light
          if (Math.floor(obs.lightningTimer / 500) % 2 === 0) {
            ctx.fillStyle = '#FF0000'
            ctx.beginPath()
            ctx.arc(0, 0, 3, 0, Math.PI * 2)
            ctx.fill()
          }
        } else if (obs.type === 'mine') {
          // Spiked mine
          ctx.save()
          ctx.rotate(obs.rotation)

          // Center circle
          ctx.fillStyle = '#333'
          ctx.beginPath()
          ctx.arc(0, 0, 12, 0, Math.PI * 2)
          ctx.fill()

          // 6 triangular spikes
          ctx.fillStyle = '#555'
          for (let i = 0; i < 6; i++) {
            const angle = (Math.PI * 2 / 6) * i
            ctx.save()
            ctx.rotate(angle)
            ctx.beginPath()
            ctx.moveTo(0, -12)
            ctx.lineTo(-4, -18)
            ctx.lineTo(4, -18)
            ctx.closePath()
            ctx.fill()
            ctx.restore()
          }

          ctx.restore()
        } else if (obs.type === 'cloud') {
          // Storm cloud
          ctx.fillStyle = '#666'
          ctx.beginPath()
          ctx.arc(-8, 0, 8, 0, Math.PI * 2)
          ctx.arc(0, -3, 10, 0, Math.PI * 2)
          ctx.arc(8, 0, 8, 0, Math.PI * 2)
          ctx.fill()

          // Lightning bolt (every 2 seconds)
          if (obs.lightningTimer % 2000 < 200) {
            ctx.strokeStyle = '#FFFF00'
            ctx.lineWidth = 2
            ctx.beginPath()
            ctx.moveTo(0, 5)
            ctx.lineTo(-3, 12)
            ctx.lineTo(2, 12)
            ctx.lineTo(-1, 18)
            ctx.stroke()
          }
        }

        ctx.restore()
      })

      // Draw balloon with rope physics
      if (!state.isExploding) {
        // Rope starts at bottom of balloon and hangs DOWN
        const ropeStart = { x: state.balloon.x, y: state.balloon.y + state.balloon.size / 2 }

        // Rope is 20% longer (was ~40px, now ~48px)
        const ropeLength = state.balloon.size * 1.2

        // End point has horizontal lag based on velocity and swing
        const horizontalLag = state.balloon.ropeSwing * 10
        const ropeEnd = {
          x: state.balloon.x + horizontalLag,
          y: ropeStart.y + ropeLength
        }

        // Rope with Bezier curve (swinging downward)
        ctx.strokeStyle = '#EF4444'
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(ropeStart.x, ropeStart.y)

        // Control point for curve (between start and end, with swing)
        const time = Date.now() * 0.002
        const controlX = state.balloon.x + horizontalLag * 0.5 + Math.sin(time) * 5
        const controlY = ropeStart.y + ropeLength * 0.6

        ctx.quadraticCurveTo(controlX, controlY, ropeEnd.x, ropeEnd.y)
        ctx.stroke()

        // Balloon body
        ctx.save()
        ctx.translate(state.balloon.x, state.balloon.y)
        ctx.rotate(state.balloon.rotation)

        ctx.fillStyle = '#EF4444'
        ctx.beginPath()
        ctx.arc(0, 0, state.balloon.size / 2, 0, Math.PI * 2)
        ctx.fill()

        // Balloon highlight
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
        ctx.beginPath()
        ctx.arc(-5, -5, state.balloon.size / 4, 0, Math.PI * 2)
        ctx.fill()

        ctx.restore()
      }

      // Draw particles
      state.particles.forEach(p => {
        ctx.fillStyle = `rgba(239, 68, 68, ${p.life})`
        ctx.beginPath()
        ctx.arc(p.x, p.y, 3, 0, Math.PI * 2)
        ctx.fill()
      })

      // Explosion text
      if (state.isExploding) {
        ctx.font = 'bold 60px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('💥', state.balloon.x, state.balloon.y)
      }
    }

    const gameLoop = () => {
      const now = Date.now()
      const deltaTime = now - lastTime
      lastTime = now

      const shouldContinue = updatePhysics(deltaTime)
      if (!shouldContinue) return

      drawScene()

      animationFrameRef.current = requestAnimationFrame(gameLoop)
    }

    gameLoop()

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
      canvas.removeEventListener('mousemove', handleMouseMove)
      canvas.removeEventListener('touchmove', handleTouchMove)
    }
  }, [isPlaying, gameState, imagesProcessed, totalImages])

  if (!isPlaying) return null

  // Initial Screen
  if (gameState === 'initial') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-5 shadow-2xl w-full text-center relative" style={{ maxWidth: '326px' }}>
          {/* Close Button (X) - Top Right Corner */}
          <button
            onClick={onExit}
            className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white rounded-full shadow-md hover:shadow-lg transition-all"
            title="Exit Game"
            aria-label="Close game"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>

          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Processing Your Images...
          </h3>

          <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl p-6 mb-6">
            <p className="text-gray-700 mb-4 font-medium">
              While you wait, why not play a mini-game?
            </p>

            <div className="space-y-2 text-sm text-gray-600 mb-6">
              <p>🎈 Control the balloon with your mouse or keyboard</p>
              <p>⚡ Dodge drones, mines and storm clouds</p>
              <p>🏆 Watch the sky change as processing progresses!</p>
            </div>

            <button
              onClick={() => setGameState('playing')}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-3 px-8 rounded-lg shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all"
            >
              ▶️ Play Game
            </button>
          </div>

          <p className="text-sm text-gray-500">
            Or just wait... ({imagesProcessed}/{totalImages} processed)
          </p>
        </div>
      </div>
    )
  }

  // Completion Screen
  if (gameState === 'completed') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-5 shadow-2xl w-full text-center" style={{ maxWidth: '326px' }}>
          <h3 className="text-2xl font-bold text-green-600 mb-4">
            ✅ Processing Complete!
          </h3>

          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 mb-6">
            <p className="text-3xl mb-4">🎉</p>
            <p className="text-lg font-semibold text-gray-900 mb-2">
              All images processed!
            </p>
            <p className="text-gray-600 mb-4">
              {totalImages} image{totalImages !== 1 ? 's' : ''} successfully processed and ready
            </p>

            <div className="bg-white rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-600">Your Final Score</p>
              <p className="text-3xl font-bold text-purple-600">{score}</p>
            </div>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => {
                handleManualRestart()
                setGameState('playing')
              }}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-3 px-8 rounded-lg shadow-md hover:shadow-lg transition-all w-full"
            >
              🎮 Play Again
            </button>

            <button
              onClick={onExit}
              className="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-3 px-8 rounded-lg shadow-md hover:shadow-lg transition-all w-full"
            >
              Exit Game
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-3">
            (or press ESC to exit)
          </p>
        </div>
      </div>
    )
  }

  // Playing Screen
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-4 shadow-2xl w-full relative" style={{ maxWidth: '326px' }}>
        {/* Close Button (X) - Top Right Corner */}
        <button
          onClick={onExit}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white rounded-full shadow-md hover:shadow-lg transition-all"
          title="Exit Game"
          aria-label="Close game"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        <div className="text-center mb-4">
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Processing Your Images...
          </h3>
          <p className="text-sm text-gray-600">
            Dodge obstacles while we work!
          </p>
        </div>

        <canvas
          ref={canvasRef}
          className="border-2 border-gray-200 rounded-lg w-full shadow-inner"
          style={{ touchAction: 'none' }}
        />

        {/* Restart Button */}
        <div className="mt-4 flex justify-center">
          <button
            onClick={handleManualRestart}
            className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:shadow-lg transition-all"
            title="Restart Game"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Restart
          </button>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600 drop-shadow">{score}</p>
            <p className="text-xs text-gray-600">Score</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600 drop-shadow">
              {imagesProcessed}/{totalImages}
            </p>
            <p className="text-xs text-gray-600">Images Done</p>
          </div>
        </div>

        <p className="text-xs text-gray-500 text-center mt-4">
          Use mouse, touch or arrow keys ← →
        </p>
      </div>
    </div>
  )
}
