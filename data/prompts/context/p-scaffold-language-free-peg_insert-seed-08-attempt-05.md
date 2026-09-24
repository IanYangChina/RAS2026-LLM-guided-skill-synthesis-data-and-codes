## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0187 | 0.85 | ✅ accepted |
| 4 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0366 | 0.84 | ✅ accepted |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0644 | 0.84 | ✅ accepted |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.1606 | 0.69 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1456 | 0.71 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.48615778212844485, 0.03898214746703404, 0.08]
- Frozen socket pose: [0.48615778212844485, 0.03898214746703404, 0.025] (static fixture for this episode)
- Goal object position: (0.48615778212844485, 0.03898214746703404, 0.025)
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
  frozen_task_target: [0.4862, 0.039, 0.08]
  frozen_socket_position: [0.4862, 0.039, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.48615778212844485, 0.03898214746703404, 0.08]}
  frozen_fixtures: {'peg_socket': [0.48615778212844485, 0.03898214746703404, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.845, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.48615778212844485, 0.03898214746703404, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.48615778212844485, 0.03898214746703404, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.019) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_above
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: reach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.3
- id: insertion_depth
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: align_1
  type: align
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
      tolerance: 0.1
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: reach_above
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
    - 0.01
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
      - 0.02
      - 0.1
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
  subtask_id: reach_entry
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.005
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
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: reach_entry
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.03
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    max_time:
      type: scalar
      range:
      - 1.0
      - 4.0
      default: 2.5
      binds_to:
      - path: duration.max_time
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_cap
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: insertion_depth
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_cap, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.019
- **task_score** (E): 0.845
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1640 |
| approach_1 | 1.00 | 0.00 | 0.0420 |
| contact_1 | 1.00 | 0.00 | 0.0049 |
| insert_1 | 0.00 | 1.00 | 0.0429 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.002, 0.139) | (0.504, -0.000, 0.340)→(0.512, 0.002, 0.179) | 0.260→0.102 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.512, 0.002, 0.139)→(0.513, 0.000, 0.098) | (0.512, 0.002, 0.179)→(0.513, 0.000, 0.138) | 0.102→0.067 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 1.00 / step_budget | (0.513, 0.000, 0.098)→(0.512, -0.000, 0.093) | (0.513, 0.000, 0.138)→(0.513, -0.000, 0.133) | 0.067→0.064 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.512, -0.000, 0.093)→(0.511, -0.000, 0.050) | (0.513, -0.000, 0.133)→(0.512, -0.000, 0.090) | 0.064→0.037 | 1.00 / 1.000 | 75.590 | 75.590 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.883
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.883
- phase_score: 0.427
- phase_breakdown.reach_entry_score: 0.426
- phase_breakdown.insertion_depth_score: 0.491
- phase_breakdown.reach_above_score: 0.268

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.609
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.883
- **Median Q (composite search score)**: -0.027
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.441


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `111371231b67e0c9737e2a991f4190656c428bca2212422046741d75dd4bee83`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33ad86acc0270e6e89309305f52a6240db2b433d70da525d7c59722b30949f46`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92647,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00965,"align_1.lateral_offset_y":-0.00909,"align_1.speed":0.08058,"approach_1.speed":0.04029,"contact_1.speed":0.04361,"insert_1.insertion_depth":0.05762,"insert_1.max_time":2.2238,"insert_1.speed":0.02183,"retract_1.retract_height":0.08232,"retract_1.speed":0.08374},"optimized_scores":{"best_composite_score":-0.04876,"best_fitness_score":0.54124,"best_task_score":0.81425},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.49635,0.03841,0.04998],"force_p95":89.62832,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.62832,"mean_force":89.62832,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48139,0.03743,0.05028]}],"total_contact_groups":1},"final_pose_error":0.02822,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48141,0.03744,0.05016],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":89.62832,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.4935,0.0273,0.17922],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10312,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above","tcp_end":[0.49306,0.02728,0.13923],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":144.0,"n_steps_budget":810.0,"object_pos_end":[0.48532,0.03556,0.13926],"object_pos_start":[0.4935,0.0273,0.17922],"object_to_goal_dist_end":0.07065,"object_to_goal_dist_start":0.10312,"object_z_max":0.17922,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.48488,0.03552,0.09927],"tcp_start":[0.49306,0.02728,0.13923],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.48428,0.03627,0.13431],"object_pos_start":[0.48532,0.03556,0.13926],"object_to_goal_dist_end":0.06717,"object_to_goal_dist_start":0.07065,"object_z_max":0.13926,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.48384,0.03623,0.09431],"tcp_start":[0.48488,0.03552,0.09927],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.48228,0.0375,0.09015],"object_pos_start":[0.48428,0.03627,0.13431],"object_to_goal_dist_end":0.0427,"object_to_goal_dist_start":0.06717,"object_z_max":0.13431,"peak_contact_force":89.62832,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":89.62832,"subtask_id":"insertion_depth","tcp_end":[0.48141,0.03744,0.05016],"tcp_start":[0.48384,0.03623,0.09431],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7e8ba2d913c6be5a5528190a0c7ff1e14947b230e7e2c93846f050bf72228229`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.51299,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.009,"align_1.lateral_offset_y":0.00945,"align_1.speed":0.17515,"approach_1.speed":0.0269,"contact_1.speed":0.03087,"insert_1.insertion_depth":0.05983,"insert_1.max_time":2.24646,"insert_1.speed":0.01232,"retract_1.retract_height":0.12679,"retract_1.speed":0.02951},"optimized_scores":{"best_composite_score":0.01915,"best_fitness_score":0.60915,"best_task_score":0.88269},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53734,-0.01638,0.04994],"force_p95":69.4815,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.4815,"mean_force":69.4815,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52235,-0.01609,0.05024]}],"total_contact_groups":1},"final_pose_error":0.03084,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52237,-0.01609,0.05013],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":69.4815,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":464.0,"n_steps_budget":630.0,"object_pos_end":[0.51625,-0.007,0.1786],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10017,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above","tcp_end":[0.51578,-0.007,0.1386],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.52333,-0.01462,0.13673],"object_pos_start":[0.51625,-0.007,0.1786],"object_to_goal_dist_end":0.06305,"object_to_goal_dist_start":0.10017,"object_z_max":0.1786,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.52286,-0.01461,0.09673],"tcp_start":[0.51578,-0.007,0.1386],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.52346,-0.01518,0.13208],"object_pos_start":[0.52333,-0.01462,0.13673],"object_to_goal_dist_end":0.0591,"object_to_goal_dist_start":0.06305,"object_z_max":0.13673,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.52298,-0.01517,0.09208],"tcp_start":[0.52286,-0.01461,0.09673],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.52332,-0.01611,0.09012],"object_pos_start":[0.52346,-0.01518,0.13208],"object_to_goal_dist_end":0.0301,"object_to_goal_dist_start":0.0591,"object_z_max":0.13208,"peak_contact_force":69.4815,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":69.4815,"subtask_id":"insertion_depth","tcp_end":[0.52237,-0.01609,0.05013],"tcp_start":[0.52298,-0.01517,0.09208],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `6bfe353c76201464a4c9772ff30fffbe6279f45f6a3eb14a1a3a1447c56a946a`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62832,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0038,"align_1.lateral_offset_y":0.0086,"align_1.speed":0.13791,"approach_1.speed":0.06137,"contact_1.speed":0.04527,"insert_1.insertion_depth":0.05985,"insert_1.max_time":2.74166,"insert_1.speed":0.02009,"retract_1.retract_height":0.17638,"retract_1.speed":0.0912},"optimized_scores":{"best_composite_score":-0.02654,"best_fitness_score":0.56346,"best_task_score":0.83918},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54446,-0.02273,0.04994],"force_p95":67.66055,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.66055,"mean_force":67.66055,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52948,-0.02231,0.05024]}],"total_contact_groups":1},"final_pose_error":0.0308,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.5295,-0.02231,0.05013],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":67.66055,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":518.0,"n_steps_budget":810.0,"object_pos_end":[0.52742,-0.01363,0.17786],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10253,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above","tcp_end":[0.52695,-0.01362,0.13786],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":148.0,"n_steps_budget":600.0,"object_pos_end":[0.53105,-0.02078,0.13752],"object_pos_start":[0.52742,-0.01363,0.17786],"object_to_goal_dist_end":0.06858,"object_to_goal_dist_start":0.10253,"object_z_max":0.17786,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.53056,-0.02076,0.09752],"tcp_start":[0.52695,-0.01362,0.13786],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.53095,-0.02136,0.13263],"object_pos_start":[0.53105,-0.02078,0.13752],"object_to_goal_dist_end":0.06468,"object_to_goal_dist_start":0.06858,"object_z_max":0.13752,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.53046,-0.02135,0.09263],"tcp_start":[0.53056,-0.02076,0.09752],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.53046,-0.02234,0.09012],"object_pos_start":[0.53095,-0.02136,0.13263],"object_to_goal_dist_end":0.03911,"object_to_goal_dist_start":0.06468,"object_z_max":0.13263,"peak_contact_force":67.66055,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":67.66055,"subtask_id":"insertion_depth","tcp_end":[0.5295,-0.02231,0.05013],"tcp_start":[0.53046,-0.02135,0.09263],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```