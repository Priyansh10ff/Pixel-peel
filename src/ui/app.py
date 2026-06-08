"""
PixelPeel — Main Application Window
=====================================
Single‑file UI built on CustomTkinter.
Includes: sidebar, drag-and-drop zone, split before/after preview,
          batch processing queue, animated progress, dark / light themes.
"""
from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk

from src.processor import BackgroundProcessor
from src.ui.themes import COLORS, current, set_theme

# Optional drag-and-drop support (install tkinterdnd2 for full DnD)
try:
    from tkinterdnd2 import DND_FILES  # type: ignore  # noqa: F401

    _HAS_DND = True
except ImportError:
    _HAS_DND = False


# ─────────────────────────────────────────────────────────────────────────────
#  Main application
# ─────────────────────────────────────────────────────────────────────────────


class PixelPeelApp(ctk.CTk):
    """
    Primary application window for PixelPeel.

    Layout
    ------
    ┌─────────────┬──────────────────────────────────┐
    │             │  Tabs: [Single Image] [Batch]    │
    │  Sidebar    │  ┌──────────────────────────┐   │
    │  (settings) │  │  Drop Zone / Preview      │   │
    │             │  └──────────────────────────┘   │
    │             │  [Progress bar]                  │
    └─────────────┴──────────────────────────────────┘
    │  Status bar                                     │
    └─────────────────────────────────────────────────┘
    """

    VERSION = "1.0.0"
    _WIN_W, _WIN_H = 1160, 740
    _SIDEBAR_W = 260

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        super().__init__()

        # ── app state ──────────────────────────────────────────────────
        self.current_image_path: str | None = None
        self.original_image: Image.Image | None = None
        self.processed_image: Image.Image | None = None
        self.is_processing: bool = False
        self.batch_files: list[str] = []
        self.processed_count: int = 0
        self.is_dark: bool = True
        self._photo_refs: list = []          # keep PhotoImage refs alive
        self._split_pos: float = 0.5         # 0‥1 divider position
        self._dz_hovered: bool = False

        # ── settings vars ──────────────────────────────────────────────
        self.model_var  = ctk.StringVar(value="grabcut")
        self.format_var = ctk.StringVar(value="PNG")
        self.bg_opt_var = ctk.StringVar(value="Transparent")
        self.bg_hex: str = "#FFFFFF"
        self.output_folder: str = str(Path("output").resolve())

        # ── setup ──────────────────────────────────────────────────────
        self.processor = BackgroundProcessor()
        ctk.set_appearance_mode("dark")
        self._configure_window()
        self._build_ui()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _configure_window(self) -> None:
        self.title("  PixelPeel")
        self.geometry(f"{self._WIN_W}x{self._WIN_H}")
        self.minsize(900, 580)
        self.configure(fg_color=COLORS["bg"])

        # centre on screen
        self.update_idletasks()
        x = max(0, (self.winfo_screenwidth()  - self._WIN_W) // 2)
        y = max(0, (self.winfo_screenheight() - self._WIN_H) // 2 - 30)
        self.geometry(f"{self._WIN_W}x{self._WIN_H}+{x}+{y}")

    # ------------------------------------------------------------------
    # Root layout
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # horizontal split container
        self._main = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._main.grid(row=0, column=0, sticky="nsew")
        self._main.grid_columnconfigure(1, weight=1)
        self._main.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()
        self._build_statusbar()

    # ══════════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════════════

    def _build_sidebar(self) -> None:
        sb = ctk.CTkFrame(
            self._main,
            width=self._SIDEBAR_W,
            fg_color=COLORS["sidebar"],
            corner_radius=0,
        )
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_columnconfigure(0, weight=1)
        self._sb = sb

        # ── logo ───────────────────────────────────────────────────────
        lf = ctk.CTkFrame(sb, fg_color="transparent")
        lf.grid(row=0, column=0, sticky="ew", padx=18, pady=(22, 10))
        lf.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            lf, text="◆  PixelPeel",
            font=ctk.CTkFont(family="Helvetica", size=21, weight="bold"),
            text_color=COLORS["accent"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            lf, text="AI Background Remover",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["subtext"],
        ).grid(row=1, column=0, sticky="w")

        self._theme_btn = ctk.CTkButton(
            lf, text="☀", width=34, height=34,
            fg_color=COLORS["card"], hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=15),
            corner_radius=8,
            command=self._toggle_theme,
        )
        self._theme_btn.grid(row=0, column=1, rowspan=2)

        self._divider(sb, row=1)

        # ── AI Model ───────────────────────────────────────────────────
        self._section_label(sb, row=2, text="CV ALGORITHM")

        models_f = ctk.CTkFrame(sb, fg_color="transparent")
        models_f.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 4))

        _model_defs = [
            ("grabcut",        "GrabCut",      "Best balance of speed & quality"),
            ("grabcut_detail", "GrabCut HD",   "Finer edges  •  more iterations"),
            ("edge_refined",   "Edge Refine",  "Canny edges + morphology blend"),
            ("color_range",    "Color Range",  "Best for solid/gradient backgrounds"),
        ]
        for i, (key, label, desc) in enumerate(_model_defs):
            card = ctk.CTkFrame(models_f, fg_color=COLORS["card"], corner_radius=8)
            card.grid(row=i, column=0, sticky="ew", pady=3)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkRadioButton(
                card, text="", variable=self.model_var, value=key,
                width=22,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                command=self._on_model_change,
            ).grid(row=0, column=0, rowspan=2, padx=(10, 2), pady=8)

            ctk.CTkLabel(
                card, text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text"], anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(8, 1))

            ctk.CTkLabel(
                card, text=desc,
                font=ctk.CTkFont(size=10),
                text_color=COLORS["subtext"], anchor="w",
            ).grid(row=1, column=1, sticky="w", padx=(0, 8), pady=(0, 6))

        self._divider(sb, row=4)

        # ── Output format ──────────────────────────────────────────────
        self._section_label(sb, row=5, text="OUTPUT FORMAT")

        fmt_f = ctk.CTkFrame(sb, fg_color="transparent")
        fmt_f.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 6))

        ctk.CTkSegmentedButton(
            fmt_f,
            values=["PNG", "JPEG", "WEBP"],
            variable=self.format_var,
            fg_color=COLORS["card"],
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["card"],
            unselected_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_format_change,
        ).pack(fill="x")

        # ── Background colour ──────────────────────────────────────────
        bg_f = ctk.CTkFrame(sb, fg_color="transparent")
        bg_f.grid(row=7, column=0, sticky="ew", padx=18, pady=(2, 4))
        bg_f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bg_f, text="Background",
            font=ctk.CTkFont(size=12), text_color=COLORS["subtext"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        ctk.CTkSegmentedButton(
            bg_f,
            values=["Transparent", "White", "Custom"],
            variable=self.bg_opt_var,
            fg_color=COLORS["card"],
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["card"],
            unselected_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=11),
            command=self._on_bg_change,
        ).grid(row=0, column=1, sticky="ew")

        self._divider(sb, row=8)

        # ── Output folder ──────────────────────────────────────────────
        self._section_label(sb, row=9, text="OUTPUT FOLDER")

        ff = ctk.CTkFrame(sb, fg_color="transparent")
        ff.grid(row=10, column=0, sticky="ew", padx=18, pady=(0, 6))
        ff.grid_columnconfigure(0, weight=1)

        self._folder_entry = ctk.CTkEntry(
            ff,
            fg_color=COLORS["card"], border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=11), corner_radius=8,
        )
        self._folder_entry.insert(0, self.output_folder)
        self._folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            ff, text="📁", width=36, height=36,
            fg_color=COLORS["card"], hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=17), corner_radius=8,
            command=self._browse_output_folder,
        ).grid(row=0, column=1)

        # Spacer — pushes action buttons to the bottom
        sb.grid_rowconfigure(11, weight=1)

        # ── Action buttons ─────────────────────────────────────────────
        self._process_btn = ctk.CTkButton(
            sb,
            text="▶   Remove Background",
            height=48,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            command=self._process_single,
        )
        self._process_btn.grid(row=12, column=0, sticky="ew", padx=18, pady=(8, 4))

        self._save_btn = ctk.CTkButton(
            sb,
            text="💾   Save Result",
            height=40,
            fg_color=COLORS["card"], hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=13), corner_radius=10,
            command=self._save_result,
            state="disabled",
        )
        self._save_btn.grid(row=13, column=0, sticky="ew", padx=18, pady=(0, 22))

    # ── Sidebar helpers ────────────────────────────────────────────────

    def _divider(self, parent: ctk.CTkFrame, row: int) -> None:
        ctk.CTkFrame(parent, height=1, fg_color=COLORS["border"]).grid(
            row=row, column=0, sticky="ew", padx=18, pady=6
        )

    def _section_label(self, parent: ctk.CTkFrame, row: int, text: str) -> None:
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["subtext"], anchor="w",
        ).grid(row=row, column=0, sticky="ew", padx=18, pady=(4, 2))

    # ══════════════════════════════════════════════════════════════════
    #  CONTENT AREA
    # ══════════════════════════════════════════════════════════════════

    def _build_content(self) -> None:
        content = ctk.CTkFrame(self._main, fg_color=COLORS["bg"], corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        self._content = content

        self._tabs = ctk.CTkTabview(
            content,
            fg_color=COLORS["surface"],
            segmented_button_fg_color=COLORS["sidebar"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["sidebar"],
            segmented_button_unselected_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            corner_radius=14,
        )
        self._tabs.grid(row=0, column=0, sticky="nsew", padx=14, pady=12)

        self._tabs.add("  Single Image  ")
        self._tabs.add("  Batch Process  ")

        self._build_single_tab()
        self._build_batch_tab()

    # ── Single‑image tab ───────────────────────────────────────────────

    def _build_single_tab(self) -> None:
        tab = self._tabs.tab("  Single Image  ")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Drop zone / Preview container
        self._dz_outer = ctk.CTkFrame(
            tab, fg_color=COLORS["card"], corner_radius=16
        )
        self._dz_outer.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6, 6))
        self._dz_outer.grid_columnconfigure(0, weight=1)
        self._dz_outer.grid_rowconfigure(0, weight=1)

        # Progress row
        prog_f = ctk.CTkFrame(tab, fg_color="transparent")
        prog_f.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        prog_f.grid_columnconfigure(0, weight=1)

        self._prog_bar = ctk.CTkProgressBar(
            prog_f, height=6,
            fg_color=COLORS["border"], progress_color=COLORS["accent"],
            corner_radius=3,
        )
        self._prog_bar.grid(row=0, column=0, sticky="ew")
        self._prog_bar.set(0)

        self._prog_lbl = ctk.CTkLabel(
            prog_f, text="",
            font=ctk.CTkFont(size=11), text_color=COLORS["subtext"], anchor="e",
        )
        self._prog_lbl.grid(row=0, column=1, padx=(8, 0))

        self._show_dropzone()

    def _show_dropzone(self) -> None:
        """Render the initial empty drop‑zone state."""
        for w in self._dz_outer.winfo_children():
            w.destroy()

        self._dz_canvas = tk.Canvas(
            self._dz_outer,
            bg=current("card"),
            highlightthickness=0,
            cursor="hand2",
        )
        self._dz_canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self._dz_canvas.bind("<Configure>", lambda _e: self._draw_dropzone())
        self._dz_canvas.bind("<Button-1>",  lambda _e: self._browse_image())
        self._dz_canvas.bind("<Enter>",     self._dz_enter)
        self._dz_canvas.bind("<Leave>",     self._dz_leave)

        if _HAS_DND:
            self._dz_canvas.drop_target_register(DND_FILES)
            self._dz_canvas.dnd_bind("<<Drop>>", self._on_dnd_drop)

    def _draw_dropzone(self) -> None:
        c = self._dz_canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 20 or h < 20:
            self.after(50, self._draw_dropzone)
            return

        bg   = current("card")
        bord = current("accent") if self._dz_hovered else current("border")
        txt  = current("text")
        sub  = current("subtext")
        acc  = current("accent")

        c.configure(bg=bg)

        # dashed rounded border
        pad, r = 14, 14
        self._rounded_dash(c, pad, pad, w - pad, h - pad, r, bord, (9, 5), width=2)

        # upload icon drawn with canvas
        cx, cy = w // 2, h // 2
        icon_y = cy - 70

        # arrow shaft
        c.create_line(cx, icon_y + 50, cx, icon_y + 12, fill=acc, width=3, capstyle="round")
        # arrowhead
        c.create_polygon(
            cx, icon_y,
            cx - 16, icon_y + 22,
            cx + 16, icon_y + 22,
            fill=acc, outline="",
        )
        # base line
        c.create_line(cx - 22, icon_y + 55, cx + 22, icon_y + 55, fill=acc, width=3, capstyle="round")

        head = "Drop your image here" if _HAS_DND else "Click to browse images"
        c.create_text(cx, cy + 8,  text=head, font=("Helvetica", 17, "bold"), fill=txt)
        c.create_text(cx, cy + 36, text="or click to browse",    font=("Helvetica", 12), fill=sub)
        c.create_text(cx, cy + 58, text="PNG  ·  JPG  ·  WEBP  ·  BMP  ·  TIFF",
                      font=("Helvetica", 11), fill=sub)

    @staticmethod
    def _rounded_dash(
        canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int,
        r: int, color: str, dash: tuple, width: int = 2,
    ) -> None:
        """Draw a rounded-corner dashed rectangle on *canvas*."""
        kw = dict(fill=color, width=width, dash=dash)
        canvas.create_line(x1 + r, y1,      x2 - r, y1,      **kw)
        canvas.create_line(x2,     y1 + r,  x2,     y2 - r,  **kw)
        canvas.create_line(x2 - r, y2,      x1 + r, y2,      **kw)
        canvas.create_line(x1,     y2 - r,  x1,     y1 + r,  **kw)
        arc_kw = dict(style="arc", outline=color, width=width)
        canvas.create_arc(x1,      y1,      x1+r*2, y1+r*2, start= 90, extent=90, **arc_kw)
        canvas.create_arc(x2-r*2,  y1,      x2,     y1+r*2, start=  0, extent=90, **arc_kw)
        canvas.create_arc(x2-r*2,  y2-r*2,  x2,     y2,     start=270, extent=90, **arc_kw)
        canvas.create_arc(x1,      y2-r*2,  x1+r*2, y2,     start=180, extent=90, **arc_kw)

    def _dz_enter(self, _e=None) -> None:
        self._dz_hovered = True
        self._draw_dropzone()

    def _dz_leave(self, _e=None) -> None:
        self._dz_hovered = False
        self._draw_dropzone()

    # ── Preview panel ──────────────────────────────────────────────────

    def _show_preview(self) -> None:
        """Switch drop‑zone container to the split‑preview view."""
        for w in self._dz_outer.winfo_children():
            w.destroy()

        # Preview canvas
        self._prev_canvas = tk.Canvas(
            self._dz_outer,
            bg=current("bg"),
            highlightthickness=0,
            cursor="sb_h_double_arrow",
        )
        self._prev_canvas.grid(row=0, column=0, sticky="nsew")
        self._prev_canvas.bind("<Configure>",    lambda _e: self._redraw_preview())
        self._prev_canvas.bind("<ButtonPress-1>", self._on_split_drag)
        self._prev_canvas.bind("<B1-Motion>",     self._on_split_drag)

        # Bottom toolbar
        bar = ctk.CTkFrame(self._dz_outer, fg_color=COLORS["card"], height=44, corner_radius=0)
        bar.grid(row=1, column=0, sticky="ew")
        self._dz_outer.grid_rowconfigure(0, weight=1)
        self._dz_outer.grid_rowconfigure(1, weight=0)

        ctk.CTkButton(
            bar, text="📂  Load New Image", height=30,
            fg_color=COLORS["card"], hover_color=COLORS["border"],
            text_color=COLORS["text"], font=ctk.CTkFont(size=12),
            corner_radius=8, command=self._browse_image,
        ).pack(side="left", padx=10, pady=7)

        ctk.CTkLabel(
            bar, text="← Drag slider to compare →",
            font=ctk.CTkFont(size=11), text_color=COLORS["subtext"],
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            bar, text="🗑  Clear", height=30,
            fg_color=COLORS["card"], hover_color=COLORS["border"],
            text_color=COLORS["text"], font=ctk.CTkFont(size=12),
            corner_radius=8, command=self._clear_image,
        ).pack(side="right", padx=10, pady=7)

        self.after(30, self._redraw_preview)

    def _on_split_drag(self, event: tk.Event) -> None:
        w = self._prev_canvas.winfo_width()
        if w > 0:
            self._split_pos = max(0.02, min(0.98, event.x / w))
            self._redraw_preview()

    def _redraw_preview(self) -> None:
        if self.original_image is None:
            return
        c = self._prev_canvas
        W, H = c.winfo_width(), c.winfo_height()
        if W < 20 or H < 20:
            return

        is_dark = ctk.get_appearance_mode().lower() == "dark"
        bg_tuple = (13, 13, 15) if is_dark else (240, 243, 250)
        c.configure(bg="#0D0D0F" if is_dark else "#F0F3FA")
        c.delete("all")

        orig = self.original_image.convert("RGBA")
        proc = (self.processed_image or orig).convert("RGBA")

        orig_f = self._fit(orig, W, H)
        proc_f = self._fit(proc, W, H)

        ox = (W - orig_f.width)  // 2
        oy = (H - orig_f.height) // 2

        # Original (full canvas)
        base = Image.new("RGBA", (W, H), bg_tuple + (255,))
        base.paste(orig_f, (ox, oy), orig_f)

        # Processed with checkerboard background
        checker   = self._checkerboard(proc_f.width, proc_f.height)
        proc_comp = Image.new("RGBA", proc_f.size)
        proc_comp.paste(checker)
        proc_comp.paste(proc_f, mask=proc_f.split()[3])

        proc_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        proc_layer.paste(proc_comp, (ox, oy))

        # Composite at split
        sx = int(W * self._split_pos)
        final = base.copy()
        if sx < W:
            crop = proc_layer.crop((sx, 0, W, H))
            final.paste(crop, (sx, 0), crop)

        # Divider & handle
        draw = ImageDraw.Draw(final)
        draw.line([(sx, 0), (sx, H)], fill=(255, 255, 255, 210), width=2)
        hy, hr = H // 2, 20
        draw.ellipse([(sx-hr, hy-hr), (sx+hr, hy+hr)],
                     fill=(255, 255, 255, 240), outline=(180, 180, 180, 200), width=1)
        # ⟺ arrows inside handle
        draw.text((sx - 9, hy - 9), "⟺", fill=(80, 80, 80, 255))

        # Corner labels
        lbl = (255, 255, 255, 190)
        draw.text((ox + 10, oy + 8), "BEFORE", fill=lbl)
        draw.text((ox + orig_f.width - 62, oy + 8), "AFTER", fill=lbl)

        self._photo_refs.clear()
        photo = ImageTk.PhotoImage(final)
        self._photo_refs.append(photo)
        c.create_image(0, 0, anchor="nw", image=photo)

    # ── Batch tab ──────────────────────────────────────────────────────

    def _build_batch_tab(self) -> None:
        tab = self._tabs.tab("  Batch Process  ")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Controls row
        ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 4))

        for label, cmd, primary in [
            ("＋  Add Images",  self._batch_add_files,  True),
            ("📁  Add Folder",  self._batch_add_folder, False),
            ("✕  Clear All",   self._batch_clear,       False),
        ]:
            ctk.CTkButton(
                ctrl, text=label, height=36,
                fg_color=COLORS["accent"] if primary else COLORS["card"],
                hover_color=COLORS["accent_hover"] if primary else COLORS["border"],
                text_color="#FFFFFF" if primary else COLORS["text"],
                font=ctk.CTkFont(size=13, weight="bold" if primary else "normal"),
                corner_radius=8, command=cmd,
            ).pack(side="left", padx=(0, 6))

        self._batch_count_lbl = ctk.CTkLabel(
            ctrl, text="0 files",
            font=ctk.CTkFont(size=13), text_color=COLORS["subtext"],
        )
        self._batch_count_lbl.pack(side="right", padx=(0, 8))

        self._batch_run_btn = ctk.CTkButton(
            ctrl, text="▶  Process All", height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8, command=self._batch_process_all,
            state="disabled",
        )
        self._batch_run_btn.pack(side="right")

        # Scrollable file list
        self._batch_list = ctk.CTkScrollableFrame(
            tab, fg_color=COLORS["card"], corner_radius=12, label_text="",
        )
        self._batch_list.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 4))
        self._batch_list.grid_columnconfigure(0, weight=1)
        self._batch_items: list[ctk.CTkFrame] = []

        self._batch_empty = ctk.CTkLabel(
            self._batch_list,
            text="📂\n\nNo files added yet\nClick  ＋ Add Images  to get started",
            font=ctk.CTkFont(size=14), text_color=COLORS["subtext"],
        )
        self._batch_empty.pack(expand=True, pady=60)

        # Batch progress
        bp = ctk.CTkFrame(tab, fg_color="transparent")
        bp.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))
        bp.grid_columnconfigure(0, weight=1)

        self._batch_prog = ctk.CTkProgressBar(
            bp, height=6,
            fg_color=COLORS["border"], progress_color=COLORS["accent2"],
            corner_radius=3,
        )
        self._batch_prog.grid(row=0, column=0, sticky="ew")
        self._batch_prog.set(0)

        self._batch_prog_lbl = ctk.CTkLabel(
            bp, text="", font=ctk.CTkFont(size=11),
            text_color=COLORS["subtext"], anchor="e",
        )
        self._batch_prog_lbl.grid(row=0, column=1, padx=(8, 0))

    # ── Status bar ─────────────────────────────────────────────────────

    def _build_statusbar(self) -> None:
        sb = ctk.CTkFrame(self, height=32, fg_color=COLORS["sidebar"], corner_radius=0)
        sb.grid(row=1, column=0, sticky="ew")
        sb.grid_propagate(False)

        self._status_dot = ctk.CTkLabel(
            sb, text="●", font=ctk.CTkFont(size=10),
            text_color=COLORS["success"], width=16,
        )
        self._status_dot.pack(side="left", padx=(12, 2), pady=6)

        self._status_lbl = ctk.CTkLabel(
            sb, text="Ready",
            font=ctk.CTkFont(size=12), text_color=COLORS["text"],
        )
        self._status_lbl.pack(side="left", padx=(0, 14))

        ctk.CTkFrame(sb, width=1, height=16, fg_color=COLORS["border"]).pack(
            side="left", padx=4, pady=8
        )

        self._model_lbl = ctk.CTkLabel(
            sb, text="Mode: grabcut",
            font=ctk.CTkFont(size=11), text_color=COLORS["subtext"],
        )
        self._model_lbl.pack(side="left", padx=12)

        ctk.CTkFrame(sb, width=1, height=16, fg_color=COLORS["border"]).pack(
            side="left", padx=4, pady=8
        )

        self._count_lbl = ctk.CTkLabel(
            sb, text="0 processed",
            font=ctk.CTkFont(size=11), text_color=COLORS["subtext"],
        )
        self._count_lbl.pack(side="left", padx=12)

        ctk.CTkLabel(
            sb,
            text=f"PixelPeel v{self.VERSION}   ●   100% Local",
            font=ctk.CTkFont(size=11), text_color=COLORS["subtext"],
        ).pack(side="right", padx=16)

    # ══════════════════════════════════════════════════════════════════
    #  EVENT HANDLERS — sidebar
    # ══════════════════════════════════════════════════════════════════

    def _toggle_theme(self) -> None:
        if self.is_dark:
            set_theme("light")
            self._theme_btn.configure(text="🌙")
            self.is_dark = False
        else:
            set_theme("dark")
            self._theme_btn.configure(text="☀")
            self.is_dark = True
        # refresh canvas-based widgets after CTk redraws
        self.after(80, self._refresh_canvas)

    def _refresh_canvas(self) -> None:
        if self.original_image is not None:
            try:
                self._redraw_preview()
            except Exception:
                pass
        else:
            try:
                if hasattr(self, "_dz_canvas"):
                    self._dz_canvas.configure(bg=current("card"))
                    self._draw_dropzone()
            except Exception:
                pass

    def _on_model_change(self) -> None:
        labels = {
            "grabcut":        "grabcut",
            "grabcut_detail": "grabcut-hd",
            "edge_refined":   "edge-refine",
            "color_range":    "color-range",
        }
        self._model_lbl.configure(text=f"Mode: {labels.get(self.model_var.get())}")

    def _on_format_change(self, value: str) -> None:
        if value == "JPEG" and self.bg_opt_var.get() == "Transparent":
            self.bg_opt_var.set("White")

    def _on_bg_change(self, value: str) -> None:
        if value == "Custom":
            colour = colorchooser.askcolor(title="Pick Background Colour", color=self.bg_hex)
            if colour[1]:
                self.bg_hex = colour[1]

    def _browse_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self._folder_entry.delete(0, "end")
            self._folder_entry.insert(0, folder)

    # ══════════════════════════════════════════════════════════════════
    #  EVENT HANDLERS — image loading
    # ══════════════════════════════════════════════════════════════════

    def _browse_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif"),
                ("All Files",   "*.*"),
            ],
        )
        if path:
            self._load_image(path)

    def _on_dnd_drop(self, event: tk.Event) -> None:
        files = self.tk.splitlist(event.data)
        if files:
            self._load_image(files[0])

    def _load_image(self, path: str) -> None:
        try:
            img = Image.open(path).convert("RGBA")
            self.current_image_path = path
            self.original_image     = img
            self.processed_image    = None
            self._split_pos         = 0.5
            self._show_preview()
            self._set_status(f"Loaded: {Path(path).name}", "ready")
            self._save_btn.configure(state="disabled")
            self._prog_bar.set(0)
            self._prog_lbl.configure(text="")
        except Exception as exc:
            self._set_status(f"Error loading image: {exc}", "error")

    def _clear_image(self) -> None:
        self.current_image_path = None
        self.original_image     = None
        self.processed_image    = None
        self._prog_bar.set(0)
        self._prog_lbl.configure(text="")
        self._save_btn.configure(state="disabled")
        self._show_dropzone()
        self._set_status("Ready", "ready")

    # ══════════════════════════════════════════════════════════════════
    #  SINGLE‑IMAGE PROCESSING
    # ══════════════════════════════════════════════════════════════════

    def _process_single(self) -> None:
        if self.current_image_path is None:
            self._browse_image()
            return
        if self.is_processing:
            return

        self.is_processing = True
        self._process_btn.configure(text="⏳  Processing…", state="disabled")
        self._save_btn.configure(state="disabled")
        self._prog_bar.set(0)

        threading.Thread(target=self._process_worker, daemon=True).start()

    def _process_worker(self) -> None:
        def cb(frac: float, msg: str) -> None:
            self.after(0, lambda f=frac, m=msg: self._on_progress(f, m))

        try:
            model, fmt, bg_opt = (
                self.model_var.get(),
                self.format_var.get(),
                self.bg_opt_var.get(),
            )
            bg_color = self._resolve_bg(bg_opt)

            in_p  = Path(self.current_image_path)
            out_d = Path(self._folder_entry.get() or self.output_folder)
            out_d.mkdir(parents=True, exist_ok=True)
            ext   = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}.get(fmt, ".png")
            out_p = out_d / f"{in_p.stem}_nobg{ext}"

            self.processor.remove_background(
                str(in_p), str(out_p),
                model_name=model, bg_color=bg_color,
                output_format=fmt, progress_callback=cb,
            )

            result = Image.open(str(out_p)).convert("RGBA")
            self.after(0, lambda: self._on_done(result, str(out_p)))

        except Exception as exc:
            self.after(0, lambda e=str(exc): self._on_error(e))

    def _on_progress(self, frac: float, msg: str) -> None:
        self._prog_bar.set(frac)
        self._prog_lbl.configure(text=f"{int(frac * 100)}%")
        self._set_status(msg, "processing")

    def _on_done(self, result: Image.Image, out_path: str) -> None:
        self.processed_image = result
        self.is_processing   = False
        self.processed_count += 1
        self._process_btn.configure(text="▶   Remove Background", state="normal")
        self._save_btn.configure(state="normal")
        self._prog_bar.set(1.0)
        self._prog_lbl.configure(text="100%")
        self._count_lbl.configure(text=f"{self.processed_count} processed")
        self._split_pos = 0.5
        self._redraw_preview()
        self._set_status(f"✓  Saved → {Path(out_path).name}", "success")

    def _on_error(self, msg: str) -> None:
        self.is_processing = False
        self._process_btn.configure(text="▶   Remove Background", state="normal")
        self._prog_bar.set(0)
        self._prog_lbl.configure(text="")
        self._set_status(f"Error: {msg}", "error")

    def _save_result(self) -> None:
        if self.processed_image is None:
            return
        fmt = self.format_var.get()
        ext = {"PNG": "*.png", "JPEG": "*.jpg", "WEBP": "*.webp"}.get(fmt, "*.png")
        path = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=ext.replace("*", ""),
            filetypes=[("Image File", ext), ("All Files", "*.*")],
        )
        if path:
            try:
                img = self.processed_image.copy()
                if fmt == "JPEG" and img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(path)
                self._set_status(f"✓  Saved to {Path(path).name}", "success")
            except Exception as exc:
                self._set_status(f"Save failed: {exc}", "error")

    # ══════════════════════════════════════════════════════════════════
    #  BATCH PROCESSING
    # ══════════════════════════════════════════════════════════════════

    def _batch_add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif"),
                ("All Files",   "*.*"),
            ],
        )
        for p in paths:
            if p not in self.batch_files:
                self.batch_files.append(p)
                self._add_batch_row(p)
        self._update_batch_count()

    def _batch_add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Folder")
        if not folder:
            return
        exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}
        for p in sorted(Path(folder).iterdir()):
            if p.suffix.lower() in exts:
                s = str(p)
                if s not in self.batch_files:
                    self.batch_files.append(s)
                    self._add_batch_row(s)
        self._update_batch_count()

    def _add_batch_row(self, path: str) -> None:
        if self._batch_empty.winfo_exists():
            try:
                self._batch_empty.pack_forget()
            except Exception:
                pass

        row = len(self._batch_items)
        item = ctk.CTkFrame(self._batch_list, fg_color=COLORS["card"], corner_radius=8, height=46)
        item.grid(row=row, column=0, sticky="ew", pady=2, padx=4)
        item.grid_columnconfigure(1, weight=1)
        item.grid_propagate(False)

        status_lbl = ctk.CTkLabel(item, text="○", font=ctk.CTkFont(size=14),
                                  text_color=COLORS["subtext"], width=28)
        status_lbl.grid(row=0, column=0, padx=(10, 4), pady=14)

        ctk.CTkLabel(item, text=Path(path).name,
                     font=ctk.CTkFont(size=12), text_color=COLORS["text"],
                     anchor="w").grid(row=0, column=1, sticky="ew")

        size = Path(path).stat().st_size if Path(path).exists() else 0
        ctk.CTkLabel(item, text=self._fmt_size(size),
                     font=ctk.CTkFont(size=11), text_color=COLORS["subtext"],
                     width=64, anchor="e").grid(row=0, column=2, padx=(0, 10))

        item._status = status_lbl  # type: ignore[attr-defined]
        self._batch_items.append(item)

    def _batch_clear(self) -> None:
        self.batch_files.clear()
        for item in self._batch_items:
            item.destroy()
        self._batch_items.clear()
        self._batch_empty = ctk.CTkLabel(
            self._batch_list,
            text="📂\n\nNo files added yet\nClick  ＋ Add Images  to get started",
            font=ctk.CTkFont(size=14), text_color=COLORS["subtext"],
        )
        self._batch_empty.pack(expand=True, pady=60)
        self._update_batch_count()

    def _update_batch_count(self) -> None:
        n = len(self.batch_files)
        self._batch_count_lbl.configure(text=f"{n} file{'s' if n != 1 else ''}")
        self._batch_run_btn.configure(state="normal" if n > 0 else "disabled")

    def _batch_process_all(self) -> None:
        if not self.batch_files or self.is_processing:
            return
        self.is_processing = True
        self._batch_run_btn.configure(text="⏳  Processing…", state="disabled")
        self._batch_prog.set(0)
        threading.Thread(target=self._batch_worker, daemon=True).start()

    def _batch_worker(self) -> None:
        total    = len(self.batch_files)
        out_dir  = Path(self._folder_entry.get() or self.output_folder)
        out_dir.mkdir(parents=True, exist_ok=True)

        model   = self.model_var.get()
        fmt     = self.format_var.get()
        bg_opt  = self.bg_opt_var.get()
        bg_color = self._resolve_bg(bg_opt)
        ext     = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}.get(fmt, ".png")

        for idx, path in enumerate(self.batch_files):
            self.after(0, lambda i=idx, n=total: self._batch_tick(i, n, "proc"))
            try:
                inp = Path(path)
                outp = out_dir / f"{inp.stem}_nobg{ext}"
                self.processor.remove_background(
                    str(inp), str(outp),
                    model_name=model, bg_color=bg_color, output_format=fmt,
                )
                self.processed_count += 1
                self.after(0, lambda i=idx, n=total: self._batch_tick(i, n, "done"))
            except Exception:
                self.after(0, lambda i=idx, n=total: self._batch_tick(i, n, "err"))

        self.after(0, self._batch_complete)

    def _batch_tick(self, idx: int, total: int, status: str) -> None:
        frac = (idx + 1) / total
        self._batch_prog.set(frac)
        self._batch_prog_lbl.configure(text=f"{idx + 1}/{total}")
        self._count_lbl.configure(text=f"{self.processed_count} processed")

        icons  = {"proc": "⏳", "done": "✓", "err": "✗"}
        colors = {"proc": COLORS["warning"], "done": COLORS["success"], "err": COLORS["error"]}
        if idx < len(self._batch_items):
            lbl = self._batch_items[idx]._status  # type: ignore[attr-defined]
            lbl.configure(text=icons.get(status, "○"),
                          text_color=colors.get(status, COLORS["subtext"]))

    def _batch_complete(self) -> None:
        self.is_processing = False
        self._batch_run_btn.configure(text="▶  Process All", state="normal")
        self._batch_prog.set(1.0)
        n = len(self.batch_files)
        self._set_status(f"✓  Batch complete — {n} image{'s' if n != 1 else ''} processed", "success")

    # ══════════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════════

    def _set_status(self, msg: str, kind: str = "ready") -> None:
        dot_color = {
            "ready":      COLORS["success"],
            "processing": COLORS["warning"],
            "success":    COLORS["success"],
            "error":      COLORS["error"],
        }.get(kind, COLORS["success"])
        self._status_lbl.configure(text=msg)
        self._status_dot.configure(text_color=dot_color)

    def _resolve_bg(self, option: str) -> tuple[int, int, int] | None:
        """Convert bg option string to RGB tuple (or None for transparent)."""
        if option == "White":
            return (255, 255, 255)
        if option == "Custom":
            h = self.bg_hex.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
        return None   # Transparent

    @staticmethod
    def _fit(img: Image.Image, W: int, H: int) -> Image.Image:
        """Resize *img* to fit inside W×H preserving aspect ratio."""
        iw, ih = img.size
        scale  = min(W / iw, H / ih, 1.0)
        return img.resize((max(1, int(iw * scale)), max(1, int(ih * scale))), Image.LANCZOS)

    @staticmethod
    def _checkerboard(W: int, H: int, cell: int = 12) -> Image.Image:
        """Generate a grey checkerboard RGBA image at W×H."""
        try:
            import numpy as np
            xs, ys = np.arange(W) // cell, np.arange(H) // cell
            xg, yg = np.meshgrid(xs, ys)
            mask = ((xg + yg) % 2).astype(bool)
            arr  = np.zeros((H, W, 4), dtype=np.uint8)
            arr[ mask] = [205, 205, 205, 255]
            arr[~mask] = [165, 165, 165, 255]
            return Image.fromarray(arr, "RGBA")
        except ImportError:
            img = Image.new("RGBA", (W, H))
            px  = img.load()
            for y in range(H):
                for x in range(W):
                    px[x, y] = (205, 205, 205, 255) if ((x // cell) + (y // cell)) % 2 == 0 \
                               else (165, 165, 165, 255)
            return img

    @staticmethod
    def _fmt_size(n: int) -> str:
        if n < 1024:
            return f"{n} B"
        if n < 1024 ** 2:
            return f"{n // 1024} KB"
        return f"{n / 1024**2:.1f} MB"

    # ── Run ───────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start the Tk main event loop."""
        self.mainloop()
