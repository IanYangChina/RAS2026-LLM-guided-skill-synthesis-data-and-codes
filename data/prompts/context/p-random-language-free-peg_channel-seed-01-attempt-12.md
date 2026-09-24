## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.4342 | 0.28 | ❌ rejected |
| 11 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.4476 | 0.40 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.0080 | 0.27 | ❌ rejected |
| 9 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4213 | 0.29 | ❌ rejected |
| 8 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4345 | 0.47 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.434) — your mutation base

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

- **Composite score**: -0.434
- **task_score** (E): 0.280
- **fitness_score**: 0.186  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1563 |
| descend_safe | 1.00 | 1.00 | 0.0932 |
| align_to_peg | 1.00 | 1.00 | 0.0430 |
| descend_final | 1.00 | 1.00 | 0.0192 |
| push_1 | 1.00 | 1.00 | 0.1559 |
| retract_1 | 1.00 | 1.00 | 0.1892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.088, 0.194) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.530 | 2.857 |
| descend_safe | descend | 1.00 / step_budget | (0.482, 0.088, 0.194)→(0.492, 0.080, 0.102) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.533 | 0.583 |
| align_to_peg | align | 1.00 / step_budget | (0.492, 0.080, 0.102)→(0.492, 0.097, 0.063) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.532 | 0.580 |
| descend_final | descend | 1.00 / step_budget | (0.492, 0.097, 0.063)→(0.503, 0.103, 0.049) | (0.497, 0.080, 0.034)→(0.499, 0.079, 0.032) | 0.160→0.159 | 1.00 / 2.333 | 152.300 | 169.759 |
| push_1 | push | 1.00 / time_limit | (0.503, 0.103, 0.049)→(0.495, -0.052, 0.044) | (0.499, 0.079, 0.032)→(0.496, 0.014, 0.030) | 0.159→0.096 | 1.00 / 1.333 | 21.705 | 131.892 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.052, 0.044)→(0.493, -0.052, 0.233) | (0.496, 0.014, 0.030)→(0.499, 0.005, 0.024) | 0.096→0.087 | 1.00 / 1.000 | 0.552 | 133.716 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.471
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.253
- phase_score: 0.237
- phase_breakdown.push_channel_score: 0.247
- phase_breakdown.reach_pre_contact_score: 0.214

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.243
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.425
- **Median Q (composite search score)**: -0.407
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.356


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71852,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.05999,"approach_1.approach_speed":0.197,"descend_final.descend_final_speed":0.1154,"descend_safe.descend_speed":0.11551,"push_1.push_distance":0.20845,"push_1.push_lateral_x":-8e-05,"push_1.push_max_time":9.92255,"push_1.push_speed":0.10692,"retract_1.retract_height":0.20494,"retract_1.retract_speed":0.37182},"optimized_scores":{"best_composite_score":-0.40669,"best_fitness_score":0.21331,"best_task_score":0.42494},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":324.0,"contact_point_centroid":[0.50806,0.12976,0.05211],"force_p95":160.88908,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.47201,"mean_force":105.97538,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.50095,0.13837,0.05139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.50694,0.11932,0.00764],"force_p95":154.85774,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":160.75298,"mean_force":101.8832,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.50082,0.13823,0.05169]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50543,0.07962,0.00839],"force_p95":136.27762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.33415,"mean_force":76.3943,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50692,0.06271,0.0486]},{"body_a":"attachment","body_b":"peg","contact_count":714.0,"contact_point_centroid":[0.51408,0.09032,0.05247],"force_p95":136.84252,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.80641,"mean_force":103.50674,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50911,0.08813,0.05101]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":211.0,"contact_point_centroid":[0.47473,0.08253,0.01804],"force_p95":22.16166,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.5848,"mean_force":15.18574,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50878,0.04359,0.04985]},{"body_a":"peg","body_b":"world","contact_count":42.0,"contact_point_centroid":[0.50206,0.13031,-4e-05],"force_p95":19.02104,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.32692,"mean_force":13.0314,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.50429,0.14199,0.04718]},{"body_a":"peg","body_b":"world","contact_count":7.0,"contact_point_centroid":[0.50226,0.13025,-5e-05],"force_p95":10.01401,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.19837,"mean_force":7.3683,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50483,0.14269,0.04678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":553.0,"contact_point_centroid":[0.50457,0.04865,0.00809],"force_p95":0.73967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.56257,"mean_force":0.77203,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49818,-0.02824,0.13046]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52501,0.02498,0.02445],"force_p95":9.04914,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.12478,"mean_force":3.92115,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49818,-0.02819,0.16359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50087,0.116,0.00935],"force_p95":0.63551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56651,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49845,0.16089,0.24531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":288.0,"contact_point_centroid":[0.501,0.11599,0.00943],"force_p95":0.60639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64295,"mean_force":0.54202,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49703,0.1198,0.14944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50086,0.11604,0.00944],"force_p95":0.60584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63626,"mean_force":0.54133,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49599,0.12549,0.07901]}],"total_contact_groups":12},"final_pose_error":0.01844,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5063,0.04682,0.02413],"final_tcp_position":[0.49874,-0.02822,0.22864],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":168.47201,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11612,0.03392],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5073,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":374.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49831,0.1235,0.19572],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":288.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11609,0.0338],"object_pos_start":[0.50095,0.11612,0.03392],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19622,"object_z_max":0.034,"peak_contact_force":0.50656,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":288.0,"raw_peak_contact_force":0.64295,"subtask_id":"reach_pre_contact","tcp_end":[0.49736,0.11639,0.10307],"tcp_start":[0.49831,0.1235,0.19572],"tcp_to_object_dist_end":0.06936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":600.0,"object_pos_end":[0.50094,0.116,0.03386],"object_pos_start":[0.50096,0.11609,0.0338],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19619,"object_z_max":0.03408,"peak_contact_force":0.50205,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":399.0,"raw_peak_contact_force":0.63626,"subtask_id":"reach_pre_contact","tcp_end":[0.49693,0.13353,0.06208],"tcp_start":[0.49736,0.11639,0.10307],"tcp_to_object_dist_end":0.03346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":334.0,"n_steps_budget":600.0,"object_pos_end":[0.5024,0.12065,0.02912],"object_pos_start":[0.50094,0.116,0.03386],"object_to_goal_dist_end":0.20096,"object_to_goal_dist_start":0.19609,"object_z_max":0.03391,"peak_contact_force":117.91216,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":700.0,"raw_peak_contact_force":168.47201,"subtask_id":"reach_pre_contact","tcp_end":[0.50477,0.14259,0.04669],"tcp_start":[0.49693,0.13353,0.06208],"tcp_to_object_dist_end":0.02821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49904,0.0487,0.02415],"object_pos_start":[0.5024,0.12065,0.02912],"object_to_goal_dist_end":0.12967,"object_to_goal_dist_start":0.20096,"object_z_max":0.03985,"peak_contact_force":0.64358,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1922.0,"raw_peak_contact_force":140.33415,"subtask_id":"push_channel","tcp_end":[0.50087,-0.02828,0.04201],"tcp_start":[0.50477,0.14259,0.04669],"tcp_to_object_dist_end":0.07904,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":553.0,"n_steps_budget":600.0,"object_pos_end":[0.5063,0.04682,0.02413],"object_pos_start":[0.49904,0.0487,0.02415],"object_to_goal_dist_end":0.12796,"object_to_goal_dist_start":0.12967,"object_z_max":0.0248,"peak_contact_force":0.55834,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":579.0,"raw_peak_contact_force":9.56257,"subtask_id":"push_channel","tcp_end":[0.49874,-0.02822,0.22864],"tcp_start":[0.50087,-0.02828,0.04201],"tcp_to_object_dist_end":0.21797,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68902,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.13997,"approach_1.approach_speed":0.25291,"descend_final.descend_final_speed":0.08026,"descend_safe.descend_speed":0.06075,"push_1.push_distance":0.17314,"push_1.push_lateral_x":-0.01673,"push_1.push_max_time":8.34526,"push_1.push_speed":0.07702,"retract_1.retract_height":0.24263,"retract_1.retract_speed":0.15189},"optimized_scores":{"best_composite_score":-0.37654,"best_fitness_score":0.24346,"best_task_score":0.25303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":45.0,"contact_point_centroid":[0.47498,-0.04003,0.05342],"force_p95":256.52815,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.47406,"mean_force":139.07725,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48684,-0.04002,0.05168]},{"body_a":"peg","body_b":"channel_base_body","contact_count":364.0,"contact_point_centroid":[0.50633,0.07493,0.00845],"force_p95":168.10602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.47671,"mean_force":119.97868,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49717,0.08373,0.05397]},{"body_a":"attachment","body_b":"peg","contact_count":348.0,"contact_point_centroid":[0.50677,0.07719,0.05452],"force_p95":167.61054,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.98576,"mean_force":124.98029,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49748,0.08384,0.05358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50209,0.02763,0.00861],"force_p95":111.85085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.97611,"mean_force":87.10221,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.501,0.0261,0.05248]},{"body_a":"attachment","body_b":"peg","contact_count":903.0,"contact_point_centroid":[0.50796,0.03209,0.05436],"force_p95":112.2508,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.50019,"mean_force":96.26341,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50222,0.03258,0.05312]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":716.0,"contact_point_centroid":[0.47468,0.02952,0.01594],"force_p95":22.82813,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.67556,"mean_force":13.85977,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50069,0.01655,0.05296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":924.0,"contact_point_centroid":[0.50037,-0.00873,0.00824],"force_p95":0.69716,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.96123,"mean_force":0.60737,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48539,-0.03999,0.15772]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,-0.03209,0.02434],"force_p95":5.25783,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.7961,"mean_force":2.20685,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48482,-0.03994,0.08608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":470.0,"contact_point_centroid":[0.49536,0.06384,0.00937],"force_p95":0.59655,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56361,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4887,0.13345,0.24235]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49913,0.19707,0.29727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.495,0.06348,0.0094],"force_p95":0.55085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54524,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.48916,0.07308,0.08041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.49531,0.06413,0.0094],"force_p95":0.55053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54555,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.48375,0.0688,0.14769]}],"total_contact_groups":12},"final_pose_error":0.01437,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49837,-0.01155,0.02414],"final_tcp_position":[0.48587,-0.04005,0.27393],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":289.47406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":600.0,"object_pos_end":[0.4952,0.06371,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54014,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":498.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.47975,0.0732,0.19338],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.49484,0.06393,0.03399],"object_pos_start":[0.4952,0.06371,0.03394],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.14392,"object_z_max":0.03399,"peak_contact_force":0.54558,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":337.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_pre_contact","tcp_end":[0.48996,0.06451,0.10224],"tcp_start":[0.47975,0.0732,0.19338],"tcp_to_object_dist_end":0.06842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":347.0,"n_steps_budget":600.0,"object_pos_end":[0.49538,0.06387,0.03402],"object_pos_start":[0.49484,0.06393,0.03399],"object_to_goal_dist_end":0.14407,"object_to_goal_dist_start":0.14414,"object_z_max":0.03402,"peak_contact_force":0.54919,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":347.0,"raw_peak_contact_force":0.55289,"subtask_id":"reach_pre_contact","tcp_end":[0.49063,0.0813,0.06338],"tcp_start":[0.48996,0.06451,0.10224],"tcp_to_object_dist_end":0.03447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":364.0,"n_steps_budget":600.0,"object_pos_end":[0.49747,0.06051,0.03287],"object_pos_start":[0.49538,0.06387,0.03402],"object_to_goal_dist_end":0.14071,"object_to_goal_dist_start":0.14407,"object_z_max":0.03402,"peak_contact_force":168.1354,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":712.0,"raw_peak_contact_force":169.47671,"subtask_id":"reach_pre_contact","tcp_end":[0.50339,0.08599,0.04954],"tcp_start":[0.49063,0.0813,0.06338],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49543,0.01324,0.04074],"object_pos_start":[0.49747,0.06051,0.03287],"object_to_goal_dist_end":0.09336,"object_to_goal_dist_start":0.14071,"object_z_max":0.04077,"peak_contact_force":0.48945,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2619.0,"raw_peak_contact_force":126.97611,"subtask_id":"push_channel","tcp_end":[0.4879,-0.0402,0.04552],"tcp_start":[0.50339,0.08599,0.04954],"tcp_to_object_dist_end":0.05418,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.49837,-0.01155,0.02414],"object_pos_start":[0.49543,0.01324,0.04074],"object_to_goal_dist_end":0.07028,"object_to_goal_dist_start":0.09336,"object_z_max":0.04074,"peak_contact_force":0.54234,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":972.0,"raw_peak_contact_force":289.47406,"subtask_id":"push_channel","tcp_end":[0.48587,-0.04005,0.27393],"tcp_start":[0.4879,-0.0402,0.04552],"tcp_to_object_dist_end":0.25173,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.14099,"approach_1.approach_speed":0.37407,"descend_final.descend_final_speed":0.03457,"descend_safe.descend_speed":0.0739,"push_1.push_distance":0.20187,"push_1.push_lateral_x":-0.00242,"push_1.push_max_time":11.84824,"push_1.push_speed":0.10745,"retract_1.retract_height":0.16848,"retract_1.retract_speed":0.43292},"optimized_scores":{"best_composite_score":-0.51943,"best_fitness_score":0.10057,"best_task_score":0.16324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.50594,0.07078,0.00843],"force_p95":170.64234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.32802,"mean_force":122.84645,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49617,0.07891,0.05381]},{"body_a":"attachment","body_b":"peg","contact_count":352.0,"contact_point_centroid":[0.50608,0.07276,0.05443],"force_p95":170.20051,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":170.8343,"mean_force":127.22051,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49644,0.079,0.05348]},{"body_a":"peg","body_b":"channel_base_body","contact_count":992.0,"contact_point_centroid":[0.50132,0.01548,0.00876],"force_p95":113.16879,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.36626,"mean_force":68.90887,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50313,0.00142,0.05081]},{"body_a":"attachment","body_b":"peg","contact_count":701.0,"contact_point_centroid":[0.50974,0.02838,0.05455],"force_p95":116.32174,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.89353,"mean_force":95.69913,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50561,0.0279,0.05308]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49915,-0.10017,0.065],"force_p95":100.89216,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.1108,"mean_force":80.08686,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49626,-0.08812,0.04504]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.4993,-0.10011,0.065],"force_p95":62.59544,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.98175,"mean_force":53.53056,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49638,-0.08799,0.0448]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":549.0,"contact_point_centroid":[0.47478,0.02456,0.01385],"force_p95":18.40948,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.76633,"mean_force":11.75133,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50478,0.00298,0.05233]},{"body_a":"peg","body_b":"channel_base_body","contact_count":480.0,"contact_point_centroid":[0.49448,0.05889,0.00935],"force_p95":0.58288,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5767,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48178,0.13059,0.24206]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49845,0.19611,0.2962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.4937,-0.01879,0.00807],"force_p95":0.65659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65716,"mean_force":0.60588,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49358,-0.08773,0.11813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.49408,0.0592,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54607,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.47598,0.06393,0.14701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":376.0,"contact_point_centroid":[0.49418,0.05895,0.00939],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55169,"mean_force":0.54577,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.4876,0.06863,0.07922]}],"total_contact_groups":12},"final_pose_error":0.01608,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49369,-0.0189,0.02415],"final_tcp_position":[0.49391,-0.08787,0.1974],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":171.32802,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":509.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.05906,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54295,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":515.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.46664,0.06823,0.19327],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":900.0,"object_pos_end":[0.49396,0.05898,0.0339],"object_pos_start":[0.4942,0.05906,0.03386],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13931,"object_z_max":0.0339,"peak_contact_force":0.54613,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":343.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_pre_contact","tcp_end":[0.48766,0.05977,0.10139],"tcp_start":[0.46664,0.06823,0.19327],"tcp_to_object_dist_end":0.06778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":376.0,"n_steps_budget":600.0,"object_pos_end":[0.49393,0.05907,0.03396],"object_pos_start":[0.49396,0.05898,0.0339],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13924,"object_z_max":0.03396,"peak_contact_force":0.54406,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":376.0,"raw_peak_contact_force":0.55169,"subtask_id":"reach_pre_contact","tcp_end":[0.48969,0.0767,0.06267],"tcp_start":[0.48766,0.05977,0.10139],"tcp_to_object_dist_end":0.03395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":366.0,"n_steps_budget":600.0,"object_pos_end":[0.49653,0.05652,0.03255],"object_pos_start":[0.49393,0.05907,0.03396],"object_to_goal_dist_end":0.13677,"object_to_goal_dist_start":0.13933,"object_z_max":0.03404,"peak_contact_force":170.85237,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":718.0,"raw_peak_contact_force":171.32802,"subtask_id":"reach_pre_contact","tcp_end":[0.50217,0.08097,0.04952],"tcp_start":[0.48969,0.0767,0.06267],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49371,-0.01886,0.02415],"object_pos_start":[0.49653,0.05652,0.03255],"object_to_goal_dist_end":0.06347,"object_to_goal_dist_start":0.13677,"object_z_max":0.04054,"peak_contact_force":63.98175,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2245.0,"raw_peak_contact_force":128.36626,"subtask_id":"push_channel","tcp_end":[0.49639,-0.08826,0.0448],"tcp_start":[0.50217,0.08097,0.04952],"tcp_to_object_dist_end":0.07245,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49369,-0.0189,0.02415],"object_pos_start":[0.49371,-0.01886,0.02415],"object_to_goal_dist_end":0.06343,"object_to_goal_dist_start":0.06347,"object_z_max":0.02416,"peak_contact_force":0.55613,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":549.0,"raw_peak_contact_force":102.1108,"subtask_id":"push_channel","tcp_end":[0.49391,-0.08787,0.1974],"tcp_start":[0.49639,-0.08826,0.0448],"tcp_to_object_dist_end":0.18647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```