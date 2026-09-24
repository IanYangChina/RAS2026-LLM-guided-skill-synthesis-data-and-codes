from __future__ import annotations
import pathlib
from dsl import serialiser, validator

class LoadedSkill:

    def __init__(self, skill) -> None:
        object.__setattr__(self, '_loaded_skill_inner', skill)

    @property
    def skill(self) -> str:
        return object.__getattribute__(self, '_loaded_skill_inner').name

    def __getattr__(self, name: str):
        inner = object.__getattribute__(self, '_loaded_skill_inner')
        return getattr(inner, name)

    def __repr__(self) -> str:
        inner = object.__getattribute__(self, '_loaded_skill_inner')
        return f'LoadedSkill({inner!r})'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LoadedSkill):
            return object.__getattribute__(self, '_loaded_skill_inner') == object.__getattribute__(other, '_loaded_skill_inner')
        return NotImplemented

    def __hash__(self) -> int:
        return hash(object.__getattribute__(self, '_loaded_skill_inner'))

def load_skill(path: str | pathlib.Path) -> LoadedSkill:
    path = pathlib.Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Skill YAML not found: {path}')
    yaml_text = path.read_text(encoding='utf-8')
    skill = serialiser.load_skill(yaml_text)
    errors = validator.validate(skill)
    if errors:
        msg = '\n'.join((e.message for e in errors))
        raise ValueError(f"Validation errors in '{path}':\n{msg}")
    return LoadedSkill(skill)
