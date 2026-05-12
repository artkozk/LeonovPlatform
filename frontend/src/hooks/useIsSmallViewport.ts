import { useEffect, useState } from "react";

export function useIsSmallViewport(maxWidth: number): boolean {
  const query = `(max-width: ${maxWidth}px)`;
  const [isSmallViewport, setIsSmallViewport] = useState(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") return;

    const media = window.matchMedia(query);
    const update = (event: MediaQueryListEvent) => setIsSmallViewport(event.matches);

    setIsSmallViewport(media.matches);
    if (typeof media.addEventListener === "function") {
      media.addEventListener("change", update);
      return () => media.removeEventListener("change", update);
    }

    media.addListener(update);
    return () => media.removeListener(update);
  }, [query]);

  return isSmallViewport;
}
