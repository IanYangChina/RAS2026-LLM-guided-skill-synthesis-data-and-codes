from __future__ import annotations
import argparse
import copy
import datetime
import hashlib
import json
import math
import os
import random
import re
import subprocess
import sys
import time
import yaml
from dataclasses import replace as _dc_replace
from numbers import Real
from pathlib import Path
import numpy as np
os.environ.setdefault('MUJOCO_GL', 'osmesa')
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DEEPSEEK_PROVIDER = 'deepseek'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DEFAULT_LLM_MODEL = 'deepseek-v4-flash'
MAX_LLM_PROMPT_CHARS = 100000
MAX_REPLAY_PHASES = 32
MAX_REPLAY_CONTACTS = 16
MAX_REPLAY_TRACES_PER_CONFIG = 3
PROMPT_FLOAT_DIGITS = 5
from compiler.codegen import compile as compile_skill
from dsl.nodes import Skill
from dsl.serialiser import dump_skill, load_skill
from dsl.subtask_sanitizer import sanitize_subtasks
from dsl.validator import validate
from evaluation.metrics import split_optimiser_posthoc_diagnostics
from evaluation.runner import run_evaluation
from evaluation.task_spec import SubtaskSpec, TaskSpec
from scripts.task_configs import TASK_CONFIGS, SIM_CONFIGS
from search.archive import SkillArchive
from search.parameter_optimiser import optimise_parameters
from search.proposal_metrics import append_proposal_attempt, build_attempt_record, build_evaluated_proposal_metrics
from search.context_blinding import anonymise_text, deanonymise_yaml, neutralise_scene_entities, neutralise_task_name, numeric_only_context, parse_numeric_only_response, wrong_image_skill_path, wrong_image_task_for
from search.proposer import format_proposal_context_v2
from search.semantic_context_policy import REALIZED_SCENE_BLOCK_MARKER
from simulation.mujoco_backend import MuJoCoBackend
from simulation.realized_scene import RealizedSceneConfigBank, RealizedSceneSnapshot, activate_realized_scene_configuration, canonical_realized_scene_json, coerce_realized_scene, materialize_realized_scene_config_bank, realized_scene_snapshot_hash
from simulation.scene import SceneConfig
from simulation.scene_info import get_scene_entities
from search.scaffold_init import sample_scaffold_skill, GrammarUniformInitialiser
_PROMPTS_DIR = PROJECT_ROOT / 'search' / 'prompts'
_CONDITION_PROMPT_FILE: dict[str, str] = {'full': 'skill_proposer_full.txt', 'text_only': 'skill_proposer_text_only.txt', 'text_reward': 'skill_proposer_text_reward.txt', 'text_vision': 'skill_proposer_text_vision.txt', 'no_scene_entities': 'skill_proposer_full.txt', 'no_history': 'skill_proposer_full.txt', 'no_task_subscores': 'skill_proposer_full.txt', 'creation': 'create_skill.txt', 'anonymised_dsl': 'skill_proposer_full.txt', 'no_task_language': 'skill_proposer_full.txt', 'wrong_image': 'skill_proposer_full.txt', 'numeric_only': 'skill_proposer_numeric_only.txt', 'semantics_ablation_contact_info': 'skill_proposer_full.txt', 'no_contact_info': 'skill_proposer_full.txt', 'no_scene_description': 'skill_proposer_full.txt', 'misaligned_history': 'skill_proposer_full.txt', 'misattributed_contact': 'skill_proposer_full.txt', 'wrong_scene_targets': 'skill_proposer_full.txt'}
_VISUAL_CONTEXT_CONDITIONS = frozenset({'text_vision', 'full', 'no_scene_entities', 'no_history', 'no_task_subscores', 'anonymised_dsl', 'wrong_image', 'semantics_ablation_contact_info'})

def _is_visual_context_condition(condition: str) -> bool:
    return condition in _VISUAL_CONTEXT_CONDITIONS

def _json_compatible(value: object) -> object:
    if isinstance(value, np.ndarray):
        if value.dtype.hasobject:
            raise TypeError('NumPy object arrays are not JSON serializable')
        return _json_compatible(value.tolist())
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.complexfloating):
        raise TypeError('NumPy complex scalars are not JSON serializable')
    if isinstance(value, dict):
        return {key: _json_compatible(item) for (key, item) in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_compatible(item) for item in value]
    return value

def _json_dumps(obj: object, **kw: object) -> str:
    kw['allow_nan'] = False
    return json.dumps(_json_compatible(obj), **kw)

def _dicts_to_subtask_specs(subtask_dicts: tuple[dict, ...]) -> tuple[SubtaskSpec, ...]:
    specs = []
    for d in subtask_dicts:
        sid = d['id']
        if 'anchor' not in d or 'target_entity' not in d:
            missing = [f for f in ('anchor', 'target_entity') if f not in d]
            raise ValueError(f"free-subtask '{sid}' missing required field(s): {missing}")
        specs.append(SubtaskSpec(id=sid, target_entity=d['target_entity'], metric=d.get('metric', 'distance'), anchor=d['anchor'], offset=tuple(d.get('offset', [0.0, 0.0, 0.0])), param_offset_key=d.get('param_offset_key'), weight=float(d.get('weight', 1.0))))
    return tuple(specs)

def _apply_free_subtasks(skill, task_spec: TaskSpec, subtask_mode: str) -> TaskSpec:
    if subtask_mode != 'free':
        return task_spec
    import dataclasses as _dc
    skill_subtasks = getattr(skill, 'skill_subtasks', None)
    if skill_subtasks:
        return _dc.replace(task_spec, subtasks=_dicts_to_subtask_specs(skill_subtasks))
    return task_spec

def _validate_skill_execution_ready(skill: Skill, backend: MuJoCoBackend, task_spec: TaskSpec, subtask_mode: str) -> None:
    errors = validate(skill)
    if errors:
        raise ValueError('\n'.join((error.message for error in errors)))
    artifact = compile_skill(skill)
    backend.validate_v2_runtime_references(artifact, _apply_free_subtasks(skill, task_spec, subtask_mode))

def _resume_recovery_candidates(ckpt: dict, best_skill: Skill | None, archive: SkillArchive, run_log_path: Path) -> list[tuple[str, Skill, dict | None]]:
    candidates: list[tuple[str, Skill, dict | None]] = []
    if best_skill is not None:
        candidates.append(('checkpoint_best_skill', best_skill, None))
    pending = ckpt.get('pending_proposal_metrics') or {}
    parent_yaml = pending.get('parent_skill_yaml')
    if parent_yaml:
        try:
            candidates.append(('pending_proposal_parent', load_skill(parent_yaml), pending.get('parent_metrics')))
        except Exception:
            pass
    for entry in archive.elite(100):
        candidates.append(('archive', entry.skill, entry.metrics.to_dict()))
    if run_log_path.exists():
        try:
            run_log = json.loads(run_log_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            run_log = []
        for entry in reversed(run_log):
            yaml_text = entry.get('evaluated_skill_yaml')
            if yaml_text and entry.get('task_score') is not None and (entry.get('composite_score') is not None):
                try:
                    candidates.append(('run_log_evaluated_skill', load_skill(yaml_text), entry))
                except Exception:
                    pass
    return candidates

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Agent proposer outer loop for robot-skill-synthesis.', formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--task', required=True, help='Task name (from TASK_CONFIGS)')
    p.add_argument('--condition', choices=['full', 'text_only', 'text_reward', 'text_vision', 'no_scene_entities', 'no_history', 'no_task_subscores', 'anonymised_dsl', 'no_task_language', 'wrong_image', 'numeric_only', 'semantics_ablation_contact_info', 'no_contact_info', 'no_scene_description', 'misaligned_history', 'misattributed_contact', 'wrong_scene_targets'], required=True, help='Ablation condition — determines which prompt/context path to use.')
    p.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    p.add_argument('--T', type=int, default=15, help='Number of outer iterations (default: 15)')
    p.add_argument('--out-dir', required=True, help='Base output directory')
    p.add_argument('--initial-skill', default=None, help='Path to initial skill YAML; uses the public task seed if omitted')
    p.add_argument('--resume', action='store_true', help='Resume from the latest checkpoint in out-dir')
    p.add_argument('--dry-run', action='store_true', help='Validate configuration and bound inputs without writes, simulation, or API calls')
    p.add_argument('--behavioral-validation', action='store_true', help='Run one evaluation/context-formatting iteration and stop before the LLM API call; unlike --dry-run, this writes validation artifacts')
    p.add_argument('--cma-budget', type=int, default=200, help='CMA-ES evaluation budget per iteration (default: 200)')
    p.add_argument('--k-runs', type=int, default=3, help='Number of frozen randomised CMA-ES runs/configs (default: 3); basin fraction is diagnostic only')
    p.add_argument('--init-mode', dest='init_mode', choices=['expert', 'task_conditioned_random', 'scaffold', 'agent_create', 'grammar_uniform_random'], default='expert', help="Skill initialisation strategy for generation-0. 'expert' loads the seed YAML (default), 'task_conditioned_random' samples from ScaffoldInitialiser ('scaffold' is a deprecated alias for 'task_conditioned_random'), 'agent_create' generates K=3 candidates via LLM, screens them with cheap CMA-ES, and picks the best as the initial skill, 'grammar_uniform_random' samples uniformly from the full DSL grammar space with no task-specific structural prior.")
    p.add_argument('--param-only', action='store_true', dest='param_only', help='Disable LLM structural proposals in the outer loop — only run CMA-ES parameter optimisation.  The --init-mode still applies; use with --init-mode agent_create for the agent_create_param_only arm.')
    p.add_argument('--fail-on-agent-create-fallback', action='store_true', dest='fail_on_agent_create_fallback', help='When --init-mode agent_create yields no valid LLM-created initial skill, fail instead of falling back to scaffold/expert.')
    p.add_argument('--subtask-mode', choices=['fixed', 'free'], default='fixed', dest='subtask_mode', help="Subtask binding mode. 'fixed' (default): subtasks come from task_spec; phases reference them by subtask_id. 'free': LLM creates its own subtasks block; sanitizer validates against the skill's own subtask declarations.")
    p.add_argument('--prompt-variant', type=int, choices=[0, 1, 2, 3, 4], default=0, dest='prompt_variant', help='Prompt variant for LLM proposer context (default: 0). 0=baseline; 1=explicit subtask field expansion (shows serialiser-omitted defaults); 2–4=legacy compatibility variants; variant 0 preserves the pinned baseline behaviour.')
    p.add_argument('--system-prompt-file', type=Path, default=None, help='Optional refinement system-prompt file. When supplied, its exact text replaces the prompt selected by --condition; creation calls continue to use the creation prompt.')
    p.add_argument('--semantic-manifest-root', type=Path, default=None)
    p.add_argument('--semantic-policy-version', default=None)
    p.add_argument('--realized-scene-context-version', default=None)
    p.add_argument('--initial-skill-yaml-sha256', default=None)
    p.add_argument('--realized-scene-state-sha256', default=None)
    p.add_argument('--randomized-config-bank-sha256', default=None)
    p.add_argument('--model', default=os.environ.get('OPENAI_COMPATIBLE_MODEL', DEFAULT_LLM_MODEL), help='OpenAI-compatible model override; this is a methodological variant.')
    p.add_argument('--temperature', type=float, default=0.7, help='Sampling temperature (default: 0.7).')
    return p

def _parse_args(argv: list[str] | None=None) -> argparse.Namespace:
    p = build_parser()
    args = p.parse_args(argv)
    if args.system_prompt_file is not None:
        prompt_path = args.system_prompt_file
        if not prompt_path.is_file():
            p.error(f'--system-prompt-file is not a readable file: {prompt_path}')
        try:
            prompt_path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            p.error(f'cannot read --system-prompt-file {prompt_path}: {exc}')
    semantic_values = (args.semantic_manifest_root, args.semantic_policy_version, args.realized_scene_context_version, args.initial_skill_yaml_sha256, args.realized_scene_state_sha256, args.randomized_config_bank_sha256)
    if any((value is not None for value in semantic_values)) and (not all((value is not None for value in semantic_values))):
        p.error('semantic manifest, policy/version, and all cell hashes must be supplied together')
    if all((value is not None for value in semantic_values)) and args.T != 15:
        p.error('semantic refinement protocol requires exactly --T 15')
    if not 0.0 <= args.temperature <= 2.0:
        p.error('--temperature must be between 0.0 and 2.0')
    if args.dry_run and args.behavioral_validation:
        p.error('--dry-run and --behavioral-validation are mutually exclusive')
    return args

def _load_task_spec(task_name: str) -> TaskSpec:
    return TaskSpec(**TASK_CONFIGS[task_name]['task_spec'])

def _load_initial_skill(task_name: str, initial_skill_path: str | None):
    if initial_skill_path is not None:
        return load_skill(Path(initial_skill_path).read_text())
    seed_path = PROJECT_ROOT / 'tasks' / 'seeds' / task_name / 'seed_00.yaml'
    if seed_path.exists():
        return load_skill(seed_path.read_text())
    raise FileNotFoundError(f'No --initial-skill given and no public seed for {task_name} found')

def _traces_to_list(traces) -> list[dict]:
    result: list[dict] = []
    for (trace_index, trace) in enumerate(traces):
        td: dict = {'success': trace.success, 'final_pose_error': trace.final_pose_error, 'peak_contact_force': trace.peak_contact_force}
        if getattr(trace, 'parameter_values', None):
            td['parameter_values'] = dict(trace.parameter_values)
        if getattr(trace, 'metadata', None):
            metadata = copy.deepcopy(trace.metadata)
            for key in ('contact_events', 'contact_event_summary'):
                rows = metadata.get(key)
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, dict) and row.get('episode_index') is None:
                            row['episode_index'] = trace_index
            td['metadata'] = metadata
        pt = getattr(trace, 'phase_telemetry', None)
        if pt is None and isinstance(getattr(trace, 'metadata', None), dict):
            pt = trace.metadata.get('phase_telemetry')
        if pt:
            td['phase_telemetry'] = pt
        result.append(td)
    return result

def _write_checkpoint(checkpoints_dir: Path, iter_idx: int, skill, best_so_far: float, archive: SkillArchive | None=None, evaluated_hashes: dict[str, float] | None=None, best_skill=None, consecutive_holds: int=0, best_composite: float=float('-inf'), pending_proposal_metrics: dict | None=None, initial_skill_yaml_sha256: str | None=None, realized_scene_state_sha256: str | None=None, randomized_config_bank_sha256: str | None=None, randomized_config_bank_wrapper_sha256: str | None=None, resume_recovery: dict | None=None) -> None:
    ckpt = {'iteration': iter_idx, 'skill_yaml': dump_skill(skill), 'best_so_far': best_so_far, 'best_composite': best_composite, 'evaluated_hashes': evaluated_hashes or {}, 'best_skill_yaml': dump_skill(best_skill) if best_skill is not None else None, 'consecutive_holds': consecutive_holds, 'pending_proposal_metrics': pending_proposal_metrics, 'initial_skill_yaml_sha256': initial_skill_yaml_sha256, 'realized_scene_state_sha256': realized_scene_state_sha256, 'randomized_config_bank_sha256': randomized_config_bank_sha256, 'randomized_config_bank_wrapper_sha256': randomized_config_bank_wrapper_sha256}
    if resume_recovery is not None:
        ckpt['resume_recovery'] = resume_recovery
    (checkpoints_dir / f'iter_{iter_idx:03d}.json').write_text(_json_dumps(ckpt, indent=2))
    if archive is not None:
        archive.save(checkpoints_dir / 'archive_checkpoint.jsonl')

def _find_latest_checkpoint(checkpoints_dir: Path) -> Path | None:
    checkpoints = sorted(checkpoints_dir.glob('iter_*.json'))
    return checkpoints[-1] if checkpoints else None

def _load_system_prompt(condition: str, system_prompt_file: Path | None=None) -> str:
    if system_prompt_file is not None:
        try:
            return system_prompt_file.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            raise ValueError(f'Cannot read system prompt file {system_prompt_file}: {exc}') from exc
    _lookup = condition
    if condition == 'anonymised_dsl':
        _lookup = 'full'
    fname = _CONDITION_PROMPT_FILE[_lookup]
    prompt_path = _PROMPTS_DIR / fname
    if not prompt_path.exists():
        raise FileNotFoundError(f'System prompt not found: {prompt_path}. Expected file in search/prompts/.')
    text = prompt_path.read_text(encoding='utf-8')
    if condition == 'anonymised_dsl':
        text = anonymise_text(text)
    return text

def _load_deepseek_api_key() -> str:
    token = os.environ.get("DEEPSEEK_API_KEY")
    if token and token.strip():
        return token.strip()
    raise EnvironmentError("DEEPSEEK_API_KEY environment variable is required for LLM refinement.")

def _prompt_section_sizes(system_prompt: str, context_md: str) -> dict[str, int]:
    sizes = {'system_prompt': len(system_prompt)}
    current = 'user_preamble'
    sizes[current] = 0
    for line in context_md.splitlines(keepends=True):
        if line.startswith('#'):
            heading = line.lstrip('#').strip() or 'untitled'
            current = f'user:{heading}'
            sizes.setdefault(current, 0)
        sizes[current] += len(line)
    return sizes

def _check_prompt_size(system_prompt: str, context_md: str) -> dict[str, int]:
    section_sizes = _prompt_section_sizes(system_prompt, context_md)
    total_chars = len(system_prompt) + len(context_md)
    if total_chars > MAX_LLM_PROMPT_CHARS:
        breakdown = ', '.join((f'{name}={size}' for (name, size) in section_sizes.items()))
        raise RuntimeError(f'Refusing oversized LLM prompt before API call: total_chars={total_chars} exceeds bound={MAX_LLM_PROMPT_CHARS}. Section sizes (characters): {breakdown}')
    return section_sizes

def _call_llm_api(context_md: str, condition: str, iter_dir: Path, *, model: str=DEFAULT_LLM_MODEL, temperature: float=0.7, max_retries: int=5, log_suffix: str='', image_paths: list[str] | None=None, system_prompt_file: Path | None=None) -> str:
    import openai
    provider = DEEPSEEK_PROVIDER
    base_url = os.environ.get('OPENAI_COMPATIBLE_BASE_URL', DEEPSEEK_BASE_URL).strip()
    system_prompt = _load_system_prompt(condition, system_prompt_file)
    _check_prompt_size(system_prompt, context_md)
    token = _load_deepseek_api_key()
    client = openai.OpenAI(api_key=token, base_url=base_url, timeout=180.0)
    prompt_hash = hashlib.md5(system_prompt.encode()).hexdigest()[:12]
    context_hash = hashlib.md5(context_md.encode()).hexdigest()[:12]
    visual_condition = _is_visual_context_condition(condition)
    visual_context_suppressed = visual_condition
    requested_image_count = len(image_paths or [])
    images_requested = requested_image_count > 0
    images_sent_count = 0
    images_suppressed_count = requested_image_count
    if images_requested:
        print(f'[warn] {provider} text-only mode: suppressing {requested_image_count} requested image(s); continuing with text context.')
    messages: list[dict] = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': context_md}]
    backoff = 10.0
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(model=model, temperature=temperature, messages=messages)
            raw_text = response.choices[0].message.content or ''
            response_hash = hashlib.md5(raw_text.encode()).hexdigest()[:12]
            tokens_in = response.usage.prompt_tokens if response.usage else None
            tokens_out = response.usage.completion_tokens if response.usage else None
            api_log = {'provider': provider, 'condition': condition, 'model': model, 'base_url': base_url, 'temperature': temperature, 'text_only': True, 'visual_condition': visual_condition, 'visual_context_suppressed': visual_context_suppressed, 'images_requested': images_requested, 'requested_image_count': requested_image_count, 'images_suppressed': images_requested, 'images_suppressed_count': images_suppressed_count, 'images_sent': False, 'images_sent_count': images_sent_count, 'prompt_hash': prompt_hash, 'context_hash': context_hash, 'response_hash': response_hash, 'attempt': attempt, 'tokens_in': tokens_in, 'tokens_out': tokens_out, 'multimodal': False, 'timestamp_utc': datetime.datetime.utcnow().isoformat()}
            (iter_dir / f'api_call_log{log_suffix}.json').write_text(json.dumps(api_log, indent=2))
            return raw_text
        except Exception as exc:
            exc_str = str(exc)
            is_rate_limit = '429' in exc_str or 'rate_limit' in exc_str.lower() or 'RateLimitError' in type(exc).__name__
            if is_rate_limit:
                is_hard_quota = 'insufficient_quota' in exc_str.lower() or 'quota' in exc_str.lower() or '86400' in exc_str or ('RateLimitReached' in exc_str)
                if is_hard_quota:
                    raise RuntimeError(f'DeepSeek API quota exhausted (hard limit — cannot recover by retrying). Error: {exc}')
                print(f'  Rate limit hit (attempt {attempt + 1}/{max_retries}). Backing off {backoff:.0f}s…')
                time.sleep(backoff)
                backoff = min(backoff * 2, 300.0)
                last_exc = exc
            else:
                raise
    raise RuntimeError(f'DeepSeek API call failed after {max_retries} retries. Last error: {last_exc}')

def _parse_yaml_from_response(raw_text: str) -> str:
    match = re.search('```(?:ya?ml)?\\s*\\n(.*?)```', raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    lines = raw_text.splitlines()
    for (i, line) in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('skill:') or stripped.startswith('-') or (':' in stripped and (not stripped.startswith('#'))):
            return '\n'.join(lines[i:]).strip()
    return raw_text.strip()

def _normalise_yaml_for_condition(yaml_text: str, condition: str) -> str:
    if condition == 'anonymised_dsl':
        return deanonymise_yaml(yaml_text)
    return yaml_text

def _parse_full_skill_yaml(text: str, condition: str='full'):
    yaml_str = _normalise_yaml_for_condition(_parse_yaml_from_response(text), condition)
    try:
        return load_skill(yaml_str)
    except Exception:
        return None

def _append_run_log(run_log_path: Path, record: dict) -> None:
    record['proposal_status'] = record.get('parse_status')
    (optimiser, posthoc) = split_optimiser_posthoc_diagnostics(record.get('optimiser_diagnostics') or record.get('skill_parameter_optimisation_scores', {}))
    if optimiser:
        record['optimiser_diagnostics'] = optimiser
        record['skill_parameter_optimisation_scores'] = optimiser
    elif 'optimiser_diagnostics' not in record:
        record['optimiser_diagnostics'] = {}
    if posthoc:
        record['posthoc_diagnostics'] = {**record.get('posthoc_diagnostics', {}), **posthoc}
    if run_log_path.exists():
        existing: list = json.loads(run_log_path.read_text())
    else:
        existing = []
    existing.append(record)
    tmp_path = run_log_path.with_suffix('.json.tmp')
    tmp_path.write_text(_json_dumps(existing, indent=2))
    os.replace(tmp_path, run_log_path)

def _image_is_informative(path: Path) -> bool:
    try:
        from PIL import Image as _PIL_Image
        import numpy as _np
    except ImportError:
        return True
    try:
        arr = _np.asarray(_PIL_Image.open(path))
        frac = float(_np.count_nonzero(arr)) / max(arr.size, 1)
        return frac > 0.03
    except Exception:
        return False

def _camera_priority_for_task(task_name: str) -> dict[str, int]:
    if 'door' in task_name.lower():
        order = ['side', 'wrist', 'top_down', 'overview']
    else:
        order = ['wrist', 'side', 'top_down', 'overview']
    return {cam: rank for (rank, cam) in enumerate(order)}

def _capture_keyframes(task_name: str, skill_path: Path, seed: int, keyframes_dir: Path) -> dict:
    return {}

def _normalize_finite_real_scalar(value: object) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise TypeError(f'expected a non-boolean real scalar, got {type(value).__name__}')
    try:
        normalized = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError('real scalar is outside the finite Python float range') from exc
    if not math.isfinite(normalized):
        raise ValueError('real scalar is not finite in the Python float range')
    return normalized

def _validate_randomized_config_feedback(bank: RealizedSceneConfigBank, diagnostic_results: object, traces: list[dict] | None) -> dict[int, dict]:
    expected = [configuration.config_index for configuration in bank.configurations]
    expected_set = set(expected)
    if len(expected_set) != len(expected):
        raise RuntimeError('randomized configuration bank has duplicate configuration_index values')
    if not isinstance(diagnostic_results, list):
        raise RuntimeError(f'randomized configuration feedback is missing the diagnostic result list for configuration_index values {expected}')
    results_by_index: dict[int, dict] = {}
    for (row_number, result) in enumerate(diagnostic_results):
        if not isinstance(result, dict):
            raise RuntimeError(f'randomized diagnostic row {row_number} is not a mapping')
        configuration_index = result.get('configuration_index')
        if type(configuration_index) is not int or configuration_index not in expected_set:
            raise RuntimeError(f'randomized diagnostic row {row_number} has unexpected configuration_index={configuration_index!r}; expected one of {expected}')
        if configuration_index in results_by_index:
            raise RuntimeError(f'configuration_index={configuration_index} has duplicate diagnostic results')
        for score_field in ('best_task_score', 'best_fitness_score', 'best_composite_score'):
            score = result.get(score_field)
            try:
                _normalize_finite_real_scalar(score)
            except (TypeError, ValueError):
                raise RuntimeError(f'configuration_index={configuration_index} diagnostic result must include finite numeric {score_field}; got {score!r}') from None
        if not isinstance(result.get('best_params'), dict):
            raise RuntimeError(f'configuration_index={configuration_index} diagnostic result is missing mapping best_params')
        results_by_index[configuration_index] = result
    for configuration_index in expected:
        if configuration_index not in results_by_index:
            raise RuntimeError(f'configuration_index={configuration_index} is missing its diagnostic result')
    if traces is None:
        return results_by_index
    replay_counts = {configuration_index: 0 for configuration_index in expected}
    for (row_number, trace) in enumerate(traces):
        if not isinstance(trace, dict):
            raise RuntimeError(f'randomized replay row {row_number} is not a mapping')
        configuration_index = trace.get('configuration_index')
        if type(configuration_index) is not int or configuration_index not in expected_set:
            raise RuntimeError(f'randomized replay row {row_number} has unexpected configuration_index={configuration_index!r}; expected one of {expected}')
        success = trace.get('success')
        if not isinstance(success, (bool, np.bool_)):
            raise RuntimeError(f'configuration_index={configuration_index} replay must include boolean success; got {success!r}')
        for outcome_field in ('final_pose_error', 'peak_contact_force'):
            outcome = trace.get(outcome_field)
            try:
                _normalize_finite_real_scalar(outcome)
            except (TypeError, ValueError):
                raise RuntimeError(f'configuration_index={configuration_index} replay must include finite numeric {outcome_field}; got {outcome!r}') from None
        metadata = trace.get('metadata')
        if not isinstance(metadata, dict):
            raise RuntimeError(f'configuration_index={configuration_index} replay is missing mapping metadata')
        phase_telemetry = trace.get('phase_telemetry', metadata.get('phase_telemetry'))
        if not isinstance(phase_telemetry, list) or not phase_telemetry:
            raise RuntimeError(f'configuration_index={configuration_index} replay must include non-empty phase_telemetry')
        if any((not isinstance(phase, dict) for phase in phase_telemetry)):
            raise RuntimeError(f'configuration_index={configuration_index} replay phase_telemetry rows must be mappings')
        ik_statistics = metadata.get('ik_statistics')
        if not isinstance(ik_statistics, dict):
            raise RuntimeError(f'configuration_index={configuration_index} replay metadata must include mapping ik_statistics')
        counts: dict[str, int] = {}
        for count_field in ('solve_count', 'success_count', 'failure_count'):
            count = ik_statistics.get(count_field)
            if isinstance(count, (bool, np.bool_)) or not isinstance(count, (int, np.integer)) or int(count) < 0:
                raise RuntimeError(f'configuration_index={configuration_index} replay ik_statistics must include non-negative integer {count_field}; got {count!r}')
            counts[count_field] = int(count)
        mean_iterations = ik_statistics.get('mean_iterations')
        try:
            normalized_mean_iterations = _normalize_finite_real_scalar(mean_iterations)
            if normalized_mean_iterations < 0.0:
                raise ValueError('mean_iterations is negative')
        except (TypeError, ValueError):
            raise RuntimeError(f'configuration_index={configuration_index} replay ik_statistics must include finite non-negative numeric mean_iterations; got {mean_iterations!r}') from None
        if counts['success_count'] + counts['failure_count'] != counts['solve_count']:
            raise RuntimeError(f'configuration_index={configuration_index} replay ik_statistics counts are incoherent: success_count + failure_count must equal solve_count')
        if counts['solve_count'] == 0 and normalized_mean_iterations != 0.0:
            raise RuntimeError(f'configuration_index={configuration_index} replay ik_statistics with zero solves must have mean_iterations=0.0')
        replay_counts[configuration_index] += 1
    for (configuration_index, count) in replay_counts.items():
        if count == 0:
            raise RuntimeError(f'configuration_index={configuration_index} is missing its expected replay')
    return results_by_index

def _evaluation_identity(best_params: dict[str, float], randomized_config_bank: RealizedSceneConfigBank | None) -> dict[str, object]:
    if not isinstance(best_params, dict):
        raise RuntimeError("CMA-ES evaluation did not return optimized parameters")
    if randomized_config_bank is None:
        raise RuntimeError("CMA-ES evaluation did not bind a frozen scene bank")
    return {"best_params": best_params, "configuration_bank_sha256": randomized_config_bank.sha256}


def _run_cma_eval(artifact, backend, task_spec: TaskSpec, task_name: str, seed: int, budget: int, k_runs: int, randomized_config_bank: RealizedSceneConfigBank | None=None) -> tuple:
    (metrics, best_params, cma_diagnostics) = optimise_parameters(artifact, backend, task_spec=task_spec, budget=budget, K_basin_runs=k_runs, seed=seed, task_name=task_name, n_samples_per_eval=3, randomized_config_bank=randomized_config_bank)
    (optimiser_diag, posthoc_diag) = split_optimiser_posthoc_diagnostics(cma_diagnostics)
    metrics = _dc_replace(metrics, skill_parameter_optimisation_scores=optimiser_diag, optimiser_diagnostics=optimiser_diag, posthoc_diagnostics={**getattr(metrics, 'posthoc_diagnostics', {}), **posthoc_diag})
    if randomized_config_bank is None:
        raw_traces = run_evaluation(artifact, backend, n_samples=10, seed=seed, task_spec=task_spec, fixed_params=best_params)
        traces = _traces_to_list(raw_traces)
    else:
        config_results = cma_diagnostics.get('posthoc_diagnostics', {}).get('randomised_config_results')
        results_by_index = _validate_randomized_config_feedback(randomized_config_bank, config_results, traces=None)
        traces = []
        for configuration in randomized_config_bank.configurations:
            result = results_by_index[configuration.config_index]
            activate_realized_scene_configuration(backend, configuration)
            replay = run_evaluation(artifact, backend, n_samples=1, seed=configuration.seed, task_spec=task_spec, fixed_params=result['best_params'])
            replay_rows = _traces_to_list(replay)
            for row in replay_rows:
                metadata = dict(row.get('metadata') or {})
                metadata.update({'configuration_index': configuration.config_index, 'configuration_seed': configuration.seed, 'configuration_sha256': configuration.sha256, 'realized_scene_sha256': configuration.snapshot.sha256, 'configuration_bank_sha256': randomized_config_bank.sha256})
                row['metadata'] = metadata
                row['configuration_index'] = configuration.config_index
                row['configuration_sha256'] = configuration.sha256
            traces.extend(replay_rows)
        _validate_randomized_config_feedback(randomized_config_bank, config_results, traces)
    return (metrics, best_params, cma_diagnostics, traces)

def _validate_loop_completion(final_evaluation_error: Exception | None, successful_evaluations: int) -> None:
    if final_evaluation_error is not None:
        raise RuntimeError('Final evaluation failed; loop results are invalid') from final_evaluation_error
    if successful_evaluations == 0:
        raise RuntimeError('No CMA-ES evaluation completed; loop results are invalid')

def _canonical_json(value: object) -> str:
    return _json_dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def _realized_scene_state_path(out_dir: Path) -> Path:
    return out_dir / 'realized_scene_state.json'

def _randomized_config_bank_path(out_dir: Path) -> Path:
    return out_dir / 'randomized_config_bank.json'

def _write_randomized_config_bank(out_dir: Path, bank: RealizedSceneConfigBank) -> str:
    path = _randomized_config_bank_path(out_dir)
    temp = path.with_name(f'.{path.name}.tmp.{os.getpid()}')
    canonical_bytes = (_canonical_json(bank.to_dict()) + '\n').encode('utf-8')
    try:
        temp.write_bytes(canonical_bytes)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return hashlib.sha256(canonical_bytes).hexdigest()

def _load_randomized_config_bank(out_dir: Path, task: str, k_runs: int) -> RealizedSceneConfigBank:
    path = _randomized_config_bank_path(out_dir)
    try:
        persisted_bytes = path.read_bytes()
        bank = RealizedSceneConfigBank.from_dict(json.loads(persisted_bytes))
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(f'missing or invalid randomized configuration bank: {path}') from exc
    if bank.task_name != task or len(bank.configurations) != k_runs:
        raise RuntimeError(f'randomized configuration bank protocol mismatch: {path}')
    canonical_bytes = (_canonical_json(bank.to_dict()) + '\n').encode('utf-8')
    if persisted_bytes != canonical_bytes:
        raise RuntimeError(f'randomized configuration bank wrapper is not canonical: {path}')
    return bank

def _randomized_config_bank_wrapper_sha256(out_dir: Path) -> str:
    return hashlib.sha256(_randomized_config_bank_path(out_dir).read_bytes()).hexdigest()
_NOMINAL_RANDOMIZATION_FIELDS = ('enabled', 'distribution', 'object_xy_delta', 'goal_xy_delta', 'obstacle_xy_delta', 'fixture_xy_delta', 'target_xy_delta', 'goal_z_delta', 'hinge_delta_deg')
_SCORE_FIELDS = ('best_task_score', 'best_fitness_score', 'best_composite_score', 'termination_fidelity', 'force_compliance')
_PHASE_FIELDS = ('phase_index', 'phase_name', 'phase_type', 'subtask_id', 'tcp_start', 'tcp_end', 'object_pos_start', 'object_pos_end', 'tcp_to_object_dist_end', 'object_to_goal_dist_start', 'object_to_goal_dist_end', 'object_z_max', 'terminated_normally', 'termination_reason', 'n_steps', 'n_steps_budget', 'contact_detected', 'contact_event_count', 'peak_contact_force', 'raw_contact_event_count', 'raw_peak_contact_force', 'phase_peak_obstacle_force')
_KEY_STATE_FIELDS = ('final_tcp_position', 'actual_goal_position', 'realised_goal_position', 'realised_object_initial_position', 'realised_fixture_position', 'realised_door_panel_position', 'actual_obstacle_position', 'realised_obstacle_position', 'socket_entry_position', 'goal_marker_position', 'final_object_position', 'hinge_angle', 'initial_hinge_angle', 'realised_initial_hinge_angle')
_CONTACT_FIELDS = ('phase_index', 'phase_name', 'phase_type', 'body_a', 'geom_a', 'body_b', 'geom_b', 'contact_count', 'force', 'max_force', 'mean_force', 'force_p95', 'contact_point', 'contact_point_centroid', 'tcp_position', 'tcp_position_centroid', 'involves_obstacle', 'involves_robot_link', 'involves_task_object')
_IK_CONTAINER_FIELDS = ('ik_statistics', 'ik_stats', 'ik_summary')
_IK_ALIASES = {'solve_count': ('solve_count', 'ik_solve_count', 'total_solves'), 'success_count': ('success_count', 'ik_success_count', 'successful_solves'), 'failure_count': ('failure_count', 'ik_failure_count', 'failed_solves'), 'mean_iterations': ('mean_iterations', 'ik_mean_iterations', 'mean_ik_iterations')}

def _prompt_scalar(value: object) -> object:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, Real):
        return round(_normalize_finite_real_scalar(value), PROMPT_FLOAT_DIGITS)
    raise TypeError(f'unsupported prompt scalar type: {type(value).__name__}')

def _prompt_value(value: object, *, max_items: int=4) -> object:
    if isinstance(value, np.ndarray):
        value = value.tolist()
    if isinstance(value, (list, tuple)):
        if len(value) > max_items or any((isinstance(item, (list, tuple, np.ndarray, dict)) for item in value)):
            raise ValueError('prompt summary only accepts short one-dimensional vectors')
        return [_prompt_scalar(item) for item in value]
    return _prompt_scalar(value)

def _allowlisted_row(row: object, fields: tuple[str, ...]) -> dict:
    if not isinstance(row, dict):
        return {}
    return {key: _prompt_value(row[key]) for key in fields if key in row and row[key] is not None}

def _summarize_scene(snapshot: RealizedSceneSnapshot) -> dict:
    source = snapshot.to_dict()
    result: dict = {'task_name': source['task_name'], 'object_starts': [], 'targets': [], 'obstacles': [], 'fixtures': [], 'fixture_states': [], 'axes': [], 'limits': [], 'anchors': []}
    for category in ('object_starts', 'targets', 'obstacles', 'fixtures'):
        if len(source[category]) > 16:
            raise ValueError(f'too many realized-scene {category} entries')
        result[category] = [{key: _prompt_value(item[key]) for key in ('name', 'position', 'orientation') if key in item} for item in source[category]]
    for (category, value_field) in (('fixture_states', 'state'), ('axes', 'value'), ('limits', 'value'), ('anchors', 'value')):
        if len(source[category]) > 16:
            raise ValueError(f'too many realized-scene {category} entries')
        result[category] = [{'name': _prompt_value(item['name']), value_field: _prompt_value(item[value_field])} for item in source[category]]
    if 'door' in source:
        door = source['door']
        result['door'] = {'panel': {key: _prompt_value(door['panel'][key]) for key in ('name', 'position', 'orientation') if key in door['panel']}, **{key: _prompt_value(door[key]) for key in ('hinge_axis', 'initial_hinge_angle', 'target_hinge_angle') if key in door}}
    return result

def _summarize_contacts(metadata: dict) -> dict:
    rows = metadata.get('contact_event_summary')
    if not isinstance(rows, list) or not rows:
        rows = metadata.get('contact_events')
    if not isinstance(rows, list):
        rows = []
    normalized = [_allowlisted_row(row, _CONTACT_FIELDS) for row in rows]
    normalized = [row for row in normalized if row]
    normalized.sort(key=lambda row: (-float(row.get('max_force', row.get('force', 0.0))), int(row.get('phase_index', -1)), str(row.get('phase_name', '')), str(row.get('body_a', '')), str(row.get('body_b', ''))))
    return {'total_contact_groups': len(normalized), 'reported_contact_groups': normalized[:MAX_REPLAY_CONTACTS], 'omitted_contact_groups': max(0, len(normalized) - MAX_REPLAY_CONTACTS)}

def _extract_ik_stats(metadata: dict) -> dict[str, float]:
    sources = [metadata]
    sources.extend((metadata[key] for key in _IK_CONTAINER_FIELDS if isinstance(metadata.get(key), dict)))
    found: dict[str, float] = {}
    for (output_name, aliases) in _IK_ALIASES.items():
        for source in sources:
            value = next((source[key] for key in aliases if key in source), None)
            if isinstance(value, (int, float, np.number)) and math.isfinite(float(value)):
                found[output_name] = float(value)
                break
    return found

def _average_ik_stats(rows: list[dict[str, float]]) -> dict:
    if not rows:
        return {'available': False}
    summary: dict[str, object] = {'available': True, 'replay_count': len(rows)}
    for key in _IK_ALIASES:
        values = [row[key] for row in rows if key in row]
        if values:
            summary[f'average_{key}'] = round(float(np.mean(values)), PROMPT_FLOAT_DIGITS)
    failures = summary.get('average_failure_count')
    solves = summary.get('average_solve_count')
    if isinstance(failures, float) and isinstance(solves, float) and (solves > 0):
        summary['average_failure_rate'] = round(failures / solves, PROMPT_FLOAT_DIGITS)
    return summary

def _summarize_replay(trace: dict) -> tuple[dict, dict[str, float]]:
    metadata = trace.get('metadata') if isinstance(trace.get('metadata'), dict) else {}
    phases = trace.get('phase_telemetry', metadata.get('phase_telemetry', []))
    if not isinstance(phases, list):
        phases = []
    if len(phases) > MAX_REPLAY_PHASES:
        raise ValueError(f'replay has {len(phases)} phases; maximum concise-context count is {MAX_REPLAY_PHASES}')
    outcome = _allowlisted_row(trace, ('success', 'final_pose_error', 'peak_contact_force'))
    outcome['key_states'] = _allowlisted_row(metadata, _KEY_STATE_FIELDS)
    outcome['phases'] = [_allowlisted_row(row, _PHASE_FIELDS) for row in phases]
    outcome['contacts'] = _summarize_contacts(metadata)
    return (outcome, _extract_ik_stats(metadata))

def _format_randomized_config_bank_context(bank: RealizedSceneConfigBank, cma_diagnostics: dict, traces: list[dict], nominal_randomization: dict | None=None) -> str:
    results = cma_diagnostics.get('posthoc_diagnostics', {}).get('randomised_config_results', [])
    results_by_index = _validate_randomized_config_feedback(bank, results, traces)
    nominal_protocol = {'distribution': 'independent_uniform', 'range_semantics': {'*_xy_delta': 'independent per-axis draws in [-delta, +delta]', 'hinge_delta_deg': 'draw in [-delta_deg, +delta_deg]', 'goal_z_delta': 'draw in [0, max_delta]'}, 'parameters': _allowlisted_row(nominal_randomization or {}, _NOMINAL_RANDOMIZATION_FIELDS)}
    lines = ['## Frozen randomized evaluation bank (shared across every structure)', f'Bank SHA-256: `{bank.sha256}`. Stable order: configuration 1 to configuration {len(bank.configurations)}.', '### Nominal task randomization distribution and ranges', 'These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.', f'```json\n{_canonical_json(nominal_protocol)}\n```']
    for configuration in bank.configurations:
        result = results_by_index[configuration.config_index]
        config_traces = [trace for trace in traces if trace.get('configuration_index') == configuration.config_index]
        if len(config_traces) > MAX_REPLAY_TRACES_PER_CONFIG:
            raise ValueError(f'configuration {configuration.config_index} has {len(config_traces)} replay traces; maximum concise-context count is {MAX_REPLAY_TRACES_PER_CONFIG}')
        replay_outcomes = []
        ik_rows = []
        for trace in config_traces:
            (outcome, ik_stats) = _summarize_replay(trace)
            replay_outcomes.append(outcome)
            if ik_stats:
                ik_rows.append(ik_stats)
        params = result.get('best_params') if isinstance(result.get('best_params'), dict) else {}
        sorted_params = sorted(params.items())
        feedback = {'optimized_scores': _allowlisted_row(result, _SCORE_FIELDS), 'optimized_parameters': {key: _prompt_value(value) for (key, value) in sorted_params[:32]}, 'omitted_parameter_count': max(0, len(sorted_params) - 32), 'replay_outcomes': replay_outcomes, 'averaged_ik_statistics': _average_ik_stats(ik_rows)}
        lines.extend([f'### Configuration {configuration.config_index + 1} of {len(bank.configurations)}', f'Configuration SHA-256: `{configuration.sha256}`; realized-scene SHA-256: `{configuration.snapshot.sha256}`.', REALIZED_SCENE_BLOCK_MARKER, 'Realized scene facts (concise typed schema):', f'```json\n{_canonical_json(_summarize_scene(configuration.snapshot))}\n```', 'Aligned optimization and replay/contact feedback:', f'```json\n{_canonical_json(feedback)}\n```'])
    return '\n\n'.join(lines)

def _initial_skill_state_path(out_dir: Path) -> Path:
    return out_dir / 'initial_skill_state.json'

def _write_initial_skill_state(out_dir: Path, skill_yaml: str) -> str:
    payload = {'initial_skill_yaml': skill_yaml, 'initial_skill_sha256': hashlib.sha256(skill_yaml.encode('utf-8')).hexdigest()}
    path = _initial_skill_state_path(out_dir)
    temp = path.with_name(f'.{path.name}.tmp.{os.getpid()}')
    try:
        temp.write_text(_canonical_json(payload) + '\n', encoding='utf-8')
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return payload['initial_skill_sha256']

def _load_initial_skill_state(out_dir: Path) -> str:
    path = _initial_skill_state_path(out_dir)
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        skill_yaml = payload['initial_skill_yaml']
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f'missing or invalid initial skill state for resume: {path}') from exc
    if not isinstance(skill_yaml, str) or not skill_yaml.strip():
        raise RuntimeError(f'missing or invalid initial skill state for resume: {path}')
    digest = hashlib.sha256(skill_yaml.encode('utf-8')).hexdigest()
    if payload.get('initial_skill_sha256') != digest:
        raise RuntimeError(f'initial skill state hash mismatch: {path}')
    return digest

def _validate_checkpoint_bindings(checkpoint: dict, *, initial_skill_sha256: str, realized_scene_sha256: str) -> None:
    if checkpoint.get('initial_skill_yaml_sha256') != initial_skill_sha256:
        raise RuntimeError('checkpoint initial-skill hash mismatch')
    if checkpoint.get('realized_scene_state_sha256') != realized_scene_sha256:
        raise RuntimeError('checkpoint realized-scene hash mismatch')

def _write_realized_scene_state(out_dir: Path, snapshot: RealizedSceneSnapshot) -> None:
    digest = realized_scene_snapshot_hash(snapshot)
    payload = {'realized_scene': snapshot.to_dict(), 'realized_scene_sha256': digest, 'realized_scene_state_sha256': digest}
    path = _realized_scene_state_path(out_dir)
    temp = path.with_name(f'.{path.name}.tmp.{os.getpid()}')
    try:
        temp.write_text(_canonical_json(payload) + '\n', encoding='utf-8')
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def _load_realized_scene_state(out_dir: Path, task: str) -> RealizedSceneSnapshot:
    path = _realized_scene_state_path(out_dir)
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        snapshot = coerce_realized_scene(payload['realized_scene'])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(f'missing or invalid realized scene state for resume: {path}') from exc
    if snapshot is None or snapshot.task_name != task:
        raise RuntimeError(f'realized scene state does not match task {task}: {path}')
    digest = realized_scene_snapshot_hash(snapshot)
    if payload.get('realized_scene_sha256') != digest or payload.get('realized_scene_state_sha256') != digest:
        raise RuntimeError(f'realized scene state hash mismatch: {path}')
    if canonical_realized_scene_json(snapshot) != _canonical_json(snapshot.to_dict()):
        raise RuntimeError(f'realized scene state is not canonical: {path}')
    return snapshot

def _load_semantic_manifest_cell(args: argparse.Namespace) -> dict | None:
    if args.semantic_manifest_root is None:
        return None
    from search import semantic_context_policy as semantic_policy
    manifest = json.loads((Path(args.semantic_manifest_root) / 'manifest.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(_canonical_json({k: v for (k, v) in manifest.items() if k != 'manifest_sha256'}).encode('utf-8')).hexdigest()
    if manifest.get('manifest_sha256') != digest:
        raise RuntimeError('semantic manifest SHA256 mismatch')
    if args.semantic_policy_version != semantic_policy.SEMANTIC_CONTEXT_POLICY_VERSION:
        raise RuntimeError('semantic policy version does not match the runner capability')
    if args.realized_scene_context_version != semantic_policy.REALIZED_SCENE_CONTEXT_VERSION:
        raise RuntimeError('realized-scene context version does not match the runner capability')
    try:
        cell = next((cell for cell in manifest['cells'] if cell['task'] == args.task and cell['seed'] == args.seed))
    except (KeyError, StopIteration) as exc:
        raise RuntimeError(f'semantic manifest lacks {args.task}_seed{args.seed}') from exc
    if cell.get('initial_skill_yaml_sha256') != args.initial_skill_yaml_sha256:
        raise RuntimeError('semantic initial-skill hash mismatch')
    if cell.get('realized_scene_state_sha256') != args.realized_scene_state_sha256:
        raise RuntimeError('semantic realized-scene hash mismatch')
    if hashlib.sha256(cell['initial_skill_yaml'].encode('utf-8')).hexdigest() != args.initial_skill_yaml_sha256:
        raise RuntimeError('semantic initial-skill payload hash mismatch')
    if hashlib.sha256(cell['realized_scene_state_json'].encode('utf-8')).hexdigest() != args.realized_scene_state_sha256:
        raise RuntimeError('semantic realized-scene payload hash mismatch')
    bank_text = cell.get('randomized_config_bank_json')
    if not isinstance(bank_text, str) or hashlib.sha256(bank_text.encode('utf-8')).hexdigest() != args.randomized_config_bank_sha256:
        raise RuntimeError('semantic randomized-configuration-bank payload hash mismatch')
    try:
        bank = RealizedSceneConfigBank.from_dict(json.loads(bank_text))
    except (TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError('semantic randomized-configuration-bank is invalid') from exc
    if bank.task_name != args.task or bank.outer_seed != args.seed or len(bank.configurations) != args.k_runs:
        raise RuntimeError('semantic randomized-configuration-bank protocol mismatch')
    if bank.configurations[0].snapshot.sha256 != args.realized_scene_state_sha256:
        raise RuntimeError('semantic realized scene is not bank configuration zero')
    return {'manifest': manifest, 'cell': cell}

def _semantic_ledger_provenance(args: argparse.Namespace, binding: dict) -> dict:
    from search.semantic_capability import validate_manifest_capability
    integration = validate_manifest_capability(binding['manifest'])
    if args.system_prompt_file is None or not args.system_prompt_file.is_file():
        raise RuntimeError('semantic intervention requires a pinned public system prompt')
    return {'policy_hash': integration['policy_hashes'][args.condition], 'capability_integration_digest': integration['capability_integration_digest'], 'policy_implementation_hash': integration['source_hashes']['policy'], 'capability_implementation_hash': integration['source_hashes']['capability'], 'truth_table_report_sha256': integration['truth_table_report_sha256'], 'pinned_system_prompt_sha256': hashlib.sha256(args.system_prompt_file.read_bytes()).hexdigest()}

def _append_semantic_ledger(path: Path, *, iteration: int, attempt_kind: str, condition: str, pre_prompt: str, post_prompt: str, provenance: dict, total_iterations: int) -> None:
    from search import semantic_context_policy as semantic_policy
    evidence = semantic_policy.prompt_manipulation_evidence(condition, pre_prompt, post_prompt)
    if evidence['applicable'] and (not evidence['applied']):
        raise RuntimeError(f'semantic {condition} policy produced an applied no-op at iteration {iteration}')
    existing = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
    attempt_index = sum((1 for line in existing if json.loads(line).get('iteration') == iteration))
    row = {'prompt_index': len(existing), 'iteration': iteration, 'attempt_index': attempt_index, 'attempt_kind': attempt_kind, 'condition': condition, 'policy_version': semantic_policy.SEMANTIC_CONTEXT_POLICY_VERSION, **provenance, 'text_only_compliant': True, 'pre_prompt_sha256': hashlib.sha256(pre_prompt.encode('utf-8')).hexdigest(), 'post_prompt_sha256': hashlib.sha256(post_prompt.encode('utf-8')).hexdigest(), 'prompt_count': total_iterations, 'input_token_count': len(post_prompt.split()), 'applicable': evidence['applicable'], 'applied': evidence['applied'], 'non_applicable_reason': evidence['non_applicable_reason'], 'invariant_evidence': {key: evidence[key] for key in ('target_absent', 'only_target_changed', 'multiset_preserved', 'non_identity_outcome', 'outcome_permutation')}}
    with path.open('a', encoding='utf-8') as handle:
        handle.write(_canonical_json(row) + '\n')

def _apply_semantic_prompt_once(condition: str, generic_prompt: str) -> str:
    from search.semantic_context_policy import apply_prompt_text
    return apply_prompt_text(condition, generic_prompt)

def _semantic_generation0_fields(binding: dict | None, condition: str, iteration: int) -> dict:
    if binding is None or iteration != 0:
        return {}
    return {'realized_scene_state_json': binding['cell']['realized_scene_state_json'], 'manipulation_check': {'condition': condition, 'intervention_boundary': 'refinement_only_after_generation_zero', 'coverage': {'prompt_count': 0, 'affected_prompt_count': 0, 'applicable_prompt_count': 0, 'primary_prompt_count': 0, 'retry_prompt_count': 0, 'complete': False}, 'text_only_compliant': True}}

def _finalize_semantic_coverage(run_log_path: Path, ledger_path: Path) -> None:
    rows = [json.loads(line) for line in ledger_path.read_text(encoding='utf-8').splitlines()]
    log = json.loads(run_log_path.read_text(encoding='utf-8'))
    if not log or not isinstance(log[0].get('manipulation_check'), dict):
        raise RuntimeError('semantic run lacks generation-zero manipulation metadata')
    primary = sum((row['attempt_kind'] == 'primary' for row in rows))
    log[0]['manipulation_check']['coverage'] = {'prompt_count': len(rows), 'affected_prompt_count': sum((bool(row['applied']) for row in rows)), 'applicable_prompt_count': sum((bool(row['applicable']) for row in rows)), 'primary_prompt_count': primary, 'retry_prompt_count': len(rows) - primary, 'complete': primary == 15}
    temp = run_log_path.with_suffix('.json.tmp')
    temp.write_text(_json_dumps(log, indent=2), encoding='utf-8')
    os.replace(temp, run_log_path)

def main(argv: list[str] | None=None) -> None:
    args = _parse_args(argv)
    if args.task not in TASK_CONFIGS:
        print(f"Error: unknown task '{args.task}'. Available: {', '.join(TASK_CONFIGS.keys())}", file=sys.stderr)
        sys.exit(1)
    if args.task not in SIM_CONFIGS:
        print(f"Error: task '{args.task}' has no SIM_CONFIGS entry. Add it to scripts/task_configs.SIM_CONFIGS before running.", file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        _load_system_prompt(args.condition, args.system_prompt_file)
        _load_semantic_manifest_cell(args)
        print('Dry-run preflight passed; no files written and no API calls made.')
        return
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir = out_dir / 'checkpoints'
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    run_log_path = out_dir / 'run_log.json'
    archive_path = out_dir / 'archive.jsonl'
    current_skill_path = out_dir / 'current_skill.yaml'
    proposal_attempts_path = out_dir / 'proposal_attempts.jsonl'
    manipulation_ledger_path = out_dir / 'manipulation_ledger.jsonl'
    task_spec = _load_task_spec(args.task)
    task_config = TASK_CONFIGS[args.task]
    semantic_binding = _load_semantic_manifest_cell(args)
    semantic_provenance = _semantic_ledger_provenance(args, semantic_binding) if semantic_binding is not None else None
    if semantic_binding is not None:
        if not args.resume:
            manipulation_ledger_path.unlink(missing_ok=True)
            (out_dir / 'realized_scene_state.json').write_text(semantic_binding['cell']['realized_scene_state_json'], encoding='utf-8')
    archive = SkillArchive(max_size=100)
    start_iter = 0
    best_so_far = float('-inf')
    best_composite: float = float('-inf')
    best_skill: Skill | None = None
    consecutive_holds: int = 0
    evaluated_hashes: dict[str, float] = {}
    iteration_history: list[dict] = []
    pending_proposal_metrics: dict | None = None
    successful_evaluations = 0
    resumed_checkpoint = False
    initial_skill_sha256: str | None = None
    realized_scene_state_sha256: str | None = None
    resumed_realized_scene_snapshot: RealizedSceneSnapshot | None = None
    randomized_config_bank: RealizedSceneConfigBank | None = None
    randomized_config_bank_wrapper_sha256: str | None = None
    if args.resume:
        ckpt_path = _find_latest_checkpoint(checkpoints_dir)
        if ckpt_path is not None:
            resumed_checkpoint = True
            print(f'Resuming from checkpoint: {ckpt_path}')
            ckpt = json.loads(ckpt_path.read_text())
            initial_skill_sha256 = _load_initial_skill_state(out_dir)
            if semantic_binding is None:
                resumed_realized_scene_snapshot = _load_realized_scene_state(out_dir, args.task)
                realized_scene_state_sha256 = realized_scene_snapshot_hash(resumed_realized_scene_snapshot)
            else:
                scene_state_path = _realized_scene_state_path(out_dir)
                try:
                    scene_state_text = scene_state_path.read_text(encoding='utf-8')
                except OSError as exc:
                    raise RuntimeError(f'missing realized scene state for semantic resume: {scene_state_path}') from exc
                realized_scene_state_sha256 = hashlib.sha256(scene_state_text.encode('utf-8')).hexdigest()
                if realized_scene_state_sha256 != args.realized_scene_state_sha256:
                    raise RuntimeError('semantic resume realized-scene hash mismatch')
                if initial_skill_sha256 != args.initial_skill_yaml_sha256:
                    raise RuntimeError('semantic resume initial-skill hash mismatch')
            _validate_checkpoint_bindings(ckpt, initial_skill_sha256=initial_skill_sha256, realized_scene_sha256=realized_scene_state_sha256)
            start_iter = ckpt['iteration'] + 1
            current_skill = load_skill(ckpt['skill_yaml'])
            if 'best_composite' not in ckpt:
                best_so_far = float('-inf')
                best_composite = float('-inf')
            else:
                best_so_far = float(ckpt.get('best_so_far', float('-inf')))
                best_composite = float(ckpt.get('best_composite', float('-inf')))
            if ckpt.get('best_skill_yaml'):
                best_skill = load_skill(ckpt['best_skill_yaml'])
            consecutive_holds = int(ckpt.get('consecutive_holds', 0))
            pending_proposal_metrics = ckpt.get('pending_proposal_metrics')
            archive_ckpt = checkpoints_dir / 'archive_checkpoint.jsonl'
            if archive_ckpt.exists():
                archive.load(archive_ckpt)
            elif archive_path.exists():
                archive.load(archive_path)
            evaluated_hashes = {k: float(v) for (k, v) in ckpt.get('evaluated_hashes', {}).items()}
            if not evaluated_hashes and run_log_path.exists():
                old_log = json.loads(run_log_path.read_text())
                for entry in old_log:
                    if entry.get('proposed_skill_yaml'):
                        try:
                            old_skill = load_skill(entry['proposed_skill_yaml'])
                            h = SkillArchive._skill_hash(old_skill)
                            evaluated_hashes[h] = entry.get('fitness_score', entry.get('task_score', 0.0))
                        except Exception:
                            pass
            iteration_history = []
            if run_log_path.exists():
                try:
                    existing_run_log = json.loads(run_log_path.read_text())
                    successful_evaluations = sum((entry.get('task_score') is not None and entry.get('composite_score') is not None for entry in existing_run_log))
                    for entry in existing_run_log:
                        yaml_str = entry.get('proposed_skill_yaml') or entry.get('evaluated_skill_yaml')
                        if yaml_str and entry.get('composite_score') is not None:
                            try:
                                sk = load_skill(yaml_str)
                                iteration_history.append({'iter': entry.get('iteration', 0), 'hash': SkillArchive._skill_hash(sk), 'score': float(entry.get('composite_score', 0.0)), 'task_score': float(entry.get('task_score', 0.0)), 'phases': [{'id': p.phase_id, 'type': p.phase_type.value, 'generator': getattr(getattr(p, 'generator', None), 'name', '').lower() or None, 'control': getattr(getattr(p, 'control', None), 'name', '').lower() or None, 'termination': getattr(getattr(p, 'termination', None), 'name', '').lower() or None, 'n_params': len(getattr(p, 'parameters', None) or {})} for p in sk.phases], 'n_total_params': sum((len(getattr(p, 'parameters', None) or {}) for p in sk.phases)), 'subtask_ids': [getattr(p, 'subtask_id', None) for p in sk.phases if getattr(p, 'subtask_id', None)], 'accepted': bool(entry.get('accepted', False))})
                            except Exception:
                                pass
                except Exception:
                    pass
            print(f'  Resuming at iteration {start_iter}, best_task_score={best_so_far:.3f}, best_composite={best_composite:.3f}')
        else:
            print('No checkpoint found — starting from scratch.')
            current_skill = _load_initial_skill(args.task, args.initial_skill)
    if semantic_binding is not None and (not resumed_checkpoint):
        current_skill = load_skill(semantic_binding['cell']['initial_skill_yaml'])
    elif not args.resume:
        if args.init_mode in ('task_conditioned_random', 'scaffold'):
            current_skill = sample_scaffold_skill(args.task, rng=random.Random(args.seed))
        elif args.init_mode == 'grammar_uniform_random':
            _gu_min_ph = SIM_CONFIGS[args.task].get('min_phases', 1)
            current_skill = GrammarUniformInitialiser(args.task, rng=random.Random(args.seed), min_phases=_gu_min_ph).sample()
        else:
            current_skill = _load_initial_skill(args.task, args.initial_skill)
    evaluated_hashes[SkillArchive._skill_hash(current_skill)] = best_so_far
    if best_skill is None:
        best_skill = current_skill
    _sim_cfg = SIM_CONFIGS[args.task]
    scene_config = SceneConfig(robot=_sim_cfg.get('robot', 'panda'), gripper=_sim_cfg['gripper'], object_xml=_sim_cfg['object_xml'], target_markers=_sim_cfg.get('target_markers', ()), tcp_markers=_sim_cfg.get('tcp_markers', ()))
    backend = MuJoCoBackend(scene_config)
    scene_entities = get_scene_entities(args.task, task_spec, _sim_cfg)
    if semantic_binding is not None:
        realized_state = json.loads(semantic_binding['cell']['realized_scene_state_json'])
        if isinstance(realized_state.get('scene_entities'), dict):
            scene_entities = realized_state['scene_entities']
    _rand_cfg = task_config.get('randomisation', {})
    if _rand_cfg.get('enabled', False):
        backend._rand_config = _rand_cfg
        backend._rand_rng = np.random.default_rng(args.seed)
    if args.T > 0 and semantic_binding is None:
        if resumed_checkpoint:
            try:
                randomized_config_bank = _load_randomized_config_bank(out_dir, args.task, args.k_runs)
                randomized_config_bank_wrapper_sha256 = _randomized_config_bank_wrapper_sha256(out_dir)
            except RuntimeError:
                if args.k_runs != 1:
                    raise
                randomized_config_bank = materialize_realized_scene_config_bank(backend, args.task, task_spec, outer_seed=args.seed, k_runs=1)
                randomized_config_bank_wrapper_sha256 = _write_randomized_config_bank(out_dir, randomized_config_bank)
            assert resumed_realized_scene_snapshot is not None
            if randomized_config_bank.configurations[0].snapshot != resumed_realized_scene_snapshot:
                raise RuntimeError('realized-scene state does not match configuration bank')
            checkpoint_bank_hash = ckpt.get('randomized_config_bank_sha256')
            if checkpoint_bank_hash != randomized_config_bank.sha256:
                raise RuntimeError('checkpoint randomized-configuration-bank hash mismatch')
            if ckpt.get('randomized_config_bank_wrapper_sha256') != randomized_config_bank_wrapper_sha256:
                raise RuntimeError('checkpoint randomized-configuration-bank wrapper hash mismatch')
        else:
            randomized_config_bank = materialize_realized_scene_config_bank(backend, args.task, task_spec, outer_seed=args.seed, k_runs=args.k_runs)
            randomized_config_bank_wrapper_sha256 = _write_randomized_config_bank(out_dir, randomized_config_bank)
            _write_realized_scene_state(out_dir, randomized_config_bank.configurations[0].snapshot)
    elif args.T > 0:
        randomized_config_bank = RealizedSceneConfigBank.from_dict(json.loads(semantic_binding['cell']['randomized_config_bank_json']))
        if resumed_checkpoint and ckpt.get('randomized_config_bank_sha256') != randomized_config_bank.sha256:
            raise RuntimeError('checkpoint randomized-configuration-bank hash mismatch')
        activate_realized_scene_configuration(backend, randomized_config_bank.configurations[0])
        if resumed_checkpoint:
            persisted_bank = _load_randomized_config_bank(out_dir, args.task, args.k_runs)
            if persisted_bank != randomized_config_bank:
                raise RuntimeError('semantic resume randomized-configuration-bank mismatch')
            randomized_config_bank_wrapper_sha256 = _randomized_config_bank_wrapper_sha256(out_dir)
            if ckpt.get('randomized_config_bank_wrapper_sha256') != randomized_config_bank_wrapper_sha256:
                raise RuntimeError('checkpoint randomized-configuration-bank wrapper hash mismatch')
        else:
            randomized_config_bank_wrapper_sha256 = _write_randomized_config_bank(out_dir, randomized_config_bank)
    _logged_init_mode = 'task_conditioned_random' if args.init_mode == 'scaffold' else args.init_mode
    print(f'Agent proposer loop | task={args.task} | T={args.T} | seed={args.seed} | condition={args.condition} | init_mode={_logged_init_mode} | subtask_mode={args.subtask_mode}')
    print(f'Output: {out_dir}')
    if not args.resume and args.init_mode == 'agent_create':
        K_CREATION = 3
        CHEAP_CMA_BUDGET = 50
        creation_dir = out_dir / 'creation_init'
        creation_dir.mkdir(parents=True, exist_ok=True)
        print(f'\n[agent_create] Generating {K_CREATION} candidate skills via LLM…')
        creation_candidates = []
        for k in range(K_CREATION):
            try:
                creation_context = format_proposal_context_v2(skill=None, metrics=None, traces=None, cma_diagnostics=None, task_spec=task_spec, task_name=args.task, condition=args.condition, seed=args.seed, iteration=0, creation_mode=True, subtask_mode=args.subtask_mode, prompt_variant=args.prompt_variant, scene_entities=scene_entities, nominal_randomisation=_rand_cfg)
            except Exception as exc:
                print(f'  [agent_create] Context formatting failed for candidate {k}: {exc}', file=sys.stderr)
                continue
            try:
                raw_text = _call_llm_api(creation_context, 'creation', creation_dir, log_suffix=f'_creation_{k}', temperature=args.temperature, model=args.model)
            except Exception as exc:
                print(f'  [agent_create] LLM call for candidate {k} failed: {exc}', file=sys.stderr)
                append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration='creation', attempt_kind=f'creation_{k}', proposal_source='llm_creation', task=args.task, candidate_yaml=None, parent_skill=None, parent_yaml=None, task_spec=task_spec, subtask_mode=args.subtask_mode, condition='creation', accepted=False, parse_status='api_error', error=str(exc)))
                continue
            _creation_yaml = _normalise_yaml_for_condition(_parse_yaml_from_response(raw_text), args.condition)
            append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration='creation', attempt_kind=f'creation_{k}', proposal_source='llm_creation', task=args.task, candidate_yaml=_creation_yaml, parent_skill=None, parent_yaml=None, task_spec=task_spec, subtask_mode=args.subtask_mode, condition='creation', accepted=None, parse_status='raw'))
            candidate = _parse_full_skill_yaml(raw_text, args.condition)
            if candidate is None:
                print(f'  [agent_create] Candidate {k}: YAML parse failed — skipping.', file=sys.stderr)
                continue
            try:
                _validate_skill_execution_ready(candidate, backend, task_spec, args.subtask_mode)
            except Exception as exc:
                print(f'  [agent_create] Candidate {k}: execution preflight failed ({exc}) — skipping.', file=sys.stderr)
                continue
            creation_candidates.append(candidate)
            print(f'  [agent_create] Candidate {k}: valid ✓')
        best_creation = None
        best_creation_score = float('-inf')
        for (idx, candidate) in enumerate(creation_candidates):
            try:
                (candidate, _) = sanitize_subtasks(candidate, task_spec)
                _eval_task_spec = _apply_free_subtasks(candidate, task_spec, args.subtask_mode)
                artifact = compile_skill(candidate)
                (metrics_c, _params_c, _diag_c) = optimise_parameters(artifact, backend, task_spec=_eval_task_spec, budget=CHEAP_CMA_BUDGET, K_basin_runs=args.k_runs, seed=args.seed, task_name=args.task, n_samples_per_eval=3, randomized_config_bank=randomized_config_bank)
                print(f'  [agent_create] Candidate {idx} CMA score: {metrics_c.composite_score:.3f}')
                if metrics_c.composite_score > best_creation_score:
                    best_creation_score = metrics_c.composite_score
                    best_creation = candidate
            except Exception as exc:
                print(f'  [agent_create] CMA screening failed for candidate {idx}: {exc}', file=sys.stderr)
                continue
        if best_creation is not None:
            print(f'  [agent_create] Best candidate score: {best_creation_score:.3f} — using as initial skill.')
            current_skill = best_creation
        else:
            if args.fail_on_agent_create_fallback:
                raise RuntimeError('agent_create produced no valid LLM-created initial skill; refusing scaffold/expert fallback because --fail-on-agent-create-fallback was set.')
            print('  [agent_create] No candidates survived screening — falling back.', file=sys.stderr)
            if sample_scaffold_skill is not None:
                current_skill = sample_scaffold_skill(args.task, rng=random.Random(args.seed))
            else:
                print('  [agent_create] scaffold_init unavailable — retaining expert seed.', file=sys.stderr)
        evaluated_hashes.clear()
        evaluated_hashes[SkillArchive._skill_hash(current_skill)] = best_so_far
    resume_recovery: dict | None = None
    stale_invalid_pending_proposal: dict | None = None
    try:
        _validate_skill_execution_ready(current_skill, backend, task_spec, args.subtask_mode)
    except Exception as current_error:
        if not resumed_checkpoint:
            raise RuntimeError('initial skill failed execution preflight') from current_error
        recovered = None
        for (source, candidate, candidate_metrics) in _resume_recovery_candidates(ckpt, best_skill, archive, run_log_path):
            try:
                _validate_skill_execution_ready(candidate, backend, task_spec, args.subtask_mode)
            except Exception:
                continue
            recovered = (source, candidate, candidate_metrics)
            break
        if recovered is None:
            raise RuntimeError('checkpoint current skill failed execution preflight and no known valid evaluated/best parent is available for recovery') from current_error
        (source, current_skill, candidate_metrics) = recovered
        best_skill = current_skill
        stale_invalid_pending_proposal = pending_proposal_metrics
        pending_proposal_metrics = None
        if candidate_metrics is not None:
            best_so_far = float(candidate_metrics.get('task_score', best_so_far))
            best_composite = float(candidate_metrics.get('composite_score', best_composite))
        resume_recovery = {'checkpoint': str(ckpt_path), 'rejected_current_error': str(current_error), 'restored_from': source, 'cleared_pending_proposal': stale_invalid_pending_proposal is not None}
        if stale_invalid_pending_proposal is not None:
            resume_recovery['discarded_pending_proposal'] = {'proposal_iteration': stale_invalid_pending_proposal.get('proposal_iteration'), 'proposal_source': stale_invalid_pending_proposal.get('proposal_source'), 'reason': 'checkpoint_current_failed_execution_preflight'}
        print(f'  Resume recovery: restored {source}; rejected invalid checkpoint current skill.')
    if best_skill is not None:
        try:
            _validate_skill_execution_ready(best_skill, backend, task_spec, args.subtask_mode)
        except Exception as best_error:
            recovered = None
            for (source, candidate, candidate_metrics) in _resume_recovery_candidates(ckpt if resumed_checkpoint else {}, None, archive, run_log_path):
                try:
                    _validate_skill_execution_ready(candidate, backend, task_spec, args.subtask_mode)
                except Exception:
                    continue
                recovered = (source, candidate, candidate_metrics)
                break
            if recovered is None:
                raise RuntimeError('best skill failed execution preflight with no valid recovery parent') from best_error
            (source, best_skill, candidate_metrics) = recovered
            if candidate_metrics is not None:
                best_so_far = float(candidate_metrics.get('task_score', best_so_far))
                best_composite = float(candidate_metrics.get('composite_score', best_composite))
            if resume_recovery is not None:
                resume_recovery['restored_best_from'] = source
    current_skill_path.write_text(dump_skill(current_skill))
    evaluated_hashes.setdefault(SkillArchive._skill_hash(current_skill), best_composite)
    if resume_recovery is not None:
        (out_dir / 'resume_recovery.json').write_text(_json_dumps(resume_recovery, indent=2), encoding='utf-8')
    if not resumed_checkpoint:
        if semantic_binding is not None:
            initial_skill_yaml = semantic_binding['cell']['initial_skill_yaml']
        elif args.initial_skill is not None and args.init_mode != 'agent_create':
            initial_skill_yaml = Path(args.initial_skill).read_text(encoding='utf-8')
        else:
            initial_skill_yaml = dump_skill(current_skill)
        initial_skill_sha256 = _write_initial_skill_state(out_dir, initial_skill_yaml)
        if semantic_binding is not None and initial_skill_sha256 != args.initial_skill_yaml_sha256:
            raise RuntimeError('semantic initial-skill state hash mismatch')
    if args.T == 0:
        return
    if semantic_binding is None:
        assert randomized_config_bank is not None
        realized_scene_snapshot = randomized_config_bank.configurations[0].snapshot
        realized_scene_state_sha256 = realized_scene_snapshot_hash(realized_scene_snapshot)
    else:
        realized_scene_snapshot = coerce_realized_scene(json.loads(semantic_binding['cell']['realized_scene_state_json']))
        realized_scene_state_sha256 = args.realized_scene_state_sha256
    assert initial_skill_sha256 is not None
    assert realized_scene_state_sha256 is not None
    if stale_invalid_pending_proposal is not None and ckpt_path is not None and (ckpt.get('iteration') == args.T - 1) and (start_iter == args.T):
        _write_checkpoint(checkpoints_dir, args.T - 1, current_skill, best_so_far, archive, evaluated_hashes, best_skill=best_skill, consecutive_holds=consecutive_holds, best_composite=best_composite, pending_proposal_metrics=None, initial_skill_yaml_sha256=initial_skill_sha256, realized_scene_state_sha256=realized_scene_state_sha256, randomized_config_bank_sha256=randomized_config_bank.sha256 if randomized_config_bank else None, randomized_config_bank_wrapper_sha256=randomized_config_bank_wrapper_sha256, resume_recovery=resume_recovery)
    pending_eval = pending_proposal_metrics is not None
    for iter_idx in range(start_iter, args.T):
        iter_dir = out_dir / f'iter_{iter_idx:03d}'
        iter_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n{'=' * 60}")
        print(f'Iteration {iter_idx}/{args.T - 1}')
        print(f"{'=' * 60}")
        pending_eval = False
        evaluated_skill_yaml = dump_skill(current_skill)
        print('Running CMA-ES evaluation…')
        (current_skill, _fallback_count) = sanitize_subtasks(current_skill, task_spec)
        if _fallback_count > 0:
            print(f'  subtask sanitizer: {_fallback_count} phase(s) repaired')
        _eval_task_spec = _apply_free_subtasks(current_skill, task_spec, args.subtask_mode)
        artifact = compile_skill(current_skill)
        try:
            (metrics, _best_params, cma_diagnostics, traces) = _run_cma_eval(artifact, backend, task_spec=_eval_task_spec, task_name=args.task, seed=args.seed + iter_idx, budget=args.cma_budget, k_runs=args.k_runs, randomized_config_bank=randomized_config_bank)
        except Exception as exc:
            print(f'  CMA-ES crashed: {exc}', file=sys.stderr)
            (iter_dir / 'cma_error.txt').write_text(str(exc))
            (iter_dir / 'SKIPPED').write_text('reason=cma_crash\n')
            raise RuntimeError(f'Iteration {iter_idx} CMA-ES evaluation failed') from exc
        successful_evaluations += 1
        print(f'  composite={metrics.composite_score:.3f}  task_score={metrics.task_score:.3f}  termination_fidelity={metrics.termination_fidelity:.3f}')
        (iter_dir / 'metrics.json').write_text(_json_dumps(metrics.to_dict(), indent=2))
        (iter_dir / 'cma_diagnostics.json').write_text(_json_dumps(cma_diagnostics, indent=2))
        (iter_dir / 'traces.json').write_text(_json_dumps(traces, indent=2))
        _iter_accepted = metrics.task_score > best_so_far or (metrics.task_score == best_so_far and metrics.composite_score > best_composite)
        if _iter_accepted:
            best_so_far = metrics.task_score
            best_composite = metrics.composite_score
            best_skill = current_skill
        archive.add(current_skill, metrics, generation=iter_idx)
        archive.save(archive_path)
        evaluated_hashes[SkillArchive._skill_hash(current_skill)] = metrics.composite_score
        iteration_history.append({'iter': iter_idx, 'hash': SkillArchive._skill_hash(current_skill), 'score': metrics.composite_score, 'task_score': float(metrics.task_score), 'canonical_task_score': float(metrics.task_score), 'fitness_score': float(metrics.fitness_score), 'search_fitness_score': float(metrics.fitness_score), 'phases': [{'id': p.phase_id, 'type': p.phase_type.value, 'generator': getattr(getattr(p, 'generator', None), 'name', '').lower() or None, 'control': getattr(getattr(p, 'control', None), 'name', '').lower() or None, 'termination': getattr(getattr(p, 'termination', None), 'name', '').lower() or None, 'n_params': len(getattr(p, 'parameters', None) or {})} for p in current_skill.phases], 'n_total_params': sum((len(getattr(p, 'parameters', None) or {}) for p in current_skill.phases)), 'subtask_ids': [getattr(p, 'subtask_id', None) for p in current_skill.phases if getattr(p, 'subtask_id', None)], 'accepted': _iter_accepted})
        _evaluated_parent_yaml = None
        _evaluated_parent_metrics = None
        _evaluated_source = 'initial'
        if pending_proposal_metrics:
            _evaluated_parent_yaml = pending_proposal_metrics.get('parent_skill_yaml')
            _evaluated_parent_metrics = pending_proposal_metrics.get('parent_metrics')
            _evaluated_source = pending_proposal_metrics.get('proposal_source', 'llm')
        evaluated_proposal_fields = build_evaluated_proposal_metrics(task=args.task, candidate_skill=current_skill, parent_skill=None, candidate_yaml=dump_skill(current_skill), parent_yaml=_evaluated_parent_yaml, candidate_metrics=metrics, parent_metrics=_evaluated_parent_metrics, task_spec=task_spec, subtask_mode=args.subtask_mode, proposal_source=_evaluated_source, accepted_as_elite=_iter_accepted, parse_status='evaluated')
        pending_proposal_metrics = None
        if metrics.task_score < best_so_far or (metrics.task_score == best_so_far and metrics.composite_score < best_composite):
            current_skill = best_skill
            current_skill_path.write_text(dump_skill(current_skill))
            print(f'  Reverted to best skill (task_score={best_so_far:.3f}, Q={best_composite:.3f}) for next iteration.')
        if args.param_only:
            _append_run_log(run_log_path, {'iteration': iter_idx, 'evaluated_skill_yaml': evaluated_skill_yaml, 'proposed_skill_yaml': None, **metrics.to_dict(), **_evaluation_identity(_best_params, randomized_config_bank), 'accepted': False, 'parse_status': 'param_only', 'best_so_far': best_so_far, 'consecutive_holds': consecutive_holds, **evaluated_proposal_fields, 'timestamp_utc': datetime.datetime.utcnow().isoformat(), 'proposal_parse_accepted': False, 'is_best_update': _iter_accepted, **_semantic_generation0_fields(semantic_binding, args.condition, iter_idx)})
            _write_checkpoint(checkpoints_dir, iter_idx, current_skill, best_so_far, archive, evaluated_hashes, best_skill=best_skill, consecutive_holds=consecutive_holds, best_composite=best_composite, pending_proposal_metrics=pending_proposal_metrics, initial_skill_yaml_sha256=initial_skill_sha256, realized_scene_state_sha256=realized_scene_state_sha256, randomized_config_bank_sha256=randomized_config_bank.sha256 if randomized_config_bank else None, randomized_config_bank_wrapper_sha256=randomized_config_bank_wrapper_sha256)
            continue
        keyframes: dict | None = None
        _vision_conditions = _VISUAL_CONTEXT_CONDITIONS - {'wrong_image'}
        if args.condition in _vision_conditions:
            try:
                keyframes = _capture_keyframes(args.task, current_skill_path, args.seed + iter_idx, iter_dir / 'keyframes')
            except Exception:
                print(f'  [keyframes] unexpected error capturing keyframes for {args.task} seed={args.seed + iter_idx}; continuing with empty dict', file=sys.stderr)
                keyframes = {}
        elif args.condition == 'wrong_image':
            _wrong_task = wrong_image_task_for(args.task)
            _wrong_skill = wrong_image_skill_path(args.task)
            if _wrong_task and _wrong_skill and _wrong_skill.exists():
                try:
                    keyframes = _capture_keyframes(_wrong_task, _wrong_skill, args.seed + iter_idx, iter_dir / 'keyframes')
                except Exception:
                    print(f'  [keyframes] unexpected error capturing wrong-task keyframes ({_wrong_task}) for {args.task}; continuing with empty dict', file=sys.stderr)
                    keyframes = {}
            else:
                keyframes = {}
        parent_skill_for_proposal = current_skill
        parent_yaml_for_proposal = dump_skill(parent_skill_for_proposal)
        parent_metrics_for_proposal = metrics.to_dict()
        _eff_condition = args.condition
        _eff_task_name: str = args.task
        _eff_scene_entities = scene_entities
        if args.condition == 'anonymised_dsl':
            _eff_condition = 'full'
        elif args.condition == 'no_task_language':
            _eff_condition = 'full'
            _eff_task_name = neutralise_task_name(args.task)
            _eff_scene_entities = neutralise_scene_entities(scene_entities, args.task)
        elif args.condition == 'wrong_image':
            _eff_condition = 'full'
        elif semantic_binding is not None:
            _eff_condition = 'full'
        if args.condition == 'numeric_only':
            _ts_history = [e.get('canonical_task_score', e.get('task_score', 0.0)) for e in iteration_history if isinstance(e, dict) and ('canonical_task_score' in e or 'task_score' in e)]
            _fs_history = [e.get('search_fitness_score', e.get('fitness_score', 0.0)) for e in iteration_history if isinstance(e, dict) and ('search_fitness_score' in e or 'fitness_score' in e)]
            _cs_history = [e.get('composite_score', 0.0) for e in iteration_history if isinstance(e, dict) and 'composite_score' in e]
            context_md = numeric_only_context(iteration=iter_idx, total_iterations=args.T, task_score_history=_ts_history or [0.0], fitness_score_history=_fs_history or [0.0], composite_score_history=_cs_history or [0.0], termination_fidelity=metrics.termination_fidelity, complexity_penalty=metrics.complexity_penalty, phase_count=len(current_skill.phases), parameter_count=sum((len(getattr(p, 'parameters', {})) for p in current_skill.phases)), current_composite=metrics.composite_score, best_composite=best_composite)
        else:
            _context_keyframes = None if _is_visual_context_condition(args.condition) else keyframes
            context_md = format_proposal_context_v2(current_skill, metrics, traces, cma_diagnostics, task_spec, keyframes=_context_keyframes, task_name=_eff_task_name, condition=_eff_condition, seed=args.seed, iteration=iter_idx, total_iterations=args.T, proposal_history=list(evaluated_hashes.items()), subtask_mode=args.subtask_mode, subtask_fallback_count=_fallback_count, best_skill=best_skill, iteration_history=iteration_history, task_score=metrics.task_score if metrics is not None else None, prompt_variant=args.prompt_variant, best_task_score=best_so_far if best_so_far != float('-inf') else 0.0, scene_entities=_eff_scene_entities, realized_scene_snapshot=realized_scene_snapshot)
            if randomized_config_bank is not None:
                context_md = f'{context_md}\n\n{_format_randomized_config_bank_context(randomized_config_bank, cma_diagnostics, traces, _rand_cfg)}'
        if args.condition == 'anonymised_dsl':
            context_md = anonymise_text(context_md)
        elif args.condition == 'no_task_language':
            context_md = '\n'.join((line for line in context_md.split('\n') if not any((marker in line.lower() for marker in ('reach target while avoiding', 'grasp and place', 'push the box', 'pull the door', 'peg must traverse', 'obstacle-clearing', 'collision-prone', 'object transfer', 'door opening', 'object must be placed', 'task success criterion', 'avoid obstacle', 'clear the obstacle', 'collision penalty', 'transport displacement', 'goal_beyond_obstacle')))))
        generic_context_md = context_md
        if semantic_binding is not None:
            pre_policy_context = generic_context_md
            context_md = _apply_semantic_prompt_once(args.condition, pre_policy_context)
            _append_semantic_ledger(manipulation_ledger_path, iteration=iter_idx, attempt_kind='primary', condition=args.condition, pre_prompt=pre_policy_context, post_prompt=context_md, provenance=semantic_provenance, total_iterations=args.T)
        (iter_dir / 'context.md').write_text(context_md)
        (iter_dir / 'agent_template.txt').write_text(args.condition)
        (iter_dir / 'READY_FOR_AGENT').write_text(f'iteration={iter_idx}\ncondition={args.condition}\n')
        if args.behavioral_validation:
            print('Behavioral validation passed through evaluation and context formatting; no API call made.')
            return
        proposed_skill_path = iter_dir / 'proposed_skill.yaml'
        print(f'Calling LLM API (condition={args.condition})…')
        t_start = time.monotonic()
        found = False
        api_error_msg: str | None = None
        image_paths: list[str] | None = None
        if _is_visual_context_condition(args.condition) and keyframes:
            phase_frames = keyframes.get('phases', {})
            _cam_priority = _camera_priority_for_task(args.task)
            all_entries = [(phase_name, camera_name, str(p)) for (phase_name, cameras) in phase_frames.items() for (camera_name, p) in cameras.items()]
            total = len(all_entries)
            phase_to_best: dict[str, tuple[str, str]] = {}
            for (phase_name, camera_name, path) in all_entries:
                if not _image_is_informative(Path(path)):
                    continue
                existing = phase_to_best.get(phase_name)
                if existing is None or _cam_priority.get(camera_name, 99) < _cam_priority.get(existing[0], 99):
                    phase_to_best[phase_name] = (camera_name, path)
            ordered_phases = [p for p in phase_frames if p in phase_to_best]
            if len(ordered_phases) >= 2:
                earliest_path = phase_to_best[ordered_phases[0]][1]
                latest_path = phase_to_best[ordered_phases[-1]][1]
                image_paths = [earliest_path, latest_path]
            elif len(ordered_phases) == 1:
                image_paths = [phase_to_best[ordered_phases[0]][1]]
            else:
                image_paths = None
            print(f'keyframes: selected {len(image_paths or [])}/{total} informative images')
        try:
            raw_text = _call_llm_api(context_md, args.condition, iter_dir, image_paths=image_paths, system_prompt_file=args.system_prompt_file, temperature=args.temperature, model=args.model)
            if args.condition == 'numeric_only':
                _n_result = parse_numeric_only_response(raw_text)
                if _n_result is not None:
                    _op_name = _n_result['operator']
                    _n_rng = random.Random(args.seed * 1000 + iter_idx)
                    from mutation.operators import ALL_OPERATORS as _ALL_OPS
                    _op_map = {f.__name__: f for f in _ALL_OPS}
                    _op_fn = _op_map.get(_op_name)
                    if _op_fn is not None:
                        _mutated = _op_fn(current_skill, _n_rng)
                        proposed_skill_path.write_text(dump_skill(_mutated))
                        found = True
                    else:
                        yaml_str = f'# unknown operator: {_op_name}\n'
                else:
                    yaml_str = '# parse_numeric_only_response returned None\n'
            else:
                yaml_str = _normalise_yaml_for_condition(_parse_yaml_from_response(raw_text), args.condition)
            if not found:
                try:
                    parsed = yaml.safe_load(yaml_str)
                    proposed_skill_path.write_text(yaml.dump(parsed, default_flow_style=False, allow_unicode=True) if isinstance(parsed, dict) else yaml_str)
                except Exception:
                    proposed_skill_path.write_text(yaml_str)
                found = True
        except EnvironmentError:
            raise
        except RuntimeError as exc:
            api_error_msg = str(exc)
            print(f'  LLM API error: {api_error_msg}', file=sys.stderr)
            found = False
        elapsed_s = time.monotonic() - t_start
        append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration=iter_idx, attempt_kind='initial', proposal_source='llm', task=args.task, candidate_yaml=proposed_skill_path.read_text() if found and proposed_skill_path.exists() else None, parent_skill=parent_skill_for_proposal, parent_yaml=parent_yaml_for_proposal, task_spec=task_spec, subtask_mode=args.subtask_mode, condition=args.condition, accepted=None, parse_status='raw' if found else 'api_error', error=api_error_msg, elapsed_s=elapsed_s))
        if not found:
            print(f'  API call failed after {elapsed_s:.1f}s — keeping current skill.')
            skipped_content = f"reason=api_error\nmessage={api_error_msg or 'unknown'}\n"
            (iter_dir / 'SKIPPED').write_text(skipped_content)
            _append_run_log(run_log_path, {'iteration': iter_idx, 'evaluated_skill_yaml': evaluated_skill_yaml, 'proposed_skill_yaml': None, **metrics.to_dict(), **_evaluation_identity(_best_params, randomized_config_bank), 'accepted': False, 'parse_status': 'api_error', 'best_so_far': best_so_far, 'consecutive_holds': consecutive_holds, **evaluated_proposal_fields, 'timestamp_utc': datetime.datetime.utcnow().isoformat(), 'proposal_parse_accepted': False, 'is_best_update': _iter_accepted, **_semantic_generation0_fields(semantic_binding, args.condition, iter_idx)})
            _write_checkpoint(checkpoints_dir, iter_idx, current_skill, best_so_far, archive, evaluated_hashes, best_skill=best_skill, consecutive_holds=consecutive_holds, best_composite=best_composite, pending_proposal_metrics=pending_proposal_metrics, initial_skill_yaml_sha256=initial_skill_sha256, realized_scene_state_sha256=realized_scene_state_sha256, randomized_config_bank_sha256=randomized_config_bank.sha256 if randomized_config_bank else None, randomized_config_bank_wrapper_sha256=randomized_config_bank_wrapper_sha256)
            continue
        MAX_RETRIES = 3
        retry_count = 0
        accepted = False
        parse_status = 'validation_failed'
        proposed_skill = None
        error_msg: str | None = None
        proposed_skill_yaml: str | None = None
        while retry_count <= MAX_RETRIES:
            raw_yaml = proposed_skill_path.read_text()
            proposed_skill_yaml = raw_yaml
            candidate = None
            error_msg = None
            try:
                candidate = load_skill(raw_yaml)
            except Exception as exc:
                error_msg = f'Parse error: {exc}'
            if error_msg is None and candidate is not None:
                errors = validate(candidate)
                if errors:
                    error_msg = '\n'.join((str(e) for e in errors))
                else:
                    if args.subtask_mode == 'free':
                        skill_subtasks = getattr(candidate, 'skill_subtasks', None)
                        if skill_subtasks:
                            for _st in skill_subtasks:
                                _sid = _st.get('id', '<unknown>')
                                _missing = [f for f in ('anchor', 'target_entity') if f not in _st]
                                if _missing:
                                    error_msg = f"free-subtask '{_sid}' missing required field(s): {_missing}. Each subtask must explicitly declare 'anchor' and 'target_entity' to prevent reward hacking."
                                    print(f'  Validation error: free-subtask missing required anchor/target_entity — rejecting proposal.')
                                    (iter_dir / 'validation_error.txt').write_text(error_msg)
                                    break
                    if error_msg is None:
                        try:
                            _validate_skill_execution_ready(candidate, backend, task_spec, args.subtask_mode)
                        except Exception as exc:
                            error_msg = str(exc)
                    if error_msg is None:
                        _proposed_hash = SkillArchive._skill_hash(candidate)
                        if best_skill is not None and _proposed_hash == SkillArchive._skill_hash(best_skill):
                            consecutive_holds += 1
                            if best_so_far >= 0.9:
                                print(f'  HOLD ({consecutive_holds}): task_score={best_so_far:.3f} is near-perfect — accepting HOLD.')
                                parse_status = 'hold'
                                accepted = False
                                _append_run_log(run_log_path, {'iteration': iter_idx, 'evaluated_skill_yaml': evaluated_skill_yaml, 'proposed_skill_yaml': dump_skill(best_skill), **metrics.to_dict(), **_evaluation_identity(_best_params, randomized_config_bank), 'accepted': False, 'parse_status': 'hold', 'best_so_far': best_so_far, 'consecutive_holds': consecutive_holds, **evaluated_proposal_fields, 'timestamp_utc': datetime.datetime.utcnow().isoformat(), 'proposal_parse_accepted': True, 'is_best_update': _iter_accepted, **_semantic_generation0_fields(semantic_binding, args.condition, iter_idx)})
                                _write_checkpoint(checkpoints_dir, iter_idx, current_skill, best_so_far, archive, evaluated_hashes, best_skill=best_skill, consecutive_holds=consecutive_holds, best_composite=best_composite, pending_proposal_metrics=pending_proposal_metrics, initial_skill_yaml_sha256=initial_skill_sha256, realized_scene_state_sha256=realized_scene_state_sha256, randomized_config_bank_sha256=randomized_config_bank.sha256 if randomized_config_bank else None, randomized_config_bank_wrapper_sha256=randomized_config_bank_wrapper_sha256)
                                break
                            print(f'  HOLD ({consecutive_holds}): task_score={best_so_far:.3f} not near-perfect — nudging to try different structure.')
                            _hold_tried_phases = ' → '.join((p.phase_type.value for p in best_skill.phases)) if best_skill else '?'
                            _hold_note = f'⚠️ HOLD DETECTED: Your last proposal was structurally identical to the best-known skill (Q={best_composite:.4f}, task_score={best_so_far:.4f}). This wastes an iteration. You MUST propose a genuinely DIFFERENT structure.\n\nThe best-known skill has phases: {_hold_tried_phases}\n\nSuggestions to break the pattern:\n- If task_score is low (<0.2): completely rethink — add a missing phase, change phase types, restructure entirely.\n- If task_score is moderate: try changing a generator (e.g. linear_cartesian → arc_cartesian), control mode, or termination condition.\n- Consider phases that have NOT been tried yet based on the mutation history in the context.\n\nDO NOT output the same structure again. Propose something structurally new.'
                            if semantic_binding is not None and args.condition == 'no_history':
                                _hold_note = 'A structurally novel proposal is required. Propose a genuinely different valid structure without relying on prior outcomes.'
                            hold_retry_pre_policy = f'{_hold_note}\n\n{generic_context_md}'
                            hold_retry_context = hold_retry_pre_policy
                            if semantic_binding is not None:
                                hold_retry_context = _apply_semantic_prompt_once(args.condition, hold_retry_pre_policy)
                                _append_semantic_ledger(manipulation_ledger_path, iteration=iter_idx, attempt_kind='hold_retry', condition=args.condition, pre_prompt=hold_retry_pre_policy, post_prompt=hold_retry_context, provenance=semantic_provenance, total_iterations=args.T)
                                (iter_dir / 'retry_policy_evidence.json').write_text(_json_dumps({'kind': 'hold', 'condition': args.condition, 'pre_sha256': hashlib.sha256(hold_retry_pre_policy.encode()).hexdigest(), 'post_sha256': hashlib.sha256(hold_retry_context.encode()).hexdigest(), 'policy_hash': semantic_provenance['policy_hash']}, indent=2))
                            _hold_retry_accepted = False
                            try:
                                raw_hold = _call_llm_api(hold_retry_context, args.condition, iter_dir, log_suffix='_hold_retry', system_prompt_file=args.system_prompt_file, temperature=args.temperature, model=args.model)
                                yaml_hold = _parse_yaml_from_response(raw_hold)
                                _hold_retry_path = iter_dir / 'proposed_skill_hold_retry.yaml'
                                try:
                                    parsed_hold = yaml.safe_load(yaml_hold)
                                    _hold_retry_path.write_text(yaml.dump(parsed_hold, default_flow_style=False, allow_unicode=True) if isinstance(parsed_hold, dict) else yaml_hold)
                                except Exception:
                                    _hold_retry_path.write_text(yaml_hold)
                                append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration=iter_idx, attempt_kind='hold_retry', proposal_source='llm', task=args.task, candidate_yaml=_hold_retry_path.read_text(), parent_skill=parent_skill_for_proposal, parent_yaml=parent_yaml_for_proposal, task_spec=task_spec, subtask_mode=args.subtask_mode, condition=args.condition, accepted=None, parse_status='raw'))
                                _hold_candidate = load_skill(_hold_retry_path.read_text())
                                _validate_skill_execution_ready(_hold_candidate, backend, task_spec, args.subtask_mode)
                                _hold_hash = SkillArchive._skill_hash(_hold_candidate)
                                if _hold_hash != SkillArchive._skill_hash(best_skill):
                                    print(f'  HOLD retry succeeded: new structure proposed.')
                                    candidate = _hold_candidate
                                    _proposed_hash = _hold_hash
                                    _hold_retry_accepted = True
                            except Exception as _he:
                                print(f'  HOLD retry failed: {_he}')
                            if not _hold_retry_accepted:
                                parse_status = 'hold'
                                accepted = False
                                _append_run_log(run_log_path, {'iteration': iter_idx, 'evaluated_skill_yaml': evaluated_skill_yaml, 'proposed_skill_yaml': dump_skill(best_skill), **metrics.to_dict(), **_evaluation_identity(_best_params, randomized_config_bank), 'accepted': False, 'parse_status': 'hold', 'best_so_far': best_so_far, 'consecutive_holds': consecutive_holds, **evaluated_proposal_fields, 'timestamp_utc': datetime.datetime.utcnow().isoformat(), 'proposal_parse_accepted': False, 'is_best_update': False, **_semantic_generation0_fields(semantic_binding, args.condition, iter_idx)})
                                _write_checkpoint(checkpoints_dir, iter_idx, current_skill, best_so_far, archive, evaluated_hashes, best_skill=best_skill, consecutive_holds=consecutive_holds, best_composite=best_composite, pending_proposal_metrics=pending_proposal_metrics, initial_skill_yaml_sha256=initial_skill_sha256, realized_scene_state_sha256=realized_scene_state_sha256, randomized_config_bank_sha256=randomized_config_bank.sha256 if randomized_config_bank else None, randomized_config_bank_wrapper_sha256=randomized_config_bank_wrapper_sha256)
                                break
                        candidate_hash = _proposed_hash
                        if candidate_hash in evaluated_hashes:
                            prior_score = evaluated_hashes[candidate_hash]
                            if retry_count < MAX_RETRIES:
                                print(f'  Duplicate structure detected (hash={candidate_hash}, prior_score={prior_score:.3f}) — retrying ({retry_count + 1}/{MAX_RETRIES})…')
                                retry_note = f'RETRY {retry_count + 1}/{MAX_RETRIES}: The structure you just proposed (hash {candidate_hash}) was already evaluated and scored {prior_score:.3f}. Please propose a DIFFERENT structure.'
                                if semantic_binding is not None and args.condition == 'no_history':
                                    retry_note = f'RETRY {retry_count + 1}/{MAX_RETRIES}: propose a DIFFERENT valid structure without relying on prior outcomes.'
                                (iter_dir / 'retry_note.txt').write_text(retry_note)
                                proposed_skill_path.unlink()
                                (iter_dir / 'READY_FOR_AGENT').write_text(f'iteration={iter_idx}\ncondition={args.condition}\nretry={retry_count + 1}\n{retry_note}\n')
                                retry_pre_policy = f'RETRY NOTE: {retry_note}\n\n{generic_context_md}'
                                retry_context_md = retry_pre_policy
                                if semantic_binding is not None:
                                    retry_context_md = _apply_semantic_prompt_once(args.condition, retry_pre_policy)
                                    _append_semantic_ledger(manipulation_ledger_path, iteration=iter_idx, attempt_kind=f'duplicate_retry_{retry_count + 1}', condition=args.condition, pre_prompt=retry_pre_policy, post_prompt=retry_context_md, provenance=semantic_provenance, total_iterations=args.T)
                                    (iter_dir / 'retry_policy_evidence.json').write_text(_json_dumps({'kind': 'duplicate', 'condition': args.condition, 'pre_sha256': hashlib.sha256(retry_pre_policy.encode()).hexdigest(), 'post_sha256': hashlib.sha256(retry_context_md.encode()).hexdigest(), 'policy_hash': semantic_provenance['policy_hash']}, indent=2))
                                try:
                                    raw_text = _call_llm_api(retry_context_md, args.condition, iter_dir, log_suffix='_retry', system_prompt_file=args.system_prompt_file, temperature=args.temperature, model=args.model)
                                    yaml_str = _parse_yaml_from_response(raw_text)
                                    try:
                                        parsed = yaml.safe_load(yaml_str)
                                        proposed_skill_path.write_text(yaml.dump(parsed, default_flow_style=False, allow_unicode=True) if isinstance(parsed, dict) else yaml_str)
                                    except Exception:
                                        proposed_skill_path.write_text(yaml_str)
                                    append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration=iter_idx, attempt_kind=f'retry_{retry_count + 1}', proposal_source='llm', task=args.task, candidate_yaml=proposed_skill_path.read_text(), parent_skill=parent_skill_for_proposal, parent_yaml=parent_yaml_for_proposal, task_spec=task_spec, subtask_mode=args.subtask_mode, condition=args.condition, accepted=None, parse_status='raw'))
                                    found = True
                                except EnvironmentError:
                                    raise
                                except Exception as exc:
                                    print(f'  Retry API call failed: {exc}', file=sys.stderr)
                                    print(f'  Retry API error — skipping iteration.')
                                    error_msg = f'retry_api_error: {exc}'
                                    parse_status = 'api_error'
                                    break
                                retry_count += 1
                                continue
                            else:
                                print(f'  All {MAX_RETRIES} retries produced duplicate structures — advancing without CMA re-evaluation.')
                                parse_status = 'duplicate_exhausted'
                                break
                        else:
                            proposed_skill = candidate
                            accepted = True
                            consecutive_holds = 0
                            parse_status = 'ok'
                            break
            else:
                break
            break
        if not accepted:
            if parse_status == 'hold':
                continue
            if parse_status == 'validation_failed':
                print(f'  Validation failed: {error_msg}')
                (iter_dir / 'validation_error.txt').write_text(error_msg or 'unknown')
                (iter_dir / 'SKIPPED').write_text(f"reason=validation_failed\ndetails={error_msg or 'unknown'}\n")
            elif parse_status == 'api_error':
                print(f'  API error on retry — keeping current skill.')
                (iter_dir / 'SKIPPED').write_text(f"reason=api_error\nmessage={error_msg or 'unknown'}\n")
            elif parse_status == 'duplicate_exhausted':
                print(f'  All retries produced duplicates — advancing without re-evaluation.')
        if accepted and proposed_skill is not None:
            print(f'  Proposal accepted.')
            pending_eval = True
            pending_proposal_metrics = {'proposal_source': 'llm', 'parent_skill_yaml': parent_yaml_for_proposal, 'parent_metrics': parent_metrics_for_proposal, 'proposal_iteration': iter_idx}
            current_skill = proposed_skill
            current_skill_path.write_text(dump_skill(current_skill))
        else:
            print(f'  Proposal rejected (status={parse_status}) — keeping current skill.')
        (iter_dir / 'proposal_metadata.json').write_text(_json_dumps({'iteration': iter_idx, 'accepted': accepted, 'parse_status': parse_status, 'elapsed_s': elapsed_s, 'agent_template': args.condition, 'timestamp_utc': datetime.datetime.utcnow().isoformat()}, indent=2))
        _append_run_log(run_log_path, {'iteration': iter_idx, 'evaluated_skill_yaml': evaluated_skill_yaml, 'proposed_skill_yaml': dump_skill(proposed_skill) if accepted and proposed_skill is not None else None, **metrics.to_dict(), **_evaluation_identity(_best_params, randomized_config_bank), 'accepted': accepted, 'parse_status': parse_status, 'best_so_far': best_so_far, 'consecutive_holds': consecutive_holds, **evaluated_proposal_fields, 'timestamp_utc': datetime.datetime.utcnow().isoformat(), 'proposal_parse_accepted': accepted, 'is_best_update': _iter_accepted, **_semantic_generation0_fields(semantic_binding, args.condition, iter_idx)})
        _write_checkpoint(checkpoints_dir, iter_idx, current_skill, best_so_far, archive, evaluated_hashes, best_skill=best_skill, consecutive_holds=consecutive_holds, best_composite=best_composite, pending_proposal_metrics=pending_proposal_metrics, initial_skill_yaml_sha256=initial_skill_sha256, realized_scene_state_sha256=realized_scene_state_sha256, randomized_config_bank_sha256=randomized_config_bank.sha256 if randomized_config_bank else None, randomized_config_bank_wrapper_sha256=randomized_config_bank_wrapper_sha256)
    final_evaluation_error: Exception | None = None
    if pending_eval or pending_proposal_metrics is not None:
        print('\nRunning final evaluation on last accepted proposal…')
        final_iter_label = args.T
        final_iter_dir = out_dir / f'iter_{final_iter_label:03d}'
        final_iter_dir.mkdir(parents=True, exist_ok=True)
        final_evaluated_skill_yaml = dump_skill(current_skill)
        try:
            (current_skill, _) = sanitize_subtasks(current_skill, task_spec)
            _final_task_spec = _apply_free_subtasks(current_skill, task_spec, args.subtask_mode)
            artifact = compile_skill(current_skill)
            (metrics, _best_params, cma_diagnostics, traces) = _run_cma_eval(artifact, backend, task_spec=_final_task_spec, task_name=args.task, seed=args.seed + args.T, budget=args.cma_budget, k_runs=args.k_runs, randomized_config_bank=randomized_config_bank)
            successful_evaluations += 1
            print(f'  [final] composite={metrics.composite_score:.3f}  task_score={metrics.task_score:.3f}')
            if metrics.task_score > best_so_far or (metrics.task_score == best_so_far and metrics.composite_score > best_composite):
                _final_is_best = True
                best_so_far = metrics.task_score
                best_composite = metrics.composite_score
                best_skill = current_skill
            else:
                _final_is_best = False
            archive.add(current_skill, metrics, generation=args.T)
            archive.save(archive_path)
            (final_iter_dir / 'metrics.json').write_text(_json_dumps(metrics.to_dict(), indent=2))
            (final_iter_dir / 'cma_diagnostics.json').write_text(_json_dumps(cma_diagnostics, indent=2))
            (final_iter_dir / 'traces.json').write_text(_json_dumps(traces, indent=2))
            _final_parent_yaml = None
            _final_parent_metrics = None
            _final_source = 'final_eval'
            if pending_proposal_metrics:
                _final_parent_yaml = pending_proposal_metrics.get('parent_skill_yaml')
                _final_parent_metrics = pending_proposal_metrics.get('parent_metrics')
                _final_source = pending_proposal_metrics.get('proposal_source', 'llm')
            final_proposal_fields = build_evaluated_proposal_metrics(task=args.task, candidate_skill=current_skill, parent_skill=None, candidate_yaml=dump_skill(current_skill), parent_yaml=_final_parent_yaml, candidate_metrics=metrics, parent_metrics=_final_parent_metrics, task_spec=task_spec, subtask_mode=args.subtask_mode, proposal_source=_final_source, accepted_as_elite=_final_is_best, parse_status='final_eval')
            pending_proposal_metrics = None
            _append_run_log(run_log_path, {'iteration': 'final_eval', 'evaluated_skill_yaml': final_evaluated_skill_yaml, 'proposed_skill_yaml': None, **metrics.to_dict(), **_evaluation_identity(_best_params, randomized_config_bank), 'accepted': True, 'parse_status': 'final_eval', 'best_so_far': best_so_far, 'consecutive_holds': consecutive_holds, **final_proposal_fields, 'timestamp_utc': datetime.datetime.utcnow().isoformat(), 'proposal_parse_accepted': False, 'is_best_update': _final_is_best})
            _write_checkpoint(checkpoints_dir, args.T, current_skill, best_so_far, archive, evaluated_hashes, best_skill=best_skill, consecutive_holds=consecutive_holds, best_composite=best_composite, pending_proposal_metrics=pending_proposal_metrics, initial_skill_yaml_sha256=initial_skill_sha256, realized_scene_state_sha256=realized_scene_state_sha256, randomized_config_bank_sha256=randomized_config_bank.sha256 if randomized_config_bank else None, randomized_config_bank_wrapper_sha256=randomized_config_bank_wrapper_sha256)
        except Exception as exc:
            print(f'  Final eval crashed: {exc}', file=sys.stderr)
            (final_iter_dir / 'cma_error.txt').write_text(str(exc))
            (final_iter_dir / 'SKIPPED').write_text('reason=final_cma_crash\n')
            final_evaluation_error = exc
    if semantic_binding is not None:
        _finalize_semantic_coverage(run_log_path, manipulation_ledger_path)
    _validate_loop_completion(final_evaluation_error, successful_evaluations)
    summary = {"task": args.task, "seed": args.seed, "backend_name": "mujoco", "scientific": True, "best_task_score": best_so_far, "best_composite_score": best_composite, "scene_bank_sha256": randomized_config_bank.sha256 if randomized_config_bank is not None else None}
    (out_dir / "summary.json").write_text(_json_dumps(summary, indent=2), encoding="utf-8")
    print(f'\nLoop complete.  Best task_score: {best_so_far:.3f}  Best composite score: {best_composite:.3f}')
    print(f'Output: {out_dir}')
if __name__ == '__main__':
    main()
