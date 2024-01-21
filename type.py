from typing import Type, TypeVar


class Geometry: 
    pass


T = TypeVar('T', bound=Geometry)
# M = TypeVar('M', int, float)

class Point2D(Geometry):
    pass


def factory_point(cls_geometry: Type[T]) -> T:
    """cls_geometry -- Класс!!!"""
    return cls_geometry()


geometry: Geometry = factory_point(Geometry)
point: Point2D = factory_point(Point2D)
