"use client"

import React, { useMemo, useRef, useState, useEffect } from "react"

type LogoPosition = "top_right" | "top_left" | "bottom_right" | "bottom_left"

export default function BrandingPreviewPage() {
  const [whatsapp, setWhatsapp] = useState<string>("0758406188")
  const [email, setEmail] = useState<string>("example@email.com")
  const [logoUrl, setLogoUrl] = useState<string>("")
  const [logoWidth, setLogoWidth] = useState<number>(150)
  const [logoPosition, setLogoPosition] = useState<LogoPosition>("top_right")
  const [logoXY, setLogoXY] = useState<{ x: number; y: number }>({ x: 16, y: 16 })
  const [contactColor, setContactColor] = useState<string>("#ffffff")
  const [contactFontSize, setContactFontSize] = useState<number>(22)
  const [contactXY, setContactXY] = useState<{ x: number; y: number }>({ x: 0, y: 0 })

  const containerRef = useRef<HTMLDivElement | null>(null)
  const logoRef = useRef<HTMLDivElement | null>(null)
  const contactRef = useRef<HTMLDivElement | null>(null)
  const dragState = useRef<{ type: "logo" | "contact" | null; offsetX: number; offsetY: number; resizing: boolean }>({ type: null, offsetX: 0, offsetY: 0, resizing: false })

  const contactLine = useMemo(() => {
    const parts: string[] = []
    if (whatsapp) parts.push(whatsapp)
    if (email) parts.push(email)
    return parts.join("   |   ")
  }, [whatsapp, email])

  // Keep old corner presets as a quick starter if user hasn't dragged yet
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const positionStyle = useMemo<React.CSSProperties>(() => {
    const style: React.CSSProperties = { position: "absolute" }
    switch (logoPosition) {
      case "top_right":
        style.top = 16
        style.right = 16
        break
      case "top_left":
        style.top = 16
        style.left = 16
        break
      case "bottom_right":
        style.bottom = 16
        style.right = 16
        break
      case "bottom_left":
        style.bottom = 16
        style.left = 16
        break
      default:
        style.top = 16
        style.right = 16
    }
    return style
  }, [logoPosition])

  // Initialize centered bottom contact position after mount
  useEffect(() => {
    const el = containerRef.current
    const contactEl = contactRef.current
    if (el && contactEl) {
      const rect = el.getBoundingClientRect()
      setContactXY({ x: Math.round(rect.width / 2), y: Math.round(rect.height - 24) })
    }
  }, [])

  const clampToContainer = (x: number, y: number) => {
    const rect = containerRef.current?.getBoundingClientRect()
    if (!rect) return { x, y }
    const nx = Math.max(0, Math.min(x, rect.width))
    const ny = Math.max(0, Math.min(y, rect.height))
    return { x: nx, y: ny }
  }

  // Drag handlers (no external libs)
  const onPointerDown = (e: React.PointerEvent, type: "logo" | "contact", resizing = false) => {
    const containerRect = containerRef.current?.getBoundingClientRect()
    if (!containerRect) return
    const target = (type === "logo" ? logoRef.current : contactRef.current) as HTMLDivElement
    if (!target) return
    const targetRect = target.getBoundingClientRect()
    dragState.current = {
      type,
      resizing,
      offsetX: e.clientX - targetRect.left,
      offsetY: e.clientY - targetRect.top,
    }
    ;(e.target as Element).setPointerCapture?.((e as unknown as PointerEvent).pointerId)
  }

  const onPointerMove = (e: React.PointerEvent) => {
    const state = dragState.current
    if (!state.type) return
    const containerRect = containerRef.current?.getBoundingClientRect()
    if (!containerRect) return

    if (state.type === "logo") {
      if (state.resizing) {
        // Resize by horizontal delta, keep aspect by width only
        const logoRect = logoRef.current?.getBoundingClientRect()
        if (!logoRect) return
        const newWidth = Math.max(40, Math.min(400, e.clientX - logoRect.left))
        setLogoWidth(Math.round(newWidth))
      } else {
        const newX = e.clientX - containerRect.left - state.offsetX
        const newY = e.clientY - containerRect.top - state.offsetY
        const clamped = clampToContainer(newX, newY)
        setLogoXY({ x: Math.round(clamped.x), y: Math.round(clamped.y) })
        setLogoPosition("top_right") // neutralize preset once dragged
      }
    } else if (state.type === "contact") {
      const newX = e.clientX - containerRect.left
      const newY = e.clientY - containerRect.top
      const clamped = clampToContainer(newX, newY)
      setContactXY({ x: Math.round(clamped.x), y: Math.round(clamped.y) })
    }
  }

  const onPointerUp = () => {
    dragState.current = { type: null, offsetX: 0, offsetY: 0, resizing: false }
  }

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-xl font-semibold mb-3">Branding Preview (Temporary)</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          {/* Poster Preview */}
          <div
            ref={containerRef}
            className="relative w-full aspect-[16/9] rounded-lg overflow-hidden border border-gray-300 bg-gray-100 select-none"
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerLeave={onPointerUp}
          >
            {/* Background placeholder image */}
            <div
              className="absolute inset-0 bg-cover bg-center"
              style={{
                backgroundImage:
                  "url(https://images.unsplash.com/photo-1520975922284-9f53b7b0f5d8?q=80&w=1600&auto=format&fit=crop)",
                filter: "saturate(0.95)",
              }}
            />

            {/* Logo (width only, preserved aspect) */}
            {/* Draggable/Resizable Logo */}
            <div
              ref={logoRef}
              style={{ position: "absolute", left: logoXY.x, top: logoXY.y, cursor: "move" }}
              onPointerDown={(e) => onPointerDown(e, "logo", false)}
            >
              {logoUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={logoUrl}
                  alt="Company Logo"
                  style={{ width: logoWidth, height: "auto" }}
                />
              ) : (
                <div
                  className="flex items-center justify-center bg-white/90 text-gray-700 border border-gray-300"
                  style={{ width: logoWidth, height: Math.max(logoWidth * 0.6, 60) }}
                >
                  Logo
                </div>
              )}
              {/* Resize handle */}
              <div
                onPointerDown={(e) => onPointerDown(e, "logo", true)}
                className="absolute w-3 h-3 bg-white border border-gray-400 right-[-6px] bottom-[-6px] cursor-se-resize"
                title="Drag to resize"
              />
            </div>

            {/* Draggable contact text */}
            <div
              ref={contactRef}
              className="absolute"
              style={{ left: contactXY.x, top: contactXY.y, transform: "translate(-50%, -50%)" }}
              onPointerDown={(e) => onPointerDown(e, "contact")}
            >
              <div
                className="font-semibold drop-shadow-[0_2px_2px_rgba(0,0,0,0.35)]"
                style={{ color: contactColor, fontSize: contactFontSize, textAlign: "center", padding: "0 12px", cursor: "move" }}
              >
                {contactLine}
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">WhatsApp</label>
            <input
              className="w-full border rounded px-3 py-2"
              placeholder="Enter WhatsApp number"
              value={whatsapp}
              onChange={(e) => setWhatsapp(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              className="w-full border rounded px-3 py-2"
              placeholder="Enter email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Logo URL</label>
            <input
              className="w-full border rounded px-3 py-2"
              placeholder="Paste a logo image URL"
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Logo Width (px)</label>
            <input
              type="number"
              className="w-full border rounded px-3 py-2"
              min={40}
              max={400}
              value={logoWidth}
              onChange={(e) => setLogoWidth(Number(e.target.value || 150))}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Contact Color</label>
              <input
                type="color"
                className="w-full border rounded h-10"
                value={contactColor}
                onChange={(e) => setContactColor(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Contact Size</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                min={12}
                max={64}
                value={contactFontSize}
                onChange={(e) => setContactFontSize(Number(e.target.value || 22))}
              />
            </div>
          </div>
          <div className="text-xs text-gray-600">
            Tip: Drag the logo or contact text to move. Use the small square on the logo to resize. You can also change contact color and size above.
          </div>
        </div>
      </div>
    </div>
  )
}



