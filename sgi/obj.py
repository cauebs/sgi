from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, NewType

from .model import Vec2


VertexIndex = NewType("VertexIndex", int)


@dataclass
class OBJWriter:
    _vertices: list[Vec2] = field(default_factory=list)
    _vertex_indices: dict[Vec2, VertexIndex] = field(default_factory=dict)
    _lines: list[list[VertexIndex]] = field(default_factory=list)
    _faces: list[list[VertexIndex]] = field(default_factory=list)

    def _get_vertex_index(self, vertex: Vec2) -> VertexIndex:
        if (index := self._vertex_indices.get(vertex)) is not None:
            return index
        
        self._vertices.append(vertex)
        index = VertexIndex(len(self._vertices))
        self._vertex_indices[vertex] = index
        return index

    def add_line(self, vertices: list[Vec2]) -> None:
        self._lines.append([
            self._get_vertex_index(v)
            for v in vertices
        ])

    def add_face(self, vertices: list[Vec2]) -> None:
        self._faces.append([
            self._get_vertex_index(v)
            for v in vertices
        ])

    def _serialize_vertex(self, vertex: Vec2) -> str:
        return f"v {vertex.x} {vertex.y} 0\n"

    def _serialize_line(self, indices: list[VertexIndex]) -> str:
        return f"l {' '.join(str(i) for i in indices)}\n"

    def _serialize_face(self, indices: list[VertexIndex]) -> str:
        return f"f {' '.join(str(i) for i in indices)}\n"

    def write(self, output: Path) -> None:
        with output.open('w') as f:
            for vertex in self._vertices:
                f.write(self._serialize_vertex(vertex))

            for line in self._lines:
                f.write(self._serialize_line(line))

            for face in self._faces:
                f.write(self._serialize_face(face))


class ParseError(Exception):
    ...


@dataclass
class OBJReader:
    _vertices: list[Vec2] = field(default_factory=list)
    _lines: list[list[Vec2]] = field(default_factory=list)
    _faces: list[list[Vec2]] = field(default_factory=list)

    def read(self, input: Path) -> None:
        with input.open('r') as f:
            for line in f.readlines():
                match line.split():
                    case ["v", x, y, z]:
                        vertex = Vec2(float(x), float(y))
                        self._vertices.append(vertex)
                    case ["l", *indices]:
                        vertices = [self._vertices[int(index) - 1] for index in indices]
                        self._lines.append(vertices)
                    case ["f", *indices]:
                        vertices = [self._vertices[int(index) - 1] for index in indices]
                        self._faces.append(vertices)
                    case _:
                        raise ParseError(line)
                    
    def iter_lines(self) -> Iterable[list[Vec2]]:
        yield from self._lines
                    
    def iter_faces(self) -> Iterable[list[Vec2]]:
        yield from self._faces