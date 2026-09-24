## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3659 | 0.99 | ❌ rejected |
| 10 | approach → align → insert | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.7069 | 0.98 | ❌ rejected |
| 9 | approach → align → insert | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.8277 | 0.99 | ❌ rejected |
| 8 | approach → align → insert | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.7172 | 0.99 | ❌ rejected |
| 7 | approach → align → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.4968 | 0.91 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.46685193337148995, -0.021055159472312023, 0.08]
- Frozen socket pose: [0.46685193337148995, -0.021055159472312023, 0.025] (static fixture for this episode)
- Goal object position: (0.46685193337148995, -0.021055159472312023, 0.025)
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
  frozen_task_target: [0.4669, -0.0211, 0.08]
  frozen_socket_position: [0.4669, -0.0211, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.46685193337148995, -0.021055159472312023, 0.08]}
  frozen_fixtures: {'peg_socket': [0.46685193337148995, -0.021055159472312023, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.994, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.46685193337148995, -0.021055159472312023, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.46685193337148995, -0.021055159472312023, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.366) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_above_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: contact_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insert_goal
  weight: 0.5
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
    - 0.15
    orientation:
      mode: none
  parameters:
    approach_z:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_socket
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
  parameters:
    lateral_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: contact_socket
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    pose_tol:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
  subtask_id: insert_goal
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
    - 0.15
    orientation:
      mode: none
  parameters:
    retract_z:
      type: scalar
      range:
      - 0.08
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
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_y: status=consumed; consumers=target.offset.y (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - retract_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.366
- **task_score** (E): 0.990
- **fitness_score**: 0.876  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1300 |
| align_1 | 1.00 | 0.00 | 0.0910 |
| insert_1 | 1.00 | 1.00 | 0.0099 |
| retract_1 | 1.00 | 0.00 | 0.0660 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.001, 0.175) | (0.504, -0.000, 0.340)→(0.515, 0.001, 0.213) | 0.260→0.137 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.505, 0.001, 0.175)→(0.494, -0.001, 0.089) | (0.515, 0.001, 0.213)→(0.495, -0.001, 0.129) | 0.137→0.049 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 1.00 / step_budget | (0.494, -0.001, 0.089)→(0.498, -0.001, 0.080) | (0.495, -0.001, 0.129)→(0.497, -0.001, 0.120) | 0.049→0.040 | 1.00 / 1.333 | 346.268 | 370.382 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.001, 0.080)→(0.505, 0.001, 0.135) | (0.497, -0.001, 0.120)→(0.501, 0.001, 0.175) | 0.040→0.100 | 0.00 / 0.000 | 0.000 | 95.750 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.996
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.996
- phase_score: 0.808
- phase_breakdown.reach_above_socket_score: 0.883
- phase_breakdown.insert_goal_score: 0.983
- phase_breakdown.contact_socket_score: 0.466

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.883
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.996
- **Median Q (composite search score)**: 0.369
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.363


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f11800d9c2e1994b03c35d775c68a936832c378ea82102a5404a99f161f65289`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ef8adc000d20c9595fb92eedb002c99ab6f0fb118834572ef2a426eae092b67`; realized-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04167,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_x":0.02853,"align_1.lateral_y":0.02006,"approach_1.approach_z":0.14151,"approach_1.speed":0.0959,"insert_1.insert_speed":0.01542,"insert_1.insertion_depth":0.03274,"insert_1.pose_tol":0.00368,"retract_1.retract_z":0.14063,"retract_1.speed":0.04073},"optimized_scores":{"best_composite_score":0.3685,"best_fitness_score":0.8785,"best_task_score":0.97843},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":902.0,"contact_point_centroid":[0.48388,0.00895,0.07993],"force_p95":411.22031,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":414.65933,"mean_force":295.61709,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.491,-0.0031,0.07994]},{"body_a":"attachment","body_b":"peg_socket","contact_count":689.0,"contact_point_centroid":[0.49754,-0.01015,0.07998],"force_p95":171.9088,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.02612,"mean_force":135.53097,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48988,-0.00309,0.07992]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.48762,0.00895,0.07994],"force_p95":60.73733,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.82222,"mean_force":55.20666,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49644,-0.00317,0.08012]}],"total_contact_groups":3},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46592,-0.01975,0.1558],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":414.65933,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":395.0,"n_steps_budget":930.0,"object_pos_end":[0.48015,-0.01898,0.21402],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13681,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_socket","tcp_end":[0.46736,-0.01878,0.17612],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":336.0,"n_steps_budget":660.0,"object_pos_end":[0.48915,-0.00311,0.12693],"object_pos_start":[0.48015,-0.01898,0.21402],"object_to_goal_dist_end":0.04827,"object_to_goal_dist_start":0.13681,"object_z_max":0.21402,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact_socket","tcp_end":[0.48869,-0.00311,0.08693],"tcp_start":[0.46736,-0.01878,0.17612],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.49531,-0.00316,0.12006],"object_pos_start":[0.48915,-0.00311,0.12693],"object_to_goal_dist_end":0.04046,"object_to_goal_dist_start":0.04827,"object_z_max":0.12693,"peak_contact_force":412.06416,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1591.0,"raw_peak_contact_force":414.65933,"subtask_id":"insert_goal","tcp_end":[0.4964,-0.00316,0.08008],"tcp_start":[0.48869,-0.00311,0.08693],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.46289,-0.01963,0.19568],"object_pos_start":[0.49531,-0.00316,0.12006],"object_to_goal_dist_end":0.12307,"object_to_goal_dist_start":0.04046,"object_z_max":0.19557,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5.0,"raw_peak_contact_force":60.82222,"tcp_end":[0.46592,-0.01975,0.1558],"tcp_start":[0.4964,-0.00316,0.08008],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3e77e957595308cac760f5f4d0307201511ded613ae0a20d2d9d48ef360ca4f0`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03101,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_x":-0.03997,"align_1.lateral_y":-0.00097,"approach_1.approach_z":0.1389,"approach_1.speed":0.04927,"insert_1.insert_speed":0.04768,"insert_1.insertion_depth":0.02188,"insert_1.pose_tol":0.00983,"retract_1.retract_z":0.08051,"retract_1.speed":0.03306},"optimized_scores":{"best_composite_score":0.35607,"best_fitness_score":0.86607,"best_task_score":0.99607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":61.0,"contact_point_centroid":[0.50544,0.00708,0.07973],"force_p95":452.7161,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.18545,"mean_force":409.93852,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49632,2e-05,0.07952]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.50544,0.00795,0.07993],"force_p95":168.98532,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":172.88526,"mean_force":133.71942,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49699,4e-05,0.07987]}],"total_contact_groups":2},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52856,0.00077,0.09832],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":462.18545,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.53698,0.00077,0.21043],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13557,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_socket","tcp_end":[0.52897,0.00076,0.17124],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":234.0,"n_steps_budget":630.0,"object_pos_end":[0.49793,3e-05,0.12973],"object_pos_start":[0.53698,0.00077,0.21043],"object_to_goal_dist_end":0.04977,"object_to_goal_dist_start":0.13557,"object_z_max":0.21043,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact_socket","tcp_end":[0.49738,3e-05,0.08973],"tcp_start":[0.52897,0.00076,0.17124],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":100.0,"n_steps_budget":600.0,"object_pos_end":[0.49705,3e-05,0.11985],"object_pos_start":[0.49793,3e-05,0.12973],"object_to_goal_dist_end":0.03995,"object_to_goal_dist_start":0.04977,"object_z_max":0.12973,"peak_contact_force":418.98602,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":61.0,"raw_peak_contact_force":462.18545,"subtask_id":"insert_goal","tcp_end":[0.49697,3e-05,0.07985],"tcp_start":[0.49738,3e-05,0.08973],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":431.0,"n_steps_budget":870.0,"object_pos_end":[0.52565,0.00077,0.13821],"object_pos_start":[0.49705,3e-05,0.11985],"object_to_goal_dist_end":0.06361,"object_to_goal_dist_start":0.03995,"object_z_max":0.13817,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":14.0,"raw_peak_contact_force":172.88526,"tcp_end":[0.52856,0.00077,0.09832],"tcp_start":[0.49697,3e-05,0.07985],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f1677605f38c34d5c76967e3b08a88589314d198860b89f86514cd0f3e96f4b3`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96403,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_x":-0.02673,"align_1.lateral_y":-0.02902,"approach_1.approach_z":0.14362,"approach_1.speed":0.05157,"insert_1.insert_speed":0.02038,"insert_1.insertion_depth":0.02949,"insert_1.pose_tol":0.00391,"retract_1.retract_z":0.13515,"retract_1.speed":0.05507},"optimized_scores":{"best_composite_score":0.37328,"best_fitness_score":0.88328,"best_task_score":0.99635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":514.0,"contact_point_centroid":[0.49841,-0.00536,0.07995],"force_p95":208.81768,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":234.29976,"mean_force":194.37661,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49741,-0.00071,0.07991]},{"body_a":"attachment","body_b":"peg_socket","contact_count":512.0,"contact_point_centroid":[0.48954,0.01022,0.07995],"force_p95":210.07743,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.93503,"mean_force":192.54544,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49742,-0.00071,0.07991]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.48616,0.00588,0.07996],"force_p95":47.12268,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.54329,"mean_force":21.59325,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49953,-0.0007,0.07994]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.4944,-0.00536,0.07997],"force_p95":14.72235,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":15.00099,"mean_force":11.45055,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49953,-0.0007,0.07994]}],"total_contact_groups":4},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52001,0.02324,0.15132],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":234.29976,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.52751,0.02206,0.21537],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13989,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_socket","tcp_end":[0.5189,0.02205,0.17631],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":260.0,"n_steps_budget":660.0,"object_pos_end":[0.49777,-0.00063,0.1291],"object_pos_start":[0.52751,0.02206,0.21537],"object_to_goal_dist_end":0.04916,"object_to_goal_dist_start":0.13989,"object_z_max":0.21537,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact_socket","tcp_end":[0.49725,-0.00063,0.08911],"tcp_start":[0.5189,0.02205,0.17631],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":572.0,"n_steps_budget":900.0,"object_pos_end":[0.49948,-0.00069,0.11992],"object_pos_start":[0.49777,-0.00063,0.1291],"object_to_goal_dist_end":0.03993,"object_to_goal_dist_start":0.04916,"object_z_max":0.1291,"peak_contact_force":207.75407,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1026.0,"raw_peak_contact_force":234.29976,"subtask_id":"insert_goal","tcp_end":[0.49952,-0.00071,0.07992],"tcp_start":[0.49725,-0.00063,0.08911],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":818.0,"n_steps_budget":990.0,"object_pos_end":[0.51526,0.02288,0.19104],"object_pos_start":[0.49948,-0.00069,0.11992],"object_to_goal_dist_end":0.11439,"object_to_goal_dist_start":0.03993,"object_z_max":0.19097,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":10.0,"raw_peak_contact_force":53.54329,"tcp_end":[0.52001,0.02324,0.15132],"tcp_start":[0.49952,-0.00071,0.07992],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```