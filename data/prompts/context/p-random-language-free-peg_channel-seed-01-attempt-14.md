## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4205 | 0.49 | ✅ accepted |
| 13 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.5530 | 0.21 | ❌ rejected |
| 12 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.4342 | 0.28 | ❌ rejected |
| 11 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.4476 | 0.40 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.0080 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.49 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.420) — your mutation base

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

- **Composite score**: -0.420
- **task_score** (E): 0.492
- **fitness_score**: 0.350  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1589 |
| descend_safe | 1.00 | 1.00 | 0.0755 |
| align_to_peg | 1.00 | 1.00 | 0.0504 |
| descend_final | 1.00 | 1.00 | 0.0377 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.1483 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.131, 0.158) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.559 | 2.857 |
| descend_safe | descend | 1.00 / step_budget | (0.497, 0.131, 0.158)→(0.496, 0.166, 0.095) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.525 | 0.580 |
| align_to_peg | align | 1.00 / step_budget | (0.496, 0.166, 0.095)→(0.493, 0.118, 0.081) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.537 | 0.580 |
| descend_final | descend | 1.00 / step_budget | (0.493, 0.118, 0.081)→(0.492, 0.111, 0.044) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.549 | 0.573 |
| push_1 | push | 0.00 / guard_failure | (0.489, -0.003, 0.040)→(0.489, -0.003, 0.040) | (0.497, 0.079, 0.034)→(0.504, -0.028, 0.038) | 0.160→0.056 | 1.00 / 3.000 | 23.836 | 44.284 |
| retract_1 | retract | 1.00 / step_budget | (0.489, -0.003, 0.040)→(0.486, -0.003, 0.188) | (0.504, -0.028, 0.038)→(0.498, -0.039, 0.027) | 0.056→0.044 | 1.00 / 1.000 | 0.654 | 203.282 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.329
- terminal_score: 1.000
- phase_score: 0.220
- phase_breakdown.push_channel_score: 0.174
- phase_breakdown.reach_pre_contact_score: 0.328

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.532
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.487
- **K-run variance**: 0.0171
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.257


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80147,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.119,"approach_1.approach_speed":0.34571,"approach_1.approach_y":0.12283,"descend_final.descend_final_speed":0.07425,"descend_final.descend_height":-0.00793,"descend_safe.descend_speed":0.10534,"descend_safe.descend_y":0.1943,"push_1.force_guard_threshold":33.49834,"push_1.push_distance":0.21314,"push_1.push_max_time":6.97264,"push_1.push_speed":0.13361,"retract_1.retract_height":0.15637,"retract_1.retract_speed":0.27778},"optimized_scores":{"best_composite_score":-0.23786,"best_fitness_score":0.53214,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.50724,-0.10047,0.05999],"force_p95":32.43559,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.53804,"mean_force":21.71731,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49238,-0.05455,0.02976]},{"body_a":"attachment","body_b":"peg","contact_count":695.0,"contact_point_centroid":[0.4995,0.03497,0.04052],"force_p95":15.70712,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.46243,"mean_force":4.65161,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49255,0.04574,0.02998]},{"body_a":"attachment","body_b":"peg","contact_count":87.0,"contact_point_centroid":[0.49785,-0.06569,0.05693],"force_p95":14.69008,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.79392,"mean_force":4.76464,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48964,-0.05504,0.04161]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.50637,0.01253,0.0099],"force_p95":13.55671,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.60076,"mean_force":5.61453,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49272,0.0552,0.03016]},{"body_a":"peg","body_b":"channel_base_body","contact_count":69.0,"contact_point_centroid":[0.50634,-0.10018,0.06026],"force_p95":12.85745,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.36341,"mean_force":5.38293,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48986,-0.05502,0.03704]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":691.0,"contact_point_centroid":[0.52511,0.01318,0.02841],"force_p95":6.76932,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.4925,"mean_force":1.92556,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49248,0.03934,0.0299]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52518,-0.08212,0.05491],"force_p95":6.97475,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.4468,"mean_force":4.18877,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49022,-0.05499,0.03334]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.50479,-0.08137,0.00952],"force_p95":0.71433,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.3584,"mean_force":0.5782,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48903,-0.05516,0.10345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.501,0.11603,0.00937],"force_p95":0.63701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56267,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49789,0.16335,0.22587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.50073,0.11607,0.00942],"force_p95":0.60284,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63619,"mean_force":0.54251,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49578,0.15631,0.12373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":156.0,"contact_point_centroid":[0.50151,0.11583,0.00939],"force_p95":0.61777,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.633,"mean_force":0.54546,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49551,0.17054,0.08584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.50077,0.11599,0.00944],"force_p95":0.58975,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61573,"mean_force":0.5411,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49571,0.15067,0.05814]}],"total_contact_groups":12},"final_pose_error":0.01515,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50263,-0.07795,0.03383],"final_tcp_position":[0.48946,-0.05526,0.17102],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":33.53804,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":441.0,"n_steps_budget":600.0,"object_pos_end":[0.50088,0.11608,0.03381],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":425.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49719,0.12846,0.15754],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":331.0,"n_steps_budget":600.0,"object_pos_end":[0.50099,0.11602,0.03386],"object_pos_start":[0.50088,0.11608,0.03381],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19618,"object_z_max":0.03394,"peak_contact_force":0.48013,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":331.0,"raw_peak_contact_force":0.63619,"subtask_id":"reach_pre_contact","tcp_end":[0.49633,0.18556,0.09263],"tcp_start":[0.49719,0.12846,0.15754],"tcp_to_object_dist_end":0.09117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":156.0,"n_steps_budget":600.0,"object_pos_end":[0.50098,0.11612,0.03383],"object_pos_start":[0.50099,0.11602,0.03386],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19612,"object_z_max":0.03386,"peak_contact_force":0.51797,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":156.0,"raw_peak_contact_force":0.633,"subtask_id":"reach_pre_contact","tcp_end":[0.4965,0.1545,0.08112],"tcp_start":[0.49633,0.18556,0.09263],"tcp_to_object_dist_end":0.06107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":164.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11604,0.03386],"object_pos_start":[0.50098,0.11612,0.03383],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19622,"object_z_max":0.03401,"peak_contact_force":0.564,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":164.0,"raw_peak_contact_force":0.61573,"subtask_id":"reach_pre_contact","tcp_end":[0.4963,0.14707,0.03442],"tcp_start":[0.4965,0.1545,0.08112],"tcp_to_object_dist_end":0.03138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":953.0,"n_steps_budget":990.0,"object_pos_end":[0.50721,-0.0819,0.03609],"object_pos_start":[0.50095,0.11604,0.03386],"object_to_goal_dist_end":0.00842,"object_to_goal_dist_start":0.19614,"object_z_max":0.03696,"peak_contact_force":10.14592,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1873.0,"raw_peak_contact_force":33.53804,"subtask_id":"push_channel","tcp_end":[0.49218,-0.05552,0.02955],"tcp_start":[0.49224,-0.05548,0.02961],"tcp_to_object_dist_end":0.03106,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50263,-0.07795,0.03383],"object_pos_start":[0.50719,-0.08208,0.03596],"object_to_goal_dist_end":0.00702,"object_to_goal_dist_start":0.0085,"object_z_max":0.03751,"peak_contact_force":0.54661,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":680.0,"raw_peak_contact_force":16.79392,"subtask_id":"push_channel","tcp_end":[0.48946,-0.05526,0.17102],"tcp_start":[0.49218,-0.05552,0.02955],"tcp_to_object_dist_end":0.13968,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92857,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.12733,"approach_1.approach_speed":0.36379,"approach_1.approach_y":0.10614,"descend_final.descend_final_speed":0.06377,"descend_final.descend_height":0.00893,"descend_safe.descend_speed":0.1548,"descend_safe.descend_y":0.17123,"push_1.force_guard_threshold":38.00646,"push_1.push_distance":0.17491,"push_1.push_max_time":5.95097,"push_1.push_speed":0.08278,"retract_1.retract_height":0.16222,"retract_1.retract_speed":0.32924},"optimized_scores":{"best_composite_score":-0.48681,"best_fitness_score":0.28319,"best_task_score":0.32863},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.47498,0.01731,0.05392],"force_p95":286.44813,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.73275,"mean_force":179.42143,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48677,0.01738,0.05179]},{"body_a":"attachment","body_b":"peg","contact_count":510.0,"contact_point_centroid":[0.49519,0.04324,0.0481],"force_p95":31.93195,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.23152,"mean_force":14.12342,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48694,0.05155,0.04738]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":414.0,"contact_point_centroid":[0.52539,0.02555,0.04179],"force_p95":28.47774,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.32168,"mean_force":12.57463,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48682,0.04436,0.0473]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":102.0,"contact_point_centroid":[0.475,0.04375,0.04945],"force_p95":33.84107,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.96079,"mean_force":22.39284,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4868,0.04376,0.04731]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.49694,0.01208,0.04642],"force_p95":37.46241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.46915,"mean_force":19.21954,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,0.01751,0.04804]},{"body_a":"peg","body_b":"channel_base_body","contact_count":524.0,"contact_point_centroid":[0.50672,0.02643,0.00984],"force_p95":22.4607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.22196,"mean_force":9.33115,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48713,0.05513,0.04757]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":54.0,"contact_point_centroid":[0.52564,0.00417,0.03616],"force_p95":33.89913,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.11445,"mean_force":5.94564,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,0.01738,0.05184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50053,-0.01075,0.00837],"force_p95":1.61858,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.98215,"mean_force":0.91539,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4843,0.0175,0.11993]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,-0.03899,0.02423],"force_p95":7.2636,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.46805,"mean_force":2.40915,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48425,0.01756,0.19354]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49563,0.06391,0.00936],"force_p95":0.59762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56489,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49782,0.15427,0.22362]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49957,0.19788,0.29657]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.49546,0.0638,0.0094],"force_p95":0.55086,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54528,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49281,0.13262,0.08547]},{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.49387,0.06359,0.0094],"force_p95":0.55049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55275,"mean_force":0.54516,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49078,0.09928,0.06663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.49478,0.064,0.0094],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54563,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49578,0.13686,0.1242]}],"total_contact_groups":14},"final_pose_error":0.01537,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.494,-0.01485,0.02431],"final_tcp_position":[0.48428,0.01756,0.19456],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":316.73275,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.49504,0.06406,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54637,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":467.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.49717,0.11277,0.15684],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.49492,0.06369,0.03398],"object_pos_start":[0.49504,0.06406,0.03394],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14427,"object_z_max":0.03398,"peak_contact_force":0.54655,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":303.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_pre_contact","tcp_end":[0.4963,0.1627,0.09358],"tcp_start":[0.49717,0.11277,0.15684],"tcp_to_object_dist_end":0.11557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":275.0,"n_steps_budget":600.0,"object_pos_end":[0.49493,0.0641,0.03402],"object_pos_start":[0.49492,0.06369,0.03398],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.1439,"object_z_max":0.03402,"peak_contact_force":0.5434,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":275.0,"raw_peak_contact_force":0.55289,"subtask_id":"reach_pre_contact","tcp_end":[0.49166,0.10233,0.08059],"tcp_start":[0.4963,0.1627,0.09358],"tcp_to_object_dist_end":0.06034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.49511,0.06359,0.03402],"object_pos_start":[0.49493,0.0641,0.03402],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14432,"object_z_max":0.03402,"peak_contact_force":0.54106,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":107.0,"raw_peak_contact_force":0.55275,"subtask_id":"reach_pre_contact","tcp_end":[0.49067,0.09623,0.05159],"tcp_start":[0.49166,0.10233,0.08059],"tcp_to_object_dist_end":0.03734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.50838,0.00063,0.03828],"object_pos_start":[0.49511,0.06359,0.03402],"object_to_goal_dist_end":0.08108,"object_to_goal_dist_start":0.14379,"object_z_max":0.04051,"peak_contact_force":33.80313,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1550.0,"raw_peak_contact_force":45.23152,"subtask_id":"push_channel","tcp_end":[0.48678,0.01768,0.0475],"tcp_start":[0.4868,0.01773,0.04753],"tcp_to_object_dist_end":0.02902,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.494,-0.01485,0.02431],"object_pos_start":[0.50836,0.00037,0.03814],"object_to_goal_dist_end":0.06728,"object_to_goal_dist_start":0.08082,"object_z_max":0.03909,"peak_contact_force":0.64559,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":643.0,"raw_peak_contact_force":316.73275,"subtask_id":"push_channel","tcp_end":[0.48428,0.01756,0.19456],"tcp_start":[0.48678,0.01768,0.0475],"tcp_to_object_dist_end":0.17358,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77686,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.12546,"approach_1.approach_speed":0.28637,"approach_1.approach_y":0.14792,"descend_final.descend_final_speed":0.11712,"descend_final.descend_height":0.0036,"descend_safe.descend_speed":0.12103,"descend_safe.descend_y":0.15199,"push_1.force_guard_threshold":36.19279,"push_1.push_distance":0.23797,"push_1.push_max_time":6.93846,"push_1.push_speed":0.12001,"retract_1.retract_height":0.17033,"retract_1.retract_speed":0.15279},"optimized_scores":{"best_composite_score":-0.53678,"best_fitness_score":0.23322,"best_task_score":0.14821},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":58.0,"contact_point_centroid":[0.47498,0.02809,0.05221],"force_p95":237.19821,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.3187,"mean_force":139.20158,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48677,0.02808,0.05008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.49464,0.02578,0.0098],"force_p95":32.53394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.08322,"mean_force":16.26549,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48724,0.06124,0.04296]},{"body_a":"attachment","body_b":"peg","contact_count":316.0,"contact_point_centroid":[0.49098,0.04727,0.04251],"force_p95":32.28205,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.725,"mean_force":17.57413,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48709,0.05829,0.04279]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.06738,0.04459],"force_p95":30.24977,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.73287,"mean_force":23.28166,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48681,0.06738,0.04246]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.4957,-0.02215,0.00814],"force_p95":0.77438,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.70548,"mean_force":0.68785,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48501,0.0283,0.11932]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49289,0.01824,0.04278],"force_p95":15.87597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.01583,"mean_force":3.11477,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48714,0.02843,0.04359]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47499,-0.04785,0.02388],"force_p95":8.93456,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.29579,"mean_force":2.81446,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48594,0.028,0.0621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.49444,0.05906,0.00934],"force_p95":0.59679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58462,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49788,0.1745,0.22453]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49953,0.19826,0.2953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.49423,0.05891,0.00939],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54607,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49257,0.12458,0.08887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.49411,0.05854,0.00939],"force_p95":0.5507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54617,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.496,0.15112,0.12907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":129.0,"contact_point_centroid":[0.49378,0.05906,0.00939],"force_p95":0.54991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.551,"mean_force":0.54583,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49003,0.09449,0.0644]}],"total_contact_groups":12},"final_pose_error":0.01428,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49704,-0.02462,0.02405],"final_tcp_position":[0.48507,0.0284,0.19957],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":276.3187,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":410.0,"n_steps_budget":600.0,"object_pos_end":[0.49404,0.05888,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.55091,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":416.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.49723,0.15181,0.15876],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":192.0,"n_steps_budget":600.0,"object_pos_end":[0.49425,0.05892,0.03388],"object_pos_start":[0.49404,0.05888,0.03385],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.13915,"object_z_max":0.03388,"peak_contact_force":0.54868,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":192.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_pre_contact","tcp_end":[0.49621,0.15099,0.09919],"tcp_start":[0.49723,0.15181,0.15876],"tcp_to_object_dist_end":0.1129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.49428,0.059,0.0339],"object_pos_start":[0.49425,0.05892,0.03388],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.13918,"object_z_max":0.0339,"peak_contact_force":0.5496,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":242.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_pre_contact","tcp_end":[0.49112,0.09798,0.08162],"tcp_start":[0.49621,0.15099,0.09919],"tcp_to_object_dist_end":0.0617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.49427,0.05885,0.03392],"object_pos_start":[0.49428,0.059,0.0339],"object_to_goal_dist_end":0.1391,"object_to_goal_dist_start":0.13925,"object_z_max":0.03392,"peak_contact_force":0.5432,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":129.0,"raw_peak_contact_force":0.551,"subtask_id":"reach_pre_contact","tcp_end":[0.49,0.091,0.04623],"tcp_start":[0.49112,0.09798,0.08162],"tcp_to_object_dist_end":0.03469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.49743,-0.00213,0.03966],"object_pos_start":[0.49427,0.05885,0.03392],"object_to_goal_dist_end":0.07791,"object_to_goal_dist_start":0.1391,"object_z_max":0.04035,"peak_contact_force":27.5586,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":669.0,"raw_peak_contact_force":54.08322,"subtask_id":"push_channel","tcp_end":[0.48759,0.02856,0.0433],"tcp_start":[0.48761,0.02863,0.04332],"tcp_to_object_dist_end":0.03244,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.49704,-0.02462,0.02405],"object_pos_start":[0.4975,-0.00257,0.03962],"object_to_goal_dist_end":0.05771,"object_to_goal_dist_start":0.07747,"object_z_max":0.03962,"peak_contact_force":0.77008,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":733.0,"raw_peak_contact_force":276.3187,"subtask_id":"push_channel","tcp_end":[0.48507,0.0284,0.19957],"tcp_start":[0.48759,0.02856,0.0433],"tcp_to_object_dist_end":0.18374,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```