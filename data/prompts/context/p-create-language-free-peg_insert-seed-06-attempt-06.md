## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3744 | 0.91 | ❌ rejected |
| 5 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3069 | 0.91 | ❌ rejected |
| 4 | approach → align → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0017 | 0.87 | ❌ rejected |
| 3 | approach → align → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2459 | 0.87 | ❌ rejected |
| 2 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0929 | 0.87 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5030531481177555, -0.012538330414932925, 0.08]
- Frozen socket pose: [0.5030531481177555, -0.012538330414932925, 0.025] (static fixture for this episode)
- Goal object position: (0.5030531481177555, -0.012538330414932925, 0.025)
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
  frozen_task_target: [0.5031, -0.0125, 0.08]
  frozen_socket_position: [0.5031, -0.0125, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5030531481177555, -0.012538330414932925, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5030531481177555, -0.012538330414932925, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.912, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5030531481177555, -0.012538330414932925, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5030531481177555, -0.012538330414932925, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.374) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_standoff
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: insertion
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
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
  subtask_id: approach_standoff
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 10.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.002
    - 0.0
  subtask_id: insertion
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force: status=consumed; consumers=guards.force_guard.threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=10.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.002, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.374
- **task_score** (E): 0.909
- **fitness_score**: 0.784  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1642 |
| contact_1 | 0.00 | 0.00 | 0.0264 |
| insert_1 | 0.00 | 1.00 | 0.0640 |
| retract_1 | 1.00 | 0.00 | 0.1071 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.018, 0.139) | (0.504, -0.000, 0.340)→(0.497, 0.018, 0.179) | 0.260→0.103 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 0.00 / step_budget | (0.497, 0.018, 0.139)→(0.496, 0.019, 0.113) | (0.497, 0.018, 0.179)→(0.496, 0.019, 0.153) | 0.103→0.079 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.496, 0.019, 0.113)→(0.496, 0.012, 0.050) | (0.496, 0.019, 0.153)→(0.496, 0.012, 0.090) | 0.079→0.020 | 1.00 / 1.667 | 64.205 | 69.320 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.012, 0.050)→(0.496, 0.018, 0.157) | (0.496, 0.012, 0.090)→(0.497, 0.019, 0.196) | 0.020→0.120 | 0.00 / 0.000 | 0.000 | 89.675 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.962
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.962
- phase_score: 0.818
- phase_breakdown.insertion_score: 0.849
- phase_breakdown.approach_standoff_score: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.876
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.962
- **Median Q (composite search score)**: 0.365
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.300


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2bcd5d362bce9ed2c176357e9c3237720ebba2a98dd8bfe48970c9fba5840ac0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ac7031668c6a08077e83f2359534923b723fe0e5a20a177feb2fc3bf67104f66`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78241,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01105,"contact_1.contact_force":8.22453,"contact_1.speed":0.02289,"insert_1.insertion_depth":0.14687,"insert_1.insertion_force":35.13728,"insert_1.speed":0.06972,"retract_1.speed":0.04917},"optimized_scores":{"best_composite_score":0.46557,"best_fitness_score":0.87557,"best_task_score":0.96223},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51183,-0.00434,0.04994],"force_p95":139.30746,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.30746,"mean_force":139.30746,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49683,-0.00438,0.05005]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.5118,-0.00429,0.04987],"force_p95":57.50224,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.55091,"mean_force":35.44161,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49681,-0.00434,0.04992]}],"total_contact_groups":2},"final_pose_error":0.02873,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.4987,-0.01102,0.15164],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":139.30746,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,-0.01149,0.17911],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09978,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_standoff","tcp_end":[0.49963,-0.01148,0.13912],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":168.0,"n_steps_budget":810.0,"object_pos_end":[0.49929,-0.01225,0.1526],"object_pos_start":[0.50009,-0.01149,0.17911],"object_to_goal_dist_end":0.07363,"object_to_goal_dist_start":0.09978,"object_z_max":0.17911,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49884,-0.01225,0.1126],"tcp_start":[0.49963,-0.01148,0.13912],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.49731,-0.00436,0.0899],"object_pos_start":[0.49929,-0.01225,0.1526],"object_to_goal_dist_end":0.01114,"object_to_goal_dist_start":0.07363,"object_z_max":0.1526,"peak_contact_force":139.30746,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":139.30746,"subtask_id":"insertion","tcp_end":[0.49686,-0.00436,0.0499],"tcp_start":[0.49884,-0.01225,0.1126],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49959,-0.01102,0.19163],"object_pos_start":[0.49731,-0.00436,0.0899],"object_to_goal_dist_end":0.11218,"object_to_goal_dist_start":0.01114,"object_z_max":0.19152,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8.0,"raw_peak_contact_force":62.55091,"tcp_end":[0.4987,-0.01102,0.15164],"tcp_start":[0.49686,-0.00436,0.0499],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4cf364ad7cdeb78864f76dd2c5686ed9e91b61eb5e5b2735897d619cb8f6dad4`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31884,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08534,"contact_1.contact_force":11.21285,"contact_1.speed":0.02584,"insert_1.insertion_depth":0.05136,"insert_1.insertion_force":25.95822,"insert_1.speed":0.07511,"retract_1.speed":0.0427},"optimized_scores":{"best_composite_score":0.36523,"best_fitness_score":0.77523,"best_task_score":0.90742},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.50207,0.00176,0.05001],"force_p95":131.06148,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.12527,"mean_force":99.81796,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.502,0.01674,0.04995]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.51692,0.01725,0.04989],"force_p95":110.04845,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.38512,"mean_force":45.25187,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50193,0.01683,0.04997]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51699,0.01724,0.04999],"force_p95":51.80131,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.80131,"mean_force":51.80131,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.502,0.01675,0.05015]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50207,0.00177,0.05016],"force_p95":28.56539,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":28.56539,"mean_force":28.56539,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.502,0.01675,0.05015]}],"total_contact_groups":4},"final_pose_error":0.03283,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50506,0.02839,0.14772],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":134.12527,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50652,0.0291,0.17859],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10301,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_standoff","tcp_end":[0.50607,0.02907,0.1386],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":166.0,"n_steps_budget":720.0,"object_pos_end":[0.50612,0.03092,0.15229],"object_pos_start":[0.50652,0.0291,0.17859],"object_to_goal_dist_end":0.07887,"object_to_goal_dist_start":0.10301,"object_z_max":0.17859,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50566,0.0309,0.1123],"tcp_start":[0.50607,0.02907,0.1386],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":343.0,"n_steps_budget":690.0,"object_pos_end":[0.50247,0.01674,0.09002],"object_pos_start":[0.50612,0.03092,0.15229],"object_to_goal_dist_end":0.01967,"object_to_goal_dist_start":0.07887,"object_z_max":0.15229,"peak_contact_force":51.80131,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":51.80131,"subtask_id":"insertion","tcp_end":[0.50201,0.01672,0.05003],"tcp_start":[0.50566,0.0309,0.1123],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.02843,0.18771],"object_pos_start":[0.50247,0.01674,0.09002],"object_to_goal_dist_end":0.11156,"object_to_goal_dist_start":0.01967,"object_z_max":0.18762,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":11.0,"raw_peak_contact_force":134.12527,"tcp_end":[0.50506,0.02839,0.14772],"tcp_start":[0.50201,0.01672,0.05003],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `989b6885a6cc20cf657766879d873fa27d37f906fbac12db49d02020abcc24a4`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94634,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01357,"contact_1.contact_force":18.82517,"contact_1.speed":0.02681,"insert_1.insertion_depth":0.03559,"insert_1.insertion_force":8.05356,"insert_1.speed":0.04818,"retract_1.speed":0.08336},"optimized_scores":{"best_composite_score":0.29255,"best_fitness_score":0.70255,"best_task_score":0.85691},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.48869,0.00897,0.0501],"force_p95":71.36363,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.35001,"mean_force":62.48621,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48869,0.02396,0.0501]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50367,0.02445,0.04997],"force_p95":47.71403,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.48072,"mean_force":39.49597,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48868,0.024,0.05011]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.48867,0.00898,0.05023],"force_p95":16.8523,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16.8523,"mean_force":16.8523,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48867,0.02397,0.05022]}],"total_contact_groups":3},"final_pose_error":0.01032,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48324,0.03812,0.17014],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":72.35001,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.4846,0.03568,0.17909],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10644,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_standoff","tcp_end":[0.48416,0.03564,0.1391],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":163.0,"n_steps_budget":690.0,"object_pos_end":[0.48283,0.03793,0.15295],"object_pos_start":[0.4846,0.03568,0.17909],"object_to_goal_dist_end":0.084,"object_to_goal_dist_start":0.10644,"object_z_max":0.17909,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48239,0.0379,0.11295],"tcp_start":[0.48416,0.03564,0.1391],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":478.0,"n_steps_budget":870.0,"object_pos_end":[0.48913,0.02397,0.09012],"object_pos_start":[0.48283,0.03793,0.15295],"object_to_goal_dist_end":0.0282,"object_to_goal_dist_start":0.084,"object_z_max":0.15295,"peak_contact_force":1.50605,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":16.8523,"subtask_id":"insertion","tcp_end":[0.48869,0.02395,0.05013],"tcp_start":[0.48239,0.0379,0.11295],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":891.0,"n_steps_budget":990.0,"object_pos_end":[0.48412,0.03817,0.21013],"object_pos_start":[0.48913,0.02397,0.09012],"object_to_goal_dist_end":0.13654,"object_to_goal_dist_start":0.0282,"object_z_max":0.21003,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":6.0,"raw_peak_contact_force":72.35001,"tcp_end":[0.48324,0.03812,0.17014],"tcp_start":[0.48869,0.02395,0.05013],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```