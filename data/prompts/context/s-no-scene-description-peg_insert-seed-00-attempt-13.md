## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → insert | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | pose_tolerance | 5 | 0.5826 | 0.82 | ❌ rejected |
| 12 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.6646 | 0.86 | ❌ rejected |
| 11 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6625 | 0.89 | ❌ rejected |
| 10 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3299 | 0.82 | ❌ rejected |
| 9 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6972 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.583) — your mutation base

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

- **Composite score**: 0.583
- **task_score** (E): 0.823
- **fitness_score**: 0.333  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2156 |
| insert_1 | 0.00 | 1.00 | 0.0711 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / force_exceeded | (0.500, -0.000, 0.301)→(0.444, -0.000, 0.092) | (0.504, -0.000, 0.340)→(0.482, -0.000, 0.104) | 0.260→0.031 | 1.00 / 1.667 | 1025.064 | 1025.064 |
| insert_1 | insert | 0.00 / step_budget | (0.444, -0.000, 0.092)→(0.409, 0.000, 0.032) | (0.482, -0.000, 0.104)→(0.420, -0.000, 0.070) | 0.031→0.082 | 1.00 / 1.000 | 474.592 | 977.270 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.832
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.832
- phase_score: 0.006
- phase_breakdown.insert_peg_score: 0.000
- phase_breakdown.approach_hole_score: 0.021

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.337
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.832
- **Median Q (composite search score)**: 0.582
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.256


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89583,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0626,"approach_1.contact_force_threshold":10.74052,"insert_1.insert_depth":0.11862,"insert_1.insert_speed":0.03185,"insert_1.pose_tolerance":0.01496},"optimized_scores":{"best_composite_score":0.58664,"best_fitness_score":0.33664,"best_task_score":0.83226},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":822.0,"contact_point_centroid":[0.45114,-0.00757,0.07996],"force_p95":475.43394,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1046.70296,"mean_force":292.8368,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.42982,-0.00744,0.04741]},{"body_a":"peg_socket","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.54231,-0.00868,0.0775],"force_p95":819.74036,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":971.18479,"mean_force":266.86931,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44155,-0.00514,0.0949]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.45834,-0.00441,0.07983],"force_p95":911.87043,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.87043,"mean_force":911.87043,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45326,-0.00439,0.09377]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.53842,0.01208,0.07892],"force_p95":681.64307,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":744.73448,"mean_force":298.15784,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44168,-0.005,0.09459]},{"body_a":"peg_socket","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53955,-0.04848,0.07962],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44215,-0.00471,0.09379]}],"total_contact_groups":5},"final_pose_error":0.11189,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.42215,-0.00917,0.02881],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1046.70296,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":91.0,"n_steps_budget":600.0,"object_pos_end":[0.48849,-0.00455,0.10554],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02838,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":911.87043,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":911.87043,"subtask_id":"approach_hole","tcp_end":[0.45061,-0.00442,0.0927],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43252,-0.00935,0.06744],"object_pos_start":[0.48849,-0.00455,0.10554],"object_to_goal_dist_end":0.06927,"object_to_goal_dist_start":0.02838,"object_z_max":0.11179,"peak_contact_force":474.41839,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":866.0,"raw_peak_contact_force":1046.70296,"subtask_id":"insert_peg","tcp_end":[0.42215,-0.00917,0.02881],"tcp_start":[0.45061,-0.00442,0.0927],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86364,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09625,"approach_1.contact_force_threshold":8.99236,"insert_1.insert_depth":0.12254,"insert_1.insert_speed":0.03086,"insert_1.pose_tolerance":0.00818},"optimized_scores":{"best_composite_score":0.58198,"best_fitness_score":0.33198,"best_task_score":0.82117},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5436,0.00428,0.0787],"force_p95":1092.53141,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1092.53141,"mean_force":1092.53141,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44429,0.00676,0.0924]},{"body_a":"peg_socket","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53466,0.0048,0.07694],"force_p95":738.29918,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":943.45914,"mean_force":196.52635,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.43644,0.0071,0.0946]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.45023,0.00678,0.07928],"force_p95":847.83281,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":892.45559,"mean_force":446.2278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44562,0.00676,0.09284]},{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52994,0.00439,0.07881],"force_p95":649.84146,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":736.368,"mean_force":300.82106,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.43627,0.0071,0.09509]},{"body_a":"attachment","body_b":"peg_socket","contact_count":852.0,"contact_point_centroid":[0.44111,0.012,0.07996],"force_p95":465.68428,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":505.29449,"mean_force":257.49035,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.42076,0.01185,0.05209]}],"total_contact_groups":5},"final_pose_error":0.11567,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.41444,0.01615,0.03164],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1092.53141,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.48061,0.00697,0.10322],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03104,"object_to_goal_dist_start":0.26034,"object_z_max":0.34433,"peak_contact_force":1092.53141,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":1092.53141,"subtask_id":"approach_hole","tcp_end":[0.44224,0.00677,0.09195],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42376,0.01644,0.07053],"object_pos_start":[0.48061,0.00697,0.10322],"object_to_goal_dist_end":0.07857,"object_to_goal_dist_start":0.03104,"object_z_max":0.10797,"peak_contact_force":498.18878,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":903.0,"raw_peak_contact_force":943.45914,"subtask_id":"insert_peg","tcp_end":[0.41444,0.01615,0.03164],"tcp_start":[0.44224,0.00677,0.09195],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38298,"average_solve_count":47.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06705,"approach_1.contact_force_threshold":9.9518,"insert_1.insert_depth":0.10864,"insert_1.insert_speed":0.02535,"insert_1.pose_tolerance":0.01313},"optimized_scores":{"best_composite_score":0.5792,"best_fitness_score":0.3292,"best_task_score":0.81426},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54084,-0.00699,0.07987],"force_p95":1070.79069,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1070.79069,"mean_force":1070.79069,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44209,-0.00319,0.09288]},{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53125,-0.0073,0.07715],"force_p95":780.21852,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":941.64767,"mean_force":329.77716,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.43311,-0.00349,0.09536]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.44822,-0.00319,0.07956],"force_p95":849.7936,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":894.51958,"mean_force":447.25979,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44343,-0.00318,0.09334]},{"body_a":"attachment","body_b":"peg_socket","contact_count":872.0,"contact_point_centroid":[0.42124,-0.00547,0.07996],"force_p95":437.40358,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.23706,"mean_force":262.4892,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.39723,-0.00532,0.04958]}],"total_contact_groups":4},"final_pose_error":0.11111,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.39015,-0.00694,0.03476],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1070.79069,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":92.0,"n_steps_budget":600.0,"object_pos_end":[0.47823,-0.00331,0.1041],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03265,"object_to_goal_dist_start":0.26034,"object_z_max":0.34412,"peak_contact_force":1070.79069,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":1070.79069,"subtask_id":"approach_hole","tcp_end":[0.44,-0.00321,0.09234],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4028,-0.00712,0.07271],"object_pos_start":[0.47823,-0.00331,0.1041],"object_to_goal_dist_end":0.09774,"object_to_goal_dist_start":0.03265,"object_z_max":0.11211,"peak_contact_force":451.1677,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":895.0,"raw_peak_contact_force":941.64767,"subtask_id":"insert_peg","tcp_end":[0.39015,-0.00694,0.03476],"tcp_start":[0.44,-0.00321,0.09234],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```