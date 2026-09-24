## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4213 | 0.29 | ❌ rejected |
| 8 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4345 | 0.47 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.3902 | 0.39 | ✅ accepted |
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | 14 | -0.4785 | 0.11 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1871 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.421) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.05
  weight: 0.3
- id: push_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_y:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_safe
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.09
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    descend_y:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_pre_contact
- id: align_to_peg
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_final
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_final_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    descend_height:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 39.0
      default: 38.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 38.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_channel
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_y: status=consumed; consumers=target.offset.y (replace)
- **descend_safe** (`descend`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.09], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_y: status=consumed; consumers=target.offset.y (replace)
- **align_to_peg** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_final** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_final_speed: status=consumed; consumers=generator.speed (replace)
    - descend_height: status=consumed; consumers=target.offset.z (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=38.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.421
- **task_score** (E): 0.293
- **fitness_score**: 0.449  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.870

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1429 |
| descend_safe | 1.00 | 1.00 | 0.0791 |
| align_to_peg | 1.00 | 1.00 | 0.0741 |
| descend_final | 1.00 | 1.00 | 0.0240 |
| push_1 | 0.00 | 1.00 | 0.0004 |
| retract_1 | 1.00 | 1.00 | 0.1785 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.205, 0.159) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.551 | 2.857 |
| descend_safe | descend | 1.00 / step_budget | (0.482, 0.205, 0.159)→(0.491, 0.191, 0.090) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.553 | 0.577 |
| align_to_peg | align | 1.00 / step_budget | (0.491, 0.191, 0.090)→(0.493, 0.118, 0.080) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.554 | 0.581 |
| descend_final | descend | 1.00 / step_budget | (0.493, 0.118, 0.080)→(0.492, 0.112, 0.056) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.532 | 0.582 |
| push_1 | push | 0.00 / guard_failure | (0.509, 0.106, 0.039)→(0.510, 0.107, 0.039) | (0.497, 0.080, 0.034)→(0.497, 0.078, 0.034) | 0.160→0.158 | 1.00 / 1.333 | 473.618 | 666.315 |
| retract_1 | retract | 1.00 / step_budget | (0.510, 0.107, 0.039)→(0.507, 0.106, 0.218) | (0.497, 0.078, 0.034)→(0.496, -0.011, 0.028) | 0.158→0.077 | 1.00 / 1.000 | 0.590 | 210.425 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.863
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.592
- phase_score: 0.741
- phase_breakdown.push_channel_score: 0.871
- phase_breakdown.reach_pre_contact_score: 0.436

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.681
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.592
- **Median Q (composite search score)**: -0.308
- **K-run variance**: 0.0623
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2037,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.13822,"approach_1.approach_speed":0.29302,"approach_1.approach_y":0.09415,"descend_final.descend_final_speed":0.09716,"descend_final.descend_height":0.01993,"descend_safe.descend_speed":0.18159,"descend_safe.descend_y":0.13002,"push_1.force_guard_threshold":34.38689,"push_1.push_distance":0.17861,"push_1.push_max_time":4.84714,"push_1.push_speed":0.08268,"push_1.retry_offset_x":-5e-05,"push_1.retry_offset_y":0.0048,"retract_1.retract_height":0.22806,"retract_1.retract_speed":0.22695},"optimized_scores":{"best_composite_score":-0.76757,"best_fitness_score":0.10243,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.55467,0.11427,0.05857],"force_p95":1847.60481,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1856.47653,"mean_force":1665.9217,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53383,0.14374,0.02306]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.55455,0.10848,0.05824],"force_p95":486.62138,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.13194,"mean_force":175.24832,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54231,0.14343,0.02213]},{"body_a":"peg","body_b":"channel_base_body","contact_count":376.0,"contact_point_centroid":[0.50091,0.11591,0.00939],"force_p95":0.62588,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49842,0.2036,0.22719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":624.0,"contact_point_centroid":[0.50094,0.11595,0.00942],"force_p95":0.61092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64509,"mean_force":0.5426,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53428,0.14295,0.11785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":67.0,"contact_point_centroid":[0.50062,0.11656,0.00944],"force_p95":0.59619,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64129,"mean_force":0.53987,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49672,0.15152,0.07158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":380.0,"contact_point_centroid":[0.50082,0.11594,0.00942],"force_p95":0.61411,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63885,"mean_force":0.54267,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49585,0.19576,0.08237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":262.0,"contact_point_centroid":[0.501,0.11614,0.00944],"force_p95":0.59642,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6252,"mean_force":0.54104,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49682,0.22263,0.12364]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50135,0.11537,0.00943],"force_p95":0.60133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60194,"mean_force":0.5461,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51468,0.14842,0.04634]}],"total_contact_groups":8},"final_pose_error":0.01941,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50098,0.11605,0.03383],"final_tcp_position":[0.53403,0.14311,0.22893],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":1856.47653,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.50093,0.11608,0.03391],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.56207,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":376.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49814,0.20802,0.15927],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":262.0,"n_steps_budget":600.0,"object_pos_end":[0.50093,0.11601,0.03392],"object_pos_start":[0.50093,0.11608,0.03391],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19617,"object_z_max":0.0341,"peak_contact_force":0.57361,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":262.0,"raw_peak_contact_force":0.6252,"subtask_id":"reach_pre_contact","tcp_end":[0.49725,0.23895,0.08955],"tcp_start":[0.49814,0.20802,0.15927],"tcp_to_object_dist_end":0.13498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":600.0,"object_pos_end":[0.50097,0.11613,0.03387],"object_pos_start":[0.50093,0.11601,0.03392],"object_to_goal_dist_end":0.19623,"object_to_goal_dist_start":0.19611,"object_z_max":0.03404,"peak_contact_force":0.56875,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":380.0,"raw_peak_contact_force":0.63885,"subtask_id":"reach_pre_contact","tcp_end":[0.49712,0.15392,0.07944],"tcp_start":[0.49725,0.23895,0.08955],"tcp_to_object_dist_end":0.05932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":67.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.116,0.03391],"object_pos_start":[0.50097,0.11613,0.03387],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19623,"object_z_max":0.03395,"peak_contact_force":0.50639,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":67.0,"raw_peak_contact_force":0.64129,"subtask_id":"reach_pre_contact","tcp_end":[0.49665,0.14897,0.0623],"tcp_start":[0.49712,0.15392,0.07944],"tcp_to_object_dist_end":0.04372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.11607,0.03386],"object_pos_start":[0.50095,0.116,0.03391],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.1961,"object_z_max":0.03392,"peak_contact_force":1417.76722,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":32.0,"raw_peak_contact_force":1856.47653,"subtask_id":"push_channel","tcp_end":[0.53617,0.14379,0.02015],"tcp_start":[0.53525,0.14352,0.02081],"tcp_to_object_dist_end":0.04687,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":624.0,"n_steps_budget":660.0,"object_pos_end":[0.50098,0.11605,0.03383],"object_pos_start":[0.50103,0.11603,0.03386],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19613,"object_z_max":0.03404,"peak_contact_force":0.55912,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":643.0,"raw_peak_contact_force":612.13194,"subtask_id":"push_channel","tcp_end":[0.53403,0.14311,0.22893],"tcp_start":[0.53617,0.14379,0.02015],"tcp_to_object_dist_end":0.19973,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":69.0,"average_failure_rate":0.40588,"average_mean_iterations":83.58235,"average_solve_count":170.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.09357,"approach_1.approach_speed":0.22293,"approach_1.approach_y":0.12988,"descend_final.descend_final_speed":0.10543,"descend_final.descend_height":0.00697,"descend_safe.descend_speed":0.12902,"descend_safe.descend_y":0.08074,"push_1.force_guard_threshold":35.66856,"push_1.push_distance":0.20066,"push_1.push_max_time":6.99177,"push_1.push_speed":0.0908,"push_1.retry_offset_x":0.00365,"push_1.retry_offset_y":-0.00224,"retract_1.retract_height":0.16877,"retract_1.retract_speed":0.31009},"optimized_scores":{"best_composite_score":-0.18884,"best_fitness_score":0.68116,"best_task_score":0.59179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49464,0.08092,0.04958],"force_p95":64.57017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.31428,"mean_force":34.90326,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49385,0.09241,0.04653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.4902,0.07119,0.00934],"force_p95":54.57287,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.86299,"mean_force":14.1044,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49218,0.094,0.04791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":499.0,"contact_point_centroid":[0.49779,-0.06588,0.00846],"force_p95":0.97222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.97483,"mean_force":0.66643,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49369,0.08948,0.12245]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47499,-0.04983,0.0245],"force_p95":8.43997,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54754,"mean_force":2.66824,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49376,0.08968,0.15036]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52509,-0.09869,0.02693],"force_p95":3.53206,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.54556,"mean_force":1.27886,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49324,0.08952,0.08535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.49056,-0.10016,0.0214],"force_p95":1.12931,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.29203,"mean_force":0.36319,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49335,0.08944,0.09037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.4957,0.06379,0.00936],"force_p95":0.62558,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56927,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48907,0.19608,0.22545]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49927,0.19944,0.29649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":113.0,"contact_point_centroid":[0.49552,0.06315,0.0094],"force_p95":0.55186,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54528,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49017,0.09882,0.06544]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.49474,0.06397,0.0094],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54571,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.4839,0.17228,0.12416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.49542,0.06418,0.0094],"force_p95":0.55032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55124,"mean_force":0.54541,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.48925,0.12579,0.08343]}],"total_contact_groups":11},"final_pose_error":0.01611,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49347,-0.07417,0.0241],"final_tcp_position":[0.49416,0.08975,0.19752],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":68.31428,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":384.0,"n_steps_budget":600.0,"object_pos_end":[0.4952,0.06402,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14423,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54442,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.48016,0.19327,0.15983],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":278.0,"n_steps_budget":600.0,"object_pos_end":[0.49516,0.06366,0.03396],"object_pos_start":[0.4952,0.06402,0.03392],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14423,"object_z_max":0.03396,"peak_contact_force":0.54402,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":278.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_pre_contact","tcp_end":[0.48977,0.15055,0.08971],"tcp_start":[0.48016,0.19327,0.15983],"tcp_to_object_dist_end":0.10338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.49483,0.06391,0.034],"object_pos_start":[0.49516,0.06366,0.03396],"object_to_goal_dist_end":0.14413,"object_to_goal_dist_start":0.14387,"object_z_max":0.034,"peak_contact_force":0.54609,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":242.0,"raw_peak_contact_force":0.55124,"subtask_id":"reach_pre_contact","tcp_end":[0.49086,0.10183,0.08022],"tcp_start":[0.48977,0.15055,0.08971],"tcp_to_object_dist_end":0.05991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":113.0,"n_steps_budget":600.0,"object_pos_end":[0.49513,0.06415,0.03401],"object_pos_start":[0.49483,0.06391,0.034],"object_to_goal_dist_end":0.14436,"object_to_goal_dist_start":0.14413,"object_z_max":0.03401,"peak_contact_force":0.53807,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":113.0,"raw_peak_contact_force":0.55289,"subtask_id":"reach_pre_contact","tcp_end":[0.49033,0.09584,0.04965],"tcp_start":[0.49086,0.10183,0.08022],"tcp_to_object_dist_end":0.03566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.49548,0.06081,0.0342],"object_pos_start":[0.49513,0.06415,0.03401],"object_to_goal_dist_end":0.14101,"object_to_goal_dist_start":0.14436,"object_z_max":0.03401,"peak_contact_force":2.33089,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":68.31428,"subtask_id":"push_channel","tcp_end":[0.49663,0.09024,0.04466],"tcp_start":[0.49663,0.09024,0.04466],"tcp_to_object_dist_end":0.03125,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.49347,-0.07417,0.0241],"object_pos_start":[0.49548,0.06081,0.0342],"object_to_goal_dist_end":0.01815,"object_to_goal_dist_start":0.14101,"object_z_max":0.04366,"peak_contact_force":0.6368,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":636.0,"raw_peak_contact_force":8.97483,"subtask_id":"push_channel","tcp_end":[0.49416,0.08975,0.19752],"tcp_start":[0.49663,0.09024,0.04466],"tcp_to_object_dist_end":0.23863,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":45.0,"average_failure_rate":0.30201,"average_mean_iterations":63.77181,"average_solve_count":149.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.14991,"approach_1.approach_speed":0.27524,"approach_1.approach_y":0.15735,"descend_final.descend_final_speed":0.03813,"descend_final.descend_height":0.01505,"descend_safe.descend_speed":0.1037,"descend_safe.descend_y":0.12071,"push_1.force_guard_threshold":31.73972,"push_1.push_distance":0.18168,"push_1.push_max_time":9.23928,"push_1.push_speed":0.08446,"push_1.retry_offset_x":0.00163,"push_1.retry_offset_y":-0.00332,"retract_1.retract_height":0.19108,"retract_1.retract_speed":0.25181},"optimized_scores":{"best_composite_score":-0.30756,"best_fitness_score":0.56244,"best_task_score":0.28738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49386,0.07563,0.05419],"force_p95":73.31112,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.15393,"mean_force":65.72582,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4937,0.08739,0.05401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.48893,0.04369,0.00939],"force_p95":67.90271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.15258,"mean_force":18.7899,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49143,0.08964,0.0558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50065,-0.07057,0.00821],"force_p95":1.42724,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.16782,"mean_force":0.78328,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49316,0.08492,0.13998]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52507,-0.09948,0.02472],"force_p95":9.56944,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76249,"mean_force":4.40837,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49267,0.08487,0.08971]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47499,-0.04984,0.02444],"force_p95":8.66948,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.86573,"mean_force":2.94493,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49359,0.08515,0.21954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.49451,0.05908,0.00934],"force_p95":0.60498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4824,0.2066,0.22491]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4987,0.19991,0.29524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":94.0,"contact_point_centroid":[0.48747,-0.10045,0.02735],"force_p95":1.12495,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.99712,"mean_force":0.29393,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49298,0.08486,0.12875]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.49433,0.05912,0.00939],"force_p95":0.55001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54592,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.48726,0.13908,0.08288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.49396,0.05871,0.00939],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54618,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.47595,0.1986,0.12399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":85.0,"contact_point_centroid":[0.49344,0.05911,0.0094],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5514,"mean_force":0.54576,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.48957,0.09425,0.06928]}],"total_contact_groups":11},"final_pose_error":0.01756,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49316,-0.07449,0.02486],"final_tcp_position":[0.49376,0.08519,0.22627],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":74.15393,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":394.0,"n_steps_budget":600.0,"object_pos_end":[0.49402,0.05894,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54783,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":400.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.4674,0.21354,0.15933],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.49421,0.05885,0.03388],"object_pos_start":[0.49402,0.05894,0.03385],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.1392,"object_z_max":0.03388,"peak_contact_force":0.54206,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":273.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_pre_contact","tcp_end":[0.48693,0.18335,0.08982],"tcp_start":[0.4674,0.21354,0.15933],"tcp_to_object_dist_end":0.13668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":395.0,"n_steps_budget":600.0,"object_pos_end":[0.49396,0.05907,0.03393],"object_pos_start":[0.49421,0.05885,0.03388],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13911,"object_z_max":0.03393,"peak_contact_force":0.54676,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":395.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_pre_contact","tcp_end":[0.49009,0.09683,0.07979],"tcp_start":[0.48693,0.18335,0.08982],"tcp_to_object_dist_end":0.05953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":85.0,"n_steps_budget":600.0,"object_pos_end":[0.49394,0.05886,0.03395],"object_pos_start":[0.49396,0.05907,0.03393],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13933,"object_z_max":0.03395,"peak_contact_force":0.5513,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":85.0,"raw_peak_contact_force":0.5514,"subtask_id":"reach_pre_contact","tcp_end":[0.48958,0.09157,0.05752],"tcp_start":[0.49009,0.09683,0.07979],"tcp_to_object_dist_end":0.04056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.49388,0.05791,0.0344],"object_pos_start":[0.49394,0.05886,0.03395],"object_to_goal_dist_end":0.13816,"object_to_goal_dist_start":0.13912,"object_z_max":0.0344,"peak_contact_force":0.75722,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":74.15393,"subtask_id":"push_channel","tcp_end":[0.49594,0.08561,0.05261],"tcp_start":[0.49594,0.08561,0.05261],"tcp_to_object_dist_end":0.03322,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.49316,-0.07449,0.02486],"object_pos_start":[0.49398,0.05634,0.03525],"object_to_goal_dist_end":0.0175,"object_to_goal_dist_start":0.13656,"object_z_max":0.04637,"peak_contact_force":0.57262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":628.0,"raw_peak_contact_force":10.16782,"subtask_id":"push_channel","tcp_end":[0.49376,0.08519,0.22627],"tcp_start":[0.49594,0.08561,0.05261],"tcp_to_object_dist_end":0.25703,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```