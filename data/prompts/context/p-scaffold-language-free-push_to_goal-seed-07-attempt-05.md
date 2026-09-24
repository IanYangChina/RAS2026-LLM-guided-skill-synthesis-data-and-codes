## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2790 | 0.71 | ✅ accepted |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0940 | 0.00 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0079 | 0.00 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.2661 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0681 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.708, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.279) — your mutation base

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

- **Composite score**: 0.279
- **task_score** (E): 0.708
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2767 |
| contact_1 | 1.00 | 1.00 | 0.0579 |
| push_1 | 1.00 | 1.00 | 0.1280 |
| retract_1 | 0.00 | 1.00 | 0.1251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.104, 0.048) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.104, 0.048)→(0.508, 0.054, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 3.333 | 4.725 | 11.361 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.054, 0.021)→(0.500, -0.071, 0.023) | (0.515, 0.018, 0.025)→(0.507, -0.105, 0.027) | 0.171→0.056 | 1.00 / 3.333 | 46.758 | 73.992 |
| retract_1 | retract | 0.00 / step_budget | (0.500, -0.071, 0.023)→(0.496, 0.039, 0.081) | (0.507, -0.105, 0.027)→(0.505, -0.103, 0.025) | 0.056→0.054 | 1.00 / 4.000 | 0.245 | 28.890 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.863
- lateral_force_integral: None
- approach_alignment: 0.471
- goal_progress: 0.762
- terminal_score: 0.762
- phase_score: 0.816
- phase_breakdown.approach_score: 0.820
- phase_breakdown.contact_score: 0.860
- phase_breakdown.push_score: 0.788

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.794
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.762
- **Median Q (composite search score)**: 0.204
- **K-run variance**: 0.0121
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.369


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96774,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04441,"contact_1.speed":0.04739,"push_1.push_depth":0.09923,"push_1.push_distance":0.15855,"push_1.push_speed":0.03085,"retract_1.speed":0.05011},"optimized_scores":{"best_composite_score":0.20357,"best_fitness_score":0.56357,"best_task_score":0.69962},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1200.0,"contact_point_centroid":[0.51391,-0.03797,-0.0001],"force_p95":31.78079,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.80766,"mean_force":13.1245,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50286,0.01661,0.01995]},{"body_a":"attachment","body_b":"push_box","contact_count":766.0,"contact_point_centroid":[0.51677,-0.00095,0.04544],"force_p95":31.12672,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.12809,"mean_force":13.91981,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50231,0.01026,0.02002]},{"body_a":"push_box","body_b":"link7","contact_count":528.0,"contact_point_centroid":[0.52967,0.00366,0.05266],"force_p95":28.16218,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.88898,"mean_force":16.84832,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50361,0.02385,0.02005]},{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.5154,0.06835,0.0383],"force_p95":11.43992,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.79942,"mean_force":6.58097,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50984,0.0802,0.02618]},{"body_a":"world","body_b":"push_box","contact_count":2658.0,"contact_point_centroid":[0.51528,0.04628,-1e-05],"force_p95":3.34143,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.17428,"mean_force":0.59413,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50778,0.09856,0.0413]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.50041,-0.09045,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70763,"mean_force":0.24621,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49351,-0.00013,0.04926]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51121,-0.06467,0.04992],"force_p95":1.27724,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.31529,"mean_force":0.75004,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49641,-0.05282,0.02004]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50294,0.07203,0.19077]}],"total_contact_groups":8},"final_pose_error":0.12278,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50039,-0.09046,0.02499],"final_tcp_position":[0.49446,0.04889,0.08057],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":35.80766,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50875,0.12221,0.06447],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":720.0,"n_steps_budget":840.0,"object_pos_end":[0.51682,0.03859,0.02492],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18934,"object_to_goal_dist_start":0.19823,"object_z_max":0.02509,"peak_contact_force":7.41972,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2798.0,"raw_peak_contact_force":14.79942,"tcp_end":[0.51051,0.07549,0.02234],"tcp_start":[0.50875,0.12221,0.06447],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.50043,-0.08972,0.02499],"object_pos_start":[0.51682,0.03859,0.02492],"object_to_goal_dist_end":0.06028,"object_to_goal_dist_start":0.18934,"object_z_max":0.02792,"peak_contact_force":9.76817,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2494.0,"raw_peak_contact_force":35.80766,"tcp_end":[0.49644,-0.05272,0.02007],"tcp_start":[0.51051,0.07549,0.02234],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50039,-0.09046,0.02499],"object_pos_start":[0.50043,-0.08972,0.02499],"object_to_goal_dist_end":0.05955,"object_to_goal_dist_start":0.06028,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3999.0,"raw_peak_contact_force":1.70763,"tcp_end":[0.49446,0.04889,0.08057],"tcp_start":[0.49644,-0.05272,0.02007],"tcp_to_object_dist_end":0.15014,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27016,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07645,"contact_1.speed":0.0342,"push_1.push_depth":0.09955,"push_1.push_distance":0.08064,"push_1.push_speed":0.03885,"retract_1.speed":0.04117},"optimized_scores":{"best_composite_score":0.19919,"best_fitness_score":0.55919,"best_task_score":0.66201},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1421.0,"contact_point_centroid":[0.48955,-0.0312,-0.0001],"force_p95":48.22233,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.95821,"mean_force":11.86472,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48474,0.01498,0.01963]},{"body_a":"attachment","body_b":"push_box","contact_count":855.0,"contact_point_centroid":[0.4918,0.0124,0.03427],"force_p95":34.79578,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.87297,"mean_force":13.30762,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48346,0.02376,0.01973]},{"body_a":"push_box","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.50643,0.03724,0.0514],"force_p95":35.38205,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.3596,"mean_force":25.39876,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4781,0.06032,0.02018]},{"body_a":"attachment","body_b":"push_box","contact_count":190.0,"contact_point_centroid":[0.47844,0.0788,0.03014],"force_p95":8.59621,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.32621,"mean_force":4.56991,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47468,0.0906,0.02388]},{"body_a":"world","body_b":"push_box","contact_count":3197.0,"contact_point_centroid":[0.47956,0.05688,-1e-05],"force_p95":2.61429,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.17259,"mean_force":0.51598,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4737,0.10906,0.03242]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.48586,-0.08057,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99628,"mean_force":0.24644,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49219,0.00668,0.0495]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49217,-0.05573,0.0213],"force_p95":0.80513,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.83611,"mean_force":0.60192,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49462,-0.04407,0.02001]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48524,0.0798,0.18347]}],"total_contact_groups":8},"final_pose_error":0.11864,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48586,-0.08062,0.02499],"final_tcp_position":[0.49357,0.05375,0.08094],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":55.95821,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47601,0.13421,0.04779],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.4811,0.04882,0.02501],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.19971,"object_to_goal_dist_start":0.2095,"object_z_max":0.02504,"peak_contact_force":2.40087,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3387.0,"raw_peak_contact_force":11.32621,"tcp_end":[0.47502,0.08553,0.0216],"tcp_start":[0.47601,0.13421,0.04779],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":947.0,"n_steps_budget":1000.0,"object_pos_end":[0.48616,-0.07987,0.025],"object_pos_start":[0.4811,0.04882,0.02501],"object_to_goal_dist_end":0.07148,"object_to_goal_dist_start":0.19971,"object_z_max":0.02988,"peak_contact_force":0.76302,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2636.0,"raw_peak_contact_force":55.95821,"tcp_end":[0.49464,-0.04399,0.02004],"tcp_start":[0.47502,0.08553,0.0216],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48586,-0.08062,0.02499],"object_pos_start":[0.48616,-0.07987,0.025],"object_to_goal_dist_end":0.07081,"object_to_goal_dist_start":0.07148,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":0.99628,"tcp_end":[0.49357,0.05375,0.08094],"tcp_start":[0.49464,-0.04399,0.02004],"tcp_to_object_dist_end":0.14575,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61856,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08216,"contact_1.speed":0.03351,"push_1.push_depth":0.09856,"push_1.push_distance":0.12049,"push_1.push_speed":0.07673,"retract_1.speed":0.06302},"optimized_scores":{"best_composite_score":0.43426,"best_fitness_score":0.79426,"best_task_score":0.7617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":992.0,"contact_point_centroid":[0.55561,-0.07533,0.05408],"force_p95":108.76256,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.20972,"mean_force":75.08277,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52248,-0.05873,0.02331]},{"body_a":"attachment","body_b":"push_box","contact_count":997.0,"contact_point_centroid":[0.54145,-0.06722,0.05329],"force_p95":83.93261,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.47482,"mean_force":50.41792,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52257,-0.05842,0.02329]},{"body_a":"world","body_b":"push_box","contact_count":1950.0,"contact_point_centroid":[0.54877,-0.10933,-0.00034],"force_p95":71.36383,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.73979,"mean_force":48.40818,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52234,-0.05944,0.02341]},{"body_a":"push_box","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.5485,-0.12514,0.05622],"force_p95":76.27456,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.96618,"mean_force":31.29,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50752,-0.11292,0.02954]},{"body_a":"world","body_b":"push_box","contact_count":3659.0,"contact_point_centroid":[0.53004,-0.13871,-3e-05],"force_p95":0.24821,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.09782,"mean_force":0.57966,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50239,-0.04426,0.05686]},{"body_a":"attachment","body_b":"push_box","contact_count":73.0,"contact_point_centroid":[0.53141,-0.11589,0.06048],"force_p95":57.21795,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.80618,"mean_force":20.5348,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50703,-0.11079,0.02993]},{"body_a":"attachment","body_b":"push_box","contact_count":176.0,"contact_point_centroid":[0.54548,-0.00508,0.03676],"force_p95":6.24153,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.95736,"mean_force":2.68742,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53914,0.00681,0.02039]},{"body_a":"world","body_b":"push_box","contact_count":3461.0,"contact_point_centroid":[0.54462,-0.02746,-1e-05],"force_p95":1.49242,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.96006,"mean_force":0.38761,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5367,0.03018,0.02375]},{"body_a":"world","body_b":"push_box","contact_count":3804.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51727,0.04387,0.17032]}],"total_contact_groups":9},"final_pose_error":0.15245,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52934,-0.13859,0.02499],"final_tcp_position":[0.50064,0.01308,0.08298],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":130.20972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3804.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53809,0.0561,0.03245],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.54732,-0.03468,0.02518],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12465,"object_to_goal_dist_start":0.13211,"object_z_max":0.02521,"peak_contact_force":4.3557,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3637.0,"raw_peak_contact_force":7.95736,"tcp_end":[0.5397,0.00205,0.01977],"tcp_start":[0.53809,0.0561,0.03245],"tcp_to_object_dist_end":0.0379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53558,-0.14622,0.03096],"object_pos_start":[0.54732,-0.03468,0.02518],"object_to_goal_dist_end":0.03627,"object_to_goal_dist_start":0.12465,"object_z_max":0.03096,"peak_contact_force":129.74362,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3939.0,"raw_peak_contact_force":130.20972,"tcp_end":[0.50866,-0.11761,0.02856],"tcp_start":[0.5397,0.00205,0.01977],"tcp_to_object_dist_end":0.03935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52934,-0.13859,0.02499],"object_pos_start":[0.53558,-0.14622,0.03096],"object_to_goal_dist_end":0.03148,"object_to_goal_dist_start":0.03627,"object_z_max":0.03495,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3793.0,"raw_peak_contact_force":83.96618,"tcp_end":[0.50064,0.01308,0.08298],"tcp_start":[0.50866,-0.11761,0.02856],"tcp_to_object_dist_end":0.16489,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```