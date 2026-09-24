## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.2624 | 0.03 | ❌ rejected |
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9088 | 0.92 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9092 | 0.92 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9148 | 0.94 | ✅ accepted |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4187 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.262) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_phase
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.0
    tolerance: 0.01
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_phase
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_phase
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_phase** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0], tolerance=0.01
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_phase** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.03, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.262
- **task_score** (E): 0.031
- **fitness_score**: 0.259  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_phase | 1.00 | 1.00 | 0.2838 |
| contact_phase | 1.00 | 1.00 | 0.0401 |
| push_phase | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_phase | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_phase | contact | 1.00 / force_exceeded | (0.526, 0.082, 0.032)→(0.526, 0.044, 0.021) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 25309.350 | 0.245 |
| push_phase | push | 0.00 / guard_failure | (0.524, 0.039, 0.019)→(0.524, 0.039, 0.019) | (0.531, 0.007, 0.025)→(0.530, 0.002, 0.025) | 0.161→0.156 | 1.00 / 4.000 | 27.233 | 33.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.048
- lateral_force_integral: None
- approach_alignment: 0.424
- goal_progress: 0.048
- terminal_score: 0.048
- phase_score: 0.409
- phase_breakdown.approach_score: 0.819
- phase_breakdown.push_score: 0.039
- phase_breakdown.contact_score: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.265
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.048
- **Median Q (composite search score)**: 0.260
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.439


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62366,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.09404,"contact_phase.contact_force_threshold":3.32369,"contact_phase.contact_speed":0.04007,"push_phase.push_extra_distance":0.03016,"push_phase.push_force_guard_threshold":19.26282,"push_phase.push_speed":0.11999},"optimized_scores":{"best_composite_score":0.26836,"best_fitness_score":0.26502,"best_task_score":0.04836},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.55066,-0.01029,-5e-05],"force_p95":20.64862,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.23139,"mean_force":7.92956,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.54554,0.0351,0.01917]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.57643,0.01171,0.04991],"force_p95":35.1423,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.5268,"mean_force":16.98106,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.54417,0.03261,0.01852]},{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.55505,0.02409,0.04473],"force_p95":22.06966,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.20108,"mean_force":8.74194,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.54604,0.03609,0.01941]},{"body_a":"world","body_b":"push_box","contact_count":3832.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.52231,0.03844,0.16446]},{"body_a":"world","body_b":"push_box","contact_count":2360.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.54519,0.05727,0.02322]}],"total_contact_groups":5},"final_pose_error":0.18725,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55107,-0.00613,0.02483],"final_tcp_position":[0.54346,0.03087,0.01825],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":40.23139,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3832.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54657,0.07718,0.03124],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":590.0,"n_steps_budget":750.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":16.40396,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2360.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54753,0.0384,0.02019],"tcp_start":[0.54657,0.07718,0.03124],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":29.0,"n_steps_budget":1000.0,"object_pos_end":[0.55116,-0.00594,0.02485],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15288,"object_to_goal_dist_start":0.16043,"object_z_max":0.0252,"peak_contact_force":40.23139,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":66.0,"raw_peak_contact_force":40.23139,"subtask_id":"push","tcp_end":[0.54346,0.03087,0.01825],"tcp_start":[0.54355,0.03109,0.01829],"tcp_to_object_dist_end":0.03818,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49398,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.14653,"contact_phase.contact_force_threshold":3.16081,"contact_phase.contact_speed":0.02706,"push_phase.push_extra_distance":0.01324,"push_phase.push_force_guard_threshold":21.29916,"push_phase.push_speed":0.06221},"optimized_scores":{"best_composite_score":0.25853,"best_fitness_score":0.25519,"best_task_score":0.0361},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.55989,0.05201,0.05019],"force_p95":27.31746,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.64406,"mean_force":17.46261,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.52911,0.0698,0.019]},{"body_a":"world","body_b":"push_box","contact_count":47.0,"contact_point_centroid":[0.53745,0.02851,-6e-05],"force_p95":9.36116,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.63585,"mean_force":3.71943,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.5299,0.07154,0.01953]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.54125,0.06015,0.04783],"force_p95":15.05899,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.46781,"mean_force":6.51837,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.53013,0.07212,0.01968]},{"body_a":"world","body_b":"push_box","contact_count":3716.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.51458,0.05559,0.16385]},{"body_a":"world","body_b":"push_box","contact_count":3168.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.52918,0.0913,0.02292]}],"total_contact_groups":5},"final_pose_error":0.20333,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53458,0.03034,0.02497],"final_tcp_position":[0.52842,0.06787,0.01854],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3716.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53088,0.11132,0.03065],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3168.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53113,0.07397,0.02039],"tcp_start":[0.53088,0.11132,0.03065],"tcp_to_object_dist_end":0.0377,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.53461,0.03055,0.02495],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18384,"object_to_goal_dist_start":0.1905,"object_z_max":0.02537,"peak_contact_force":25.46673,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":65.0,"raw_peak_contact_force":27.64406,"subtask_id":"push","tcp_end":[0.52842,0.06787,0.01854],"tcp_start":[0.52851,0.0681,0.01861],"tcp_to_object_dist_end":0.03836,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64634,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.15544,"contact_phase.contact_force_threshold":2.6041,"contact_phase.contact_speed":0.02967,"push_phase.push_extra_distance":0.01237,"push_phase.push_force_guard_threshold":23.03577,"push_phase.push_speed":0.03108},"optimized_scores":{"best_composite_score":0.26021,"best_fitness_score":0.25688,"best_task_score":0.00847},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.5017,0.00589,0.02589],"force_p95":27.50038,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.16467,"mean_force":12.37298,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.4993,0.01784,0.021]},{"body_a":"world","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.50519,-0.01697,-1e-05],"force_p95":9.81104,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.02289,"mean_force":4.4126,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.4993,0.01783,0.021]},{"body_a":"world","body_b":"push_box","contact_count":3200.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.49931,0.02863,0.16614]},{"body_a":"world","body_b":"push_box","contact_count":3140.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.49812,0.03678,0.02488]}],"total_contact_groups":4},"final_pose_error":0.14942,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50437,-0.01991,0.02491],"final_tcp_position":[0.49884,0.01698,0.0205],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":33.16467,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3200.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50028,0.05779,0.03318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":18.10951,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3140.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49956,0.01816,0.02131],"tcp_start":[0.50028,0.05779,0.03318],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50438,-0.01978,0.02493],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13029,"object_to_goal_dist_start":0.13127,"object_z_max":0.02509,"peak_contact_force":16.0,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":47.0,"raw_peak_contact_force":33.16467,"subtask_id":"push","tcp_end":[0.49884,0.01698,0.0205],"tcp_start":[0.4989,0.01711,0.02058],"tcp_to_object_dist_end":0.03744,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```