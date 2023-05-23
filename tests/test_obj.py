from pathlib import Path
from sgi.obj import OBJReader, OBJWriter
from sgi.model import Vec2


def test_obj_import_export(tmp_path: Path) -> None:
    lines = [
        [Vec2(0, 1), Vec2(1.5, -25)],
        [Vec2(-3.1415, -2.71828), Vec2(0, 0)],
    ]

    faces = [
        [
            Vec2(0.2, 0.2),
            Vec2(0.8, 0.2),
            Vec2(0.6, 0.5),
            Vec2(0.8, 0.8),
            Vec2(0.2, 0.8),
            Vec2(0.4, 0.5),
        ]
    ]

    file_path = tmp_path / "test.obj" 

    writer = OBJWriter()
    for line in lines:
        writer.add_line(line)
    for face in faces:
        writer.add_face(face)
    writer.write(file_path)

    reader = OBJReader()
    reader.read(file_path)

    assert list(reader.iter_lines()) == lines
    assert list(reader.iter_faces()) == faces