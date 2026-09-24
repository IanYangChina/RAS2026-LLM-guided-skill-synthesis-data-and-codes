## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

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
- Frozen realised-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.4809289707399447, -0.016120708526870135, 0.08]
- Frozen socket pose: [0.4809289707399447, -0.016120708526870135, 0.025] (static fixture for this episode)
- Goal object position: (0.4809289707399447, -0.016120708526870135, 0.025)
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
  frozen_task_target: [0.4809, -0.0161, 0.08]
  frozen_socket_position: [0.4809, -0.0161, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.4809289707399447, -0.016120708526870135, 0.08]}
  frozen_fixtures: {'peg_socket': [0.4809289707399447, -0.016120708526870135, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.862, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.4809289707399447, -0.016120708526870135, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.4809289707399447, -0.016120708526870135, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.030) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_target
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insert_target
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_entry
  type: approach
  generator: arc_cartesian
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
      - -1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_target
- id: align_over_hole
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
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.015
      default: 0.008
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_target
- id: descend_contact
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
    - -0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insert_target
- id: insert_down
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - -0.055
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: insert_target

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **align_over_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - lateral_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_y: status=consumed; consumers=target.offset.y (replace)
- **descend_contact** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.005]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_down** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.055]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.030
- **task_score** (E): 0.862
- **fitness_score**: 0.440  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entry | 0.00 | 1.00 | 0.1573 |
| align_over_hole | 1.00 | 1.00 | 0.0161 |
| descend_contact | 1.00 | 1.00 | 0.0001 |
| insert_down | 0.00 | 1.00 | 0.1203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entry | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.468, 0.004, 0.147) | (0.504, -0.000, 0.340)→(0.506, 0.003, 0.135) | 0.260→0.055 | 1.00 / 1.000 | 292.436 | 1057.102 |
| align_over_hole | align | 1.00 / step_budget | (0.468, 0.004, 0.147)→(0.479, 0.001, 0.157) | (0.506, 0.003, 0.135)→(0.515, -0.000, 0.140) | 0.055→0.063 | 1.00 / 1.000 | 317.411 | 453.513 |
| descend_contact | contact | 1.00 / force_exceeded | (0.479, 0.001, 0.157)→(0.479, 0.001, 0.157) | (0.515, -0.000, 0.140)→(0.515, -0.000, 0.140) | 0.063→0.063 | 1.00 / 1.000 | 245.399 | 245.399 |
| insert_down | insert | 0.00 / step_budget | (0.479, 0.001, 0.157)→(0.526, -0.053, 0.240) | (0.515, -0.000, 0.140)→(0.547, -0.054, 0.208) | 0.063→0.149 | 1.00 / 1.000 | 297.040 | 1092.361 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.914
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.914
- phase_score: 0.244
- phase_breakdown.approach_target_score: 0.812
- phase_breakdown.insert_target_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.512
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.914
- **Median Q (composite search score)**: -0.003
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: approach_entry.approach_height
- **Final σ (mean)**: 0.316


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`; realized-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.81818,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.07445,"align_over_hole.align_tolerance":0.01055,"align_over_hole.lateral_x":0.00805,"align_over_hole.lateral_y":0.00043,"approach_entry.approach_height":0.12603,"approach_entry.approach_speed":0.05923,"approach_entry.approach_tolerance":0.01685,"approach_entry.arc_height":0.13929,"descend_contact.contact_force_threshold":12.80919,"descend_contact.descend_speed":0.02469,"insert_down.insert_speed":0.00778,"insert_down.insert_tolerance":0.01067},"optimized_scores":{"best_composite_score":-0.00803,"best_fitness_score":0.40197,"best_task_score":0.83914},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":45.0,"contact_point_centroid":[0.65309,-0.0619,-0.00056],"force_p95":1500.79584,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1982.52621,"mean_force":459.47444,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52888,0.04161,0.19441]},{"body_a":"peg_socket","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.5404,-0.07578,0.07848],"force_p95":1076.3906,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1893.70282,"mean_force":392.73099,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.54856,-0.0174,0.25216]},{"body_a":"peg_socket","body_b":"link7","contact_count":831.0,"contact_point_centroid":[0.5408,-0.00402,0.07996],"force_p95":402.9457,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1245.57769,"mean_force":341.49749,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47578,0.02988,0.1349]},{"body_a":"peg_socket","body_b":"link7","contact_count":783.0,"contact_point_centroid":[0.54075,-0.00132,0.07986],"force_p95":321.7119,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1041.00569,"mean_force":300.73145,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.46538,0.00125,0.13226]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.455,0.01429,0.0795],"force_p95":896.04651,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":903.07539,"mean_force":624.44426,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.45079,0.00511,0.08964]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.4467,0.00328,0.07861],"force_p95":687.94553,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":772.16902,"mean_force":201.9934,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.44286,-0.00048,0.09018]},{"body_a":"peg_socket","body_b":"link7","contact_count":455.0,"contact_point_centroid":[0.54085,-0.0036,0.07997],"force_p95":317.35822,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.35624,"mean_force":308.95083,"phase_index":1.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.47013,0.00412,0.13833]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54085,-0.00461,0.07997],"force_p95":312.58458,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.58458,"mean_force":312.58458,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.47134,0.00528,0.13946]}],"total_contact_groups":8},"final_pose_error":0.24341,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.54895,-0.03207,0.25816],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1982.52621,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":875.0,"n_steps_budget":1000.0,"object_pos_end":[0.50814,0.00088,0.12706],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04776,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":314.59167,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":1041.00569,"subtask_id":"approach_target","tcp_end":[0.46972,0.00216,0.13811],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50943,0.00237,0.12759],"object_pos_start":[0.50814,0.00088,0.12706],"object_to_goal_dist_end":0.04857,"object_to_goal_dist_start":0.04776,"object_z_max":0.12759,"peak_contact_force":317.64819,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":455.0,"raw_peak_contact_force":344.35624,"subtask_id":"approach_target","tcp_end":[0.47134,0.00528,0.13946],"tcp_start":[0.46972,0.00216,0.13811],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50943,0.00238,0.12759],"object_pos_start":[0.50943,0.00237,0.12759],"object_to_goal_dist_end":0.04857,"object_to_goal_dist_start":0.04857,"object_z_max":0.12759,"peak_contact_force":312.58458,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":312.58458,"subtask_id":"insert_target","tcp_end":[0.47134,0.00528,0.13946],"tcp_start":[0.47134,0.00528,0.13946],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56674,-0.0384,0.2229],"object_pos_start":[0.50943,0.00238,0.12759],"object_to_goal_dist_end":0.16233,"object_to_goal_dist_start":0.04857,"object_z_max":0.22287,"peak_contact_force":304.09845,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":986.0,"raw_peak_contact_force":1982.52621,"subtask_id":"insert_target","tcp_end":[0.54895,-0.03207,0.25816],"tcp_start":[0.47134,0.00528,0.13946],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`; realized-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.0,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.06116,"align_over_hole.align_tolerance":0.01162,"align_over_hole.lateral_x":-0.00028,"align_over_hole.lateral_y":-0.007,"approach_entry.approach_height":0.12091,"approach_entry.approach_speed":0.04193,"approach_entry.approach_tolerance":0.01899,"approach_entry.arc_height":0.1322,"descend_contact.contact_force_threshold":12.50521,"descend_contact.descend_speed":0.02089,"insert_down.insert_speed":0.00663,"insert_down.insert_tolerance":0.01661},"optimized_scores":{"best_composite_score":-0.00258,"best_fitness_score":0.40742,"best_task_score":0.83121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45268,0.00912,0.07898],"force_p95":1021.90328,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1058.01046,"mean_force":654.59086,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.44804,0.00658,0.09193]},{"body_a":"world","body_b":"link6","contact_count":58.0,"contact_point_centroid":[0.62872,-0.07371,-0.00037],"force_p95":642.71122,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":780.47605,"mean_force":336.0491,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.50924,0.01823,0.19195]},{"body_a":"peg_socket","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.52661,-0.00714,0.07994],"force_p95":437.89001,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.70106,"mean_force":372.79646,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47343,0.04334,0.13374]},{"body_a":"peg_socket","body_b":"link6","contact_count":576.0,"contact_point_centroid":[0.52676,-0.08095,0.07994],"force_p95":281.84561,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":560.95091,"mean_force":274.8836,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.53164,-0.0428,0.26046]},{"body_a":"peg_socket","body_b":"link7","contact_count":901.0,"contact_point_centroid":[0.52674,0.00303,0.07993],"force_p95":319.40635,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":556.31354,"mean_force":296.35195,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.45476,0.00694,0.1326]},{"body_a":"peg_socket","body_b":"link7","contact_count":455.0,"contact_point_centroid":[0.52676,-0.0045,0.07998],"force_p95":387.23649,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.17886,"mean_force":363.91687,"phase_index":1.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.46814,0.00754,0.14675]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.66973,-0.00096,-9e-05],"force_p95":375.74454,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":386.02484,"mean_force":115.69538,"phase_index":1.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.46971,0.00737,0.14824]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52676,-0.02566,0.08],"force_p95":375.99385,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":375.99385,"mean_force":375.99385,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.47035,0.00698,0.1485]}],"total_contact_groups":8},"final_pose_error":0.24535,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.52951,-0.04438,0.26106],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1058.01046,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49824,0.00747,0.12574],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04638,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":322.16849,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":911.0,"raw_peak_contact_force":1058.01046,"subtask_id":"approach_target","tcp_end":[0.46063,0.00757,0.13937],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50558,0.00413,0.12978],"object_pos_start":[0.49824,0.00747,0.12574],"object_to_goal_dist_end":0.05026,"object_to_goal_dist_start":0.04638,"object_z_max":0.12977,"peak_contact_force":385.06573,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":525.0,"raw_peak_contact_force":420.17886,"subtask_id":"approach_target","tcp_end":[0.47035,0.00698,0.1485],"tcp_start":[0.46063,0.00757,0.13937],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50559,0.00419,0.12974],"object_pos_start":[0.50558,0.00413,0.12978],"object_to_goal_dist_end":0.05023,"object_to_goal_dist_start":0.05026,"object_z_max":0.12978,"peak_contact_force":375.99385,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":375.99385,"subtask_id":"insert_target","tcp_end":[0.47036,0.00707,0.14847],"tcp_start":[0.47035,0.00698,0.1485],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54393,-0.05152,0.22444],"object_pos_start":[0.50559,0.00419,0.12974],"object_to_goal_dist_end":0.15952,"object_to_goal_dist_start":0.05023,"object_z_max":0.22566,"peak_contact_force":266.87312,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":994.0,"raw_peak_contact_force":780.47605,"subtask_id":"insert_target","tcp_end":[0.52951,-0.04438,0.26106],"tcp_start":[0.47036,0.00707,0.14847],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.52688,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.0579,"align_over_hole.align_tolerance":0.01014,"align_over_hole.lateral_x":0.00629,"align_over_hole.lateral_y":-0.01019,"approach_entry.approach_height":0.15,"approach_entry.approach_speed":0.06127,"approach_entry.approach_tolerance":0.01267,"approach_entry.arc_height":0.05592,"descend_contact.contact_force_threshold":6.08631,"descend_contact.descend_speed":0.02348,"insert_down.insert_speed":0.01085,"insert_down.insert_tolerance":0.00627},"optimized_scores":{"best_composite_score":0.10197,"best_fitness_score":0.51197,"best_task_score":0.91433},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.48341,0.00051,0.07888],"force_p95":1011.94361,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1072.29007,"mean_force":227.26377,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.47902,0.0005,0.09209]},{"body_a":"peg_socket","body_b":"link7","contact_count":202.0,"contact_point_centroid":[0.59138,0.00347,0.07951],"force_p95":397.01563,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":818.03838,"mean_force":258.85397,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.47378,0.00074,0.13707]},{"body_a":"peg_socket","body_b":"link6","contact_count":640.0,"contact_point_centroid":[0.59537,-0.00209,0.07982],"force_p95":335.1564,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":596.00364,"mean_force":254.83322,"phase_index":1.0,"phase_name":"align_over_hole","phase_type":"align","tcp_position_centroid":[0.4742,0.00041,0.17585]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.56109,-0.05896,0.07975],"force_p95":406.91691,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.08104,"mean_force":290.0221,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.49828,-0.07919,0.19945]},{"body_a":"peg_socket","body_b":"link6","contact_count":287.0,"contact_point_centroid":[0.59541,-0.00046,0.07988],"force_p95":274.18824,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":513.66529,"mean_force":245.24261,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.47275,0.0012,0.1587]},{"body_a":"peg_socket","body_b":"link6","contact_count":937.0,"contact_point_centroid":[0.59535,-0.01164,0.07981],"force_p95":333.68834,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":480.82768,"mean_force":265.57987,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47837,-0.03144,0.1877]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59542,-0.00213,0.07995],"force_p95":47.61989,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.61989,"mean_force":47.61989,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49417,-0.00821,0.18255]}],"total_contact_groups":7},"final_pose_error":0.19704,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.49897,-0.08336,0.19934],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1072.29007,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":586.0,"n_steps_budget":810.0,"object_pos_end":[0.51079,0.00137,0.15114],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07197,"object_to_goal_dist_start":0.26034,"object_z_max":0.34617,"peak_contact_force":240.5478,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":502.0,"raw_peak_contact_force":1072.29007,"subtask_id":"approach_target","tcp_end":[0.47246,0.00147,0.16255],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":664.0,"n_steps_budget":780.0,"object_pos_end":[0.52961,-0.00741,0.16402],"object_pos_start":[0.51079,0.00137,0.15114],"object_to_goal_dist_end":0.0894,"object_to_goal_dist_start":0.07197,"object_z_max":0.1796,"peak_contact_force":249.51993,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":640.0,"raw_peak_contact_force":596.00364,"subtask_id":"approach_target","tcp_end":[0.49417,-0.00821,0.18255],"tcp_start":[0.47246,0.00147,0.16255],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52963,-0.00742,0.16412],"object_pos_start":[0.52961,-0.00741,0.16402],"object_to_goal_dist_end":0.08949,"object_to_goal_dist_start":0.0894,"object_z_max":0.16402,"peak_contact_force":47.61989,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":47.61989,"subtask_id":"insert_target","tcp_end":[0.49418,-0.00825,0.18263],"tcp_start":[0.49417,-0.00821,0.18255],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53116,-0.0728,0.17807],"object_pos_start":[0.52963,-0.00742,0.16412],"object_to_goal_dist_end":0.12605,"object_to_goal_dist_start":0.08949,"object_z_max":0.187,"peak_contact_force":320.14974,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":963.0,"raw_peak_contact_force":514.08104,"subtask_id":"insert_target","tcp_end":[0.49897,-0.08336,0.19934],"tcp_start":[0.49418,-0.00825,0.18263],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```