#!/usr/bin/env python3
from mesh import MeshNetwork
from gui import MeshGUIFancy


def main():
    mesh = MeshNetwork(rows=8, cols=8)
    gui = MeshGUIFancy(mesh)
    gui.run()


if __name__ == "__main__":
    main()

