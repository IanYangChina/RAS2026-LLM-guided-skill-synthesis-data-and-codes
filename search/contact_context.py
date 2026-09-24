from __future__ import annotations
import math
from typing import Any
_MISSING = '—'

def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

def _metadata(trace: dict[str, Any]) -> dict[str, Any]:
    meta = _as_dict(trace.get('metadata'))
    return {**trace, **meta}

def _num(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None

def _fmt_num(value: Any, digits: int=3) -> str:
    val = _num(value)
    return _MISSING if val is None else f'{val:.{digits}f}'

def _fmt_int(value: Any) -> str:
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return _MISSING

def _fmt_vec(value: Any) -> str:
    if value is None:
        return _MISSING
    try:
        vals = [float(v) for v in value]
    except (TypeError, ValueError):
        return _MISSING
    if not vals:
        return _MISSING
    return '(' + ', '.join((f'{v:.3f}' for v in vals[:3])) + ')'

def _pair_parts(item: dict[str, Any]) -> tuple[tuple[str, str], tuple[str, str]]:
    a = (str(item.get('body_a') or _MISSING), str(item.get('geom_a') or _MISSING))
    b = (str(item.get('body_b') or _MISSING), str(item.get('geom_b') or _MISSING))
    ordered = sorted((a, b), key=lambda part: (part[0], part[1]))
    return (ordered[0], ordered[1])

def _fmt_pair(pair: tuple[tuple[str, str], tuple[str, str]]) -> str:
    return f'{pair[0][0]}/{pair[0][1]} ↔ {pair[1][0]}/{pair[1][1]}'

def _phase_key(item: dict[str, Any]) -> tuple[Any, str, str]:
    return (item.get('phase_index'), str(item.get('phase_name') or _MISSING), str(item.get('phase_type') or _MISSING))

def _row_key(item: dict[str, Any]) -> tuple[Any, str, str, tuple[tuple[str, str], tuple[str, str]]]:
    return (*_phase_key(item), _pair_parts(item))

def _row_from_event(event: dict[str, Any]) -> dict[str, Any]:
    force = _num(event.get('force')) or 0.0
    point = event.get('contact_point')
    distance = _num(event.get('contact_distance'))
    return {'phase_index': event.get('phase_index'), 'phase_name': event.get('phase_name'), 'phase_type': event.get('phase_type'), 'body_a': event.get('body_a'), 'geom_a': event.get('geom_a'), 'body_b': event.get('body_b'), 'geom_b': event.get('geom_b'), 'contact_count': 1, 'first_time': event.get('time'), 'first_step': event.get('sim_step'), 'max_force': force, 'mean_force': force, 'force_p95': force, 'contact_point_centroid': point, 'tcp_position_centroid': event.get('tcp_position'), 'min_contact_distance': distance, 'max_contact_distance': distance, 'involves_obstacle': event.get('involves_obstacle'), 'involves_robot_link': event.get('involves_robot_link'), 'involves_task_object': event.get('involves_task_object')}

def _aggregate_rows(rows: list[dict[str, Any]], total_events_by_trace: list[int | None]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, str, str, tuple[tuple[str, str], tuple[str, str]]], dict[str, Any]] = {}
    total_events = sum((v for v in total_events_by_trace if v is not None))
    for row in rows:
        key = _row_key(row)
        count = int(_num(row.get('contact_count')) or 0)
        if count <= 0:
            count = 1
        acc = grouped.setdefault(key, {'phase_index': key[0], 'phase_name': key[1], 'phase_type': key[2], 'pair': key[3], 'contact_count': 0, 'mean_force_weighted': 0.0, 'max_force': None, 'force_p95': None, 'first_time': None, 'first_step': None, 'point_weighted': [0.0, 0.0, 0.0], 'point_count': 0, 'tcp_weighted': [0.0, 0.0, 0.0], 'tcp_count': 0, 'min_contact_distance': None, 'max_contact_distance': None, 'involves_obstacle': False, 'involves_robot_link': False, 'involves_task_object': False})
        acc['contact_count'] += count
        mean_force = _num(row.get('mean_force'))
        if mean_force is not None:
            acc['mean_force_weighted'] += mean_force * count
        max_force = _num(row.get('max_force') or row.get('peak_force') or row.get('force'))
        if max_force is not None:
            acc['max_force'] = max(max_force, acc['max_force'] or max_force)
        p95 = _num(row.get('force_p95') or row.get('p95_force'))
        if p95 is not None:
            acc['force_p95'] = max(p95, acc['force_p95'] or p95)
        first_time = _num(row.get('first_time') or row.get('time'))
        if first_time is not None and (acc['first_time'] is None or first_time < acc['first_time']):
            acc['first_time'] = first_time
        first_step = _num(row.get('first_step') or row.get('sim_step'))
        if first_step is not None and (acc['first_step'] is None or first_step < acc['first_step']):
            acc['first_step'] = int(first_step)
        point = row.get('contact_point_centroid') or row.get('representative_contact_point') or row.get('contact_point')
        try:
            point_vals = [float(v) for v in point][:3]
        except (TypeError, ValueError):
            point_vals = []
        if len(point_vals) == 3:
            for (idx, val) in enumerate(point_vals):
                acc['point_weighted'][idx] += val * count
            acc['point_count'] += count
        tcp = row.get('tcp_position_centroid') or row.get('tcp_position')
        try:
            tcp_vals = [float(v) for v in tcp][:3]
        except (TypeError, ValueError):
            tcp_vals = []
        if len(tcp_vals) == 3:
            for (idx, val) in enumerate(tcp_vals):
                acc['tcp_weighted'][idx] += val * count
            acc['tcp_count'] += count
        min_distance = _num(row.get('min_contact_distance'))
        max_distance = _num(row.get('max_contact_distance'))
        distance = _num(row.get('contact_distance'))
        if min_distance is None:
            min_distance = distance
        if max_distance is None:
            max_distance = distance
        if min_distance is not None:
            acc['min_contact_distance'] = min_distance if acc['min_contact_distance'] is None else min(acc['min_contact_distance'], min_distance)
        if max_distance is not None:
            acc['max_contact_distance'] = max_distance if acc['max_contact_distance'] is None else max(acc['max_contact_distance'], max_distance)
        acc['involves_obstacle'] = acc['involves_obstacle'] or bool(row.get('involves_obstacle'))
        acc['involves_robot_link'] = acc['involves_robot_link'] or bool(row.get('involves_robot_link'))
        acc['involves_task_object'] = acc['involves_task_object'] or bool(row.get('involves_task_object'))
    output = []
    for acc in grouped.values():
        count = acc['contact_count']
        point = None
        if acc['point_count'] > 0:
            point = [v / acc['point_count'] for v in acc['point_weighted']]
        tcp = None
        if acc['tcp_count'] > 0:
            tcp = [v / acc['tcp_count'] for v in acc['tcp_weighted']]
        output.append({**acc, 'mean_force': acc['mean_force_weighted'] / count if count else None, 'event_fraction': count / total_events if total_events and count <= total_events else None, 'contact_point': point, 'tcp_position': tcp})
    return sorted(output, key=lambda row: (-int(bool(row['involves_obstacle'])), str(row['phase_name']), _fmt_pair(row['pair']), -float(row['max_force'] or 0.0)))

def _event_sort_key(event: dict[str, Any]) -> tuple[int, float, float, int, str]:
    force = _num(event.get('force')) or 0.0
    time = _num(event.get('time')) or 0.0
    episode = int(_num(event.get('episode_index')) or 0)
    return (-int(bool(event.get('involves_obstacle'))), -force, time, episode, _fmt_pair(_pair_parts(event)))

def format_contact_telemetry_block(traces: list[dict[str, Any]] | None, *, max_rows: int=12, max_events: int=5) -> str:
    lines = ['## Contact Telemetry', '']
    if not traces:
        lines.append('- No contact telemetry available in trace metadata.')
        return '\n'.join(lines)
    summary_rows: list[dict[str, Any]] = []
    raw_events: list[dict[str, Any]] = []
    total_events_by_trace: list[int | None] = []
    telemetry_seen = False
    for (trace_index, trace) in enumerate(traces):
        if not isinstance(trace, dict):
            continue
        meta = _metadata(trace)
        retention = _as_dict(meta.get('contact_event_retention'))
        total_events = _num(retention.get('total_events'))
        total_events_by_trace.append(int(total_events) if total_events is not None else None)
        trace_summary = meta.get('contact_event_summary')
        if isinstance(trace_summary, list):
            telemetry_seen = True
            summary_rows.extend((row for row in trace_summary if isinstance(row, dict)))
        trace_events = meta.get('contact_events')
        if isinstance(trace_events, list):
            telemetry_seen = True
            for event in trace_events:
                if isinstance(event, dict):
                    copied_event = dict(event)
                    if copied_event.get('episode_index') is None:
                        copied_event['episode_index'] = trace_index
                    raw_events.append(copied_event)
    if not telemetry_seen:
        lines.append('- No contact telemetry available in trace metadata.')
        return '\n'.join(lines)
    if not summary_rows and raw_events:
        summary_rows = [_row_from_event(event) for event in raw_events]
    if not summary_rows and (not raw_events):
        lines.append('- Contact telemetry fields are present; no contact events were recorded.')
        return '\n'.join(lines)
    aggregate_rows = _aggregate_rows(summary_rows, total_events_by_trace)
    lines.append('### Aggregate rows by phase and contact pair')
    lines.append('')
    lines.append('| Phase | Contact pair | Count / Event fraction | Force peak / p95 / mean (N) | First time / step | Point / TCP | Distance min / max | Flags |')
    lines.append('|---|---|---:|---:|---:|---|---:|---|')
    for row in aggregate_rows[:max_rows]:
        flags = ','.join((name for (name, key) in (('obstacle', 'involves_obstacle'), ('robot_link', 'involves_robot_link'), ('task_object', 'involves_task_object')) if row.get(key))) or _MISSING
        event_fraction = _fmt_num(row.get('event_fraction'), 3)
        count_rate = f"{row['contact_count']} / {event_fraction}" if event_fraction != _MISSING else str(row['contact_count'])
        phase = f"{row['phase_name']} [{row['phase_type']}]"
        force = f"{_fmt_num(row.get('max_force'))} / {_fmt_num(row.get('force_p95'))} / {_fmt_num(row.get('mean_force'))}"
        first = f"{_fmt_num(row.get('first_time'))} / {_fmt_int(row.get('first_step'))}"
        point_tcp = f"{_fmt_vec(row.get('contact_point'))} / {_fmt_vec(row.get('tcp_position'))}"
        distance = f"{_fmt_num(row.get('min_contact_distance'))} / {_fmt_num(row.get('max_contact_distance'))}"
        lines.append(f"| {phase} | {_fmt_pair(row['pair'])} | {count_rate} | {force} | {first} | {point_tcp} | {distance} | {flags} |")
    if len(aggregate_rows) > max_rows:
        lines.append(f'| … | … | showing {max_rows} of {len(aggregate_rows)} rows | … | … | … | … | … |')
    lines.append('')
    lines.append('### Critical raw contact events')
    lines.append('')
    if not raw_events:
        lines.append('- Raw contact events unavailable; aggregate summary only.')
        return '\n'.join(lines)
    lines.append('| Rank | Episode | Phase | Contact pair | Force (N) | Time / step | Point / Normal / TCP | Distance | Flags |')
    lines.append('|---:|---:|---|---|---:|---:|---|---:|---|')
    for (rank, event) in enumerate(sorted(raw_events, key=_event_sort_key)[:max_events], start=1):
        flags = ','.join((name for (name, key) in (('obstacle', 'involves_obstacle'), ('robot_link', 'involves_robot_link'), ('task_object', 'involves_task_object')) if event.get(key))) or _MISSING
        phase = f"{event.get('phase_name') or _MISSING} [{event.get('phase_type') or _MISSING}]"
        time_step = f"{_fmt_num(event.get('time'))} / {_fmt_int(event.get('sim_step'))}"
        lines.append(f"| {rank} | {_fmt_int(event.get('episode_index'))} | {phase} | {_fmt_pair(_pair_parts(event))} | {_fmt_num(event.get('force'))} | {time_step} | {_fmt_vec(event.get('contact_point'))} / {_fmt_vec(event.get('contact_normal'))} / {_fmt_vec(event.get('tcp_position'))} | {_fmt_num(event.get('contact_distance'))} | {flags} |")
    return '\n'.join(lines)
