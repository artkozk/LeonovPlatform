type MonacoEditorLike = {
  layout?: () => void;
  render?: (forceRedraw?: boolean) => void;
};

type MonacoLike = {
  editor?: {
    remeasureFonts?: () => void;
  };
};

export function stabilizeMonacoLayout(
  editor: MonacoEditorLike | null | undefined,
  monaco: MonacoLike | null | undefined
): () => void {
  let disposed = false;
  let rafId: number | null = null;
  let timeoutId: number | null = null;

  const fontSet = typeof document !== "undefined" ? ((document as Document & { fonts?: FontFaceSet }).fonts ?? null) : null;

  const reflow = () => {
    if (disposed) return;
    monaco?.editor?.remeasureFonts?.();
    editor?.layout?.();
    editor?.render?.(true);
  };

  const reflowSoon = () => {
    reflow();
    if (typeof window !== "undefined") {
      window.requestAnimationFrame(() => {
        reflow();
      });
    }
  };

  reflowSoon();

  if (typeof window !== "undefined") {
    rafId = window.requestAnimationFrame(() => {
      reflow();
    });
    timeoutId = window.setTimeout(() => {
      reflow();
    }, 0);
  }

  const onFontsLoadingDone = () => {
    reflowSoon();
  };

  if (fontSet) {
    void fontSet.ready.then(() => {
      onFontsLoadingDone();
    });

    if (typeof fontSet.addEventListener === "function") {
      fontSet.addEventListener("loadingdone", onFontsLoadingDone);
      fontSet.addEventListener("loadingerror", onFontsLoadingDone);
    }
  }

  return () => {
    disposed = true;
    if (typeof window !== "undefined" && rafId !== null) {
      window.cancelAnimationFrame(rafId);
    }
    if (typeof window !== "undefined" && timeoutId !== null) {
      window.clearTimeout(timeoutId);
    }
    if (fontSet && typeof fontSet.removeEventListener === "function") {
      fontSet.removeEventListener("loadingdone", onFontsLoadingDone);
      fontSet.removeEventListener("loadingerror", onFontsLoadingDone);
    }
  };
}
