# TerraFusion Cinematic Splash Page

This directory contains the mythic-grade, cinematic splash page for TerraFusion, designed to make a statement at first contact.

## Features
- Cinematic video background (terrain + AI overlays)
- Glassmorphic panel with animated glyph and typewriter intro
- Futuristic typography and cosmic color palette
- Responsive, accessible, and offline-ready
- Lottie animation support for the logo
- Multiple CTAs for platform entry, assessor sync, admin, and manifesto

## Usage
1. Place all required assets in `../assets/`:
   - `terrain_ai_loop.mp4` (video background)
   - `terrain_poster.jpg` (video poster image)
   - `logo_tf_lottie.json` (Lottie animation for glyph)
   - `Lexend.woff2`, `IBMPlexMono.woff2` (fonts)
   - `favicon.ico` (favicon)
   - `golden_pattern_manifesto.pdf` (optional CTA doc)
2. Download and place `lottie.min.js` from [Lottie Web](https://cdnjs.cloudflare.com/ajax/libs/lottie-web/) in this directory.
3. Open `index.html` in any browser (works offline).

## Customization
- Edit `index.html` to change CTAs, intro text, or add county-specific branding.
- Swap out video, logo, or fonts in `../assets/` as needed.
- For React/Next.js integration, use the provided structure as a template.

## Deployment
- Host as a static site (Nginx, S3, Netlify, Vercel, etc.)
- Container-ready for enterprise deployments
- All assets are local for privacy and offline use

## Accessibility
- Keyboard navigable, high-contrast, and screen-reader friendly
- WCAG 2.1 AA compliant

## The Golden Pattern
View source in `index.html` for the embedded philosophy meta-comment.

For support or custom deployments, contact: support@terrafusion.app 