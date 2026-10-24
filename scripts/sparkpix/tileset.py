"""Tileset layout and Tiled TSX export for Spark tilemaps."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import Image

from sparkpix.export import save_png, scale_nearest


@dataclass
class TileProps:
    walkable: Optional[bool] = None
    collision: Optional[str] = None
    blocks_pathfinding: Optional[bool] = None
    custom: Dict[str, str] = field(default_factory=dict)

    def spark_property_elements(self) -> List[ET.Element]:
        props: List[ET.Element] = []
        if self.walkable is not None:
            props.append(_prop("spark_walkable", str(self.walkable).lower()))
        if self.collision is not None:
            props.append(_prop("spark_collision", self.collision))
        if self.blocks_pathfinding is not None:
            props.append(_prop("spark_blocks_pathfinding", str(self.blocks_pathfinding).lower()))
        for k, v in sorted(self.custom.items()):
            props.append(_prop(k, v))
        return props


def _prop(name: str, value: str) -> ET.Element:
    el = ET.Element("property")
    el.set("name", name)
    el.set("value", value)
    return el


@dataclass
class TilesetBuilder:
    tile_width: int
    tile_height: int
    spacing: int = 0
    margin: int = 0
    columns: int = 0
    tiles: List[Image.Image] = field(default_factory=list)
    tile_props: Dict[int, TileProps] = field(default_factory=dict)
    name: str = "tileset"
    gameplay_id: Optional[str] = None

    def add_tile(self, image: Image.Image, props: Optional[TileProps] = None) -> int:
        if image.size != (self.tile_width, self.tile_height):
            raise ValueError(
                f"tile size must be {self.tile_width}x{self.tile_height}, got {image.size}"
            )
        idx = len(self.tiles)
        self.tiles.append(image.convert("RGBA"))
        if props:
            self.tile_props[idx] = props
        return idx

    def build_image(self) -> Image.Image:
        n = len(self.tiles)
        if n == 0:
            raise ValueError("no tiles")
        cols = self.columns if self.columns > 0 else max(1, int(n**0.5 + 0.999))
        rows = (n + cols - 1) // cols
        w = self.margin * 2 + cols * self.tile_width + (cols - 1) * self.spacing
        h = self.margin * 2 + rows * self.tile_height + (rows - 1) * self.spacing
        sheet = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for i, tile in enumerate(self.tiles):
            col = i % cols
            row = i // cols
            x = self.margin + col * (self.tile_width + self.spacing)
            y = self.margin + row * (self.tile_height + self.spacing)
            sheet.paste(tile, (x, y))
        self.columns = cols
        return sheet

    def export_tiled(
        self,
        out_dir: Path,
        image_basename: str = "tileset.png",
        tsx_basename: str = "tileset.tsx",
    ) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        sheet = self.build_image()
        save_png(sheet, out_dir / image_basename, scale=1)
        cols = self.columns
        n = len(self.tiles)
        img_w, img_h = sheet.size

        tileset = ET.Element("tileset")
        tileset.set("version", "1.8")
        tileset.set("tiledversion", "1.8.2")
        tileset.set("name", self.name)
        tileset.set("tilewidth", str(self.tile_width))
        tileset.set("tileheight", str(self.tile_height))
        tileset.set("spacing", str(self.spacing))
        tileset.set("margin", str(self.margin))
        tileset.set("tilecount", str(n))
        tileset.set("columns", str(cols))

        if self.gameplay_id:
            gp = ET.SubElement(tileset, "properties")
            gp.append(_prop("spark_tileset_gameplay", self.gameplay_id))

        image_el = ET.SubElement(tileset, "image")
        image_el.set("source", image_basename)
        image_el.set("width", str(img_w))
        image_el.set("height", str(img_h))

        for tid, props in sorted(self.tile_props.items()):
            tile_el = ET.SubElement(tileset, "tile")
            tile_el.set("id", str(tid))
            pel = ET.SubElement(tile_el, "properties")
            for p in props.spark_property_elements():
                pel.append(p)

        tsx_path = out_dir / tsx_basename
        tree = ET.ElementTree(tileset)
        ET.indent(tree, space=" ")
        tree.write(tsx_path, encoding="utf-8", xml_declaration=True)
        return tsx_path

    def export_spark_folder(self, spark_assets_root: Path, relative_dir: str) -> Path:
        """Write under spark/assets/sprites/<relative_dir>/."""
        target = spark_assets_root / "sprites" / relative_dir
        target.mkdir(parents=True, exist_ok=True)
        self.export_tiled(target)
        return target
