## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2870 | 0.89 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.4653 | 0.89 | ✅ accepted |
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.5136 | 0.89 | ✅ accepted |
| 0 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 5 | -0.2770 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5244002338996304, 0.024635263178919502, 0.08]
- Frozen socket pose: [0.5244002338996304, 0.024635263178919502, 0.025] (static fixture for this episode)
- Goal object position: (0.5244002338996304, 0.024635263178919502, 0.025)
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
  frozen_task_target: [0.5244, 0.0246, 0.08]
  frozen_socket_position: [0.5244, 0.0246, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5244002338996304, 0.024635263178919502, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5244002338996304, 0.024635263178919502, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.890, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5244002338996304, 0.024635263178919502, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5244002338996304, 0.024635263178919502, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.287) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_socket_above
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_socket_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: insert_complete
  weight: 0.5
phases:
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
    - 0.12
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
  subtask_id: reach_socket_above
- id: descend_1
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
    - 0.08
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_socket_entry
- id: contact_1
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
    contact_force:
      type: scalar
      range:
      - 2.0
      - 12.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.008
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: guard_contact_force
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
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
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.08
  parameters:
    insert_force:
      type: scalar
      range:
      - 25.0
      - 45.0
      default: 35.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.025
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.045
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: guard_insert_force
    when: during_phase
    predicate: force_below
    threshold: 42.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insert_complete
- id: retract_1
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
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
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=guard_contact_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=channel_axis, distance=0.04, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.08
  - parameter_bindings:
    - insert_force: status=consumed; consumers=termination.force_threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=guard_insert_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=42.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.287
- **task_score** (E): 0.887
- **fitness_score**: 0.727  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1491 |
| descend_1 | 1.00 | 0.00 | 0.0459 |
| contact_1 | 0.00 | 0.00 | 0.0355 |
| insert_1 | 0.00 | 1.00 | 0.0223 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.013, 0.154) | (0.504, -0.000, 0.340)→(0.509, 0.013, 0.194) | 0.260→0.116 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | approach | 1.00 / step_budget | (0.508, 0.013, 0.154)→(0.508, 0.014, 0.108) | (0.509, 0.013, 0.194)→(0.509, 0.014, 0.148) | 0.116→0.073 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 0.00 / step_budget | (0.508, 0.014, 0.108)→(0.508, 0.014, 0.072) | (0.509, 0.014, 0.148)→(0.508, 0.014, 0.112) | 0.073→0.042 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.508, 0.014, 0.072)→(0.505, 0.014, 0.050) | (0.508, 0.014, 0.112)→(0.506, 0.014, 0.090) | 0.042→0.027 | 1.00 / 1.000 | 74.309 | 74.309 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.943
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.943
- phase_score: 0.701
- phase_breakdown.reach_socket_entry_score: 0.906
- phase_breakdown.reach_socket_above_score: 0.823
- phase_breakdown.insert_complete_score: 0.530

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.798
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.943
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.396


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5dab308f3f0d3a4c4fc859445abf2870fb989899bfcd82caf016befc5af88e16`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `195061a138fd9757490665621e9d85a89af1c36de72bed7c93df67d7bd9941b0`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62755,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.03233,"contact_1.contact_force":8.94674,"contact_1.speed":0.01899,"descend_1.speed":0.03965,"insert_1.insert_speed":0.01712,"insert_1.insertion_depth":0.05885,"retract_1.speed":0.07658},"optimized_scores":{"best_composite_score":0.25666,"best_fitness_score":0.69666,"best_task_score":0.86084},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53177,0.02493,0.04993],"force_p95":70.08842,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.08842,"mean_force":70.08842,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51679,0.02414,0.05004]}],"total_contact_groups":1},"final_pose_error":0.08411,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.5168,0.02414,0.04992],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":70.08842,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.51968,0.02243,0.19296],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11684,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_above","tcp_end":[0.51921,0.02241,0.15297],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":271.0,"n_steps_budget":780.0,"object_pos_end":[0.52048,0.02411,0.14733],"object_pos_start":[0.51968,0.02243,0.19296],"object_to_goal_dist_end":0.07439,"object_to_goal_dist_start":0.11684,"object_z_max":0.19296,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52001,0.02409,0.10733],"tcp_start":[0.51921,0.02241,0.15297],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.52024,0.02433,0.11183],"object_pos_start":[0.52048,0.02411,0.14733],"object_to_goal_dist_end":0.04488,"object_to_goal_dist_start":0.07439,"object_z_max":0.14733,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.51977,0.02431,0.07183],"tcp_start":[0.52001,0.02409,0.10733],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.51727,0.02416,0.08991],"object_pos_start":[0.52024,0.02433,0.11183],"object_to_goal_dist_end":0.03131,"object_to_goal_dist_start":0.04488,"object_z_max":0.11183,"peak_contact_force":70.08842,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":70.08842,"subtask_id":"insert_complete","tcp_end":[0.5168,0.02414,0.04992],"tcp_start":[0.51977,0.02431,0.07183],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2449f4fe819a4bbdd9aec1335ce72ae3bc4ae0ee808de76617a31b3392ec72d5`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66667,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.07581,"contact_1.contact_force":10.31729,"contact_1.speed":0.01886,"descend_1.speed":0.04631,"insert_1.insert_speed":0.00676,"insert_1.insertion_depth":0.01241,"retract_1.speed":0.05328},"optimized_scores":{"best_composite_score":0.35792,"best_fitness_score":0.79792,"best_task_score":0.94284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51129,-0.01267,0.04996],"force_p95":73.67639,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.67639,"mean_force":73.67639,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49629,-0.01247,0.05009]}],"total_contact_groups":1},"final_pose_error":0.03799,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.4963,-0.01247,0.04997],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":73.67639,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.50022,-0.01139,0.19409],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11466,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_above","tcp_end":[0.49978,-0.01139,0.15409],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":271.0,"n_steps_budget":690.0,"object_pos_end":[0.49951,-0.01233,0.14785],"object_pos_start":[0.50022,-0.01139,0.19409],"object_to_goal_dist_end":0.06897,"object_to_goal_dist_start":0.11466,"object_z_max":0.19409,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.49905,-0.01233,0.10786],"tcp_start":[0.49978,-0.01139,0.15409],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.49907,-0.01248,0.1123],"object_pos_start":[0.49951,-0.01233,0.14785],"object_to_goal_dist_end":0.03464,"object_to_goal_dist_start":0.06897,"object_z_max":0.14785,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49862,-0.01247,0.0723],"tcp_start":[0.49905,-0.01233,0.10786],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.49676,-0.01247,0.08997],"object_pos_start":[0.49907,-0.01248,0.1123],"object_to_goal_dist_end":0.01629,"object_to_goal_dist_start":0.03464,"object_z_max":0.1123,"peak_contact_force":73.67639,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":73.67639,"subtask_id":"insert_complete","tcp_end":[0.4963,-0.01247,0.04997],"tcp_start":[0.49862,-0.01247,0.0723],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c3c1e2ca75f8f9fa89b5aa82a3db3edf9cebca69b40eef83389e8297541d8019`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.21951,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.08301,"contact_1.contact_force":7.88014,"contact_1.speed":0.00585,"descend_1.speed":0.0867,"insert_1.insert_speed":0.02148,"insert_1.insertion_depth":0.05943,"retract_1.speed":0.09889},"optimized_scores":{"best_composite_score":0.24655,"best_fitness_score":0.68655,"best_task_score":0.85664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.5176,0.03165,0.04992],"force_p95":79.16075,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.16075,"mean_force":79.16075,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50262,0.03118,0.05002]}],"total_contact_groups":1},"final_pose_error":0.08464,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50263,0.03119,0.04989],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":79.16075,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.50656,0.02889,0.19349],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11729,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_above","tcp_end":[0.5061,0.02886,0.15349],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":268.0,"n_steps_budget":600.0,"object_pos_end":[0.50633,0.03111,0.14769],"object_pos_start":[0.50656,0.02889,0.19349],"object_to_goal_dist_end":0.07476,"object_to_goal_dist_start":0.11729,"object_z_max":0.19349,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.50587,0.03109,0.10769],"tcp_start":[0.5061,0.02886,0.15349],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.03141,0.11212],"object_pos_start":[0.50633,0.03111,0.14769],"object_to_goal_dist_end":0.04532,"object_to_goal_dist_start":0.07476,"object_z_max":0.14769,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50551,0.03138,0.07212],"tcp_start":[0.50587,0.03109,0.10769],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":137.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.03121,0.08989],"object_pos_start":[0.50597,0.03141,0.11212],"object_to_goal_dist_end":0.03289,"object_to_goal_dist_start":0.04532,"object_z_max":0.11212,"peak_contact_force":79.16075,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":79.16075,"subtask_id":"insert_complete","tcp_end":[0.50263,0.03119,0.04989],"tcp_start":[0.50551,0.03138,0.07212],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```