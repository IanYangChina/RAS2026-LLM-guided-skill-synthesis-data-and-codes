## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6625 | 0.89 | ❌ rejected |
| 10 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3299 | 0.82 | ❌ rejected |
| 9 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6972 | 0.91 | ✅ accepted |
| 8 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6928 | 0.91 | ✅ accepted |
| 7 | approach → align → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1924 | 0.82 | ❌ rejected |

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
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.663) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_hole
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: insert_peg
  weight: 0.7
phases:
- id: approach_1
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
    - 0.15
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_hole
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
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
  subtask_id: approach_hole
- id: insert_1
  type: insert
  generator: linear_cartesian
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
      distance: 0.08
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
    pose_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.08, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.663
- **task_score** (E): 0.886
- **fitness_score**: 0.659  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1294 |
| descend_1 | 1.00 | 1.00 | 0.0002 |
| insert_1 | 0.00 | 1.00 | 0.1199 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.454, 0.014, 0.181) | (0.504, -0.000, 0.340)→(0.489, 0.013, 0.163) | 0.260→0.086 | 1.00 / 1.333 | 273.268 | 1172.079 |
| descend_1 | descend | 1.00 / force_exceeded | (0.454, 0.014, 0.181)→(0.454, 0.014, 0.181) | (0.489, 0.013, 0.163)→(0.489, 0.013, 0.163) | 0.086→0.086 | 1.00 / 1.333 | 318.051 | 318.051 |
| insert_1 | insert | 0.00 / step_budget | (0.454, 0.014, 0.181)→(0.489, 0.004, 0.069) | (0.489, 0.013, 0.163)→(0.492, 0.004, 0.109) | 0.086→0.037 | 1.00 / 1.000 | 396.317 | 603.869 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.965
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.965
- phase_score: 0.657
- phase_breakdown.insert_peg_score: 0.858
- phase_breakdown.approach_hole_score: 0.188

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.780
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.965
- **Median Q (composite search score)**: 0.628
- **K-run variance**: 0.0078
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.275


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `193ea3a1ce1ed79056963f057d25ec25a24d300f4824e32f67c8dd96cb6cee27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a8b82e05e54fe244d72795229d8ab0587efc7638aafbc9b6be7ad9630911a897`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91111,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04874,"approach_1.arc_height":0.05061,"descend_1.contact_force_threshold":3.91668,"insert_1.insert_depth":0.06139,"insert_1.insert_speed":0.01656,"insert_1.pose_tolerance":0.01646},"optimized_scores":{"best_composite_score":0.78345,"best_fitness_score":0.78012,"best_task_score":0.96519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45438,0.00979,0.07889],"force_p95":999.05346,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1044.02955,"mean_force":198.81122,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44967,0.00977,0.09199]},{"body_a":"peg_socket","body_b":"link7","contact_count":719.0,"contact_point_centroid":[0.56878,0.01814,0.07982],"force_p95":504.23331,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":940.61146,"mean_force":255.12686,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44945,0.01618,0.14929]},{"body_a":"peg_socket","body_b":"link6","contact_count":449.0,"contact_point_centroid":[0.57083,0.01508,0.07947],"force_p95":599.10702,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":939.8612,"mean_force":296.27253,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44776,0.01761,0.15206]},{"body_a":"attachment","body_b":"peg_socket","contact_count":314.0,"contact_point_centroid":[0.48095,-0.01355,0.07985],"force_p95":393.11727,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.33685,"mean_force":338.01661,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49116,-0.00433,0.07905]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.54023,0.0116,0.07918],"force_p95":527.38262,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":578.12041,"mean_force":318.182,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44741,0.01011,0.10143]},{"body_a":"peg_socket","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.57094,0.01239,0.07995],"force_p95":449.61579,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":468.54687,"mean_force":365.89527,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44415,0.02097,0.16532]},{"body_a":"attachment","body_b":"peg_socket","contact_count":333.0,"contact_point_centroid":[0.49084,0.01159,0.07989],"force_p95":410.19657,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":425.42967,"mean_force":396.99194,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48508,-0.00219,0.08005]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.57094,0.01265,0.07996],"force_p95":342.93893,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.93893,"mean_force":342.93893,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45102,0.02013,0.16511]}],"total_contact_groups":8},"final_pose_error":0.06384,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.49446,-0.00518,0.07885],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1044.02955,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":960.0,"object_pos_end":[0.48889,0.01646,0.15278],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07544,"object_to_goal_dist_start":0.26034,"object_z_max":0.3444,"peak_contact_force":260.07634,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1202.0,"raw_peak_contact_force":1044.02955,"subtask_id":"approach_hole","tcp_end":[0.45102,0.02013,0.16511],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.48879,0.01641,0.15297],"object_pos_start":[0.48889,0.01646,0.15278],"object_to_goal_dist_end":0.07563,"object_to_goal_dist_start":0.07544,"object_z_max":0.15278,"peak_contact_force":342.93893,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":342.93893,"subtask_id":"approach_hole","tcp_end":[0.45095,0.02011,0.16539],"tcp_start":[0.45102,0.02013,0.16511],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49741,-0.00521,0.11874],"object_pos_start":[0.48879,0.01641,0.15297],"object_to_goal_dist_end":0.03917,"object_to_goal_dist_start":0.07563,"object_z_max":0.17694,"peak_contact_force":371.04899,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":656.0,"raw_peak_contact_force":612.33685,"subtask_id":"insert_peg","tcp_end":[0.49446,-0.00518,0.07885],"tcp_start":[0.45095,0.02011,0.16539],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.20213,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0856,"approach_1.arc_height":0.13601,"descend_1.contact_force_threshold":7.68739,"insert_1.insert_depth":0.06707,"insert_1.insert_speed":0.04399,"insert_1.pose_tolerance":0.01582},"optimized_scores":{"best_composite_score":0.57644,"best_fitness_score":0.5731,"best_task_score":0.83748},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45225,0.01259,0.07879],"force_p95":995.52767,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1044.06487,"mean_force":181.00503,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44795,0.01255,0.09194]},{"body_a":"peg_socket","body_b":"link7","contact_count":351.0,"contact_point_centroid":[0.55854,0.02574,0.0797],"force_p95":332.0811,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":944.23143,"mean_force":199.13667,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45019,0.02192,0.16145]},{"body_a":"attachment","body_b":"peg_socket","contact_count":677.0,"contact_point_centroid":[0.47094,0.02121,0.0799],"force_p95":408.59827,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":588.0534,"mean_force":382.1409,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48,0.03148,0.079]},{"body_a":"peg_socket","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.56091,0.02569,0.07966],"force_p95":467.72551,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.55366,"mean_force":312.09066,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44504,0.02404,0.163]},{"body_a":"peg_socket","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.55994,0.03164,0.07997],"force_p95":426.79412,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.39831,"mean_force":260.90784,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4475,0.02425,0.16631]},{"body_a":"peg_socket","body_b":"link6","contact_count":292.0,"contact_point_centroid":[0.56087,0.02487,0.07934],"force_p95":281.4514,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.09185,"mean_force":246.65564,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45229,0.02387,0.17216]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5609,0.0252,0.07941],"force_p95":265.54947,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.54947,"mean_force":265.54947,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44833,0.02429,0.16737]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55993,0.03169,0.07996],"force_p95":74.64578,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.64578,"mean_force":74.64578,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44833,0.02429,0.16737]}],"total_contact_groups":8},"final_pose_error":0.06696,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.48514,0.03255,0.0779],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1044.06487,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.4859,0.02543,0.15368],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07921,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":239.76065,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":654.0,"raw_peak_contact_force":1044.06487,"subtask_id":"approach_hole","tcp_end":[0.44833,0.02429,0.16737],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.48587,0.02535,0.15365],"object_pos_start":[0.4859,0.02543,0.15368],"object_to_goal_dist_end":0.07916,"object_to_goal_dist_start":0.07921,"object_z_max":0.15368,"peak_contact_force":265.54947,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":265.54947,"subtask_id":"approach_hole","tcp_end":[0.4483,0.02419,0.16732],"tcp_start":[0.44833,0.02429,0.16737],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49077,0.03194,0.1175],"object_pos_start":[0.48587,0.02535,0.15365],"object_to_goal_dist_end":0.05012,"object_to_goal_dist_start":0.07916,"object_z_max":0.16656,"peak_contact_force":356.23479,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":699.0,"raw_peak_contact_force":588.0534,"subtask_id":"insert_peg","tcp_end":[0.48514,0.03255,0.0779],"tcp_start":[0.4483,0.02419,0.16732],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.25166,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0451,"approach_1.arc_height":0.10771,"descend_1.contact_force_threshold":8.88935,"insert_1.insert_depth":0.08612,"insert_1.insert_speed":0.0305,"insert_1.pose_tolerance":0.01698},"optimized_scores":{"best_composite_score":0.62762,"best_fitness_score":0.62428,"best_task_score":0.85513},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":408.0,"contact_point_centroid":[0.54028,0.009,0.07962],"force_p95":372.18032,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1428.143,"mean_force":289.17606,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44176,0.00492,0.17059]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.4427,0.00497,0.07785],"force_p95":937.66448,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1111.14663,"mean_force":158.90593,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43893,0.00329,0.08955]},{"body_a":"peg_socket","body_b":"link6","contact_count":418.0,"contact_point_centroid":[0.54084,0.00145,0.07988],"force_p95":343.38752,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":958.22866,"mean_force":311.82309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45463,0.00204,0.19969]},{"body_a":"attachment","body_b":"peg_socket","contact_count":498.0,"contact_point_centroid":[0.49267,-0.00583,0.04992],"force_p95":491.22935,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":611.21669,"mean_force":472.63537,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48004,-0.01338,0.05014]},{"body_a":"peg_socket","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.5409,-0.00327,0.07995],"force_p95":458.34677,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.51597,"mean_force":369.30849,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44862,-0.00369,0.20704]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5409,-0.00286,0.07997],"force_p95":345.66453,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.66453,"mean_force":345.66453,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46133,-0.00276,0.21033]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.45094,0.01392,0.07996],"force_p95":310.38362,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.17306,"mean_force":168.30572,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44109,0.00342,0.08817]}],"total_contact_groups":7},"final_pose_error":0.05672,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.4868,-0.01409,0.05027],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1428.143,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.49114,-0.00283,0.18366],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10408,"object_to_goal_dist_start":0.26034,"object_z_max":0.34428,"peak_contact_force":319.96831,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":841.0,"raw_peak_contact_force":1428.143,"subtask_id":"approach_hole","tcp_end":[0.46133,-0.00276,0.21033],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.49117,-0.00281,0.1837],"object_pos_start":[0.49114,-0.00283,0.18366],"object_to_goal_dist_end":0.10412,"object_to_goal_dist_start":0.10408,"object_z_max":0.18366,"peak_contact_force":345.66453,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":345.66453,"subtask_id":"approach_hole","tcp_end":[0.46136,-0.00271,0.21038],"tcp_start":[0.46133,-0.00276,0.21033],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48747,-0.01344,0.09025],"object_pos_start":[0.49117,-0.00281,0.1837],"object_to_goal_dist_end":0.02104,"object_to_goal_dist_start":0.10412,"object_z_max":0.21238,"peak_contact_force":461.66868,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":515.0,"raw_peak_contact_force":611.21669,"subtask_id":"insert_peg","tcp_end":[0.4868,-0.01409,0.05027],"tcp_start":[0.46136,-0.00271,0.21038],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```