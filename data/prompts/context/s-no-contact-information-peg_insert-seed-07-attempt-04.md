## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3830 | 0.84 | ❌ rejected |
| 3 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4754 | 0.85 | ✅ accepted |
| 2 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.2960 | 0.00 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.2960 | 0.00 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.2960 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.846, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.383) — your mutation base

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
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
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
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
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
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0

## Design Metrics

- **Composite score**: 0.383
- **task_score** (E): 0.844
- **fitness_score**: 0.643  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1064 |
| descend_1 | 1.00 | 0.1092 |
| align_1 | 1.00 | 0.0075 |
| insert_1 | 0.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.014, 0.198) | (0.504, -0.000, 0.340)→(0.505, 0.014, 0.238) | 0.260→0.161 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.014, 0.198)→(0.505, 0.017, 0.089) | (0.505, 0.014, 0.238)→(0.506, 0.017, 0.129) | 0.161→0.060 |
| align_1 | align | 1.00 / step_budget | (0.505, 0.017, 0.089)→(0.504, 0.017, 0.082) | (0.506, 0.017, 0.129)→(0.505, 0.018, 0.122) | 0.060→0.054 |
| insert_1 | insert | 0.00 / guard_failure | (0.503, 0.018, 0.050)→(0.503, 0.018, 0.050) | (0.505, 0.018, 0.122)→(0.504, 0.018, 0.090) | 0.054→0.036 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.867
- alignment_error: None
- terminal_score: 0.867
- phase_score: 0.537
- phase_breakdown.insert_into_hole_score: 0.380
- phase_breakdown.reach_entry_score: 0.905

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.669
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.867
- **Median Q (composite search score)**: 0.399
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: insert_1.insertion_depth
- **Final σ (mean)**: 0.248


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09836,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.03464,"approach_1.speed":0.07459,"descend_1.speed":0.04494,"insert_1.insertion_depth":0.06},"optimized_scores":{"best_composite_score":0.39889,"best_fitness_score":0.65889,"best_task_score":0.8574},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.5185,0.03223,0.04989],"force_p95":85.29012,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.25414,"mean_force":76.61392,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50356,0.03111,0.05041]}],"total_contact_groups":1},"final_pose_error":0.03097,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50358,0.03111,0.05029],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"phases":[{"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.50642,0.02557,0.2381],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16028,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.50592,0.02553,0.1981],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,0.03088,0.12884],"object_pos_start":[0.50642,0.02557,0.2381],"object_to_goal_dist_end":0.0582,"object_to_goal_dist_start":0.16028,"object_z_max":0.2381,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.50601,0.03081,0.08885],"tcp_start":[0.50592,0.02553,0.1981],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":600.0,"object_pos_end":[0.50661,0.03117,0.12157],"object_pos_start":[0.50697,0.03088,0.12884],"object_to_goal_dist_end":0.05238,"object_to_goal_dist_start":0.0582,"object_z_max":0.12884,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_entry","tcp_end":[0.50534,0.03108,0.08159],"tcp_start":[0.50601,0.03081,0.08885],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":178.0,"n_steps_budget":600.0,"object_pos_end":[0.50528,0.03122,0.09031],"object_pos_start":[0.50661,0.03117,0.12157],"object_to_goal_dist_end":0.0333,"object_to_goal_dist_start":0.05238,"object_z_max":0.12157,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_into_hole","tcp_end":[0.50358,0.03111,0.05029],"tcp_start":[0.50357,0.03111,0.05034],"tcp_to_object_dist_end":0.04005,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03623,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.02337,"approach_1.speed":0.0415,"descend_1.speed":0.07386,"insert_1.insertion_depth":0.03222},"optimized_scores":{"best_composite_score":0.34079,"best_fitness_score":0.60079,"best_task_score":0.8083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.49655,0.03962,0.04996],"force_p95":66.8357,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.16827,"mean_force":63.84255,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48161,0.03849,0.05052]}],"total_contact_groups":1},"final_pose_error":0.00526,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48162,0.03849,0.0504],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"phases":[{"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.48705,0.03139,0.23832],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16192,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.48656,0.03135,0.19832],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.48383,0.0379,0.12933],"object_pos_start":[0.48705,0.03139,0.23832],"object_to_goal_dist_end":0.06428,"object_to_goal_dist_start":0.16192,"object_z_max":0.23832,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.48292,0.03783,0.08934],"tcp_start":[0.48656,0.03135,0.19832],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.48318,0.03823,0.12256],"object_pos_start":[0.48383,0.0379,0.12933],"object_to_goal_dist_end":0.05963,"object_to_goal_dist_start":0.06428,"object_z_max":0.12933,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_entry","tcp_end":[0.48198,0.03813,0.08258],"tcp_start":[0.48292,0.03783,0.08934],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.48324,0.03862,0.09043],"object_pos_start":[0.48318,0.03823,0.12256],"object_to_goal_dist_end":0.04337,"object_to_goal_dist_start":0.05963,"object_z_max":0.12256,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_into_hole","tcp_end":[0.48162,0.03849,0.0504],"tcp_start":[0.48161,0.03849,0.05046],"tcp_to_object_dist_end":0.04007,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40426,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.03865,"approach_1.speed":0.08435,"descend_1.speed":0.08415,"insert_1.insertion_depth":0.05993},"optimized_scores":{"best_composite_score":0.40946,"best_fitness_score":0.66946,"best_task_score":0.86742},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.53771,-0.01717,0.04995],"force_p95":227.56356,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.42379,"mean_force":147.82149,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52273,-0.01687,0.05057]}],"total_contact_groups":1},"final_pose_error":0.03114,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52274,-0.01687,0.05044],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"phases":[{"n_steps":210.0,"n_steps_budget":930.0,"object_pos_end":[0.52223,-0.01374,0.23791],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16005,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.52171,-0.01373,0.19791],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":347.0,"n_steps_budget":900.0,"object_pos_end":[0.52612,-0.01663,0.12889],"object_pos_start":[0.52223,-0.01374,0.23791],"object_to_goal_dist_end":0.05787,"object_to_goal_dist_start":0.16005,"object_z_max":0.23791,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.52515,-0.01661,0.0889],"tcp_start":[0.52171,-0.01373,0.19791],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":59.0,"n_steps_budget":600.0,"object_pos_end":[0.52599,-0.01684,0.12043],"object_pos_start":[0.52612,-0.01663,0.12889],"object_to_goal_dist_end":0.05093,"object_to_goal_dist_start":0.05787,"object_z_max":0.12889,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_entry","tcp_end":[0.52466,-0.01682,0.08045],"tcp_start":[0.52515,-0.01661,0.0889],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.52453,-0.01691,0.09047],"object_pos_start":[0.52599,-0.01684,0.12043],"object_to_goal_dist_end":0.03158,"object_to_goal_dist_start":0.05093,"object_z_max":0.12043,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_into_hole","tcp_end":[0.52274,-0.01687,0.05044],"tcp_start":[0.52274,-0.01687,0.05051],"tcp_to_object_dist_end":0.04007,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```