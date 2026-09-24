## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4540 | 0.64 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4710 | 0.73 | ❌ rejected |
| 5 | approach → contact → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.4194 | 0.05 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ❌ rejected |

**Proposal policy**: task_score is 0.64 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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

## Current Skill (Q=0.454) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.454
- **task_score** (E): 0.641
- **fitness_score**: 0.664  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2819 |
| contact_1 | 1.00 | 1.00 | 0.0493 |
| push_1 | 1.00 | 1.00 | 0.1278 |
| retract_1 | 0.00 | 1.00 | 0.1666 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.077, 0.034) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.077, 0.034)→(0.509, 0.030, 0.021) | (0.513, 0.002, 0.025)→(0.516, -0.007, 0.025) | 0.160→0.152 | 1.00 / 4.000 | 5.401 | 11.071 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.021)→(0.504, -0.092, 0.026) | (0.516, -0.007, 0.025)→(0.512, -0.115, 0.029) | 0.152→0.057 | 1.00 / 3.333 | 81.238 | 110.285 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.092, 0.026)→(0.497, 0.058, 0.099) | (0.512, -0.115, 0.029)→(0.507, -0.110, 0.025) | 0.057→0.058 | 1.00 / 4.000 | 0.245 | 58.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.905
- lateral_force_integral: None
- approach_alignment: 0.444
- goal_progress: 0.681
- terminal_score: 0.681
- phase_score: 0.844
- phase_breakdown.contact_score: 0.881
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.832

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.779
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.681
- **Median Q (composite search score)**: 0.431
- **K-run variance**: 0.0074
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.262


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26887,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0423,"contact_1.speed":0.04467,"push_1.push_depth":0.0958},"optimized_scores":{"best_composite_score":0.56881,"best_fitness_score":0.77881,"best_task_score":0.68059},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1342.0,"contact_point_centroid":[0.45964,-0.1144,-7e-05],"force_p95":42.76072,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.40176,"mean_force":7.94668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47239,-0.07492,0.0195]},{"body_a":"attachment","body_b":"push_box","contact_count":650.0,"contact_point_centroid":[0.47334,-0.07167,0.03286],"force_p95":31.44389,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.34746,"mean_force":11.33646,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46704,-0.06026,0.01962]},{"body_a":"push_box","body_b":"link7","contact_count":245.0,"contact_point_centroid":[0.48066,-0.0452,0.05068],"force_p95":27.80451,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.89321,"mean_force":20.69523,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45312,-0.02118,0.02027]},{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.45089,-0.0104,0.02978],"force_p95":11.32273,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.92714,"mean_force":4.58464,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44608,0.00152,0.02245]},{"body_a":"world","body_b":"push_box","contact_count":2436.0,"contact_point_centroid":[0.45053,-0.03257,-1e-05],"force_p95":2.00158,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.35025,"mean_force":0.44485,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44578,0.02191,0.02641]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47678,-0.01487,0.04983],"force_p95":4.66104,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.66104,"mean_force":4.66104,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44625,-0.00293,0.02167]},{"body_a":"world","body_b":"push_box","contact_count":3998.0,"contact_point_centroid":[0.45905,-0.14749,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60559,"mean_force":0.24569,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49139,-0.05114,0.05131]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]}],"total_contact_groups":8},"final_pose_error":0.14192,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45905,-0.1475,0.02499],"final_tcp_position":[0.49325,0.02344,0.08615],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":57.40176,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":656.0,"n_steps_budget":750.0,"object_pos_end":[0.45162,-0.03983,0.02493],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12032,"object_to_goal_dist_start":0.12843,"object_z_max":0.02518,"peak_contact_force":6.36389,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2542.0,"raw_peak_contact_force":15.92714,"tcp_end":[0.44626,-0.00298,0.02166],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.45913,-0.14727,0.02496],"object_pos_start":[0.45162,-0.03983,0.02493],"object_to_goal_dist_end":0.04096,"object_to_goal_dist_start":0.12032,"object_z_max":0.03095,"peak_contact_force":0.66957,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2237.0,"raw_peak_contact_force":57.40176,"tcp_end":[0.49334,-0.12862,0.01983],"tcp_start":[0.44626,-0.00298,0.02166],"tcp_to_object_dist_end":0.03929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45905,-0.1475,0.02499],"object_pos_start":[0.45913,-0.14727,0.02496],"object_to_goal_dist_end":0.04102,"object_to_goal_dist_start":0.04096,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3998.0,"raw_peak_contact_force":0.60559,"tcp_end":[0.49325,0.02344,0.08615],"tcp_start":[0.49334,-0.12862,0.01983],"tcp_to_object_dist_end":0.18474,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33831,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06064,"contact_1.speed":0.02898,"push_1.push_depth":0.09991},"optimized_scores":{"best_composite_score":0.43128,"best_fitness_score":0.64128,"best_task_score":0.62652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":828.0,"contact_point_centroid":[0.56339,-0.04514,0.05412],"force_p95":127.63631,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.64456,"mean_force":83.64277,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52771,-0.0311,0.0242]},{"body_a":"world","body_b":"push_box","contact_count":1669.0,"contact_point_centroid":[0.55748,-0.07655,-0.00036],"force_p95":94.31221,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.55091,"mean_force":52.97836,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52791,-0.03053,0.02416]},{"body_a":"attachment","body_b":"push_box","contact_count":829.0,"contact_point_centroid":[0.54668,-0.03936,0.05413],"force_p95":84.24285,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.28002,"mean_force":52.25737,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52775,-0.03101,0.0242]},{"body_a":"world","body_b":"push_box","contact_count":3645.0,"contact_point_centroid":[0.53677,-0.10221,-3e-05],"force_p95":0.42148,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.33924,"mean_force":0.5414,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50282,-0.00746,0.06688]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.55115,-0.09405,0.05717],"force_p95":62.5037,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.876,"mean_force":27.11495,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50891,-0.08695,0.03116]},{"body_a":"attachment","body_b":"push_box","contact_count":68.0,"contact_point_centroid":[0.53349,-0.0885,0.06209],"force_p95":41.89988,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.77316,"mean_force":15.81666,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50832,-0.08443,0.03175]},{"body_a":"attachment","body_b":"push_box","contact_count":221.0,"contact_point_centroid":[0.55462,0.0217,0.04123],"force_p95":6.11657,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.95778,"mean_force":2.84716,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54753,0.03367,0.02112]},{"body_a":"world","body_b":"push_box","contact_count":3378.0,"contact_point_centroid":[0.55339,-0.00163,-1e-05],"force_p95":2.17155,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.80263,"mean_force":0.44273,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54463,0.05331,0.0263]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52172,0.03756,0.16746]}],"total_contact_groups":9},"final_pose_error":0.10216,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53614,-0.10221,0.02499],"final_tcp_position":[0.50014,0.06049,0.10076],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":140.64456,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54548,0.07546,0.03715],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.55642,-0.00803,0.02507],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15277,"object_to_goal_dist_start":0.16043,"object_z_max":0.02515,"peak_contact_force":4.16371,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3599.0,"raw_peak_contact_force":7.95778,"tcp_end":[0.54832,0.02874,0.01989],"tcp_start":[0.54548,0.07546,0.03715],"tcp_to_object_dist_end":0.03801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":837.0,"n_steps_budget":930.0,"object_pos_end":[0.54264,-0.11444,0.03119],"object_pos_start":[0.55642,-0.00803,0.02507],"object_to_goal_dist_end":0.05586,"object_to_goal_dist_start":0.15277,"object_z_max":0.0312,"peak_contact_force":126.16546,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3326.0,"raw_peak_contact_force":140.64456,"tcp_end":[0.51016,-0.0914,0.03005],"tcp_start":[0.54832,0.02874,0.01989],"tcp_to_object_dist_end":0.03984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53614,-0.10221,0.02499],"object_pos_start":[0.54264,-0.11444,0.03119],"object_to_goal_dist_end":0.05991,"object_to_goal_dist_start":0.05586,"object_z_max":0.03447,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3767.0,"raw_peak_contact_force":83.33924,"tcp_end":[0.50014,0.06049,0.10076],"tcp_start":[0.51016,-0.0914,0.03005],"tcp_to_object_dist_end":0.18306,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76543,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08972,"contact_1.speed":0.0403,"push_1.push_depth":0.1},"optimized_scores":{"best_composite_score":0.36182,"best_fitness_score":0.57182,"best_task_score":0.61503},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":805.0,"contact_point_centroid":[0.55088,-0.01078,0.0544],"force_p95":117.28298,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.81,"mean_force":77.72319,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51834,0.00505,0.02367]},{"body_a":"attachment","body_b":"push_box","contact_count":806.0,"contact_point_centroid":[0.53723,-0.00359,0.05236],"force_p95":101.0316,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.4337,"mean_force":55.40657,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51836,0.00515,0.02367]},{"body_a":"world","body_b":"push_box","contact_count":1506.0,"contact_point_centroid":[0.54639,-0.04671,-0.00033],"force_p95":81.43387,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.86534,"mean_force":53.68334,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51785,0.00211,0.02401]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.55018,-0.06054,0.05582],"force_p95":82.53778,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.09417,"mean_force":38.19159,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50713,-0.05201,0.03053]},{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.52803,-0.05423,0.05958],"force_p95":61.40489,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.77184,"mean_force":20.31031,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5062,-0.04808,0.03179]},{"body_a":"world","body_b":"push_box","contact_count":3651.0,"contact_point_centroid":[0.52655,-0.08131,-3e-05],"force_p95":0.47647,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.55033,"mean_force":0.49628,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50112,0.02458,0.0715]},{"body_a":"attachment","body_b":"push_box","contact_count":144.0,"contact_point_centroid":[0.53801,0.05741,0.03795],"force_p95":6.90986,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.32864,"mean_force":2.89757,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53126,0.06937,0.02052]},{"body_a":"world","body_b":"push_box","contact_count":2450.0,"contact_point_centroid":[0.53668,0.03481,-1e-05],"force_p95":2.07561,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.75868,"mean_force":0.42237,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52919,0.08932,0.02349]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51447,0.05539,0.16429]}],"total_contact_groups":9},"final_pose_error":0.07245,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52579,-0.08135,0.02499],"final_tcp_position":[0.49881,0.08969,0.10986],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":132.81,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53083,0.111,0.03141],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.53971,0.02792,0.02505],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1823,"object_to_goal_dist_start":0.1905,"object_z_max":0.0251,"peak_contact_force":5.67618,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2594.0,"raw_peak_contact_force":9.32864,"tcp_end":[0.53185,0.06471,0.01995],"tcp_start":[0.53083,0.111,0.03141],"tcp_to_object_dist_end":0.03797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":811.0,"n_steps_budget":900.0,"object_pos_end":[0.53453,-0.0834,0.03142],"object_pos_start":[0.53971,0.02792,0.02505],"object_to_goal_dist_end":0.07529,"object_to_goal_dist_start":0.1823,"object_z_max":0.03142,"peak_contact_force":116.87956,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3117.0,"raw_peak_contact_force":132.81,"tcp_end":[0.50798,-0.05522,0.02928],"tcp_start":[0.53185,0.06471,0.01995],"tcp_to_object_dist_end":0.03878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52579,-0.08135,0.02499],"object_pos_start":[0.53453,-0.0834,0.03142],"object_to_goal_dist_end":0.07334,"object_to_goal_dist_start":0.07529,"object_z_max":0.03511,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3762.0,"raw_peak_contact_force":92.09417,"tcp_end":[0.49881,0.08969,0.10986],"tcp_start":[0.50798,-0.05522,0.02928],"tcp_to_object_dist_end":0.19284,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```