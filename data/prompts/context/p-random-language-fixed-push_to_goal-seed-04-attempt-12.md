## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9092 | 0.92 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9148 | 0.94 | ✅ accepted |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4187 | 0.80 | ❌ rejected |
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4173 | 0.79 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.79 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.909) — your mutation base

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

- **Composite score**: 0.909
- **task_score** (E): 0.921
- **fitness_score**: 0.806  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_phase | 1.00 | 1.00 | 0.2839 |
| contact_phase | 1.00 | 1.00 | 0.0401 |
| push_phase | 1.00 | 1.00 | 0.1527 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_phase | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_phase | contact | 1.00 / force_exceeded | (0.526, 0.082, 0.032)→(0.526, 0.044, 0.021) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 25306.172 | 0.245 |
| push_phase | push | 1.00 / step_budget | (0.526, 0.044, 0.021)→(0.500, -0.106, 0.022) | (0.531, 0.007, 0.025)→(0.508, -0.143, 0.027) | 0.161→0.013 | 1.00 / 3.000 | 31.089 | 72.530 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.964
- lateral_force_integral: None
- approach_alignment: 0.677
- goal_progress: 0.961
- terminal_score: 0.961
- phase_score: 0.731
- phase_breakdown.approach_score: 0.819
- phase_breakdown.push_score: 0.676
- phase_breakdown.contact_score: 0.764

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.823
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.961
- **Median Q (composite search score)**: 0.925
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21429,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.10286,"contact_phase.contact_force_threshold":2.48686,"contact_phase.contact_speed":0.02411,"push_phase.push_speed":0.05671},"optimized_scores":{"best_composite_score":0.87635,"best_fitness_score":0.77301,"best_task_score":0.84206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":500.0,"contact_point_centroid":[0.54617,-0.06967,0.05369],"force_p95":60.01433,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.52866,"mean_force":35.84241,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51823,-0.05184,0.02057]},{"body_a":"world","body_b":"push_box","contact_count":1114.0,"contact_point_centroid":[0.53847,-0.09249,-0.00015],"force_p95":45.20504,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.88902,"mean_force":23.28765,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.52065,-0.04318,0.02002]},{"body_a":"attachment","body_b":"push_box","contact_count":502.0,"contact_point_centroid":[0.53422,-0.06179,0.05117],"force_p95":53.59765,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.98242,"mean_force":30.81652,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51836,-0.05155,0.0206]},{"body_a":"world","body_b":"push_box","contact_count":3792.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.52236,0.0385,0.16425]},{"body_a":"world","body_b":"push_box","contact_count":3668.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.54519,0.05647,0.02282]}],"total_contact_groups":5},"final_pose_error":0.01494,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5232,-0.14103,0.02981],"final_tcp_position":[0.50411,-0.10565,0.02438],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":65.52866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3792.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54659,0.07725,0.031],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":13.65735,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3668.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54753,0.0384,0.02014],"tcp_start":[0.54659,0.07725,0.031],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.5232,-0.14103,0.02981],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02534,"object_to_goal_dist_start":0.16043,"object_z_max":0.02989,"peak_contact_force":62.94198,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2116.0,"raw_peak_contact_force":65.52866,"subtask_id":"push","tcp_end":[0.50411,-0.10565,0.02438],"tcp_start":[0.54753,0.0384,0.02014],"tcp_to_object_dist_end":0.04056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45283,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.151,"contact_phase.contact_force_threshold":2.83259,"contact_phase.contact_speed":0.03606,"push_phase.push_speed":0.04264},"optimized_scores":{"best_composite_score":0.92491,"best_fitness_score":0.82158,"best_task_score":0.96033},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":690.0,"contact_point_centroid":[0.52832,-0.02694,0.04619],"force_p95":54.19363,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.81084,"mean_force":24.24185,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51411,-0.0161,0.01963]},{"body_a":"world","body_b":"push_box","contact_count":1023.0,"contact_point_centroid":[0.52817,-0.06215,-0.00012],"force_p95":45.49334,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.57309,"mean_force":22.48844,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.5156,-0.00684,0.01942]},{"body_a":"push_box","body_b":"link7","contact_count":636.0,"contact_point_centroid":[0.53826,-0.03426,0.05367],"force_p95":42.33092,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.35839,"mean_force":19.81361,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51449,-0.01386,0.01962]},{"body_a":"world","body_b":"push_box","contact_count":3624.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.5146,0.05557,0.16391]},{"body_a":"world","body_b":"push_box","contact_count":2448.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.52924,0.09154,0.02303]}],"total_contact_groups":5},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50243,-0.14316,0.02709],"final_tcp_position":[0.49842,-0.10611,0.02009],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3624.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5309,0.11132,0.03065],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":612.0,"n_steps_budget":810.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2448.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53113,0.07399,0.02039],"tcp_start":[0.5309,0.11132,0.03065],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.50243,-0.14316,0.02709],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.00756,"object_to_goal_dist_start":0.1905,"object_z_max":0.02887,"peak_contact_force":29.61196,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2349.0,"raw_peak_contact_force":57.81084,"subtask_id":"push","tcp_end":[0.49842,-0.10611,0.02009],"tcp_start":[0.53113,0.07399,0.02039],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3125,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.13946,"contact_phase.contact_force_threshold":3.79111,"contact_phase.contact_speed":0.04133,"push_phase.push_speed":0.05935},"optimized_scores":{"best_composite_score":0.92625,"best_fitness_score":0.82292,"best_task_score":0.96099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":782.0,"contact_point_centroid":[0.51636,-0.09453,-0.0002],"force_p95":80.00851,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.24992,"mean_force":37.40954,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49891,-0.04283,0.02126]},{"body_a":"attachment","body_b":"push_box","contact_count":540.0,"contact_point_centroid":[0.51618,-0.0496,0.04864],"force_p95":71.66194,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.02364,"mean_force":40.01531,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49903,-0.03913,0.02131]},{"body_a":"push_box","body_b":"link7","contact_count":510.0,"contact_point_centroid":[0.5257,-0.06173,0.05357],"force_p95":53.8769,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.30161,"mean_force":33.39422,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49908,-0.03987,0.02134]},{"body_a":"world","body_b":"push_box","contact_count":3360.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.49928,0.0286,0.16627]},{"body_a":"world","body_b":"push_box","contact_count":2256.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.49817,0.03727,0.02517]}],"total_contact_groups":5},"final_pose_error":0.01485,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4983,-0.14518,0.02533],"final_tcp_position":[0.49681,-0.10624,0.02041],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":94.24992,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3360.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50029,0.05775,0.03334],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":564.0,"n_steps_budget":720.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":11.32188,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49956,0.01816,0.02134],"tcp_start":[0.50029,0.05775,0.03334],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.4983,-0.14518,0.02533],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00512,"object_to_goal_dist_start":0.13127,"object_z_max":0.03232,"peak_contact_force":0.7128,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1832.0,"raw_peak_contact_force":94.24992,"subtask_id":"push","tcp_end":[0.49681,-0.10624,0.02041],"tcp_start":[0.49956,0.01816,0.02134],"tcp_to_object_dist_end":0.03928,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```