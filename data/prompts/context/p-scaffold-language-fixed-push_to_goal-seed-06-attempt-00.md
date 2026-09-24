## Search State

- **Seed**: 6
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4850 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

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

## Current Skill (Q=0.485) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: impedance_motion
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
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.485
- **task_score** (E): 0.756
- **fitness_score**: 0.645  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2886 |
| contact_1 | 1.00 | 1.00 | 0.0387 |
| push_1 | 1.00 | 1.00 | 0.1301 |
| retract_1 | 0.00 | 1.00 | 0.1102 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.103, 0.033) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.103, 0.033)→(0.494, 0.066, 0.022) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 16.118 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.066, 0.022)→(0.496, -0.063, 0.020) | (0.500, 0.029, 0.025)→(0.495, -0.100, 0.025) | 0.180→0.050 | 1.00 / 2.000 | 1.333 | 58.399 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.063, 0.020)→(0.494, 0.018, 0.094) | (0.495, -0.100, 0.025)→(0.495, -0.101, 0.025) | 0.050→0.050 | 1.00 / 4.000 | 0.245 | 1.339 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.989
- lateral_force_integral: None
- approach_alignment: 0.546
- goal_progress: 0.986
- terminal_score: 0.986
- phase_score: 0.758
- phase_breakdown.push_score: 0.729
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.764

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.849
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.986
- **Median Q (composite search score)**: 0.392
- **K-run variance**: 0.0209
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.344


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00847,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05003,"approach_1.speed":0.03269,"contact_1.contact_force":7.15305,"contact_1.speed":0.02508,"push_1.push_depth":0.0993,"retract_1.retract_height":0.0711,"retract_1.speed":0.04549},"optimized_scores":{"best_composite_score":0.68923,"best_fitness_score":0.84923,"best_task_score":0.98599},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1020.0,"contact_point_centroid":[0.51202,-0.09931,-0.00015],"force_p95":62.77694,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.32104,"mean_force":25.60926,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49784,-0.04285,0.02084]},{"body_a":"attachment","body_b":"push_box","contact_count":721.0,"contact_point_centroid":[0.51309,-0.05413,0.0462],"force_p95":53.91843,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.61394,"mean_force":25.2009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49774,-0.04308,0.02075]},{"body_a":"push_box","body_b":"link7","contact_count":545.0,"contact_point_centroid":[0.52477,-0.05087,0.05314],"force_p95":45.74991,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.54802,"mean_force":28.49737,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4982,-0.02914,0.02099]},{"body_a":"world","body_b":"push_box","contact_count":3982.0,"contact_point_centroid":[0.49891,-0.14857,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93525,"mean_force":0.24651,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49272,-0.06612,0.05651]},{"body_a":"world","body_b":"push_box","contact_count":3812.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02866,0.16595]},{"body_a":"world","body_b":"push_box","contact_count":3572.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49793,0.03657,0.02517]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51039,-0.12271,0.05038],"force_p95":0.14508,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15035,"mean_force":0.09943,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49574,-0.11078,0.01985]}],"total_contact_groups":7},"final_pose_error":0.17908,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49889,-0.14853,0.02499],"final_tcp_position":[0.49359,-0.01922,0.09172],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75.32104,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.05779,0.03318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":13.85514,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3572.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49921,0.01819,0.02199],"tcp_start":[0.50029,0.05779,0.03318],"tcp_to_object_dist_end":0.0375,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":776.0,"n_steps_budget":870.0,"object_pos_end":[0.49882,-0.14757,0.0253],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00271,"object_to_goal_dist_start":0.13127,"object_z_max":0.02862,"peak_contact_force":0.20145,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2286.0,"raw_peak_contact_force":75.32104,"tcp_end":[0.49581,-0.11067,0.01989],"tcp_start":[0.49921,0.01819,0.02199],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49889,-0.14853,0.02499],"object_pos_start":[0.49882,-0.14757,0.0253],"object_to_goal_dist_end":0.00184,"object_to_goal_dist_start":0.00271,"object_z_max":0.0253,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3986.0,"raw_peak_contact_force":0.93525,"tcp_end":[0.49359,-0.01922,0.09172],"tcp_start":[0.49581,-0.11067,0.01989],"tcp_to_object_dist_end":0.14562,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33333,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22882,"approach_1.speed":0.07716,"contact_1.contact_force":14.06146,"contact_1.speed":0.02099,"push_1.push_depth":0.09982,"retract_1.retract_height":0.07558,"retract_1.speed":0.04272},"optimized_scores":{"best_composite_score":0.39216,"best_fitness_score":0.55216,"best_task_score":0.66022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1043.0,"contact_point_centroid":[0.51453,-0.02841,-0.0001],"force_p95":36.87544,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.95822,"mean_force":16.37048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50261,0.02676,0.02039]},{"body_a":"attachment","body_b":"push_box","contact_count":661.0,"contact_point_centroid":[0.51701,0.00714,0.04585],"force_p95":40.04478,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.46744,"mean_force":18.19758,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50198,0.01817,0.02049]},{"body_a":"push_box","body_b":"link7","contact_count":503.0,"contact_point_centroid":[0.52875,0.00738,0.05322],"force_p95":33.3678,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.82776,"mean_force":18.88161,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50284,0.0278,0.02056]},{"body_a":"world","body_b":"push_box","contact_count":3954.0,"contact_point_centroid":[0.49827,-0.08273,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36883,"mean_force":0.24946,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49323,-0.00704,0.0588]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52318,-0.06848,0.05153],"force_p95":2.123,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.27396,"mean_force":0.97308,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49604,-0.04459,0.01995]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51333,-0.05619,0.052],"force_p95":0.98938,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.99975,"mean_force":0.76341,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4963,-0.04444,0.02002]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50411,0.05967,0.16618]},{"body_a":"world","body_b":"push_box","contact_count":3732.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50793,0.10044,0.0261]}],"total_contact_groups":8},"final_pose_error":0.12924,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49831,-0.08266,0.02499],"final_tcp_position":[0.49414,0.03318,0.09502],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":44.95822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51012,0.11967,0.03503],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":15.48195,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3732.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50933,0.08466,0.02249],"tcp_start":[0.51012,0.11967,0.03503],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":735.0,"n_steps_budget":870.0,"object_pos_end":[0.49953,-0.08141,0.02599],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.0686,"object_to_goal_dist_start":0.19823,"object_z_max":0.0282,"peak_contact_force":2.34076,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2207.0,"raw_peak_contact_force":44.95822,"tcp_end":[0.49634,-0.04434,0.02005],"tcp_start":[0.50933,0.08466,0.02249],"tcp_to_object_dist_end":0.03768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49831,-0.08266,0.02499],"object_pos_start":[0.49953,-0.08141,0.02599],"object_to_goal_dist_end":0.06736,"object_to_goal_dist_start":0.0686,"object_z_max":0.02602,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3961.0,"raw_peak_contact_force":2.36883,"tcp_end":[0.49414,0.03318,0.09502],"tcp_start":[0.49634,-0.04434,0.02005],"tcp_to_object_dist_end":0.13543,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46409,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29236,"approach_1.speed":0.09436,"contact_1.contact_force":9.88433,"contact_1.speed":0.03553,"push_1.push_depth":0.09987,"retract_1.retract_height":0.12497,"retract_1.speed":0.022},"optimized_scores":{"best_composite_score":0.37351,"best_fitness_score":0.53351,"best_task_score":0.6204},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1096.0,"contact_point_centroid":[0.48951,-0.01936,-7e-05],"force_p95":41.90019,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.91899,"mean_force":10.58231,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4839,0.0271,0.01982]},{"body_a":"attachment","body_b":"push_box","contact_count":702.0,"contact_point_centroid":[0.49059,0.02051,0.03294],"force_p95":34.47509,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.17913,"mean_force":12.03523,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48314,0.03195,0.01986]},{"body_a":"push_box","body_b":"link7","contact_count":276.0,"contact_point_centroid":[0.50576,0.04462,0.05132],"force_p95":28.10269,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.2921,"mean_force":18.60602,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47758,0.0669,0.02015]},{"body_a":"world","body_b":"push_box","contact_count":3999.0,"contact_point_centroid":[0.48776,-0.07141,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71174,"mean_force":0.24569,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49185,0.00097,0.05869]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06585,0.16418]},{"body_a":"world","body_b":"push_box","contact_count":2316.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4735,0.11233,0.02466]}],"total_contact_groups":6},"final_pose_error":0.12264,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48776,-0.07142,0.02499],"final_tcp_position":[0.49312,0.04034,0.09552],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":54.91899,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47613,0.13181,0.0315],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":579.0,"n_steps_budget":870.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":19.01664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2316.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47424,0.09546,0.02206],"tcp_start":[0.47613,0.13181,0.0315],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":769.0,"n_steps_budget":870.0,"object_pos_end":[0.48778,-0.07085,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.08009,"object_to_goal_dist_start":0.2095,"object_z_max":0.02909,"peak_contact_force":1.45778,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2074.0,"raw_peak_contact_force":54.91899,"tcp_end":[0.49457,-0.03451,0.02006],"tcp_start":[0.47424,0.09546,0.02206],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48776,-0.07142,0.02499],"object_pos_start":[0.48778,-0.07085,0.02499],"object_to_goal_dist_end":0.07953,"object_to_goal_dist_start":0.08009,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3999.0,"raw_peak_contact_force":0.71174,"tcp_end":[0.49312,0.04034,0.09552],"tcp_start":[0.49457,-0.03451,0.02006],"tcp_to_object_dist_end":0.13226,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```