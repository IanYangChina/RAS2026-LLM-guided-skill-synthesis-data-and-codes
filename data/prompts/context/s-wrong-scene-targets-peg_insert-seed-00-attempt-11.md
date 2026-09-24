## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | align → approach → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.0849 | 0.78 | ❌ rejected |
| 10 | approach → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5958 | 0.87 | ✅ accepted |
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.0852 | 0.60 | ✅ accepted |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.0853 | 0.60 | ❌ rejected |
| 7 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.1470 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`
- Frozen object start: [0.5109569349857164, -0.018417062898890377, 0.08]
- Frozen task target: [0.5109569349857164, -0.018417062898890377, 0.025]
- Frozen socket pose: [0.5, 0.0, 0.3] (static fixture for this episode)
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5109569349857164, -0.018417062898890377, 0.08)
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
  frozen_task_target: [0.511, -0.0184, 0.08]
  frozen_socket_position: [0.511, -0.0184, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5109569349857164, -0.018417062898890377, 0.08]}
  frozen_targets: {'socket_entry': [0.5109569349857164, -0.018417062898890377, 0.025]}
  frozen_fixtures: {'peg_socket': [0.5, 0.0, 0.3]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.866, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5109569349857164, -0.018417062898890377, 0.08) | approach/contact targets near object start |
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

## Current Skill (Q=0.085) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_socket
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: insert_into_socket
  weight: 0.7
phases:
- id: approach_above_socket
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_socket
- id: insert_downward
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.055
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert_into_socket
- id: lift_after_insert
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
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
- **approach_above_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **insert_downward** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.055, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=abort, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift_after_insert** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.085
- **task_score** (E): 0.779
- **fitness_score**: 0.412  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_over_hole | 0.00 | 0.00 | 0.1521 |
| descend_to_contact | 0.00 | 0.00 | 0.0829 |
| insert_into_hole | 0.33 | 0.33 | 0.0551 |
| lift_after_insert | 1.00 | 0.00 | 0.0894 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_over_hole | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.394, -0.000, 0.410) | (0.504, -0.000, 0.340)→(0.424, -0.000, 0.383) | 0.260→0.312 | 0.00 / 0.000 | 0.000 | 935.780 |
| descend_to_contact | approach | 0.00 / step_budget | (0.394, -0.000, 0.410)→(0.420, -0.000, 0.331) | (0.424, -0.000, 0.383)→(0.449, -0.000, 0.304) | 0.312→0.229 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | insert | 0.33 / step_budget | (0.420, -0.000, 0.331)→(0.419, -0.000, 0.276) | (0.449, -0.000, 0.304)→(0.448, -0.000, 0.248) | 0.229→0.176 | 0.33 / 0.333 | 307.397 | 0.000 |
| lift_after_insert | lift | 1.00 / step_budget | (0.419, -0.000, 0.276)→(0.418, -0.000, 0.366) | (0.448, -0.000, 0.248)→(0.447, -0.000, 0.338) | 0.176→0.263 | 0.00 / 0.000 | 0.000 | 43.536 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.776
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.776
- phase_score: 0.167
- phase_breakdown.approach_socket_score: 0.012
- phase_breakdown.insert_into_socket_score: 0.233

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.414
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.784
- **Median Q (composite search score)**: 0.004
- **K-run variance**: 0.0137
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.320


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `193ea3a1ce1ed79056963f057d25ec25a24d300f4824e32f67c8dd96cb6cee27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a8b82e05e54fe244d72795229d8ab0587efc7638aafbc9b6be7ad9630911a897`; realized-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,-0.01842,0.08]},{"name":"task_object","value":[0.51096,-0.01842,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.51096,-0.01842,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51096,-0.01842,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.97436,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.16633,"align_over_hole.approach_height_offset":0.22522,"descend_to_contact.contact_force_threshold":18.0942,"descend_to_contact.descend_speed":0.08278,"insert_into_hole.insert_force_threshold":11.66437,"insert_into_hole.insert_speed":0.03424,"lift_after_insert.lift_speed":0.08422},"optimized_scores":{"best_composite_score":-0.00016,"best_fitness_score":0.40984,"best_task_score":0.78399},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.51245,0.01217,0.07843],"force_p95":719.22788,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":935.56799,"mean_force":131.46166,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41872,-0.00105,0.10926]},{"body_a":"peg_socket","body_b":"link6","contact_count":240.0,"contact_point_centroid":[0.56592,-0.00328,0.07981],"force_p95":247.94473,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":415.23715,"mean_force":214.6858,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41631,-0.00095,0.13464]},{"body_a":"peg_socket","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.54377,0.0011,0.07881],"force_p95":206.18401,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.56994,"mean_force":24.06227,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.4187,-0.00116,0.11397]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.51342,-0.04844,0.07984],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41787,-0.00088,0.10373]}],"total_contact_groups":4},"final_pose_error":0.01138,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.41835,-0.00029,0.37498],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":935.56799,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.42337,-7e-05,0.39298],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.32222,"object_to_goal_dist_start":0.26034,"object_z_max":0.39283,"peak_contact_force":0.0,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":312.0,"raw_peak_contact_force":935.56799,"subtask_id":"approach_socket","tcp_end":[0.39334,-6e-05,0.4194],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":414.0,"n_steps_budget":660.0,"object_pos_end":[0.44967,-0.00015,0.3147],"object_pos_start":[0.42337,-7e-05,0.39298],"object_to_goal_dist_end":0.24003,"object_to_goal_dist_start":0.32222,"object_z_max":0.39308,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_socket","tcp_end":[0.41997,-0.00014,0.34148],"tcp_start":[0.39334,-6e-05,0.4194],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.4483,-0.00024,0.2592],"object_pos_start":[0.44967,-0.00015,0.3147],"object_to_goal_dist_end":0.18651,"object_to_goal_dist_start":0.24003,"object_z_max":0.3147,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_socket","tcp_end":[0.41893,-0.00022,0.28635],"tcp_start":[0.41997,-0.00014,0.34148],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":657.0,"n_steps_budget":750.0,"object_pos_end":[0.44759,-0.00032,0.34768],"object_pos_start":[0.4483,-0.00024,0.2592],"object_to_goal_dist_end":0.27277,"object_to_goal_dist_start":0.18651,"object_z_max":0.3476,"peak_contact_force":0.0,"phase_name":"lift_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.41835,-0.00029,0.37498],"tcp_start":[0.41893,-0.00022,0.28635],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`; realized-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.03604,0.08]},{"name":"task_object","value":[0.50095,0.03604,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50095,0.03604,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78191,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.14733,"align_over_hole.approach_height_offset":0.22697,"descend_to_contact.contact_force_threshold":15.1128,"descend_to_contact.descend_speed":0.05451,"insert_into_hole.insert_force_threshold":29.19943,"insert_into_hole.insert_speed":0.02799,"lift_after_insert.lift_speed":0.02772},"optimized_scores":{"best_composite_score":0.2503,"best_fitness_score":0.4103,"best_task_score":0.77592},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.51377,-0.00262,0.07791],"force_p95":744.19855,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":936.64206,"mean_force":128.70152,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41595,-0.00019,0.11384]},{"body_a":"peg_socket","body_b":"link6","contact_count":260.0,"contact_point_centroid":[0.56015,-0.00217,0.07982],"force_p95":233.72599,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":356.15248,"mean_force":211.0942,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41445,-0.00018,0.13779]},{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.53714,0.00164,0.07871],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.93716,"mean_force":5.48557,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41612,-0.0002,0.11568]},{"body_a":"peg_socket","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.56092,-0.0057,0.07996],"force_p95":118.14149,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.60842,"mean_force":91.75028,"phase_index":3.0,"phase_name":"lift_after_insert","phase_type":"lift","tcp_position_centroid":[0.41922,-0.00023,0.27473]}],"total_contact_groups":4},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.41852,-0.00029,0.36514],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":936.64206,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42386,-7e-05,0.38154],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31101,"object_to_goal_dist_start":0.26034,"object_z_max":0.38135,"peak_contact_force":0.0,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":333.0,"raw_peak_contact_force":936.64206,"subtask_id":"approach_socket","tcp_end":[0.39464,-6e-05,0.40886],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.44934,-0.00016,0.30238],"object_pos_start":[0.42386,-7e-05,0.38154],"object_to_goal_dist_end":0.22807,"object_to_goal_dist_start":0.31101,"object_z_max":0.38168,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_socket","tcp_end":[0.42045,-0.00014,0.33004],"tcp_start":[0.39464,-6e-05,0.40886],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.44785,-0.00025,0.24705],"object_pos_start":[0.44934,-0.00016,0.30238],"object_to_goal_dist_end":0.175,"object_to_goal_dist_start":0.22807,"object_z_max":0.30238,"peak_contact_force":922.19054,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_socket","tcp_end":[0.4193,-0.00023,0.27506],"tcp_start":[0.42045,-0.00014,0.33004],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.44694,-0.00032,0.337],"object_pos_start":[0.44785,-0.00025,0.24705],"object_to_goal_dist_end":0.26242,"object_to_goal_dist_start":0.175,"object_z_max":0.33694,"peak_contact_force":0.0,"phase_name":"lift_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7.0,"raw_peak_contact_force":130.60842,"tcp_end":[0.41852,-0.00029,0.36514],"tcp_start":[0.4193,-0.00023,0.27506],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`; realized-scene SHA-256: `4c08395e36e43245f6092dd2e3719288cb8e1800970c3a851b5dc162486241ee`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,-0.01612,0.08]},{"name":"task_object","value":[0.48093,-0.01612,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.48093,-0.01612,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01829,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.13844,"align_over_hole.approach_height_offset":0.27649,"descend_to_contact.contact_force_threshold":14.2125,"descend_to_contact.descend_speed":0.0496,"insert_into_hole.insert_force_threshold":22.29987,"insert_into_hole.insert_speed":0.01999,"lift_after_insert.lift_speed":0.07344},"optimized_scores":{"best_composite_score":0.00444,"best_fitness_score":0.41444,"best_task_score":0.77811},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.52734,-0.00035,0.07896],"force_p95":660.3664,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":935.13034,"mean_force":303.0294,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41775,-0.00048,0.12397]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.51043,0.01401,0.07957],"force_p95":506.86935,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":539.83673,"mean_force":371.16389,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.41793,-0.00041,0.11065]},{"body_a":"peg_socket","body_b":"link6","contact_count":176.0,"contact_point_centroid":[0.54091,-0.0018,0.07987],"force_p95":258.23725,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.54146,"mean_force":212.52139,"phase_index":0.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.40686,-0.0002,0.15469]}],"total_contact_groups":3},"final_pose_error":0.01061,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.41837,-0.0003,0.3566],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":935.13034,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42378,-7e-05,0.37399],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30371,"object_to_goal_dist_start":0.26034,"object_z_max":0.3738,"peak_contact_force":0.0,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":263.0,"raw_peak_contact_force":935.13034,"subtask_id":"approach_socket","tcp_end":[0.39513,-6e-05,0.4019],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.44869,-0.00016,0.29421],"object_pos_start":[0.42378,-7e-05,0.37399],"object_to_goal_dist_end":0.22026,"object_to_goal_dist_start":0.30371,"object_z_max":0.37411,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_socket","tcp_end":[0.42038,-0.00014,0.32246],"tcp_start":[0.39513,-6e-05,0.4019],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.44712,-0.00025,0.23858],"object_pos_start":[0.44869,-0.00016,0.29421],"object_to_goal_dist_end":0.16717,"object_to_goal_dist_start":0.22026,"object_z_max":0.29421,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_socket","tcp_end":[0.41915,-0.00023,0.26718],"tcp_start":[0.42038,-0.00014,0.32246],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":693.0,"n_steps_budget":870.0,"object_pos_end":[0.44618,-0.00032,0.32784],"object_pos_start":[0.44712,-0.00025,0.23858],"object_to_goal_dist_end":0.25362,"object_to_goal_dist_start":0.16717,"object_z_max":0.32776,"peak_contact_force":0.0,"phase_name":"lift_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.41837,-0.0003,0.3566],"tcp_start":[0.41915,-0.00023,0.26718],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```