import { useEffect, useMemo, useRef, useState } from "react";

export type TileOption = {
  src: string;
  weight: number;
};

export type TileBackgroundProps = {
  tiles: TileOption[];
  tileSize?: number;
  /** 0 = no darkening, 1 = fully black */
  dim?: number;
  className?: string;
  style?: React.CSSProperties;
};

function pickWeightedTile(tiles: TileOption[]): TileOption {
  const totalWeight = tiles.reduce((sum, t) => sum + t.weight, 0);
  const random = Math.random() * totalWeight;
  let cumulative = 0;
  for (const tile of tiles) {
    cumulative += tile.weight;
    if (random < cumulative) return tile;
  }
  return tiles[tiles.length - 1]!;
}

export function TileBackground({
  tiles,
  tileSize = 32,
  dim = 0,
  className,
  style,
}: TileBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry!.contentRect;
      setContainerSize({ width, height });
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const cols = Math.ceil(containerSize.width / tileSize);
  const rows = Math.ceil(containerSize.height / tileSize);

  // Derive a stable string key so inline array literals don't bust the memo
  // on every parent render (avoids full grid regeneration for the same tile set)
  const tilesKey = tiles.map((t) => `${t.src}:${t.weight}`).join(",");

  const generatedTiles = useMemo(() => {
    if (cols === 0 || rows === 0) return [];
    return Array.from({ length: cols * rows }, () => pickWeightedTile(tiles));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tilesKey, cols, rows]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        ...style,
      }}
    >
      <div
        aria-hidden="true"
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${cols}, ${tileSize}px)`,
          gridTemplateRows: `repeat(${rows}, ${tileSize}px)`,
          width: cols * tileSize,
          height: rows * tileSize,
        }}
      >
        {generatedTiles.map((tile, i) => (
          <div
            key={i}
            style={{
              width: tileSize,
              height: tileSize,
              backgroundImage: `url(${tile.src})`,
              backgroundSize: "cover",
              imageRendering: "pixelated",
            }}
          />
        ))}
      </div>
      {dim > 0 && (
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            backgroundColor: "black",
            opacity: dim,
            pointerEvents: "none",
          }}
        />
      )}
    </div>
  );
}
