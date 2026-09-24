## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

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

## Current Skill (Q=0.164) — your mutation base

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

- **Composite score**: 0.164
- **task_score** (E): 0.859
- **fitness_score**: 0.360  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entry | 0.00 | 1.00 | 0.1654 |
| descend_align | 1.00 | 1.00 | 0.0002 |
| insert_down | 0.00 | 1.00 | 0.0907 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entry | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.465, -0.002, 0.139) | (0.504, -0.000, 0.340)→(0.504, -0.003, 0.129) | 0.260→0.050 | 1.00 / 1.000 | 285.879 | 1166.167 |
| descend_align | contact | 1.00 / force_exceeded | (0.465, -0.002, 0.139)→(0.465, -0.003, 0.139) | (0.504, -0.003, 0.129)→(0.504, -0.003, 0.129) | 0.050→0.050 | 1.00 / 1.000 | 310.920 | 310.920 |
| insert_down | insert | 0.00 / step_budget | (0.465, -0.003, 0.139)→(0.499, 0.036, 0.193) | (0.504, -0.003, 0.129)→(0.527, 0.032, 0.170) | 0.050→0.103 | 1.00 / 1.333 | 300.197 | 2063.167 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.809
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.809
- phase_score: 0.082
- phase_breakdown.approach_target_score: 0.002
- phase_breakdown.insert_target_score: 0.116

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.373
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.920
- **Median Q (composite search score)**: 0.172
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.25333,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_height":0.12534,"approach_entry.approach_speed":0.08213,"approach_entry.approach_tolerance":0.01977,"approach_entry.arc_height":0.18814,"descend_align.contact_force_threshold":9.66727,"descend_align.descend_speed":0.01927,"descend_align.lateral_x":-0.00285,"descend_align.lateral_y":-0.00781,"insert_down.insert_speed":0.01528,"insert_down.insert_tolerance":0.00969},"optimized_scores":{"best_composite_score":0.14334,"best_fitness_score":0.34,"best_task_score":0.84907},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":283.0,"contact_point_centroid":[0.50116,0.10529,-9e-05],"force_p95":3646.40359,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5162.89021,"mean_force":713.60717,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.53865,0.03679,0.26273]},{"body_a":"peg_socket","body_b":"link5","contact_count":272.0,"contact_point_centroid":[0.50106,0.04362,0.06215],"force_p95":3784.09721,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4617.14078,"mean_force":629.00042,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.53796,0.03917,0.26432]},{"body_a":"peg_socket","body_b":"link7","contact_count":514.0,"contact_point_centroid":[0.54073,-0.00287,0.07982],"force_p95":327.2135,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1014.7436,"mean_force":304.53297,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4659,0.00073,0.12573]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.45453,0.01454,0.07948],"force_p95":807.40988,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":809.0279,"mean_force":397.77192,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.45087,0.0031,0.08686]},{"body_a":"peg_socket","body_b":"link5","contact_count":39.0,"contact_point_centroid":[0.50366,0.04302,0.04985],"force_p95":629.14953,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":639.36919,"mean_force":131.1761,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.54261,0.01359,0.25467]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.44922,0.00952,0.07953],"force_p95":637.23234,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":637.96661,"mean_force":323.60168,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.44558,-0.00151,0.08842]},{"body_a":"world","body_b":"link6","contact_count":25.0,"contact_point_centroid":[0.65079,0.08734,-0.00108],"force_p95":488.19548,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":580.33479,"mean_force":275.08041,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.53397,-0.04317,0.18404]},{"body_a":"peg_socket","body_b":"link7","contact_count":663.0,"contact_point_centroid":[0.54078,-0.00103,0.07995],"force_p95":372.60199,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.27355,"mean_force":346.6371,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47698,-0.02829,0.13274]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54085,-0.00395,0.07997],"force_p95":356.06561,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.12479,"mean_force":202.53301,"phase_index":1.0,"phase_name":"descend_align","phase_type":"contact","tcp_position_centroid":[0.47106,0.00095,0.13339]}],"total_contact_groups":9},"final_pose_error":0.20737,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.53708,0.05077,0.26808],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":5162.89021,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":605.0,"n_steps_budget":750.0,"object_pos_end":[0.50948,3e-05,0.12267],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04371,"object_to_goal_dist_start":0.26034,"object_z_max":0.3444,"peak_contact_force":321.90898,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":1014.7436,"subtask_id":"approach_target","tcp_end":[0.47098,0.00107,0.13347],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":870.0,"object_pos_end":[0.50957,-0.00031,0.12236],"object_pos_start":[0.50948,3e-05,0.12267],"object_to_goal_dist_end":0.04343,"object_to_goal_dist_start":0.04371,"object_z_max":0.12267,"peak_contact_force":373.12479,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":373.12479,"subtask_id":"insert_target","tcp_end":[0.47109,0.00071,0.13326],"tcp_start":[0.47098,0.00107,0.13347],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55237,0.05721,0.23168],"object_pos_start":[0.50957,-0.00031,0.12236],"object_to_goal_dist_end":0.17036,"object_to_goal_dist_start":0.04343,"object_z_max":0.23168,"peak_contact_force":246.28978,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1282.0,"raw_peak_contact_force":5162.89021,"subtask_id":"insert_target","tcp_end":[0.53708,0.05077,0.26808],"tcp_start":[0.47109,0.00071,0.13326],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.0404,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_height":0.14492,"approach_entry.approach_speed":0.04071,"approach_entry.approach_tolerance":0.01443,"approach_entry.arc_height":0.16509,"descend_align.contact_force_threshold":4.56608,"descend_align.descend_speed":0.02143,"descend_align.lateral_x":0.0197,"descend_align.lateral_y":-0.00299,"insert_down.insert_speed":0.01232,"insert_down.insert_tolerance":0.01639},"optimized_scores":{"best_composite_score":0.17598,"best_fitness_score":0.37264,"best_task_score":0.8093},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":908.0,"contact_point_centroid":[0.52665,-0.01185,0.07983],"force_p95":304.93186,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1365.63791,"mean_force":289.40628,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4504,-0.00736,0.12766]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.4314,-0.00912,0.07832],"force_p95":809.50745,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":867.25116,"mean_force":218.04611,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.42815,-0.00578,0.08978]},{"body_a":"peg_socket","body_b":"link7","contact_count":998.0,"contact_point_centroid":[0.52676,-0.01817,0.07998],"force_p95":433.9039,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":723.30965,"mean_force":376.64784,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47018,0.01295,0.14388]},{"body_a":"world","body_b":"link6","contact_count":243.0,"contact_point_centroid":[0.67001,-0.02543,-5e-05],"force_p95":354.54527,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":619.48123,"mean_force":143.41537,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47136,0.01563,0.14484]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52678,-0.01369,0.07997],"force_p95":314.56174,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.56174,"mean_force":314.56174,"phase_index":1.0,"phase_name":"descend_align","phase_type":"contact","tcp_position_centroid":[0.45644,-0.00906,0.13551]}],"total_contact_groups":5},"final_pose_error":0.07922,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47628,0.0487,0.11634],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1365.63791,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,-0.01018,0.12457],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.046,"object_to_goal_dist_start":0.26034,"object_z_max":0.34397,"peak_contact_force":304.828,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":922.0,"raw_peak_contact_force":1365.63791,"subtask_id":"approach_target","tcp_end":[0.45644,-0.00906,0.13551],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.49491,-0.01016,0.12457],"object_pos_start":[0.4949,-0.01018,0.12457],"object_to_goal_dist_end":0.046,"object_to_goal_dist_start":0.046,"object_z_max":0.12457,"peak_contact_force":314.56174,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":314.56174,"subtask_id":"insert_target","tcp_end":[0.45646,-0.00901,0.13553],"tcp_start":[0.45644,-0.00906,0.13551],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5101,0.03155,0.10361],"object_pos_start":[0.49491,-0.01016,0.12457],"object_to_goal_dist_end":0.04068,"object_to_goal_dist_start":0.046,"object_z_max":0.13067,"peak_contact_force":390.58626,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1241.0,"raw_peak_contact_force":723.30965,"subtask_id":"insert_target","tcp_end":[0.47628,0.0487,0.11634],"tcp_start":[0.45646,-0.00901,0.13553],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.15714,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_height":0.1726,"approach_entry.approach_speed":0.0738,"approach_entry.approach_tolerance":0.01997,"approach_entry.arc_height":0.10017,"descend_align.contact_force_threshold":5.86667,"descend_align.descend_speed":0.02276,"descend_align.lateral_x":-0.00274,"descend_align.lateral_y":0.00491,"insert_down.insert_speed":0.01045,"insert_down.insert_tolerance":0.0137},"optimized_scores":{"best_composite_score":0.17168,"best_fitness_score":0.36835,"best_task_score":0.91962},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.48413,0.00041,0.07816],"force_p95":1066.17246,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1118.11998,"mean_force":261.719,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.47946,0.00041,0.09056]},{"body_a":"peg_socket","body_b":"link7","contact_count":164.0,"contact_point_centroid":[0.59053,0.00289,0.07947],"force_p95":420.44084,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":724.60507,"mean_force":271.33398,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4737,0.00053,0.13411]},{"body_a":"peg_socket","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.59541,-0.00055,0.0799],"force_p95":276.93493,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.30233,"mean_force":248.01011,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47439,0.00231,0.17362]},{"body_a":"peg_socket","body_b":"link6","contact_count":80.0,"contact_point_centroid":[0.59541,-0.00073,0.07983],"force_p95":246.42123,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.17359,"mean_force":229.73637,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4678,0.00069,0.14654]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59544,-0.00078,0.07998],"force_p95":245.07413,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.07413,"mean_force":245.07413,"phase_index":1.0,"phase_name":"descend_align","phase_type":"contact","tcp_position_centroid":[0.46773,0.0007,0.14819]}],"total_contact_groups":5},"final_pose_error":0.12562,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.4844,0.00863,0.19452],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1118.11998,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.50708,0.00071,0.141],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06142,"object_to_goal_dist_start":0.26034,"object_z_max":0.34603,"peak_contact_force":230.89901,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":259.0,"raw_peak_contact_force":1118.11998,"subtask_id":"approach_target","tcp_end":[0.46773,0.0007,0.14819],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50708,0.00071,0.14102],"object_pos_start":[0.50708,0.00071,0.141],"object_to_goal_dist_end":0.06144,"object_to_goal_dist_start":0.06142,"object_z_max":0.141,"peak_contact_force":245.07413,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":245.07413,"subtask_id":"insert_target","tcp_end":[0.46774,0.0007,0.14821],"tcp_start":[0.46773,0.0007,0.14819],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51907,0.00714,0.17462],"object_pos_start":[0.50708,0.00071,0.14102],"object_to_goal_dist_end":0.09679,"object_to_goal_dist_start":0.06144,"object_z_max":0.1746,"peak_contact_force":263.71542,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":991.0,"raw_peak_contact_force":303.30233,"subtask_id":"insert_target","tcp_end":[0.4844,0.00863,0.19452],"tcp_start":[0.46774,0.0007,0.14821],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```