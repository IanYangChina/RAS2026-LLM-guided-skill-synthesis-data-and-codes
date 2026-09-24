## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | time_limit | time_limit | 4 | 0.3879 | 0.40 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | time_limit | time_limit | 4 | 0.3738 | 0.40 | ✅ accepted |
| 4 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | force_exceeded | time_limit | 4 | 0.0484 | 0.00 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | force_exceeded | time_limit | 3 | -0.0342 | 0.00 | ✅ accepted |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.388) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: contact_object
  anchor: object
  weight: 0.3
- id: move_to_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_pre_contact
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.04
    offset_along_axis:
      distance: 0.07
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact_object
- id: contact_approach
  type: contact
  generator: linear_cartesian
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
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: contact_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
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
      distance: 0.5
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.5
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: move_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_contact** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.04], offset_along_axis={axis=task_goal_direction, distance=0.07, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_approach** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.5, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.388
- **task_score** (E): 0.397
- **fitness_score**: 0.618  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_contact | 1.00 | 1.00 | 0.2476 |
| contact_approach | 1.00 | 1.00 | 0.0729 |
| push_to_goal | 1.00 | 1.00 | 0.1737 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_contact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.086, 0.072) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_approach | contact | 1.00 / time_limit | (0.521, 0.086, 0.072)→(0.528, 0.018, 0.047) | (0.519, 0.022, 0.025)→(0.521, 0.012, 0.024) | 0.173→0.164 | 1.00 / 5.000 | 198.512 | 204.807 |
| push_to_goal | push | 1.00 / time_limit | (0.528, 0.018, 0.047)→(0.499, -0.152, 0.033) | (0.521, 0.012, 0.024)→(0.511, -0.045, 0.025) | 0.164→0.106 | 1.00 / 4.000 | 0.245 | 130.385 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.490
- lateral_force_integral: None
- approach_alignment: 0.747
- goal_progress: 0.489
- terminal_score: 0.489
- phase_score: 0.808
- phase_breakdown.move_to_goal_score: 0.887
- phase_breakdown.contact_object_score: 0.624

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.680
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.489
- **Median Q (composite search score)**: 0.360
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.407


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64286,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_contact.approach_speed":0.09969,"contact_approach.contact_speed":0.04916,"push_to_goal.push_distance":0.69005,"push_to_goal.push_speed":0.02737},"optimized_scores":{"best_composite_score":0.35959,"best_fitness_score":0.58959,"best_task_score":0.35823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":650.0,"contact_point_centroid":[0.55111,0.05033,0.04797],"force_p95":194.35643,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.85329,"mean_force":114.90108,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.54017,0.05322,0.04894]},{"body_a":"attachment","body_b":"push_box","contact_count":479.0,"contact_point_centroid":[0.54864,0.00045,0.0479],"force_p95":117.00447,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.77688,"mean_force":86.08034,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54,-0.00564,0.04806]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.537,0.03319,-0.0002],"force_p95":81.24146,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.20788,"mean_force":19.00294,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.53952,0.06433,0.05224]},{"body_a":"world","body_b":"push_box","contact_count":3003.0,"contact_point_centroid":[0.53034,-0.01702,-0.00016],"force_p95":81.13511,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.33579,"mean_force":14.06217,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52184,-0.06711,0.04151]},{"body_a":"world","body_b":"push_box","contact_count":3500.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_pre_contact","phase_type":"approach","tcp_position_centroid":[0.52103,0.04989,0.18373]}],"total_contact_groups":5},"final_pose_error":0.50956,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52548,-0.03043,0.02499],"final_tcp_position":[0.50031,-0.15065,0.0363],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":201.85329,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":875.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3500.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.54388,0.09998,0.07033],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53845,0.02582,0.02395],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.17998,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":194.95906,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4646.0,"raw_peak_contact_force":201.85329,"subtask_id":"contact_object","tcp_end":[0.54583,0.03099,0.04633],"tcp_start":[0.54388,0.09998,0.07033],"tcp_to_object_dist_end":0.02413,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52548,-0.03043,0.02499],"object_pos_start":[0.53845,0.02582,0.02395],"object_to_goal_dist_end":0.12226,"object_to_goal_dist_start":0.17998,"object_z_max":0.03545,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3482.0,"raw_peak_contact_force":119.77688,"subtask_id":"move_to_goal","tcp_end":[0.50031,-0.15065,0.0363],"tcp_start":[0.54583,0.03099,0.04633],"tcp_to_object_dist_end":0.12335,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16384,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_contact.approach_speed":0.04763,"contact_approach.contact_speed":0.04903,"push_to_goal.push_distance":0.19408,"push_to_goal.push_speed":0.07965},"optimized_scores":{"best_composite_score":0.45042,"best_fitness_score":0.68042,"best_task_score":0.48862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":557.0,"contact_point_centroid":[0.51764,-0.0045,0.048],"force_p95":192.17332,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":209.55061,"mean_force":116.38481,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.50626,-0.00248,0.04908]},{"body_a":"attachment","body_b":"push_box","contact_count":667.0,"contact_point_centroid":[0.52333,-0.05722,0.04596],"force_p95":142.50053,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.65856,"mean_force":108.53578,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51427,-0.06298,0.04593]},{"body_a":"world","body_b":"push_box","contact_count":2778.0,"contact_point_centroid":[0.50617,-0.06301,-0.00029],"force_p95":122.94736,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.3844,"mean_force":26.50333,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50832,-0.09074,0.03942]},{"body_a":"world","body_b":"push_box","contact_count":3998.0,"contact_point_centroid":[0.50532,-0.02145,-0.00018],"force_p95":77.70357,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.29293,"mean_force":16.51562,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.50335,0.012,0.05407]},{"body_a":"world","body_b":"push_box","contact_count":3236.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_pre_contact","phase_type":"approach","tcp_position_centroid":[0.50056,0.02367,0.1863]}],"total_contact_groups":5},"final_pose_error":0.067,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4995,-0.08287,0.02499],"final_tcp_position":[0.49751,-0.15486,0.02744],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":209.55061,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":809.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3236.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.50304,0.04792,0.07335],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50768,-0.02812,0.02393],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12213,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":199.08786,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4555.0,"raw_peak_contact_force":209.55061,"subtask_id":"contact_object","tcp_end":[0.51375,-0.022,0.04649],"tcp_start":[0.50304,0.04792,0.07335],"tcp_to_object_dist_end":0.02415,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4995,-0.08287,0.02499],"object_pos_start":[0.50768,-0.02812,0.02393],"object_to_goal_dist_end":0.06713,"object_to_goal_dist_start":0.12213,"object_z_max":0.03537,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3445.0,"raw_peak_contact_force":147.65856,"subtask_id":"move_to_goal","tcp_end":[0.49751,-0.15486,0.02744],"tcp_start":[0.51375,-0.022,0.04649],"tcp_to_object_dist_end":0.07206,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43949,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_contact.approach_speed":0.06393,"contact_approach.contact_speed":0.04617,"push_to_goal.push_distance":0.7304,"push_to_goal.push_speed":0.05159},"optimized_scores":{"best_composite_score":0.3538,"best_fitness_score":0.5838,"best_task_score":0.3446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":609.0,"contact_point_centroid":[0.52792,0.06257,0.04808],"force_p95":190.30103,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.01805,"mean_force":109.71516,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.51673,0.06511,0.04918]},{"body_a":"attachment","body_b":"push_box","contact_count":468.0,"contact_point_centroid":[0.53102,0.01337,0.0478],"force_p95":120.47943,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.7181,"mean_force":90.51101,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52219,0.00758,0.04825]},{"body_a":"world","body_b":"push_box","contact_count":3060.0,"contact_point_centroid":[0.51263,-0.00597,-0.00016],"force_p95":90.71109,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.98709,"mean_force":14.17954,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51132,-0.05924,0.04183]},{"body_a":"world","body_b":"push_box","contact_count":3994.0,"contact_point_centroid":[0.5157,0.04465,-0.00018],"force_p95":75.34126,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.27888,"mean_force":17.02863,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.51479,0.07688,0.05299]},{"body_a":"world","body_b":"push_box","contact_count":3664.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_pre_contact","phase_type":"approach","tcp_position_centroid":[0.50686,0.05536,0.18417]}],"total_contact_groups":5},"final_pose_error":0.54068,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50905,-0.02039,0.02499],"final_tcp_position":[0.49967,-0.15078,0.03656],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":203.01805,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":916.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3664.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.51569,0.11112,0.07097],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51763,0.03815,0.02397],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18897,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":201.49017,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4603.0,"raw_peak_contact_force":203.01805,"subtask_id":"contact_object","tcp_end":[0.52341,0.0458,0.04669],"tcp_start":[0.51569,0.11112,0.07097],"tcp_to_object_dist_end":0.02466,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50905,-0.02039,0.02499],"object_pos_start":[0.51763,0.03815,0.02397],"object_to_goal_dist_end":0.12992,"object_to_goal_dist_start":0.18897,"object_z_max":0.03522,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3528.0,"raw_peak_contact_force":123.7181,"subtask_id":"move_to_goal","tcp_end":[0.49967,-0.15078,0.03656],"tcp_start":[0.52341,0.0458,0.04669],"tcp_to_object_dist_end":0.13123,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```