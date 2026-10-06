import sys

if __name__ == "__main__":
    if "--arena" in sys.argv:
        from src.ui.arena_interface import ArenaApp
        ArenaApp().run()
    else:
        from src.ui.gui_interface import MenuGUI
        app = MenuGUI()
        app.iniciar()
