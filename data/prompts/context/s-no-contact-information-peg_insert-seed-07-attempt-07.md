## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3914 | 0.86 | ❌ rejected |
| 6 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2941 | 0.86 | ✅ accepted |
| 5 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2915 | 0.86 | ✅ accepted |
| 4 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3830 | 0.84 | ❌ rejected |
| 3 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4754 | 0.85 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5100076373283727, 0.031777104077566044, 0.08]
- Frozen socket pose: [0.5100076373283727, 0.031777104077566044, 0.025] (static fixture for this episode)
- Goal object position: (0.5100076373283727, 0.031777104077566044, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.51, 0.0318, 0.08]
  frozen_socket_position: [0.51, 0.0318, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5100076373283727, 0.031777104077566044, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5100076373283727, 0.031777104077566044, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.863, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283727, 0.031777104077566044, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5100076373283727, 0.031777104077566044, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.391) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insert_into_hole
  anchor: fixture
  metric: goal_progress
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.155
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_entry
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_entry
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_entry
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    retry_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: insert_into_hole

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.155], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.391
- **task_score** (E): 0.860
- **fitness_score**: 0.751  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1065 |
| descend_1 | 1.00 | 0.1092 |
| align_1 | 1.00 | 0.0075 |
| insert_1 | 1.00 | 0.0348 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.014, 0.198) | (0.504, -0.000, 0.340)→(0.505, 0.014, 0.238) | 0.260→0.161 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.014, 0.198)→(0.505, 0.017, 0.089) | (0.505, 0.014, 0.238)→(0.506, 0.017, 0.129) | 0.161→0.060 |
| align_1 | align | 1.00 / step_budget | (0.505, 0.017, 0.089)→(0.504, 0.017, 0.081) | (0.506, 0.017, 0.129)→(0.505, 0.018, 0.121) | 0.060→0.054 |
| insert_1 | insert | 1.00 / step_budget | (0.504, 0.017, 0.081)→(0.503, 0.012, 0.050) | (0.505, 0.018, 0.121)→(0.504, 0.012, 0.090) | 0.054→0.023 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.881
- alignment_error: None
- terminal_score: 0.881
- phase_score: 0.691
- phase_breakdown.insert_into_hole_score: 0.600
- phase_breakdown.reach_entry_score: 0.905

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.767
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.881
- **Median Q (composite search score)**: 0.402
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.423


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0c4288e4b4f4eb50f7d141bdaea44f8ed4eecfe7429f8148c247811f0f5250bc`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2ae90e10c3e712e9da92b27bc0ded08b6d103e49e03139a26a0fa45d3ac81c97`; realized-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00719,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.06845,"approach_1.speed":0.0984,"descend_1.speed":0.03334,"insert_1.insertion_depth":0.03762,"insert_1.lateral_offset_x":-0.00384,"insert_1.lateral_offset_y":-0.01919},"optimized_scores":{"best_composite_score":0.40199,"best_fitness_score":0.76199,"best_task_score":0.86902},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51741,0.0189,0.04978],"force_p95":193.36411,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.99032,"mean_force":159.8396,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50245,0.01815,0.05021]}],"total_contact_groups":1},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50251,0.01799,0.04987],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"phases":[{"n_steps":205.0,"n_steps_budget":810.0,"object_pos_end":[0.50633,0.02557,0.23802],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.5058,0.02553,0.19803],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.03088,0.12884],"object_pos_start":[0.50633,0.02557,0.23802],"object_to_goal_dist_end":0.05821,"object_to_goal_dist_start":0.1602,"object_z_max":0.23802,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.506,0.03081,0.08886],"tcp_start":[0.5058,0.02553,0.19803],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":600.0,"object_pos_end":[0.50663,0.03117,0.12157],"object_pos_start":[0.50699,0.03088,0.12884],"object_to_goal_dist_end":0.05238,"object_to_goal_dist_start":0.05821,"object_z_max":0.12884,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_entry","tcp_end":[0.50533,0.03108,0.0816],"tcp_start":[0.506,0.03081,0.08886],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.50421,0.01809,0.08984],"object_pos_start":[0.50663,0.03117,0.12157],"object_to_goal_dist_end":0.02102,"object_to_goal_dist_start":0.05238,"object_z_max":0.12157,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_into_hole","tcp_end":[0.50251,0.01799,0.04987],"tcp_start":[0.50533,0.03108,0.0816],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`; realized-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05983,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.06118,"approach_1.speed":0.0601,"descend_1.speed":0.07559,"insert_1.insertion_depth":0.03539,"insert_1.lateral_offset_x":0.01111,"insert_1.lateral_offset_y":-0.01999},"optimized_scores":{"best_composite_score":0.36504,"best_fitness_score":0.72504,"best_task_score":0.83057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.5049,0.02478,0.04978],"force_p95":557.36867,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":575.2547,"mean_force":371.53124,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48994,0.02378,0.05016]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.48988,0.00889,0.05028],"force_p95":369.7952,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":385.41379,"mean_force":210.02951,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4899,0.02381,0.05023]}],"total_contact_groups":2},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49027,0.02369,0.04986],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"phases":[{"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.48709,0.03144,0.23819],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1618,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.48661,0.0314,0.1982],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":359.0,"n_steps_budget":990.0,"object_pos_end":[0.48381,0.03791,0.12919],"object_pos_start":[0.48709,0.03144,0.23819],"object_to_goal_dist_end":0.06418,"object_to_goal_dist_start":0.1618,"object_z_max":0.23819,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.48291,0.03784,0.0892],"tcp_start":[0.48661,0.0314,0.1982],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.48317,0.03823,0.12258],"object_pos_start":[0.48381,0.03791,0.12919],"object_to_goal_dist_end":0.05965,"object_to_goal_dist_start":0.06418,"object_z_max":0.12919,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_entry","tcp_end":[0.48199,0.03813,0.0826],"tcp_start":[0.48291,0.03784,0.0892],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.49185,0.02379,0.08983],"object_pos_start":[0.48317,0.03823,0.12258],"object_to_goal_dist_end":0.027,"object_to_goal_dist_start":0.05965,"object_z_max":0.12258,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_into_hole","tcp_end":[0.49027,0.02369,0.04986],"tcp_start":[0.48199,0.03813,0.0826],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`; realized-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69277,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.04635,"approach_1.speed":0.05847,"descend_1.speed":0.02948,"insert_1.insertion_depth":0.04086,"insert_1.lateral_offset_x":-0.01995,"insert_1.lateral_offset_y":0.0154},"optimized_scores":{"best_composite_score":0.40718,"best_fitness_score":0.76718,"best_task_score":0.88089},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":50.0,"contact_point_centroid":[0.53015,-0.00592,0.04982],"force_p95":345.55087,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":346.71971,"mean_force":296.34098,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51517,-0.00595,0.05005]},{"body_a":"attachment","body_b":"peg_socket","contact_count":42.0,"contact_point_centroid":[0.49958,-0.00779,0.05371],"force_p95":107.49485,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.05519,"mean_force":66.54594,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51453,-0.00778,0.05315]}],"total_contact_groups":2},"final_pose_error":0.01331,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51572,-0.0059,0.05022],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"phases":[{"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.52213,-0.01375,0.23782],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15996,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.52161,-0.01374,0.19782],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.52604,-0.01663,0.12876],"object_pos_start":[0.52213,-0.01375,0.23782],"object_to_goal_dist_end":0.05773,"object_to_goal_dist_start":0.15996,"object_z_max":0.23782,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.52505,-0.01661,0.08878],"tcp_start":[0.52161,-0.01374,0.19782],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":61.0,"n_steps_budget":600.0,"object_pos_end":[0.52599,-0.01685,0.12019],"object_pos_start":[0.52604,-0.01663,0.12876],"object_to_goal_dist_end":0.05074,"object_to_goal_dist_start":0.05773,"object_z_max":0.12876,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_entry","tcp_end":[0.52464,-0.01682,0.08021],"tcp_start":[0.52505,-0.01661,0.08878],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":177.0,"n_steps_budget":600.0,"object_pos_end":[0.51655,-0.00587,0.09021],"object_pos_start":[0.52599,-0.01685,0.12019],"object_to_goal_dist_end":0.02031,"object_to_goal_dist_start":0.05074,"object_z_max":0.12019,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_into_hole","tcp_end":[0.51572,-0.0059,0.05022],"tcp_start":[0.52464,-0.01682,0.08021],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```