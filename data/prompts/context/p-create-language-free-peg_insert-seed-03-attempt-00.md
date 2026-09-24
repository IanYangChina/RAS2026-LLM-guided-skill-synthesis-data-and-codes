## Search State

- **Seed**: 3
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.5015 | 0.85 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.853, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.501) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion_complete
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - -0.05
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
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  subtask_id: reach_pre_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
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
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
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
  subtask_id: insertion_complete
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
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.501
- **task_score** (E): 0.853
- **fitness_score**: 0.411  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1280 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| insert_1 | 0.00 | 0.33 | 0.0430 |
| retract_1 | 0.33 | 0.00 | 0.1021 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.475, 0.005, 0.176) | (0.504, -0.000, 0.340)→(0.510, 0.004, 0.157) | 0.260→0.078 | 1.00 / 1.000 | 279.031 | 2283.222 |
| contact_1 | contact | 1.00 / force_exceeded | (0.475, 0.005, 0.176)→(0.475, 0.005, 0.176) | (0.510, 0.004, 0.157)→(0.510, 0.004, 0.157) | 0.078→0.078 | 1.00 / 1.000 | 225.681 | 225.681 |
| insert_1 | insert | 0.00 / step_budget | (0.475, 0.005, 0.176)→(0.510, 0.006, 0.193) | (0.510, 0.004, 0.157)→(0.547, 0.006, 0.177) | 0.078→0.110 | 0.33 / 0.333 | 98.977 | 733.395 |
| retract_1 | retract | 0.33 / step_budget | (0.510, 0.006, 0.193)→(0.514, 0.012, 0.293) | (0.547, 0.006, 0.177)→(0.552, 0.012, 0.284) | 0.110→0.213 | 0.00 / 0.000 | 0.000 | 65.430 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.833
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.833
- phase_score: 0.245
- phase_breakdown.reach_pre_contact_score: 0.727
- phase_breakdown.insertion_complete_score: 0.038

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.480
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.866
- **Median Q (composite search score)**: 0.469
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Parameters at lower bound**: contact_1.contact_force
- **Final σ (mean)**: 0.295


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.07353,"average_mean_iterations":19.66176,"average_solve_count":68.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.3737,"insert_1.insertion_depth":0.04877},"optimized_scores":{"best_composite_score":0.57015,"best_fitness_score":0.48015,"best_task_score":0.83297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":343.0,"contact_point_centroid":[0.68323,-0.01395,-0.00011],"force_p95":342.23698,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1122.55904,"mean_force":284.69794,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47353,-0.01023,0.13265]},{"body_a":"peg_socket","body_b":"link7","contact_count":658.0,"contact_point_centroid":[0.5266,-0.00948,0.06741],"force_p95":336.19475,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1080.02685,"mean_force":305.12507,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45528,-0.00585,0.11331]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.4425,0.00925,0.07981],"force_p95":609.4803,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":614.64103,"mean_force":336.50651,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44039,-0.00336,0.08681]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52679,-0.0117,0.06408],"force_p95":479.46095,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.20188,"mean_force":184.37006,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46214,-0.0066,0.1204]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.69198,-0.01843,-9e-05],"force_p95":187.18378,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.29115,"mean_force":120.81545,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48493,-0.01461,0.13698]},{"body_a":"world","body_b":"link6","contact_count":24.0,"contact_point_centroid":[0.67906,-0.01059,-8e-05],"force_p95":136.5714,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.76991,"mean_force":61.05595,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46224,-0.00656,0.12097]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52676,-0.01165,0.06419],"force_p95":101.43769,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.43769,"mean_force":101.43769,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46209,-0.00654,0.12051]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.4361,0.00709,0.07985],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4341,-0.00596,0.08681]}],"total_contact_groups":8},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46657,-0.02038,0.17005],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1122.55904,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.49962,-0.00785,0.10674],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02787,"object_to_goal_dist_start":0.26034,"object_z_max":0.3443,"peak_contact_force":334.80814,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":699.0,"raw_peak_contact_force":1080.02685,"subtask_id":"reach_pre_contact","tcp_end":[0.46209,-0.00654,0.12051],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.49963,-0.00787,0.10674],"object_pos_start":[0.49962,-0.00785,0.10674],"object_to_goal_dist_end":0.02787,"object_to_goal_dist_start":0.02787,"object_z_max":0.10674,"peak_contact_force":101.43769,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":101.43769,"tcp_end":[0.4621,-0.00656,0.12051],"tcp_start":[0.46209,-0.00654,0.12051],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":600.0,"object_pos_end":[0.52134,-0.01545,0.12038],"object_pos_start":[0.49963,-0.00787,0.10674],"object_to_goal_dist_end":0.04821,"object_to_goal_dist_start":0.02787,"object_z_max":0.12203,"peak_contact_force":296.93154,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":348.0,"raw_peak_contact_force":1122.55904,"subtask_id":"insertion_complete","tcp_end":[0.48502,-0.01455,0.13709],"tcp_start":[0.4621,-0.00656,0.12051],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":360.0,"n_steps_budget":600.0,"object_pos_end":[0.50268,-0.02127,0.15285],"object_pos_start":[0.52134,-0.01545,0.12038],"object_to_goal_dist_end":0.07594,"object_to_goal_dist_start":0.04821,"object_z_max":0.15277,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7.0,"raw_peak_contact_force":196.29115,"tcp_end":[0.46657,-0.02038,0.17005],"tcp_start":[0.48502,-0.01455,0.13709],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":39.0,"average_failure_rate":0.4382,"average_mean_iterations":92.79775,"average_solve_count":89.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":3.77943,"insert_1.insertion_depth":0.06397},"optimized_scores":{"best_composite_score":0.46492,"best_fitness_score":0.37492,"best_task_score":0.86579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.56559,0.00099,0.07911],"force_p95":813.99938,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":896.28904,"mean_force":226.08035,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44575,-0.00014,0.10572]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.47548,-0.0,0.07991],"force_p95":829.7433,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":832.16578,"mean_force":786.36111,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4644,3e-05,0.09161]},{"body_a":"peg_socket","body_b":"link7","contact_count":116.0,"contact_point_centroid":[0.59535,-0.00105,0.07988],"force_p95":466.36179,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":550.24399,"mean_force":304.62905,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5028,0.00239,0.1817]},{"body_a":"peg_socket","body_b":"link6","contact_count":122.0,"contact_point_centroid":[0.59541,-0.00266,0.07993],"force_p95":369.81483,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":461.57735,"mean_force":275.45509,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49183,0.00025,0.19442]},{"body_a":"peg_socket","body_b":"link6","contact_count":613.0,"contact_point_centroid":[0.59501,-0.00257,0.07985],"force_p95":276.50605,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.19975,"mean_force":236.80525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46234,0.00021,0.17146]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59537,-0.00205,0.07989],"force_p95":282.07438,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.07438,"mean_force":282.07438,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48579,0.00104,0.20624]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54226,-0.02928,0.07891],"force_p95":6.90163,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.00545,"mean_force":1.5337,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44569,-0.00014,0.10015]}],"total_contact_groups":7},"final_pose_error":0.17588,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.53977,0.01647,0.35513],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":896.28904,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.519,0.00103,0.18394],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10567,"object_to_goal_dist_start":0.26034,"object_z_max":0.34476,"peak_contact_force":221.54493,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":656.0,"raw_peak_contact_force":896.28904,"subtask_id":"reach_pre_contact","tcp_end":[0.48579,0.00104,0.20624],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.51899,0.00103,0.18391],"object_pos_start":[0.519,0.00103,0.18394],"object_to_goal_dist_end":0.10564,"object_to_goal_dist_start":0.10567,"object_z_max":0.18394,"peak_contact_force":282.07438,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":282.07438,"tcp_end":[0.48578,0.00105,0.2062],"tcp_start":[0.48579,0.00104,0.20624],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.56872,0.00854,0.2324],"object_pos_start":[0.51899,0.00103,0.18391],"object_to_goal_dist_end":0.16739,"object_to_goal_dist_start":0.10564,"object_z_max":0.23109,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":238.0,"raw_peak_contact_force":550.24399,"subtask_id":"insertion_complete","tcp_end":[0.53172,0.00814,0.2476],"tcp_start":[0.48578,0.00105,0.2062],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.57923,0.0174,0.34863],"object_pos_start":[0.56872,0.00854,0.2324],"object_to_goal_dist_end":0.28061,"object_to_goal_dist_start":0.16739,"object_z_max":0.34743,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.53977,0.01647,0.35513],"tcp_start":[0.53172,0.00814,0.2476],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":48.0,"average_failure_rate":0.46154,"average_mean_iterations":97.375,"average_solve_count":104.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":1.00001,"insert_1.insertion_depth":0.14836},"optimized_scores":{"best_composite_score":0.46941,"best_fitness_score":0.37941,"best_task_score":0.86099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":587.0,"contact_point_centroid":[0.58426,0.00839,0.07954],"force_p95":1804.84001,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4873.35097,"mean_force":455.14354,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46056,0.01027,0.16606]},{"body_a":"peg_socket","body_b":"link7","contact_count":217.0,"contact_point_centroid":[0.5794,0.00946,0.07951],"force_p95":4113.03037,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4842.8105,"mean_force":756.65642,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45876,0.00504,0.14246]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.46577,0.00337,0.07865],"force_p95":1047.67671,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.38637,"mean_force":274.19039,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45763,0.00337,0.09043]},{"body_a":"peg_socket","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.5518,-0.00558,0.07862],"force_p95":890.00191,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1028.96725,"mean_force":253.36778,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45392,0.00397,0.10418]},{"body_a":"peg_socket","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.58436,0.02123,0.07992],"force_p95":378.93952,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":527.38094,"mean_force":297.66288,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49615,0.02131,0.17696]},{"body_a":"peg_socket","body_b":"link6","contact_count":194.0,"contact_point_centroid":[0.58435,0.01658,0.07992],"force_p95":327.57714,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":396.15591,"mean_force":227.39787,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48447,0.01945,0.19795]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58437,0.01516,0.07996],"force_p95":293.53014,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.53014,"mean_force":293.53014,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47629,0.01908,0.20051]}],"total_contact_groups":7},"final_pose_error":0.17398,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.53423,0.04009,0.35301],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":4873.35097,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.51007,0.01867,0.17909],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10134,"object_to_goal_dist_start":0.26034,"object_z_max":0.34462,"peak_contact_force":280.7388,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":4873.35097,"subtask_id":"reach_pre_contact","tcp_end":[0.47629,0.01908,0.20051],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.51006,0.01865,0.1791],"object_pos_start":[0.51007,0.01867,0.17909],"object_to_goal_dist_end":0.10134,"object_to_goal_dist_start":0.10134,"object_z_max":0.17909,"peak_contact_force":293.53014,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":293.53014,"tcp_end":[0.47626,0.01906,0.2005],"tcp_start":[0.47629,0.01908,0.20051],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.54974,0.02399,0.17942],"object_pos_start":[0.51006,0.01865,0.1791],"object_to_goal_dist_end":0.11373,"object_to_goal_dist_start":0.10134,"object_z_max":0.17918,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":349.0,"raw_peak_contact_force":527.38094,"subtask_id":"insertion_complete","tcp_end":[0.5131,0.02375,0.19547],"tcp_start":[0.47626,0.01906,0.2005],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":97.0,"n_steps_budget":600.0,"object_pos_end":[0.57404,0.04131,0.34933],"object_pos_start":[0.54974,0.02399,0.17942],"object_to_goal_dist_end":0.28236,"object_to_goal_dist_start":0.11373,"object_z_max":0.34772,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.53423,0.04009,0.35301],"tcp_start":[0.5131,0.02375,0.19547],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```