## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 9 | -0.1122 | 0.99 | ❌ rejected |
| 12 | push → align → insert | impedance_motion | linear_cartesian | impedance_motion | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | force_exceeded | 8 | 0.1342 | 0.99 | ❌ rejected |
| 11 | push → align → insert | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | time_limit | pose_tolerance | force_exceeded | 7 | 0.5184 | 1.00 | ❌ rejected |
| 10 | push → align → insert | impedance_motion | linear_cartesian | impedance_motion | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | force_exceeded | 7 | 0.1800 | 0.98 | ❌ rejected |
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 9 | -0.1118 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.99). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`
- Frozen object start: [0.5354444884457887, 0.000906204225148928, 0.08]
- Frozen task target: [0.5354444884457887, 0.000906204225148928, 0.025]
- Frozen socket pose: [0.5, 0.0, 0.3] (static fixture for this episode)
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5354444884457887, 0.000906204225148928, 0.08)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
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
  frozen_task_target: [0.5354, 0.0009, 0.08]
  frozen_socket_position: [0.5354, 0.0009, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5354444884457887, 0.000906204225148928, 0.08]}
  frozen_targets: {'socket_entry': [0.5354444884457887, 0.000906204225148928, 0.025]}
  frozen_fixtures: {'peg_socket': [0.5, 0.0, 0.3]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.996, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5354444884457887, 0.000906204225148928, 0.08) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.3) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.112) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_socket
  anchor: fixture
  offset:
  - 0.03147
  - 0.0009
  - -0.2653
  weight: 0.2
- id: alignment
  anchor: fixture
  offset:
  - 0.03147
  - 0.0009
  - -0.3153
  weight: 0.3
- id: insertion_progress
  anchor: fixture
  offset:
  - 0.03147
  - 0.0009
  - -0.3653
  weight: 0.5
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: channel_axis
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: add
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: scale
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - -0.3153
    offset_along_axis:
      distance: 0.0
      axis: channel_axis
      mode: add_to_offset
      sign: positive
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
    lateral_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.031
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.001
      binds_to:
      - path: target.offset.y
        mode: add
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - -0.3153
    offset_along_axis:
      distance: 0.0
      axis: channel_axis
      mode: add_to_offset
      sign: positive
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
    lateral_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.031
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.001
      binds_to:
      - path: target.offset.y
        mode: add
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - -0.3153
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: negative
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
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: add
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: add
    insertion_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: scale
  guards:
  - id: insertion_progress
    when: during_phase
    predicate: force_below
    threshold: 3.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.08, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (add)
    - push_speed: status=consumed; consumers=generator.speed (scale)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, -0.3153], offset_along_axis={axis=channel_axis, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **release_1** (`release`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, -0.3153], offset_along_axis={axis=channel_axis, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, -0.3153], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (add)
    - insertion_force: status=consumed; consumers=termination.force_threshold (add)
    - insertion_speed: status=consumed; consumers=generator.speed (scale)
  - guards:
    - id=insertion_progress, when=during_phase, predicate=force_below, on_failure=continue, threshold=3.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.01, 0.0]

## Design Metrics

- **Composite score**: -0.112
- **task_score** (E): 0.994
- **fitness_score**: 0.398  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 0.00 | 0.0632 |
| align_1 | 1.00 | 0.00 | 0.2662 |
| release_1 | 0.00 | 1.00 | 0.0333 |
| insert_1 | 0.00 | 0.33 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.499, -0.000, 0.364) | (0.504, -0.000, 0.340)→(0.500, -0.000, 0.404) | 0.260→0.324 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.499, -0.000, 0.364)→(0.498, -0.003, 0.098) | (0.500, -0.000, 0.404)→(0.498, -0.003, 0.138) | 0.324→0.058 | 0.00 / 0.000 | 0.000 | 0.000 |
| release_1 | release | 0.00 / step_budget | (0.498, -0.003, 0.098)→(0.513, 0.003, 0.072) | (0.498, -0.003, 0.138)→(0.519, 0.003, 0.111) | 0.058→0.038 | 1.00 / 1.333 | 64.812 | 497.956 |
| insert_1 | insert | 0.00 / guard_failure | (0.513, 0.003, 0.072)→(0.512, 0.003, 0.072) | (0.519, 0.003, 0.111)→(0.519, 0.003, 0.111) | 0.038→0.038 | 0.33 / 0.333 | 26.464 | 76.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.997
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.997
- phase_score: 0.000
- phase_breakdown.alignment_score: 0.000
- phase_breakdown.approach_socket_score: 0.000
- phase_breakdown.insertion_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.399
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.997
- **Median Q (composite search score)**: -0.112
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.259


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1c06d48834291abac995c6cc1d2cd84f840e8dd85a042a042b29bb3e8b43f340`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a5dd99a2832e295b96a2d483dc6e44525a65c5240d3c756ec4d63dfbfe5237b3`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.00091,0.08]},{"name":"task_object","value":[0.53544,0.00091,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.53544,0.00091,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70677,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01042,"align_1.lateral_offset_y":-0.00759,"insert_1.insertion_depth":0.09307,"insert_1.insertion_force":11.23023,"insert_1.insertion_speed":0.02802,"push_1.push_distance":0.0931,"push_1.push_speed":0.03375,"release_1.lateral_offset_x":-0.02901,"release_1.lateral_offset_y":0.03895},"optimized_scores":{"best_composite_score":-0.1118,"best_fitness_score":0.3982,"best_task_score":0.99549},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1109.0,"contact_point_centroid":[0.50136,0.00995,0.07992],"force_p95":443.25068,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.91545,"mean_force":369.25924,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49645,-0.00179,0.07992]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50544,0.02,0.07998],"force_p95":79.39278,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.39278,"mean_force":79.39278,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50978,0.00588,0.07957]}],"total_contact_groups":2},"final_pose_error":0.13248,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.50976,0.00588,0.07959],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":502.91545,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4998,-1e-05,0.39588],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31588,"object_to_goal_dist_start":0.26034,"object_z_max":0.39581,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49935,-2e-05,0.35588],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.48693,-0.00722,0.12999],"object_pos_start":[0.4998,-1e-05,0.39588],"object_to_goal_dist_end":0.05217,"object_to_goal_dist_start":0.31588,"object_z_max":0.39591,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48648,-0.00721,0.08999],"tcp_start":[0.49935,-2e-05,0.35588],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51362,0.00595,0.11939],"object_pos_start":[0.48693,-0.00722,0.12999],"object_to_goal_dist_end":0.0421,"object_to_goal_dist_start":0.05217,"object_z_max":0.12999,"peak_contact_force":54.98759,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1109.0,"raw_peak_contact_force":502.91545,"tcp_end":[0.50978,0.00588,0.07957],"tcp_start":[0.48648,-0.00721,0.08999],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":840.0,"object_pos_end":[0.51358,0.00595,0.11941],"object_pos_start":[0.51362,0.00595,0.11939],"object_to_goal_dist_end":0.0421,"object_to_goal_dist_start":0.0421,"object_z_max":0.11939,"peak_contact_force":79.39278,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":79.39278,"tcp_end":[0.50976,0.00588,0.07959],"tcp_start":[0.50978,0.00588,0.07957],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`; realized-scene SHA-256: `68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.02464,0.08]},{"name":"task_object","value":[0.5244,0.02464,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.5244,0.02464,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73134,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00654,"align_1.lateral_offset_y":0.00138,"insert_1.insertion_depth":0.07775,"insert_1.insertion_force":13.61708,"insert_1.insertion_speed":0.02875,"push_1.push_distance":0.15187,"push_1.push_speed":0.05102,"release_1.lateral_offset_x":-0.00432,"release_1.lateral_offset_y":-0.00843},"optimized_scores":{"best_composite_score":-0.11106,"best_fitness_score":0.39894,"best_task_score":0.99734},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1047.0,"contact_point_centroid":[0.52336,-0.00537,0.07991],"force_p95":418.59043,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":457.21178,"mean_force":335.90543,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50944,-2e-05,0.08101]},{"body_a":"attachment","body_b":"peg_socket","contact_count":59.0,"contact_point_centroid":[0.4944,0.00517,0.07977],"force_p95":106.78719,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.87007,"mean_force":80.19414,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50058,0.00033,0.07949]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.5294,-0.00537,0.07998],"force_p95":73.90416,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.90416,"mean_force":73.90416,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51552,-0.00029,0.08251]}],"total_contact_groups":3},"final_pose_error":0.14844,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51545,-0.0003,0.08256],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":457.21178,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50011,-1e-05,0.41872],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33872,"object_to_goal_dist_start":0.26034,"object_z_max":0.41862,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49967,-2e-05,0.37872],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.50342,0.00126,0.15261],"object_pos_start":[0.50011,-1e-05,0.41872],"object_to_goal_dist_end":0.0727,"object_to_goal_dist_start":0.33872,"object_z_max":0.41877,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50296,0.00126,0.11261],"tcp_start":[0.49967,-2e-05,0.37872],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52272,-0.00035,0.12185],"object_pos_start":[0.50342,0.00126,0.15261],"object_to_goal_dist_end":0.04762,"object_to_goal_dist_start":0.0727,"object_z_max":0.15261,"peak_contact_force":65.29889,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1106.0,"raw_peak_contact_force":457.21178,"tcp_end":[0.51552,-0.00029,0.08251],"tcp_start":[0.50296,0.00126,0.11261],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.52262,-0.00036,0.12191],"object_pos_start":[0.52272,-0.00035,0.12185],"object_to_goal_dist_end":0.04763,"object_to_goal_dist_start":0.04762,"object_z_max":0.12185,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":73.90416,"tcp_end":[0.51545,-0.0003,0.08256],"tcp_start":[0.51552,-0.00029,0.08251],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`; realized-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,-0.01254,0.08]},{"name":"task_object","value":[0.50305,-0.01254,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50305,-0.01254,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72059,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00744,"align_1.lateral_offset_y":-0.00234,"insert_1.insertion_depth":0.03191,"insert_1.insertion_force":14.68714,"insert_1.insertion_speed":0.02518,"push_1.push_distance":0.09531,"push_1.push_speed":0.02876,"release_1.lateral_offset_x":-0.01716,"release_1.lateral_offset_y":0.01916},"optimized_scores":{"best_composite_score":-0.11384,"best_fitness_score":0.39616,"best_task_score":0.99039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":312.0,"contact_point_centroid":[0.53312,0.00215,0.07999],"force_p95":465.9088,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":533.74081,"mean_force":233.62958,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5132,0.00205,0.0525]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1022.0,"contact_point_centroid":[0.52385,0.00217,0.04995],"force_p95":456.40203,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.48089,"mean_force":349.58951,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50899,0.00126,0.05116]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52704,0.00261,0.04998],"force_p95":75.11774,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.11774,"mean_force":75.11774,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51234,0.00216,0.05292]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53306,0.00227,0.08],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51234,0.00216,0.05292]}],"total_contact_groups":4},"final_pose_error":0.1944,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.51227,0.00217,0.05298],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":533.74081,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4998,-1e-05,0.39651],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31651,"object_to_goal_dist_start":0.26034,"object_z_max":0.39644,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49936,-2e-05,0.35651],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.50383,-0.00226,0.13022],"object_pos_start":[0.4998,-1e-05,0.39651],"object_to_goal_dist_end":0.05042,"object_to_goal_dist_start":0.31651,"object_z_max":0.39654,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50337,-0.00226,0.09023],"tcp_start":[0.49936,-2e-05,0.35651],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5202,0.00235,0.09214],"object_pos_start":[0.50383,-0.00226,0.13022],"object_to_goal_dist_end":0.02369,"object_to_goal_dist_start":0.05042,"object_z_max":0.13022,"peak_contact_force":74.14937,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1334.0,"raw_peak_contact_force":533.74081,"tcp_end":[0.51234,0.00216,0.05292],"tcp_start":[0.50337,-0.00226,0.09023],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52011,0.00235,0.09221],"object_pos_start":[0.5202,0.00235,0.09214],"object_to_goal_dist_end":0.02364,"object_to_goal_dist_start":0.02369,"object_z_max":0.09214,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":75.11774,"tcp_end":[0.51227,0.00217,0.05298],"tcp_start":[0.51234,0.00216,0.05292],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```