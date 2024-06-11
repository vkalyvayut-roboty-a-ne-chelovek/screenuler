import typing


def get_position(geometry: str) -> typing.Tuple:
    geom = geometry.split('x')[1].split('+')
    x = int(geom[1])
    y = int(geom[2])

    return x, y


def get_size(geometry: str) -> typing.Tuple:
    geom = geometry.split('+')[0].split('x')
    width = int(geom[0])
    height = int(geom[1])

    return width, height


def is_speedup_modifier_active(state) -> bool:
    return state & 0x0004 == 4
