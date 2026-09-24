from __future__ import annotations
import copy
import hashlib
import inspect
import json
import re
from collections import Counter
from typing import Any, Callable
SEMANTIC_CONTEXT_POLICY_VERSION = 'semantic-context-policy-v1'
REALIZED_SCENE_CONTEXT_CAPABILITY = True
REALIZED_SCENE_CONTEXT_VERSION = 'skill-synthesis-realized-scene-context-v1'
RETRY_POLICY_COMPLIANT = True
RETRY_POLICY_VERSION = 'semantic-retry-policy-v1'
MANIPULATION_CHECK_CAPABILITY = 'semantic-manipulation-check-v1'
REALIZED_SCENE_BLOCK_MARKER = '<!-- skill-synthesis:realized-scene:v1 -->'
SUPPORTED_CONDITIONS = frozenset({'full', 'no_history', 'no_contact_info', 'no_scene_description', 'misaligned_history', 'misattributed_contact', 'wrong_scene_targets'})

def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode('utf-8')).hexdigest()

def _without_dynamic_contact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _without_dynamic_contact(item) for (key, item) in value.items() if 'contact' not in key.lower() and 'collision' not in key.lower() and ('peak_force' not in key.lower()) and ('raw_peak' not in key.lower()) and ('force_compliance' not in key.lower())}
    if isinstance(value, list):
        return [_without_dynamic_contact(item) for item in value]
    return value

def full(context: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(context)

def no_history(context: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(context)
    result['history'] = []
    for retry in result.get('retries', {}).values():
        if isinstance(retry, dict):
            retry.pop('history_reference', None)
    return result

def no_contact_info(context: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(context)
    for phase in result.get('phase_feedback', []):
        if isinstance(phase, dict):
            phase.pop('contact_tuple', None)
    if 'contact_telemetry' in result:
        result['contact_telemetry'] = _without_dynamic_contact(result['contact_telemetry'])
        if isinstance(result['contact_telemetry'], dict):
            result['contact_telemetry'].pop('warnings', None)
    return result

def no_scene_description(context: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(context)
    for (section, key) in (('task_specification', 'realized_geometry'), ('scene_entities', 'landmarks'), ('freest_anchor_resolution', 'anchors')):
        if isinstance(result.get(section), dict) and key in result[section]:
            result[section][key] = {}
    return result

def misaligned_history(context: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(context)
    history = result.get('history', [])
    outcomes = [row.get('outcome') for row in history if isinstance(row, dict) and 'outcome' in row]
    for (row, outcome) in zip((row for row in history if isinstance(row, dict) and 'outcome' in row), reversed(outcomes)):
        row['outcome'] = outcome
    return result

def misattributed_contact(context: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(context)
    phases = result.get('phase_feedback', [])
    tuples = [phase.get('contact_tuple') for phase in phases if isinstance(phase, dict) and 'contact_tuple' in phase]
    for (phase, value) in zip((phase for phase in phases if isinstance(phase, dict) and 'contact_tuple' in phase), reversed(tuples)):
        phase['contact_tuple'] = value
    return result

def wrong_scene_targets(context: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(context)
    for (section, key) in (('task_specification', 'realized_geometry'), ('scene_entities', 'landmarks'), ('freest_anchor_resolution', 'anchors')):
        location = result.get(section, {}).get(key, {})
        if isinstance(location, dict) and len(location) > 1:
            names = sorted(location)
            values = [location[name] for name in names]
            for (name, value) in zip(names, values[1:] + values[:1]):
                location[name] = value
    return result
condition_policy_callables: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {'full': full, 'no_history': no_history, 'no_contact_info': no_contact_info, 'no_scene_description': no_scene_description, 'misaligned_history': misaligned_history, 'misattributed_contact': misattributed_contact, 'wrong_scene_targets': wrong_scene_targets}

def apply_policy(condition: str, context: dict[str, Any]) -> dict[str, Any]:
    try:
        return condition_policy_callables[condition](context)
    except KeyError as exc:
        raise ValueError(f'unknown semantic condition: {condition}') from exc

def _drop_markdown_section(lines: list[str], heading: str) -> list[str]:
    result: list[str] = []
    skipping = False
    for line in lines:
        if line == heading:
            skipping = True
            continue
        if skipping and line.startswith('#'):
            skipping = False
        if not skipping:
            result.append(line)
    return result

def _section_name(line: str) -> str | None:
    return line[3:].strip() if line.startswith('## ') else None

def _remove_section_fields(lines: list[str], section: str, prefixes: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    current_section: str | None = None
    for line in lines:
        current_section = _section_name(line) or current_section
        if current_section == section and line.startswith(prefixes):
            continue
        result.append(line)
    return result

def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip('|').split('|')]

def _format_table_cells(cells: list[str]) -> str:
    return '| ' + ' | '.join(cells) + ' |'

def _remove_table_columns(lines: list[str], section: str, dynamic_headers: frozenset[str]) -> list[str]:
    result = list(lines)
    current_section: str | None = None
    index = 0
    while index < len(result):
        current_section = _section_name(result[index]) or current_section
        if current_section != section or not result[index].lstrip().startswith('|'):
            index += 1
            continue
        headers = _table_cells(result[index])
        removed = {column for (column, header) in enumerate(headers) if header.strip().lower() in dynamic_headers}
        if not removed:
            index += 1
            continue
        while index < len(result) and result[index].lstrip().startswith('|'):
            cells = _table_cells(result[index])
            result[index] = _format_table_cells([cell for (column, cell) in enumerate(cells) if column not in removed])
            index += 1
    return result

def _remove_contact_prompt_telemetry(lines: list[str]) -> list[str]:
    lines = _drop_markdown_section(lines, '## Contact Telemetry')
    lines = _remove_section_fields(lines, 'Design Metrics', ('- **Force Compliance**:',))
    subscore_result: list[str] = []
    current_section: str | None = None
    for line in lines:
        current_section = _section_name(line) or current_section
        if current_section == 'Task Sub-Scores' and line.startswith('- '):
            field = line[2:].split(':', 1)[0].strip().lower()
            if any((token in field for token in ('contact', 'collision', 'force'))):
                continue
        subscore_result.append(line)
    lines = subscore_result
    lines = _remove_table_columns(lines, 'Per-Phase Performance', _DYNAMIC_CONTACT_HEADERS)
    lines = _remove_table_columns(lines, 'Last Optimised Execution State', _DYNAMIC_CONTACT_HEADERS)
    result: list[str] = []
    current_section: str | None = None
    skipping_diagnostics = False
    for line in lines:
        current_section = _section_name(line) or current_section
        if current_section == 'Per-Phase Performance' and line == '**Phase Failure Diagnostics:**':
            skipping_diagnostics = True
            continue
        if skipping_diagnostics and _section_name(line) is not None:
            skipping_diagnostics = False
        if not skipping_diagnostics:
            result.append(line)
    return result
_DYNAMIC_CONTACT_HEADERS = frozenset({'contact rate', 'contact rate / events', 'contact events', 'events', 'peak force', 'raw peak force', 'contact bodies', 'bodies', 'obstacle/contact', 'contact location', 'location'})
_DYNAMIC_CONTACT_KEY_PARTS = ('contact_detected', 'contact_event', 'contact_rate', 'peak_contact_force', 'raw_peak_contact_force', 'contact_bodies', 'contact_body', 'contact_location', 'collision', 'contact_score', 'force_compliance', 'raw_peak', 'peak_force', 'obstacle_contact', 'body1', 'body2')
_HISTORY_HEADING = '### Mutation History (most recent first)'
_NUMBER = '[-+]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][-+]?\\d+)?'
_VECTOR_RE = re.compile(f'(?P<open>[\\[(])\\s*(?P<a>{_NUMBER})\\s*,\\s*(?P<b>{_NUMBER})\\s*,\\s*(?P<c>{_NUMBER})\\s*(?P<close>[\\])])')

def _section_for_lines(lines: list[str]) -> list[str | None]:
    current: str | None = None
    result: list[str | None] = []
    for line in lines:
        if line.startswith('## '):
            current = line[3:].strip()
        result.append(current)
    return result

def _history_rows(lines: list[str]) -> list[tuple[int, str, tuple[str, str, str]]]:
    try:
        start = lines.index(_HISTORY_HEADING)
    except ValueError:
        return []
    rows: list[tuple[int, str, tuple[str, str, str]]] = []
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith('#'):
            break
        if not line.lstrip().startswith('|') or '---' in line:
            continue
        cells = _table_cells(line)
        if cells and cells[0].lower() == 'iter':
            continue
        if len(cells) < 4:
            continue
        prefix = _format_table_cells(cells[:-3])
        rows.append((index, prefix, tuple(cells[-3:])))
    return rows

def _tables(lines: list[str]) -> list[dict[str, Any]]:
    sections = _section_for_lines(lines)
    tables: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        if not lines[index].lstrip().startswith('|'):
            index += 1
            continue
        block_start = index
        while index < len(lines) and lines[index].lstrip().startswith('|'):
            index += 1
        block = lines[block_start:index]
        if len(block) < 2:
            continue
        headers = _table_cells(block[0])
        rows = []
        for (offset, line) in enumerate(block[2:], start=block_start + 2):
            cells = _table_cells(line)
            if len(cells) == len(headers):
                rows.append((offset, cells))
        tables.append({'section': sections[block_start], 'headers': headers, 'rows': rows})
    return tables

def _contact_table_records(lines: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for (table_index, table) in enumerate(_tables(lines)):
        headers = [header.lower() for header in table['headers']]
        if 'phase' not in headers:
            continue
        dynamic = [i for (i, header) in enumerate(headers) if header in _DYNAMIC_CONTACT_HEADERS]
        if not dynamic:
            continue
        phase_column = headers.index('phase')
        for (row_index, (line_index, cells)) in enumerate(table['rows']):
            records.append({'table': table_index, 'row': row_index, 'line': line_index, 'phase': cells[phase_column], 'columns': tuple(dynamic), 'tuple': tuple((cells[column] for column in dynamic))})
    return records

def _is_dynamic_contact_key(key: str) -> bool:
    normal = key.lower().replace(' ', '_').replace('/', '_')
    return normal in {'events', 'rate', 'bodies', 'location'} or any((part in normal for part in _DYNAMIC_CONTACT_KEY_PARTS))

def _transform_json_blocks(lines: list[str], transform: Callable[[Any], Any]) -> list[str]:
    result = list(lines)
    index = 0
    while index < len(result):
        if result[index].strip() != '```json':
            index += 1
            continue
        end = next((i for i in range(index + 1, len(result)) if result[i].strip() == '```'), None)
        if end is None:
            break
        raw = '\n'.join(result[index + 1:end])
        try:
            value = json.loads(raw)
        except (TypeError, ValueError):
            index = end + 1
            continue
        changed = transform(value)
        if changed != value:
            result[index + 1:end] = [_canonical_json(changed)]
            end = index + 2
        index = end + 1
    return result

def _remove_dynamic_contact_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _remove_dynamic_contact_json(item) for (key, item) in value.items() if not _is_dynamic_contact_key(str(key))}
    if isinstance(value, list):
        return [_remove_dynamic_contact_json(item) for item in value]
    return value

def _permute_phase_contact_json(value: Any) -> Any:
    if isinstance(value, list):
        transformed = [_permute_phase_contact_json(item) for item in value]
        phase_rows = [item for item in transformed if isinstance(item, dict) and any((key in item for key in ('phase', 'phase_name', 'phase_id'))) and any((_is_dynamic_contact_key(str(key)) for key in item))]
        if len(phase_rows) >= 2:
            tuples = [{key: copy.deepcopy(item[key]) for key in item if _is_dynamic_contact_key(str(key))} for item in phase_rows]
            if len({_canonical_json(item) for item in tuples}) >= 2:
                rotated = tuples[1:] + tuples[:1]
                for (item, contact) in zip(phase_rows, rotated):
                    for key in [key for key in item if _is_dynamic_contact_key(str(key))]:
                        del item[key]
                    item.update(contact)
        return transformed
    if isinstance(value, dict):
        return {key: _permute_phase_contact_json(item) for (key, item) in value.items()}
    return value

def _permute_history(lines: list[str]) -> list[str]:
    rows = _history_rows(lines)
    outcomes = [row[2] for row in rows]
    if len(rows) < 2 or len(set(outcomes)) < 2:
        return lines
    rotated = outcomes[1:] + outcomes[:1]
    result = list(lines)
    for ((line_index, prefix, _), outcome) in zip(rows, rotated):
        result[line_index] = prefix[:-1] + ' | ' + ' | '.join(outcome) + ' |'
    return result

def _permute_contact_tables(lines: list[str]) -> list[str]:
    result = list(lines)
    for table in _tables(lines):
        headers = [header.lower() for header in table['headers']]
        dynamic = [i for (i, header) in enumerate(headers) if header in _DYNAMIC_CONTACT_HEADERS]
        if 'phase' not in headers or not dynamic or len(table['rows']) < 2:
            continue
        tuples = [tuple((cells[column] for column in dynamic)) for (_, cells) in table['rows']]
        if len(set(tuples)) < 2:
            continue
        rotated = tuples[1:] + tuples[:1]
        for ((line_index, cells), contact_tuple) in zip(table['rows'], rotated):
            for (column, item) in zip(dynamic, contact_tuple):
                cells[column] = item
            result[line_index] = _format_table_cells(cells)
    return result
_SCENE_TASK_PREFIXES = ('- Frozen realised-scene', '- Frozen object start:', '- Frozen task target:', '- Frozen socket pose:', '- Frozen initial hinge angle:', '- Goal TCP position:', '- Goal object position:', '- place_goal_position ', '- Object initial pose:', '- Robot initial TCP position:', '- Channel axis:', '- Phase navigation guidance:')
_CRITICAL_LABEL_PARTS = ('object start', 'object initial', 'task target', 'goal object', 'place_goal', 'socket pose', 'fixture pose', 'initial hinge angle', 'target_hinge_angle', 'robot initial tcp')
_LEGACY_REALIZED_SCENE_BLOCK_LABELS = frozenset({'Realized scene facts (canonical JSON):', 'Realized scene facts (concise typed schema):'})

def _realized_json_block_ranges(lines: list[str]) -> list[tuple[int, int, int]]:
    ranges: list[tuple[int, int, int]] = []
    index = 0
    while index < len(lines):
        if lines[index] == REALIZED_SCENE_BLOCK_MARKER:
            block_start = index
            fence_start = index + 1
        elif lines[index] in _LEGACY_REALIZED_SCENE_BLOCK_LABELS:
            block_start = index
            fence_start = index + 1
        else:
            index += 1
            continue
        search_limit = min(len(lines), fence_start + 5)
        while fence_start < search_limit and lines[fence_start].strip() != '```json' and (not lines[fence_start].startswith('#')) and (lines[fence_start] != REALIZED_SCENE_BLOCK_MARKER):
            fence_start += 1
        if fence_start >= search_limit or lines[fence_start].strip() != '```json':
            index += 1
            continue
        fence_end = next((position for position in range(fence_start + 1, len(lines)) if lines[position].strip() == '```'), None)
        if fence_end is None:
            break
        ranges.append((block_start, fence_start, fence_end))
        index = fence_end + 1
    return ranges

def _remove_realized_json_blocks(lines: list[str]) -> list[str]:
    removed_lines = {line_index for (block_start, _, fence_end) in _realized_json_block_ranges(lines) for line_index in range(block_start, fence_end + 1)}
    result: list[str] = []
    for (index, source_line) in enumerate(lines):
        if index in removed_lines:
            continue
        line = source_line
        if 'Configuration SHA-256:' in line and 'realized-scene SHA-256:' in line:
            line = re.sub('; realized-scene SHA-256: `[^`]+`', '', line)
        result.append(line)
    return result

def _remove_scene_prompt_description(lines: list[str]) -> list[str]:
    lines = _drop_markdown_section(lines, '## Scene Entities')
    lines = _remove_section_fields(lines, 'Task Specification', _SCENE_TASK_PREFIXES)
    current_section: str | None = None
    result: list[str] = []
    coordinate_suffix = re.compile('(offset from (?:object initial position|task goal position|fixture pose)) \\([^|]+\\)(\\s*\\|)')
    for line in lines:
        current_section = _section_name(line) or current_section
        if current_section == 'Subtask Layer' and line.lstrip().startswith('|'):
            line = coordinate_suffix.sub('\\1\\2', line)
        result.append(line)
    return _remove_realized_json_blocks(result)

def _critical_scene_values(lines: list[str]) -> tuple[list[tuple[float, float, float]], list[float]]:
    sections = _section_for_lines(lines)
    vectors: list[tuple[float, float, float]] = []
    scalars: list[float] = []
    for (section, line) in zip(sections, lines):
        lower = line.lower()
        if section != 'Task Specification' or not any((part in lower for part in _CRITICAL_LABEL_PARTS)):
            continue
        for match in _VECTOR_RE.finditer(line):
            vectors.append(tuple((float(match.group(name)) for name in ('a', 'b', 'c'))))
        if not _VECTOR_RE.search(line):
            match = re.search(_NUMBER, line.split(':', 1)[-1])
            if match:
                scalars.append(float(match.group()))
    return (list(dict.fromkeys(vectors)), list(dict.fromkeys(scalars)))

def _replace_vector(match: re.Match[str], mapping: dict[tuple[float, float, float], tuple[float, float, float]]) -> str:
    value = tuple((float(match.group(name)) for name in ('a', 'b', 'c')))
    replacement = mapping.get(value)
    if replacement is None:
        return match.group(0)
    (opening, closing) = (match.group('open'), match.group('close'))
    return opening + ', '.join((str(item) for item in replacement)) + closing

def _replace_scalar(match: re.Match[str], mapping: dict[float, float]) -> str:
    replacement = mapping.get(float(match.group()))
    return str(replacement) if replacement is not None else match.group()

def _scene_json_landmarks(value: Any) -> tuple[list[tuple[float, float, float]], list[float]]:
    if not isinstance(value, dict):
        return ([], [])
    vectors: list[tuple[float, float, float]] = []
    for (category, field) in (('object_starts', 'position'), ('targets', 'position'), ('fixtures', 'position'), ('anchors', 'value')):
        rows = value.get(category, [])
        if isinstance(rows, list):
            for row in rows:
                candidate = row.get(field) if isinstance(row, dict) else None
                if isinstance(candidate, list) and len(candidate) == 3 and all((isinstance(item, (int, float)) for item in candidate)):
                    vectors.append(tuple((float(item) for item in candidate)))
    door = value.get('door')
    if isinstance(door, dict):
        panel = door.get('panel')
        position = panel.get('position') if isinstance(panel, dict) else None
        if isinstance(position, list) and len(position) == 3 and all((isinstance(item, (int, float)) for item in position)):
            vectors.append(tuple((float(item) for item in position)))
        scalars = [float(door[key]) for key in ('initial_hinge_angle', 'target_hinge_angle') if isinstance(door.get(key), (int, float))]
    else:
        scalars = []
    return (list(dict.fromkeys(vectors)), list(dict.fromkeys(scalars)))

def _permute_scene_targets(lines: list[str]) -> list[str]:
    (vectors, scalars) = _critical_scene_values(lines)
    vector_map = dict(zip(vectors, vectors[1:] + vectors[:1])) if len(vectors) >= 2 else {}
    scalar_map = dict(zip(scalars, scalars[1:] + scalars[:1])) if len(scalars) >= 2 else {}
    sections = _section_for_lines(lines)
    result: list[str] = []
    for (section, line) in zip(sections, lines):
        lower = line.lower()
        allowed = section == 'Task Specification' and any((part in lower for part in _CRITICAL_LABEL_PARTS)) or section == 'Scene Entities' or (section == 'Subtask Layer' and 'offset from' in lower)
        if allowed and vector_map:
            line = _VECTOR_RE.sub(lambda match: _replace_vector(match, vector_map), line)
        if allowed and scalar_map and any((part in lower for part in ('hinge_angle', 'hinge angle'))):
            line = re.sub(_NUMBER, lambda match: _replace_scalar(match, scalar_map), line)
        result.append(line)

    def transform_scene_json(value: Any, local_vector_map: dict[tuple[float, float, float], tuple[float, float, float]], local_scalar_map: dict[float, float], *, active: bool=False, key: str='') -> Any:
        if isinstance(value, dict):
            transformed: dict[str, Any] = {}
            for (child_key, item) in value.items():
                child_active = active or child_key in {'object_starts', 'targets', 'fixtures', 'anchors', 'door'}
                transformed[child_key] = transform_scene_json(item, local_vector_map, local_scalar_map, active=child_active, key=str(child_key))
            return transformed
        if isinstance(value, list):
            if active and len(value) == 3 and all((isinstance(item, (int, float)) for item in value)):
                return list(local_vector_map.get(tuple((float(item) for item in value)), tuple(value)))
            return [transform_scene_json(item, local_vector_map, local_scalar_map, active=active, key=key) for item in value]
        if active and key in {'initial_hinge_angle', 'target_hinge_angle'} and isinstance(value, (int, float)):
            return local_scalar_map.get(float(value), value)
        return value
    for (_, start, end) in reversed(_realized_json_block_ranges(result)):
        try:
            value = json.loads('\n'.join(result[start + 1:end]))
        except ValueError:
            continue
        (local_vectors, local_scalars) = _scene_json_landmarks(value)
        local_vector_map = dict(zip(local_vectors, local_vectors[1:] + local_vectors[:1])) if len(local_vectors) >= 2 else {}
        local_scalar_map = dict(zip(local_scalars, local_scalars[1:] + local_scalars[:1])) if len(local_scalars) >= 2 else {}
        if local_vector_map or local_scalar_map:
            transformed = transform_scene_json(value, local_vector_map, local_scalar_map)
            result[start + 1:end] = [_canonical_json(transformed)]
    return result

def apply_prompt_text(condition: str, prompt: str) -> str:
    if condition == 'full':
        return prompt
    lines = prompt.splitlines()
    if condition == 'no_history':
        lines = _drop_markdown_section(lines, '### Mutation History (most recent first)')
        prompt_without_history = '\n'.join(lines)
        prompt_without_history = re.sub('RETRY NOTE:.*?(?:\\n\\n|$)', 'Retry: propose a different structure without relying on prior outcomes.\n\n', prompt_without_history, flags=re.DOTALL)
        return prompt_without_history
    elif condition == 'no_contact_info':
        lines = _remove_contact_prompt_telemetry(lines)
        lines = _transform_json_blocks(lines, _remove_dynamic_contact_json)
    elif condition == 'no_scene_description':
        lines = _remove_scene_prompt_description(lines)
    elif condition == 'misaligned_history':
        lines = _permute_history(lines)
    elif condition == 'misattributed_contact':
        lines = _permute_contact_tables(lines)
        lines = _transform_json_blocks(lines, _permute_phase_contact_json)
    elif condition == 'wrong_scene_targets':
        lines = _permute_scene_targets(lines)
    return '\n'.join(lines)

def _history_projection(prompt: str) -> tuple[list[str], list[tuple[str, str, str]]]:
    rows = _history_rows(prompt.splitlines())
    return ([row[1] for row in rows], [row[2] for row in rows])

def _contact_projection(prompt: str) -> tuple[list[tuple[Any, ...]], list[tuple[str, ...]]]:
    records = _contact_table_records(prompt.splitlines())
    identities = [(row['table'], row['row'], row['phase'], row['columns']) for row in records]
    values: list[tuple[str, ...]] = [row['tuple'] for row in records]

    def collect(value: Any, location: tuple[Any, ...]=()) -> None:
        if isinstance(value, dict):
            phase = next((value[key] for key in ('phase', 'phase_name', 'phase_id') if key in value), None)
            contact = tuple(sorted(((str(key), _canonical_json(item)) for (key, item) in value.items() if _is_dynamic_contact_key(str(key))), key=lambda item: item[0]))
            if phase is not None and contact:
                identities.append(('json', location, str(phase), tuple((key for (key, _) in contact))))
                values.append(tuple((item for (_, item) in contact)))
            for (key, item) in value.items():
                collect(item, (*location, key))
        elif isinstance(value, list):
            for (index, item) in enumerate(value):
                collect(item, (*location, index))
    lines = prompt.splitlines()
    index = 0
    block_number = 0
    while index < len(lines):
        if lines[index].strip() != '```json':
            index += 1
            continue
        end = next((i for i in range(index + 1, len(lines)) if lines[i].strip() == '```'), None)
        if end is None:
            break
        try:
            collect(json.loads('\n'.join(lines[index + 1:end])), (block_number,))
        except ValueError:
            pass
        block_number += 1
        index = end + 1
    return (identities, values)

def _scene_projection(prompt: str) -> tuple[list[tuple[float, float, float]], list[float]]:
    lines = prompt.splitlines()
    (vectors, scalars) = _critical_scene_values(lines)
    for (_, start, end) in _realized_json_block_ranges(lines):
        try:
            (block_vectors, block_scalars) = _scene_json_landmarks(json.loads('\n'.join(lines[start + 1:end])))
        except ValueError:
            continue
        vectors.extend(block_vectors)
        scalars.extend(block_scalars)
    return (vectors, scalars)

def _permutation_from_values(before: list[Any], after: list[Any]) -> list[int]:
    if len(before) != len(after):
        return []
    unmatched = list(range(len(before)))
    permutation: list[int] = []
    for value in after:
        match = next((index for index in unmatched if before[index] == value), None)
        if match is None:
            return []
        unmatched.remove(match)
        permutation.append(match)
    return permutation

def _removal_target_count(condition: str, prompt: str) -> int:
    lines = prompt.splitlines()
    if condition == 'no_history':
        return len(_history_rows(lines)) + int('RETRY NOTE:' in prompt)
    if condition == 'no_contact_info':
        table_values = sum((len(row['tuple']) for row in _contact_table_records(lines)))
        (_, json_values) = _contact_projection(prompt)
        table_record_count = len(_contact_table_records(lines))
        json_contact_values = json_values[table_record_count:]
        named = sum((1 for line in lines if 'Force Compliance' in line or line == '## Contact Telemetry'))
        return table_values + sum((len(value) for value in json_contact_values)) + named
    if condition == 'no_scene_description':
        sections = _section_for_lines(lines)
        return len(_realized_json_block_ranges(lines)) + sum((1 for (section, line) in zip(sections, lines) if section == 'Scene Entities' or (section == 'Task Specification' and line.startswith(_SCENE_TASK_PREFIXES)) or (section == 'Subtask Layer' and 'offset from' in line and _VECTOR_RE.search(line)) or (line in _LEGACY_REALIZED_SCENE_BLOCK_LABELS)))
    return 0

def prompt_manipulation_evidence(condition: str, pre_prompt: str, post_prompt: str) -> dict[str, Any]:
    expected = apply_prompt_text(condition, pre_prompt)
    exact_policy_output = post_prompt == expected
    changed = pre_prompt != post_prompt
    applicable = False
    reason = ''
    target_absent = False
    multiset_preserved = False
    non_identity = False
    permutation: list[int] = []
    if condition == 'full':
        reason = 'control_identity'
        only_target_changed = exact_policy_output and (not changed)
    elif condition in {'no_history', 'no_contact_info', 'no_scene_description'}:
        before_count = _removal_target_count(condition, pre_prompt)
        after_count = _removal_target_count(condition, post_prompt)
        applicable = before_count > 0
        reason = '' if applicable else {'no_history': 'empty_history', 'no_contact_info': 'no_dynamic_contact', 'no_scene_description': 'no_realized_geometry'}[condition]
        target_absent = after_count == 0
        only_target_changed = exact_policy_output
    elif condition == 'misaligned_history':
        (before_identity, before_values) = _history_projection(pre_prompt)
        (after_identity, after_values) = _history_projection(post_prompt)
        applicable = len(before_values) >= 2 and len(set(before_values)) >= 2
        reason = '' if applicable else 'insufficient_history_prefix'
        permutation = _permutation_from_values(before_values, after_values)
        multiset_preserved = Counter(before_values) == Counter(after_values)
        non_identity = bool(permutation and permutation != list(range(len(permutation))))
        only_target_changed = exact_policy_output and before_identity == after_identity
    elif condition == 'misattributed_contact':
        (before_identity, before_values) = _contact_projection(pre_prompt)
        (after_identity, after_values) = _contact_projection(post_prompt)
        applicable = expected != '\n'.join(pre_prompt.splitlines())
        reason = '' if applicable else 'insufficient_contact_phases'
        permutation = _permutation_from_values(before_values, after_values)
        multiset_preserved = Counter(before_values) == Counter(after_values)
        non_identity = bool(permutation and permutation != list(range(len(permutation))))
        only_target_changed = exact_policy_output and before_identity == after_identity
    elif condition == 'wrong_scene_targets':
        (before_vectors, before_scalars) = _scene_projection(pre_prompt)
        (after_vectors, after_scalars) = _scene_projection(post_prompt)
        before_values: list[Any] = [*(('v', value) for value in before_vectors), *(('s', value) for value in before_scalars)]
        after_values: list[Any] = [*(('v', value) for value in after_vectors), *(('s', value) for value in after_scalars)]
        applicable = (len(before_vectors) >= 2 or len(before_scalars) >= 2) and len(set(before_values)) >= 2
        reason = '' if applicable else 'insufficient_scene_targets'
        permutation = _permutation_from_values(before_values, after_values)
        multiset_preserved = Counter(before_values) == Counter(after_values)
        non_identity = bool(permutation and permutation != list(range(len(permutation))))
        only_target_changed = exact_policy_output
    else:
        raise ValueError(f'unknown semantic condition: {condition}')
    applied = applicable and changed and exact_policy_output
    return {'applicable': applicable, 'applied': applied, 'non_applicable_reason': reason, 'target_absent': target_absent, 'only_target_changed': only_target_changed, 'multiset_preserved': multiset_preserved, 'non_identity_outcome': non_identity, 'outcome_permutation': permutation}

def condition_policy_implementation_hash(condition: str) -> str:
    return hashlib.sha256(inspect.getsource(condition_policy_callables[condition]).encode('utf-8')).hexdigest()

