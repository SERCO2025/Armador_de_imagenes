# -*- coding: utf-8 -*-
"""Punto de entrada inicial para Windows y Android.

Esta pantalla confirma que el paquete de la aplicación arranca. El procesamiento
real de imágenes se integrará progresivamente desde src/armador/core.py.
"""
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class ArmadorRoot(BoxLayout):
    def __init__(self, **kwargs):
        super(ArmadorRoot, self).__init__(orientation="vertical",
                                          padding=dp(24), spacing=dp(16),
                                          **kwargs)
        self.add_widget(Label(
            text="[b]Armador de Imágenes[/b]\n\n"
                 "Base inicial para Windows y Android.\n"
                 "El motor de recorte y empalme está en desarrollo.",
            markup=True, halign="center", valign="middle"
        ))
        self.status = Label(
            text="Estado: aplicación iniciada correctamente.",
            halign="center", valign="middle"
        )
        self.add_widget(self.status)
        self.add_widget(Button(
            text="Comprobar inicio",
            size_hint_y=None, height=dp(48),
            on_release=self.check_start
        ))

    def check_start(self, *_args):
        self.status.text = "La interfaz responde correctamente."


class ArmadorApp(App):
    title = "Armador de Imágenes"

    def build(self):
        return ArmadorRoot()


if __name__ == "__main__":
    ArmadorApp().run()
