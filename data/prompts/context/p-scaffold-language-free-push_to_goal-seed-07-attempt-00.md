## Search State

- **Seed**: 7
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2751 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.275) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
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
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.275
- **task_score** (E): 0.691
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2792 |
| contact_1 | 1.00 | 1.00 | 0.0570 |
| push_1 | 1.00 | 1.00 | 0.1277 |
| retract_1 | 0.00 | 1.00 | 0.1318 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.105, 0.046) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.105, 0.046)→(0.508, 0.055, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 3.000 | 2.817 | 10.978 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.055, 0.021)→(0.500, -0.071, 0.023) | (0.515, 0.018, 0.025)→(0.508, -0.104, 0.027) | 0.171→0.058 | 1.00 / 2.667 | 39.535 | 81.605 |
| retract_1 | retract | 0.00 / step_budget | (0.500, -0.071, 0.023)→(0.497, 0.044, 0.086) | (0.508, -0.104, 0.027)→(0.506, -0.101, 0.025) | 0.058→0.056 | 1.00 / 4.000 | 0.245 | 27.220 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.827
- lateral_force_integral: None
- approach_alignment: 0.487
- goal_progress: 0.722
- terminal_score: 0.722
- phase_score: 0.815
- phase_breakdown.approach_score: 0.820
- phase_breakdown.contact_score: 0.858
- phase_breakdown.push_score: 0.787

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.778
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.722
- **Median Q (composite search score)**: 0.210
- **K-run variance**: 0.0102
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.422


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21759,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05599,"contact_1.speed":0.03717,"push_1.push_depth":0.09976,"push_1.push_distance":0.08453,"push_1.push_speed":0.07478,"retract_1.speed":0.0674},"optimized_scores":{"best_composite_score":0.20956,"best_fitness_score":0.56956,"best_task_score":0.70836},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1182.0,"contact_point_centroid":[0.51565,-0.03824,-9e-05],"force_p95":37.50558,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.6714,"mean_force":18.13624,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50354,0.01694,0.02023]},{"body_a":"attachment","body_b":"push_box","contact_count":725.0,"contact_point_centroid":[0.51867,0.00038,0.04699],"force_p95":39.26174,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.69241,"mean_force":20.40254,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50305,0.01137,0.02029]},{"body_a":"push_box","body_b":"link7","contact_count":618.0,"contact_point_centroid":[0.52973,-0.00052,0.05302],"force_p95":34.855,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.84219,"mean_force":21.19431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50385,0.01963,0.02029]},{"body_a":"attachment","body_b":"push_box","contact_count":199.0,"contact_point_centroid":[0.51683,0.06809,0.04103],"force_p95":10.40298,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.15293,"mean_force":5.94946,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50991,0.07992,0.02583]},{"body_a":"world","body_b":"push_box","contact_count":3332.0,"contact_point_centroid":[0.51528,0.04561,-1e-05],"force_p95":3.42897,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.44726,"mean_force":0.60495,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50785,0.09776,0.04023]},{"body_a":"world","body_b":"push_box","contact_count":3939.0,"contact_point_centroid":[0.50005,-0.09207,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72371,"mean_force":0.24972,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4936,0.00365,0.05216]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51201,-0.06581,0.0507],"force_p95":0.98228,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.98933,"mean_force":0.79191,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4964,-0.05402,0.02002]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50295,0.07211,0.19056]}],"total_contact_groups":8},"final_pose_error":0.11428,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49994,-0.09219,0.02499],"final_tcp_position":[0.49464,0.05587,0.08541],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":47.6714,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50881,0.12231,0.06383],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":915.0,"n_steps_budget":1000.0,"object_pos_end":[0.51704,0.03805,0.02505],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18882,"object_to_goal_dist_start":0.19823,"object_z_max":0.02512,"peak_contact_force":0.65066,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3531.0,"raw_peak_contact_force":12.15293,"tcp_end":[0.51056,0.07478,0.02176],"tcp_start":[0.50881,0.12231,0.06383],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.49984,-0.09082,0.02528],"object_pos_start":[0.51704,0.03805,0.02505],"object_to_goal_dist_end":0.05918,"object_to_goal_dist_start":0.18882,"object_z_max":0.02834,"peak_contact_force":2.70687,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2525.0,"raw_peak_contact_force":47.6714,"tcp_end":[0.49647,-0.05389,0.02006],"tcp_start":[0.51056,0.07478,0.02176],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49994,-0.09219,0.02499],"object_pos_start":[0.49984,-0.09082,0.02528],"object_to_goal_dist_end":0.05781,"object_to_goal_dist_start":0.05918,"object_z_max":0.02533,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3943.0,"raw_peak_contact_force":1.72371,"tcp_end":[0.49464,0.05587,0.08541],"tcp_start":[0.49647,-0.05389,0.02006],"tcp_to_object_dist_end":0.16,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0973,"contact_1.speed":0.04405,"push_1.push_depth":0.09722,"push_1.push_distance":0.17484,"push_1.push_speed":0.06124,"retract_1.speed":0.07598},"optimized_scores":{"best_composite_score":0.19833,"best_fitness_score":0.55833,"best_task_score":0.64331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1299.0,"contact_point_centroid":[0.49073,-0.02937,-0.00011],"force_p95":52.67861,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.67818,"mean_force":14.09275,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4849,0.01686,0.01974]},{"body_a":"attachment","body_b":"push_box","contact_count":797.0,"contact_point_centroid":[0.4928,0.0159,0.03579],"force_p95":37.83455,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.52059,"mean_force":14.80252,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48334,0.02718,0.01982]},{"body_a":"push_box","body_b":"link7","contact_count":388.0,"contact_point_centroid":[0.50724,0.03637,0.05136],"force_p95":37.59367,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.62908,"mean_force":26.79478,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47868,0.05889,0.02027]},{"body_a":"attachment","body_b":"push_box","contact_count":134.0,"contact_point_centroid":[0.47769,0.07916,0.02796],"force_p95":10.92654,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.22557,"mean_force":4.37839,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47461,0.09099,0.02287]},{"body_a":"world","body_b":"push_box","contact_count":2500.0,"contact_point_centroid":[0.47962,0.05735,-1e-05],"force_p95":2.56984,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.83712,"mean_force":0.48069,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47354,0.11098,0.02914]},{"body_a":"world","body_b":"push_box","contact_count":3982.0,"contact_point_centroid":[0.48416,-0.07697,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74882,"mean_force":0.24634,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49249,0.01737,0.05523]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48502,0.08112,0.18019]}],"total_contact_groups":7},"final_pose_error":0.0978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48413,-0.07698,0.02499],"final_tcp_position":[0.49414,0.07148,0.092],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":62.67818,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47582,0.13516,0.04053],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":679.0,"n_steps_budget":780.0,"object_pos_end":[0.48141,0.0496,0.02493],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20047,"object_to_goal_dist_start":0.2095,"object_z_max":0.0251,"peak_contact_force":6.61524,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2634.0,"raw_peak_contact_force":12.22557,"tcp_end":[0.47496,0.0863,0.02148],"tcp_start":[0.47582,0.13516,0.04053],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.4845,-0.07628,0.02494],"object_pos_start":[0.48141,0.0496,0.02493],"object_to_goal_dist_end":0.07533,"object_to_goal_dist_start":0.20047,"object_z_max":0.02999,"peak_contact_force":1.55561,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2484.0,"raw_peak_contact_force":62.67818,"tcp_end":[0.49465,-0.0408,0.02007],"tcp_start":[0.47496,0.0863,0.02148],"tcp_to_object_dist_end":0.03722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48413,-0.07698,0.02499],"object_pos_start":[0.4845,-0.07628,0.02494],"object_to_goal_dist_end":0.07473,"object_to_goal_dist_start":0.07533,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3982.0,"raw_peak_contact_force":0.74882,"tcp_end":[0.49414,0.07148,0.092],"tcp_start":[0.49465,-0.0408,0.02007],"tcp_to_object_dist_end":0.16319,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32212,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06175,"contact_1.speed":0.03949,"push_1.push_depth":0.1,"push_1.push_distance":0.10742,"push_1.push_speed":0.09673,"retract_1.speed":0.05681},"optimized_scores":{"best_composite_score":0.41756,"best_fitness_score":0.77756,"best_task_score":0.72152},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":829.0,"contact_point_centroid":[0.55693,-0.07336,0.05408],"force_p95":114.29574,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.4642,"mean_force":79.08169,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52302,-0.0577,0.02357]},{"body_a":"world","body_b":"push_box","contact_count":1609.0,"contact_point_centroid":[0.55072,-0.10758,-0.00033],"force_p95":82.90887,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.87498,"mean_force":52.06855,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52279,-0.0589,0.02373]},{"body_a":"attachment","body_b":"push_box","contact_count":833.0,"contact_point_centroid":[0.54167,-0.06595,0.05269],"force_p95":90.52324,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.96402,"mean_force":53.113,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52311,-0.05741,0.02356]},{"body_a":"push_box","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.5491,-0.12439,0.0567],"force_p95":74.6829,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.18669,"mean_force":31.70136,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50804,-0.11386,0.02997]},{"body_a":"world","body_b":"push_box","contact_count":3640.0,"contact_point_centroid":[0.53385,-0.1345,-3e-05],"force_p95":0.28128,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.3648,"mean_force":0.62895,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50288,-0.04841,0.0556]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.53197,-0.11646,0.06089],"force_p95":50.60345,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.4288,"mean_force":19.72466,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50752,-0.11167,0.03035]},{"body_a":"attachment","body_b":"push_box","contact_count":141.0,"contact_point_centroid":[0.54556,-0.00485,0.03719],"force_p95":8.05686,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.55677,"mean_force":3.20114,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53913,0.00704,0.02043]},{"body_a":"world","body_b":"push_box","contact_count":2999.0,"contact_point_centroid":[0.54459,-0.02716,-1e-05],"force_p95":1.73078,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.88051,"mean_force":0.39988,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53673,0.0303,0.02379]},{"body_a":"world","body_b":"push_box","contact_count":3964.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51723,0.04385,0.17045]}],"total_contact_groups":9},"final_pose_error":0.16053,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53327,-0.13429,0.02499],"final_tcp_position":[0.5011,0.00554,0.08001],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":134.4642,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5381,0.05612,0.03242],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":826.0,"n_steps_budget":930.0,"object_pos_end":[0.54757,-0.03419,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.1252,"object_to_goal_dist_start":0.13211,"object_z_max":0.02513,"peak_contact_force":1.18654,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3140.0,"raw_peak_contact_force":8.55677,"tcp_end":[0.5397,0.00256,0.01988],"tcp_start":[0.5381,0.05612,0.03242],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":838.0,"n_steps_budget":930.0,"object_pos_end":[0.53827,-0.14512,0.03108],"object_pos_start":[0.54757,-0.03419,0.02499],"object_to_goal_dist_end":0.03906,"object_to_goal_dist_start":0.1252,"object_z_max":0.03112,"peak_contact_force":114.3424,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3271.0,"raw_peak_contact_force":134.4642,"tcp_end":[0.50918,-0.11845,0.02905],"tcp_start":[0.5397,0.00256,0.01988],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53327,-0.13429,0.02499],"object_pos_start":[0.53827,-0.14512,0.03108],"object_to_goal_dist_end":0.03679,"object_to_goal_dist_start":0.03906,"object_z_max":0.03463,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3777.0,"raw_peak_contact_force":79.18669,"tcp_end":[0.5011,0.00554,0.08001],"tcp_start":[0.50918,-0.11845,0.02905],"tcp_to_object_dist_end":0.15367,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```