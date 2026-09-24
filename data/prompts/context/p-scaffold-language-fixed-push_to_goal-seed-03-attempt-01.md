## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4584 | 0.64 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4526 | 0.63 | ✅ accepted |

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

## Current Skill (Q=0.458) — your mutation base

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

- **Composite score**: 0.458
- **task_score** (E): 0.642
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2843 |
| contact_1 | 1.00 | 1.00 | 0.0495 |
| push_1 | 1.00 | 1.00 | 0.1266 |
| retract_1 | 0.00 | 1.00 | 0.1662 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.030, 0.020) | (0.513, 0.002, 0.025)→(0.516, -0.007, 0.025) | 0.160→0.152 | 1.00 / 4.000 | 6.033 | 9.579 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.020)→(0.504, -0.091, 0.026) | (0.516, -0.007, 0.025)→(0.511, -0.114, 0.029) | 0.152→0.057 | 1.00 / 4.000 | 80.396 | 108.766 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.091, 0.026)→(0.497, 0.058, 0.099) | (0.511, -0.114, 0.029)→(0.506, -0.111, 0.025) | 0.057→0.057 | 1.00 / 4.000 | 0.245 | 58.464 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.871
- lateral_force_integral: None
- approach_alignment: 0.441
- goal_progress: 0.653
- terminal_score: 0.653
- phase_score: 0.851
- phase_breakdown.contact_score: 0.885
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.843

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.772
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.653
- **Median Q (composite search score)**: 0.445
- **K-run variance**: 0.0064
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.253


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28718,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05834,"contact_1.speed":0.03877,"push_1.push_depth":0.09298},"optimized_scores":{"best_composite_score":0.5619,"best_fitness_score":0.7719,"best_task_score":0.65326},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1379.0,"contact_point_centroid":[0.4585,-0.11288,-8e-05],"force_p95":44.22098,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.21984,"mean_force":7.90758,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4728,-0.07484,0.01946]},{"body_a":"attachment","body_b":"push_box","contact_count":633.0,"contact_point_centroid":[0.47352,-0.07055,0.03318],"force_p95":31.93951,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.66453,"mean_force":11.75392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46702,-0.05917,0.01963]},{"body_a":"push_box","body_b":"link7","contact_count":249.0,"contact_point_centroid":[0.48093,-0.04607,0.05061],"force_p95":29.20997,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.7572,"mean_force":20.80688,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45332,-0.02143,0.02026]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48634,-0.1355,0.02312],"force_p95":12.06936,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.06936,"mean_force":12.06936,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49334,-0.12633,0.01984]},{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.45327,-0.01087,0.03332],"force_p95":7.89304,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.62473,"mean_force":3.7167,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44609,0.00105,0.02236]},{"body_a":"world","body_b":"push_box","contact_count":2807.0,"contact_point_centroid":[0.45046,-0.03288,-1e-05],"force_p95":2.24377,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.85183,"mean_force":0.4525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44574,0.02163,0.02631]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.47668,-0.01491,0.04987],"force_p95":6.94933,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.69871,"mean_force":5.79895,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44625,-0.00315,0.02162]},{"body_a":"world","body_b":"push_box","contact_count":3979.0,"contact_point_centroid":[0.45596,-0.14334,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.84439,"mean_force":0.24912,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49139,-0.04883,0.05161]},{"body_a":"world","body_b":"push_box","contact_count":3696.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47372,0.02261,0.16667]}],"total_contact_groups":9},"final_pose_error":0.14062,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45597,-0.14334,0.02499],"final_tcp_position":[0.49326,0.02481,0.08632],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":59.21984,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44889,0.04564,0.03442],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":764.0,"n_steps_budget":870.0,"object_pos_end":[0.45182,-0.04022,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11989,"object_to_goal_dist_start":0.12843,"object_z_max":0.0251,"peak_contact_force":7.71557,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2959.0,"raw_peak_contact_force":11.62473,"tcp_end":[0.44629,-0.00342,0.02159],"tcp_start":[0.44889,0.04564,0.03442],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.45687,-0.14236,0.025],"object_pos_start":[0.45182,-0.04022,0.02499],"object_to_goal_dist_end":0.0438,"object_to_goal_dist_start":0.11989,"object_z_max":0.03077,"peak_contact_force":3.06926,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2261.0,"raw_peak_contact_force":59.21984,"tcp_end":[0.49334,-0.12633,0.01984],"tcp_start":[0.44629,-0.00342,0.02159],"tcp_to_object_dist_end":0.04017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45597,-0.14334,0.02499],"object_pos_start":[0.45687,-0.14236,0.025],"object_to_goal_dist_end":0.04453,"object_to_goal_dist_start":0.0438,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3980.0,"raw_peak_contact_force":12.06936,"tcp_end":[0.49326,0.02481,0.08632],"tcp_start":[0.49334,-0.12633,0.01984],"tcp_to_object_dist_end":0.18283,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77515,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07872,"contact_1.speed":0.04185,"push_1.push_depth":0.09873},"optimized_scores":{"best_composite_score":0.44544,"best_fitness_score":0.65544,"best_task_score":0.651},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":796.0,"contact_point_centroid":[0.56235,-0.04551,0.05396],"force_p95":122.68349,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.87242,"mean_force":80.09764,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52738,-0.03014,0.02381]},{"body_a":"world","body_b":"push_box","contact_count":1568.0,"contact_point_centroid":[0.55701,-0.07775,-0.00035],"force_p95":91.55953,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.22509,"mean_force":52.0135,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52733,-0.03053,0.02391]},{"body_a":"attachment","body_b":"push_box","contact_count":796.0,"contact_point_centroid":[0.54681,-0.03857,0.05456],"force_p95":84.37715,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.47334,"mean_force":50.95964,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5274,-0.0301,0.02382]},{"body_a":"world","body_b":"push_box","contact_count":3690.0,"contact_point_centroid":[0.53612,-0.1069,-3e-05],"force_p95":0.25764,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.23546,"mean_force":0.50197,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50286,-0.0069,0.06648]},{"body_a":"push_box","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.55009,-0.09538,0.05744],"force_p95":65.1278,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.76609,"mean_force":27.52056,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.509,-0.08553,0.03091]},{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.53368,-0.08756,0.06182],"force_p95":44.61941,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.44895,"mean_force":16.72338,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5085,-0.08341,0.03139]},{"body_a":"attachment","body_b":"push_box","contact_count":134.0,"contact_point_centroid":[0.554,0.02219,0.0383],"force_p95":6.91305,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.52062,"mean_force":3.04774,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54764,0.03415,0.02021]},{"body_a":"world","body_b":"push_box","contact_count":2450.0,"contact_point_centroid":[0.55333,-0.00081,-1e-05],"force_p95":1.69962,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.75377,"mean_force":0.41907,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54522,0.05504,0.02308]},{"body_a":"world","body_b":"push_box","contact_count":3900.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03848,0.16433]}],"total_contact_groups":9},"final_pose_error":0.10143,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5356,-0.10679,0.02499],"final_tcp_position":[0.50014,0.06131,0.10078],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":138.87242,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3900.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07724,0.03104],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.55611,-0.00732,0.0249],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15332,"object_to_goal_dist_start":0.16043,"object_z_max":0.02512,"peak_contact_force":6.29195,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2584.0,"raw_peak_contact_force":9.52062,"tcp_end":[0.54828,0.02946,0.01966],"tcp_start":[0.5466,0.07724,0.03104],"tcp_to_object_dist_end":0.03797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":808.0,"n_steps_budget":900.0,"object_pos_end":[0.54115,-0.11463,0.03118],"object_pos_start":[0.55611,-0.00732,0.0249],"object_to_goal_dist_end":0.05461,"object_to_goal_dist_start":0.15332,"object_z_max":0.03118,"peak_contact_force":122.67437,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3160.0,"raw_peak_contact_force":138.87242,"tcp_end":[0.51019,-0.0896,0.0299],"tcp_start":[0.54828,0.02946,0.01966],"tcp_to_object_dist_end":0.03984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5356,-0.10679,0.02499],"object_pos_start":[0.54115,-0.11463,0.03118],"object_to_goal_dist_end":0.05599,"object_to_goal_dist_start":0.05461,"object_z_max":0.03472,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3801.0,"raw_peak_contact_force":83.23546,"tcp_end":[0.50014,0.06131,0.10078],"tcp_start":[0.51019,-0.0896,0.0299],"tcp_to_object_dist_end":0.18778,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65294,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09176,"contact_1.speed":0.02869,"push_1.push_depth":0.09985},"optimized_scores":{"best_composite_score":0.36799,"best_fitness_score":0.57799,"best_task_score":0.62229},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":800.0,"contact_point_centroid":[0.55001,-0.0116,0.0547],"force_p95":115.66312,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.20668,"mean_force":77.78572,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51831,0.00396,0.02361]},{"body_a":"attachment","body_b":"push_box","contact_count":806.0,"contact_point_centroid":[0.53726,-0.00438,0.05255],"force_p95":101.57164,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.2013,"mean_force":56.72352,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51841,0.00441,0.02358]},{"body_a":"world","body_b":"push_box","contact_count":1550.0,"contact_point_centroid":[0.54416,-0.04706,-0.00031],"force_p95":79.26895,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.80475,"mean_force":51.9779,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51814,0.00274,0.02378]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54918,-0.0617,0.05608],"force_p95":75.4456,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.08808,"mean_force":36.68691,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50703,-0.05307,0.03036]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.52773,-0.05549,0.0585],"force_p95":56.93284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.99363,"mean_force":19.20748,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50616,-0.04932,0.03157]},{"body_a":"world","body_b":"push_box","contact_count":3684.0,"contact_point_centroid":[0.52612,-0.08278,-3e-05],"force_p95":0.25418,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.36984,"mean_force":0.47603,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50115,0.02331,0.0711]},{"body_a":"attachment","body_b":"push_box","contact_count":218.0,"contact_point_centroid":[0.53814,0.05709,0.03792],"force_p95":5.12014,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.59128,"mean_force":2.2557,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5313,0.06905,0.02036]},{"body_a":"world","body_b":"push_box","contact_count":3288.0,"contact_point_centroid":[0.53667,0.03411,-1e-05],"force_p95":1.85153,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.69707,"mean_force":0.40374,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5292,0.08892,0.0229]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51453,0.05559,0.1638]}],"total_contact_groups":9},"final_pose_error":0.07289,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52558,-0.08275,0.02499],"final_tcp_position":[0.49882,0.08923,0.10976],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":128.20668,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53088,0.11131,0.03067],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.53974,0.02707,0.02504],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18147,"object_to_goal_dist_start":0.1905,"object_z_max":0.02513,"peak_contact_force":4.09057,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3506.0,"raw_peak_contact_force":7.59128,"tcp_end":[0.5319,0.06391,0.01977],"tcp_start":[0.53088,0.11131,0.03067],"tcp_to_object_dist_end":0.03804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.53428,-0.08483,0.03141],"object_pos_start":[0.53974,0.02707,0.02504],"object_to_goal_dist_end":0.07391,"object_to_goal_dist_start":0.18147,"object_z_max":0.03141,"peak_contact_force":115.44348,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3156.0,"raw_peak_contact_force":128.20668,"tcp_end":[0.508,-0.05625,0.02925],"tcp_start":[0.5319,0.06391,0.01977],"tcp_to_object_dist_end":0.03889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52558,-0.08275,0.02499],"object_pos_start":[0.53428,-0.08483,0.03141],"object_to_goal_dist_end":0.07195,"object_to_goal_dist_start":0.07391,"object_z_max":0.03492,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3794.0,"raw_peak_contact_force":80.08808,"tcp_end":[0.49882,0.08923,0.10976],"tcp_start":[0.508,-0.05625,0.02925],"tcp_to_object_dist_end":0.19359,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```