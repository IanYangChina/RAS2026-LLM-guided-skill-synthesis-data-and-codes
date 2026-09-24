## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.1095 | 0.84 | ❌ rejected |
| 3 | align → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.1610 | 0.84 | ❌ rejected |
| 2 | align → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.1126 | 0.85 | ✅ accepted |
| 1 | align → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2839 | 0.85 | ✅ accepted |
| 0 | align → approach → contact → insert → retract | linear_cartesian | arc_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 6 | -0.3271 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5009457299760205, 0.03603709570607482, 0.08]
- Frozen socket pose: [0.5009457299760205, 0.03603709570607482, 0.025] (static fixture for this episode)
- Goal object position: (0.5009457299760205, 0.03603709570607482, 0.025)
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
  frozen_task_target: [0.5009, 0.036, 0.08]
  frozen_socket_position: [0.5009, 0.036, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5009457299760205, 0.03603709570607482, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5009457299760205, 0.03603709570607482, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.848, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5009457299760205, 0.03603709570607482, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5009457299760205, 0.03603709570607482, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.110) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_align
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_entry
  weight: 0.4
- id: achieve_insertion
  target_entity: object
  metric: goal_progress
  weight: 0.4
phases:
- id: align_above
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
    - 0.12
    offset_along_axis:
      distance: 0.0
      axis: channel_axis
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
    align_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    pose_tol:
      type: scalar
      range:
      - 0.002
      - 0.02
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_align
- id: descend_to_entry
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_entry
- id: insert_into_hole
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_distance:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 25.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 45.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: achieve_insertion
- id: retract_upward
  type: retract
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_above** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], offset_along_axis={axis=channel_axis, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - align_height: status=consumed; consumers=target.offset.z (replace)
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - lateral_y: status=consumed; consumers=target.offset.y (add)
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_entry** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_limit: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=45.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **retract_upward** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.110
- **task_score** (E): 0.843
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_above | 1.00 | 0.00 | 0.1824 |
| descend_to_entry | 0.00 | 0.00 | 0.0380 |
| insert_into_hole | 0.00 | 0.00 | 0.0207 |
| retract_upward | 1.00 | 0.00 | 0.1018 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_above | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.485, -0.001, 0.121) | (0.504, -0.000, 0.340)→(0.485, -0.001, 0.161) | 0.260→0.087 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_entry | contact | 0.00 / step_budget | (0.485, -0.001, 0.121)→(0.480, -0.001, 0.084) | (0.485, -0.001, 0.161)→(0.481, -0.001, 0.124) | 0.087→0.056 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | insert | 0.00 / step_budget | (0.480, -0.001, 0.084)→(0.479, -0.000, 0.063) | (0.481, -0.001, 0.124)→(0.479, -0.000, 0.103) | 0.056→0.042 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_upward | retract | 1.00 / step_budget | (0.479, -0.000, 0.063)→(0.480, -0.000, 0.165) | (0.479, -0.000, 0.103)→(0.481, -0.000, 0.205) | 0.042→0.130 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.882
- alignment_error: None
- force_efficiency: 1.000
- terminal_score: 0.882
- phase_score: 0.534
- phase_breakdown.achieve_insertion_score: 0.351
- phase_breakdown.reach_entry_score: 0.593
- phase_breakdown.reach_align_score: 0.782

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.673
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.882
- **Median Q (composite search score)**: 0.108
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `4865da8c78c0d766958c01aea638a491e86f6ad380c20093f3e1db2b764e8196`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `66fcf22dcc3bcf7c938cd95aa7e21cfd304510ff9d22bdf68d85d724037825f3`; realized-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50095,0.03604,0.025]},{"name":"target","value":[0.50095,0.03604,0.025]},{"name":"socket","value":[0.50095,0.03604,0.025]},{"name":"goal","value":[0.50095,0.03604,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.03604,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02985,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.align_height":0.09206,"align_above.lateral_x":0.00661,"align_above.lateral_y":-0.00367,"align_above.pose_tol":0.0135,"descend_to_entry.contact_force_threshold":4.88664,"descend_to_entry.speed":0.02307,"insert_into_hole.insertion_distance":0.03515,"insert_into_hole.insertion_force_limit":26.01353,"retract_upward.retract_speed":0.06041},"optimized_scores":{"best_composite_score":0.10824,"best_fitness_score":0.61824,"best_task_score":0.8419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01074,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49752,0.03576,0.16483],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.50423,0.03082,0.1599],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08575,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_align","tcp_end":[0.50377,0.0308,0.11991],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.49883,0.03473,0.12371],"object_pos_start":[0.50423,0.03082,0.1599],"object_to_goal_dist_end":0.05584,"object_to_goal_dist_start":0.08575,"object_z_max":0.1599,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.49792,0.03467,0.08372],"tcp_start":[0.50377,0.0308,0.11991],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":137.0,"n_steps_budget":600.0,"object_pos_end":[0.49703,0.03541,0.10236],"object_pos_start":[0.49883,0.03473,0.12371],"object_to_goal_dist_end":0.04198,"object_to_goal_dist_start":0.05584,"object_z_max":0.12371,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"achieve_insertion","tcp_end":[0.49655,0.03538,0.06236],"tcp_start":[0.49792,0.03467,0.08372],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49847,0.03582,0.20481],"object_pos_start":[0.49703,0.03541,0.10236],"object_to_goal_dist_end":0.12986,"object_to_goal_dist_start":0.04198,"object_z_max":0.20472,"peak_contact_force":0.0,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49752,0.03576,0.16483],"tcp_start":[0.49655,0.03538,0.06236],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `93acd10de345eed07b6dc6c2bbc440a51ca07353b2db3e19ce9d53254358a6c5`; realized-scene SHA-256: `4c08395e36e43245f6092dd2e3719288cb8e1800970c3a851b5dc162486241ee`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13492,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.align_height":0.08678,"align_above.lateral_x":0.00905,"align_above.lateral_y":0.00473,"align_above.pose_tol":0.01979,"descend_to_entry.contact_force_threshold":8.75087,"descend_to_entry.speed":0.01811,"insert_into_hole.insertion_distance":0.03027,"insert_into_hole.insertion_force_limit":30.54295,"retract_upward.retract_speed":0.09963},"optimized_scores":{"best_composite_score":0.16317,"best_fitness_score":0.67317,"best_task_score":0.88169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01129,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47771,-0.01603,0.16418],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.48749,-0.01086,0.15574],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07753,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_align","tcp_end":[0.48705,-0.01085,0.11574],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.47977,-0.01483,0.12429],"object_pos_start":[0.48749,-0.01086,0.15574],"object_to_goal_dist_end":0.0509,"object_to_goal_dist_start":0.07753,"object_z_max":0.15574,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.4789,-0.01482,0.0843],"tcp_start":[0.48705,-0.01085,0.11574],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":162.0,"n_steps_budget":600.0,"object_pos_end":[0.47734,-0.01577,0.09811],"object_pos_start":[0.47977,-0.01483,0.12429],"object_to_goal_dist_end":0.03301,"object_to_goal_dist_start":0.0509,"object_z_max":0.12429,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"achieve_insertion","tcp_end":[0.47689,-0.01576,0.05811],"tcp_start":[0.4789,-0.01482,0.0843],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.47859,-0.01605,0.20417],"object_pos_start":[0.47734,-0.01577,0.09811],"object_to_goal_dist_end":0.12702,"object_to_goal_dist_start":0.03301,"object_z_max":0.20405,"peak_contact_force":0.0,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47771,-0.01603,0.16418],"tcp_start":[0.47689,-0.01576,0.05811],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e4487702be29fc714aef807905297ccb2e376a648cd6f3407ac6d1ceee44c37e`; realized-scene SHA-256: `71c7bcc0411146bb1295ec697eba8abcb9eaa89bf878970856d0e0a8305cc755`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95652,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.align_height":0.09776,"align_above.lateral_x":-0.00166,"align_above.lateral_y":-0.00435,"align_above.pose_tol":0.01343,"descend_to_entry.contact_force_threshold":4.98947,"descend_to_entry.speed":0.02431,"insert_into_hole.insertion_distance":0.04165,"insert_into_hole.insertion_force_limit":30.87602,"retract_upward.retract_speed":0.05724},"optimized_scores":{"best_composite_score":0.05723,"best_fitness_score":0.56723,"best_task_score":0.80533},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46356,-0.02095,0.16565],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.46413,-0.02406,0.16733],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09743,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_align","tcp_end":[0.46372,-0.02405,0.12734],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.46376,-0.02142,0.12299],"object_pos_start":[0.46413,-0.02406,0.16733],"object_to_goal_dist_end":0.06016,"object_to_goal_dist_start":0.09743,"object_z_max":0.16733,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.46293,-0.02139,0.083],"tcp_start":[0.46372,-0.02405,0.12734],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.46282,-0.02109,0.1087],"object_pos_start":[0.46376,-0.02142,0.12299],"object_to_goal_dist_end":0.05149,"object_to_goal_dist_start":0.06016,"object_z_max":0.12299,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"achieve_insertion","tcp_end":[0.46235,-0.02108,0.06871],"tcp_start":[0.46293,-0.02139,0.083],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":849.0,"n_steps_budget":1000.0,"object_pos_end":[0.46447,-0.02098,0.20564],"object_pos_start":[0.46282,-0.02109,0.1087],"object_to_goal_dist_end":0.13224,"object_to_goal_dist_start":0.05149,"object_z_max":0.20555,"peak_contact_force":0.0,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46356,-0.02095,0.16565],"tcp_start":[0.46235,-0.02108,0.06871],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```