# -*- coding: utf-8 -*-
"""Interfaz inicial para emparejar y unir capturas localmente.

Los originales nunca se modifican. La detección de solapamiento es una
propuesta revisable: el usuario puede ajustar los píxeles antes de guardar.
"""
from __future__ import print_function

import io
import os
import sys
import traceback
# PyInstaller --windowed puede dejar stdout/stderr como None.
# Kivy inicializa su logger durante el import y necesita streams escribibles.
# Solo sustituirlos cuando no existen; no alterar la consola ni Android.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput

# En Android no solicitar permisos durante la importación del módulo.
# Hacerlo antes de que Kivy/SDL2 termine de inicializar puede provocar un
# cambio de foco durante el arranque y cerrar el proceso nativo.
# The app runs from the repository root on Windows and from the APK package
# root on Android. Add src explicitly so the same core module works in both.
_SOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _SOURCE_DIR not in sys.path:
    sys.path.insert(0, _SOURCE_DIR)

from armador.core import (
    pair_images, find_vertical_overlap, stitch_vertical,
    detect_side_borders, crop_side_borders,
)


def _button(text, callback, height=44):
    return Button(text=text, size_hint_y=None, height=dp(height),
                  on_release=callback)


class ArmadorRoot(BoxLayout):
    def __init__(self, **kwargs):
        super(ArmadorRoot, self).__init__(
            orientation="vertical", padding=dp(10), spacing=dp(7), **kwargs
        )
        self.folder = os.path.expanduser("~")
        self.scan_result = None
        self.current_pair = None
        self.top_image = None
        self.bottom_image = None
        self.joined_image = None
        self.overlap_slider = None
        self.pair_index = -1
        self._pending_border_crop = None

        self.add_widget(Label(
            text="[b]Armador de Imágenes[/b]",
            markup=True, size_hint_y=None, height=dp(34),
            font_size="20sp"
        ))

        folder_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
        self.folder_input = TextInput(
            text=self.folder, multiline=False, write_tab=False,
            size_hint_x=1
        )
        folder_row.add_widget(self.folder_input)
        folder_row.add_widget(_button("Carpeta…", self.choose_folder, 42))
        self.add_widget(folder_row)
        self.add_widget(_button("Analizar carpeta", self.scan_folder, 42))

        self.summary = Label(
            text="Selecciona la carpeta que contiene capturas llamadas "
                 "'Nombre 1.png' y 'Nombre 2.png'.",
            size_hint_y=None, height=dp(48), halign="left", valign="middle"
        )
        self.summary.bind(size=self._fit_label)
        self.add_widget(self.summary)

        self.list_scroll = ScrollView(size_hint_y=0.32)
        self.pair_list = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(4)
        )
        self.pair_list.bind(minimum_height=self.pair_list.setter("height"))
        self.list_scroll.add_widget(self.pair_list)
        self.add_widget(self.list_scroll)

        self.selection_label = Label(
            text="Selecciona una pareja para ver la unión.",
            size_hint_y=None, height=dp(28), halign="left", valign="middle"
        )
        self.selection_label.bind(size=self._fit_label)
        self.add_widget(self.selection_label)

        self.overlap_label = Label(
            text="Solapamiento: sin calcular",
            size_hint_y=None, height=dp(26)
        )
        self.add_widget(self.overlap_label)
        self.slider_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        self.slider_value = Label(text="—", size_hint_x=0.18)
        self.slider_row.add_widget(self.slider_value)
        self.slider_holder = BoxLayout()
        self.slider_row.add_widget(self.slider_holder)
        self.add_widget(self.slider_row)

        actions = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
        actions.add_widget(_button("Bordes", self.propose_border_crop, 42))
        actions.add_widget(_button("Solapamiento", self.detect_overlap, 42))
        actions.add_widget(_button("Guardar PNG", self.save_join, 42))
        actions.add_widget(_button("Siguiente", self.next_pair, 42))
        self.add_widget(actions)

        self.preview = KivyImage(
            allow_stretch=True, keep_ratio=True, size_hint_y=1
        )
        self.add_widget(self.preview)

        self.footer = Label(
            text="Los originales permanecen intactos.",
            size_hint_y=None, height=dp(22)
        )
        self.add_widget(self.footer)

    @staticmethod
    def _fit_label(widget, _size):
        widget.text_size = (max(0, widget.width - dp(8)), None)

    def choose_folder(self, *_args):
        # Solicitar acceso al almacenamiento solo cuando el usuario lo necesita.
        # Así evitamos abrir el diálogo Android mientras SDL2 está arrancando.
        try:
            from android.permissions import request_permissions, Permission
            request_permissions(
                [
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                ],
                self._on_storage_permissions,
            )
            return
        except ImportError:
            # Ejecución de escritorio: no existe el módulo android.
            pass
        self._open_folder_chooser()

    def _on_storage_permissions(self, _permissions, _grants):
        self._open_folder_chooser()

    def _open_folder_chooser(self):
        start = self.folder_input.text.strip() or os.path.expanduser("~")
        if not os.path.isdir(start):
            start = os.path.expanduser("~")
        chooser = FileChooserListView(path=start, dirselect=True)
        layout = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(8))
        layout.add_widget(chooser)
        controls = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        popup = Popup(title="Seleccionar carpeta", content=layout,
                      size_hint=(0.96, 0.92), auto_dismiss=False)
        controls.add_widget(_button("Cancelar", lambda *_: popup.dismiss(), 44))

        def use_folder(*_args):
            selected = chooser.selection[0] if chooser.selection else chooser.path
            if os.path.isdir(selected):
                self.folder_input.text = selected
                popup.dismiss()
            else:
                self.footer.text = "Selecciona una carpeta, no un archivo."

        controls.add_widget(_button("Usar esta carpeta", use_folder, 44))
        layout.add_widget(controls)
        popup.open()

    def scan_folder(self, *_args):
        folder = os.path.abspath(os.path.expanduser(self.folder_input.text.strip()))
        if not os.path.isdir(folder):
            self._message("Carpeta inválida", "La ruta no existe o no es una carpeta.")
            return
        try:
            paths = [
                os.path.join(folder, name)
                for name in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, name))
            ]
            self.scan_result = pair_images(paths)
        except Exception as exc:
            self._message("No se pudo analizar", str(exc))
            return

        self.folder = folder
        self.pair_list.clear_widgets()
        self.current_pair = None
        self.top_image = None
        self.bottom_image = None
        self.joined_image = None
        self.preview.texture = None
        pairs = self.scan_result["pairs"]
        incomplete = self.scan_result["incomplete"]
        ambiguous = self.scan_result["ambiguous"]
        unmatched = self.scan_result["unmatched"]
        self.summary.text = (
            "Parejas: %d | Incompletas: %d | Ambiguas: %d | Sin pareja: %d"
            % (len(pairs), len(incomplete), len(ambiguous), len(unmatched))
        )

        for pair in pairs:
            label = "%s  (1 + 2)" % pair["base_name"]
            self.pair_list.add_widget(_button(
                label, lambda _button, selected=pair: self.select_pair(selected), 40
            ))
        for item in incomplete:
            part = "falta la captura 1" if item["missing_part"] == "top" else "falta la captura 2"
            self.pair_list.add_widget(Label(
                text="Incompleta: %s — %s" % (item["base_name"], part),
                size_hint_y=None, height=dp(30), color=(1, 0.65, 0.25, 1)
            ))
        for item in ambiguous:
            self.pair_list.add_widget(Label(
                text="Ambigua: %s — revisa archivos duplicados" % item["base_name"],
                size_hint_y=None, height=dp(30), color=(1, 0.35, 0.3, 1)
            ))
        if not pairs and not incomplete and not ambiguous:
            self.pair_list.add_widget(Label(
                text="No se encontraron nombres con formato 'Nombre 1.ext' / 'Nombre 2.ext'.",
                size_hint_y=None, height=dp(52)
            ))
        self.footer.text = "El análisis solo lee nombres; no modifica ningún archivo."

    def select_pair(self, pair):
        try:
            from PIL import Image
            top = Image.open(pair["top"])
            bottom = Image.open(pair["bottom"])
            # Materialize independent pixel data and close source file handles.
            top.load()
            bottom.load()
            if top.width != bottom.width:
                self._message(
                    "Anchos diferentes",
                    "Las capturas miden %d y %d píxeles de ancho. "
                    "Esta versión requiere el mismo ancho y no las escalará."
                    % (top.width, bottom.width)
                )
                top.close()
                bottom.close()
                return
            if top.mode != bottom.mode:
                # Converting color mode changes representation, not dimensions;
                # make the mode explicit so the core can paste safely.
                bottom = bottom.convert(top.mode)
            self.current_pair = pair
            self.pair_index = next((i for i, candidate in enumerate(
                self.scan_result["pairs"] if self.scan_result else [])
                if candidate == pair), self.pair_index)
            self.top_image = top.copy()
            self.bottom_image = bottom.copy()
            self.joined_image = None
            self.selection_label.text = "%s — %dx%d + %dx%d" % (
                pair["base_name"], top.width, top.height, bottom.width, bottom.height
            )
            self.overlap_slider = Slider(
                min=1, max=max(1, min(top.height, bottom.height) - 1),
                value=max(1, min(40, min(top.height, bottom.height) - 1)),
                step=1
            )
            self.overlap_slider.bind(value=self.on_overlap_change)
            self.slider_holder.clear_widgets()
            self.slider_holder.add_widget(self.overlap_slider)
            self.on_overlap_change(self.overlap_slider, self.overlap_slider.value)
            self.detect_overlap()
        except Exception as exc:
            self._message("No se pudieron abrir las capturas", str(exc))


    def propose_border_crop(self, *_args):
        if self.top_image is None or self.bottom_image is None:
            self.footer.text = "Primero selecciona una pareja."
            return
        try:
            top_bounds = detect_side_borders(self.top_image)
            bottom_bounds = detect_side_borders(self.bottom_image)
            top_removed = (top_bounds[0], self.top_image.width - top_bounds[1])
            bottom_removed = (bottom_bounds[0], self.bottom_image.width - bottom_bounds[1])
            if top_bounds == (0, self.top_image.width) and bottom_bounds == (
                    0, self.bottom_image.width):
                self._message(
                    "Sin bordes detectados",
                    "No se encontraron bordes laterales oscuros suficientemente uniformes. "
                    "No se modificó ninguna imagen."
                )
                return
            if top_bounds[1] - top_bounds[0] != bottom_bounds[1] - bottom_bounds[0]:
                self._message(
                    "Recorte no aplicado",
                    "Los recortes propuestos dejarían anchos diferentes: captura 1 = %d px; "
                    "captura 2 = %d px. No se aplicó el recorte para evitar deformar o "
                    "desplazar contenido. Revisa las imágenes manualmente."
                    % (top_bounds[1] - top_bounds[0],
                       bottom_bounds[1] - bottom_bounds[0])
                )
                return
            self._pending_border_crop = (top_bounds, bottom_bounds)
            body = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
            message = (
                "Propuesta de recorte lateral (sin escalar):\n\n"
                "Captura 1: quitar %d px izquierda y %d px derecha.\n"
                "Captura 2: quitar %d px izquierda y %d px derecha.\n\n"
                "¿Aplicar estos recortes a la vista de trabajo? Los archivos originales "
                "seguirán intactos."
                % (top_removed[0], top_removed[1], bottom_removed[0], bottom_removed[1])
            )
            label = Label(text=message, halign="left", valign="middle")
            label.bind(size=self._fit_label)
            body.add_widget(label)
            controls = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
            popup = Popup(title="Revisar bordes", content=body,
                          size_hint=(0.92, 0.55), auto_dismiss=False)
            controls.add_widget(_button("Cancelar", lambda *_: popup.dismiss(), 44))

            def apply_crop(*_args):
                bounds = self._pending_border_crop
                if not bounds:
                    popup.dismiss()
                    return
                self.top_image = crop_side_borders(self.top_image, bounds[0])
                self.bottom_image = crop_side_borders(self.bottom_image, bounds[1])
                self._pending_border_crop = None
                self.joined_image = None
                self.selection_label.text = "%s — bordes recortados: %dx%d + %dx%d" % (
                    self.current_pair["base_name"],
                    self.top_image.width, self.top_image.height,
                    self.bottom_image.width, self.bottom_image.height
                )
                self.overlap_slider.max = max(
                    1, min(self.top_image.height, self.bottom_image.height) - 1
                )
                self.overlap_slider.value = min(
                    self.overlap_slider.value, self.overlap_slider.max
                )
                self.detect_overlap()
                popup.dismiss()
                self.footer.text = "Recorte aplicado solo a la copia de trabajo; originales intactos."

            controls.add_widget(_button("Aplicar recorte", apply_crop, 44))
            body.add_widget(controls)
            popup.open()
        except Exception as exc:
            self._message("No se pudieron detectar los bordes", str(exc))

    def next_pair(self, *_args):
        pairs = self.scan_result["pairs"] if self.scan_result else []
        if not pairs:
            self.footer.text = "Analiza una carpeta y selecciona una pareja primero."
            return
        next_index = (self.pair_index + 1) % len(pairs)
        self.select_pair(pairs[next_index])

    def detect_overlap(self, *_args):
        if self.top_image is None or self.bottom_image is None:
            self.footer.text = "Primero selecciona una pareja."
            return
        try:
            proposal = find_vertical_overlap(
                self.top_image, self.bottom_image,
                min_overlap=1,
                max_overlap=max(1, min(self.top_image.height,
                                       self.bottom_image.height) - 1),
                stride=1
            )
            self.overlap_slider.value = proposal["overlap_pixels"]
            confidence = "revisión recomendada" if proposal["needs_review"] else "propuesta automática"
            self.overlap_label.text = "Solapamiento sugerido: %d px (%s)" % (
                proposal["overlap_pixels"], confidence
            )
            self.footer.text = (
                "Comprueba visualmente la unión y ajusta los píxeles antes de guardar."
            )
        except Exception as exc:
            self._message("No se pudo estimar el solapamiento", str(exc))

    def on_overlap_change(self, _slider, value):
        amount = int(round(value))
        self.slider_value.text = "%d px" % amount
        if self.top_image is None or self.bottom_image is None:
            return
        try:
            self.joined_image = stitch_vertical(
                self.top_image, self.bottom_image, amount
            )
            self._show_preview(self.joined_image)
            self.overlap_label.text = "Solapamiento: %d px — revisa la vista previa" % amount
        except Exception as exc:
            self.footer.text = "No se pudo preparar la vista previa: %s" % exc

    def _show_preview(self, image):
        # Resize only the on-screen preview. The image saved to disk retains
        # its actual pixel dimensions and is never resampled by this preview.
        preview = image.copy()
        preview.thumbnail((1200, 900))
        stream = io.BytesIO()
        preview.save(stream, format="PNG")
        stream.seek(0)
        self.preview.texture = CoreImage(stream, ext="png").texture

    def save_join(self, *_args):
        if self.current_pair is None or self.joined_image is None:
            self.footer.text = "Selecciona una pareja antes de guardar."
            return
        folder = os.path.dirname(self.current_pair["top"])
        base = os.path.splitext(os.path.basename(self.current_pair["output_name"]))[0]
        destination = os.path.join(folder, base + ".png")
        suffix = 1
        while os.path.exists(destination):
            destination = os.path.join(folder, "%s_unido_%d.png" % (base, suffix))
            suffix += 1
        try:
            self.joined_image.save(destination, format="PNG")
            self.footer.text = "Guardado: %s (%d x %d px)" % (
                os.path.basename(destination),
                self.joined_image.width, self.joined_image.height
            )
            self._message(
                "Unión guardada",
                "%s\n%d × %d píxeles\n\nLos archivos originales no se modificaron."
                % (destination, self.joined_image.width, self.joined_image.height)
            )
        except Exception as exc:
            self._message("No se pudo guardar", str(exc))

    def _message(self, title, message):
        body = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        label = Label(text=message, halign="left", valign="middle")
        label.bind(size=self._fit_label)
        body.add_widget(label)
        body.add_widget(_button("Cerrar", lambda *_: popup.dismiss(), 42))
        popup = Popup(title=title, content=body, size_hint=(0.9, 0.55))
        popup.open()


class ArmadorApp(App):
    title = "Armador de Imágenes"

    def build(self):
        return ArmadorRoot()


if __name__ == "__main__":
    ArmadorApp().run()
