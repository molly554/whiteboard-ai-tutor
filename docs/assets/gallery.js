// Quiet preview; reduced-motion visitors choose when to start it.
const preview = document.querySelector('#hero-video');
if (preview && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  preview.muted = true;
  const start = () => {
    // Begin at the diagram, while the full recording remains available in the controls.
    preview.currentTime = Math.min(6, preview.duration / 3);
    preview.play().catch(() => {});
  };
  if (preview.readyState >= 1) start();
  else preview.addEventListener('loadedmetadata', start, { once: true });
}
