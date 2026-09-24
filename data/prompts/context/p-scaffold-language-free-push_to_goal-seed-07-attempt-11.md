## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2542 | 0.67 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4392 | 0.31 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3099 | 0.38 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.0419 | 0.01 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2748 | 0.69 | ❌ rejected |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.254) — your mutation base

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

- **Composite score**: 0.254
- **task_score** (E): 0.667
- **fitness_score**: 0.614  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2853 |
| contact_1 | 1.00 | 1.00 | 0.0541 |
| push_1 | 1.00 | 1.00 | 0.1205 |
| retract_1 | 0.00 | 1.00 | 0.1355 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.105, 0.039) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.105, 0.039)→(0.508, 0.055, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.172 | 1.00 / 3.000 | 3.623 | 10.740 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.055, 0.021)→(0.501, -0.063, 0.024) | (0.515, 0.018, 0.025)→(0.508, -0.097, 0.028) | 0.172→0.061 | 1.00 / 4.000 | 59.770 | 78.199 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.063, 0.024)→(0.497, 0.054, 0.090) | (0.508, -0.097, 0.028)→(0.505, -0.094, 0.025) | 0.061→0.062 | 1.00 / 4.000 | 0.245 | 46.794 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.787
- lateral_force_integral: None
- approach_alignment: 0.463
- goal_progress: 0.738
- terminal_score: 0.738
- phase_score: 0.736
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.854
- phase_breakdown.push_score: 0.631

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.737
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.738
- **Median Q (composite search score)**: 0.197
- **K-run variance**: 0.0076
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.399


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4802,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08256,"contact_1.speed":0.04312,"push_1.push_depth":0.09323,"push_1.push_distance":0.02442,"push_1.push_speed":0.07489,"retract_1.speed":0.01125},"optimized_scores":{"best_composite_score":0.18834,"best_fitness_score":0.54834,"best_task_score":0.62504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1723.0,"contact_point_centroid":[0.52349,-0.04404,-0.00021],"force_p95":50.82249,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.67394,"mean_force":35.40708,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50477,0.01077,0.02243]},{"body_a":"push_box","body_b":"link7","contact_count":925.0,"contact_point_centroid":[0.53195,-0.00358,0.05468],"force_p95":57.72848,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.16251,"mean_force":49.22019,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50485,0.01356,0.02221]},{"body_a":"attachment","body_b":"push_box","contact_count":938.0,"contact_point_centroid":[0.52372,0.00431,0.05163],"force_p95":55.49304,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.18857,"mean_force":40.71924,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50492,0.01442,0.02219]},{"body_a":"push_box","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53146,-0.06619,0.05483],"force_p95":52.45777,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.35179,"mean_force":25.4606,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5005,-0.04234,0.02452]},{"body_a":"attachment","body_b":"push_box","contact_count":45.0,"contact_point_centroid":[0.52192,-0.05015,0.05682],"force_p95":39.37833,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.69522,"mean_force":12.86266,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49986,-0.04049,0.02495]},{"body_a":"world","body_b":"push_box","contact_count":3829.0,"contact_point_centroid":[0.51004,-0.07686,-2e-05],"force_p95":0.24994,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.48179,"mean_force":0.32968,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49699,0.01008,0.05451]},{"body_a":"attachment","body_b":"push_box","contact_count":139.0,"contact_point_centroid":[0.51579,0.06841,0.03544],"force_p95":10.48228,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.31799,"mean_force":4.31713,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.08026,0.02268]},{"body_a":"world","body_b":"push_box","contact_count":2546.0,"contact_point_centroid":[0.51517,0.04584,-1e-05],"force_p95":2.45473,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.04028,"mean_force":0.48603,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50814,0.10095,0.03017]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50343,0.07571,0.18098]}],"total_contact_groups":9},"final_pose_error":0.11484,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50969,-0.0763,0.02499],"final_tcp_position":[0.49683,0.05589,0.08425],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":66.67394,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50981,0.12485,0.04309],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":708.0,"n_steps_budget":810.0,"object_pos_end":[0.51693,0.03865,0.02491],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18941,"object_to_goal_dist_start":0.19823,"object_z_max":0.02506,"peak_contact_force":7.05542,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2685.0,"raw_peak_contact_force":11.31799,"tcp_end":[0.51045,0.07547,0.02102],"tcp_start":[0.50981,0.12485,0.04309],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.51162,-0.08086,0.02949],"object_pos_start":[0.51693,0.03865,0.02491],"object_to_goal_dist_end":0.07025,"object_to_goal_dist_start":0.18941,"object_z_max":0.02951,"peak_contact_force":56.95535,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3586.0,"raw_peak_contact_force":66.67394,"tcp_end":[0.50122,-0.04354,0.02433],"tcp_start":[0.51045,0.07547,0.02102],"tcp_to_object_dist_end":0.03909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50969,-0.0763,0.02499],"object_pos_start":[0.51162,-0.08086,0.02949],"object_to_goal_dist_end":0.07433,"object_to_goal_dist_start":0.07025,"object_z_max":0.02949,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3902.0,"raw_peak_contact_force":55.35179,"tcp_end":[0.49683,0.05589,0.08425],"tcp_start":[0.50122,-0.04354,0.02433],"tcp_to_object_dist_end":0.14544,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13492,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09489,"contact_1.speed":0.0334,"push_1.push_depth":0.09879,"push_1.push_distance":0.08251,"push_1.push_speed":0.02422,"retract_1.speed":0.0956},"optimized_scores":{"best_composite_score":0.1972,"best_fitness_score":0.5572,"best_task_score":0.63786},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1550.0,"contact_point_centroid":[0.48473,-0.02982,-7e-05],"force_p95":41.57784,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.91146,"mean_force":9.30196,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48442,0.01619,0.01935]},{"body_a":"push_box","body_b":"link7","contact_count":353.0,"contact_point_centroid":[0.50535,0.04034,0.05099],"force_p95":29.90633,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.73125,"mean_force":21.88905,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47732,0.06293,0.01964]},{"body_a":"attachment","body_b":"push_box","contact_count":886.0,"contact_point_centroid":[0.49021,0.01327,0.03288],"force_p95":28.64758,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.90221,"mean_force":10.90974,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48308,0.02468,0.01934]},{"body_a":"attachment","body_b":"push_box","contact_count":188.0,"contact_point_centroid":[0.47939,0.07887,0.03107],"force_p95":8.19055,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.3644,"mean_force":3.94657,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47464,0.09063,0.02299]},{"body_a":"world","body_b":"push_box","contact_count":3194.0,"contact_point_centroid":[0.47965,0.0568,-1e-05],"force_p95":2.37288,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.5275,"mean_force":0.47932,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47357,0.10998,0.02961]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49105,-0.05474,0.02181],"force_p95":3.358,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.358,"mean_force":3.358,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49459,-0.04343,0.01998]},{"body_a":"world","body_b":"push_box","contact_count":3990.0,"contact_point_centroid":[0.4785,-0.07726,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6921,"mean_force":0.24662,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49278,0.02449,0.06117]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48504,0.08099,0.18058]}],"total_contact_groups":8},"final_pose_error":0.07525,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47851,-0.07724,0.02499],"final_tcp_position":[0.49479,0.08988,0.10504],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":46.91146,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47586,0.13497,0.04205],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.48167,0.04878,0.02503],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.19962,"object_to_goal_dist_start":0.2095,"object_z_max":0.02509,"peak_contact_force":1.59517,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3382.0,"raw_peak_contact_force":9.3644,"tcp_end":[0.47498,0.08547,0.02129],"tcp_start":[0.47586,0.13497,0.04205],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.47876,-0.0767,0.02496],"object_pos_start":[0.48167,0.04878,0.02503],"object_to_goal_dist_end":0.07631,"object_to_goal_dist_start":0.19962,"object_z_max":0.02748,"peak_contact_force":6.35358,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2789.0,"raw_peak_contact_force":46.91146,"tcp_end":[0.4946,-0.04334,0.02],"tcp_start":[0.47498,0.08547,0.02129],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47851,-0.07724,0.02499],"object_pos_start":[0.47876,-0.0767,0.02496],"object_to_goal_dist_end":0.07587,"object_to_goal_dist_start":0.07631,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":3.358,"tcp_end":[0.49479,0.08988,0.10504],"tcp_start":[0.4946,-0.04334,0.02],"tcp_to_object_dist_end":0.18601,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34848,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06686,"contact_1.speed":0.04658,"push_1.push_depth":0.08344,"push_1.push_distance":0.08705,"push_1.push_speed":0.07319,"retract_1.speed":0.05934},"optimized_scores":{"best_composite_score":0.37714,"best_fitness_score":0.73714,"best_task_score":0.7383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":930.0,"contact_point_centroid":[0.55446,-0.06896,0.05424],"force_p95":104.869,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.01045,"mean_force":73.52648,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52169,-0.0521,0.02342]},{"body_a":"attachment","body_b":"push_box","contact_count":937.0,"contact_point_centroid":[0.54102,-0.06082,0.05446],"force_p95":78.76631,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.15681,"mean_force":48.51577,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52182,-0.05169,0.02339]},{"body_a":"world","body_b":"push_box","contact_count":3666.0,"contact_point_centroid":[0.52729,-0.12825,-3e-05],"force_p95":0.27571,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.67105,"mean_force":0.5451,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50174,-0.03586,0.0559]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.54836,-0.11119,0.05537],"force_p95":75.19371,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.62432,"mean_force":34.78553,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5067,-0.09975,0.02918]},{"body_a":"world","body_b":"push_box","contact_count":1858.0,"contact_point_centroid":[0.54659,-0.10315,-0.00033],"force_p95":68.32568,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.0852,"mean_force":46.58078,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52173,-0.05203,0.02344]},{"body_a":"attachment","body_b":"push_box","contact_count":73.0,"contact_point_centroid":[0.52968,-0.10328,0.05973],"force_p95":57.17072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.45728,"mean_force":20.39492,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50602,-0.09697,0.0297]},{"body_a":"attachment","body_b":"push_box","contact_count":114.0,"contact_point_centroid":[0.54477,-0.00456,0.03513],"force_p95":9.43316,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.53751,"mean_force":3.48427,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53911,0.00733,0.02045]},{"body_a":"world","body_b":"push_box","contact_count":2517.0,"contact_point_centroid":[0.54461,-0.02704,-1e-05],"force_p95":1.1163,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.57075,"mean_force":0.40781,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5367,0.03103,0.02388]},{"body_a":"world","body_b":"push_box","contact_count":3948.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51724,0.04385,0.1704]}],"total_contact_groups":9},"final_pose_error":0.14946,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52665,-0.12797,0.02499],"final_tcp_position":[0.50021,0.0172,0.08144],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":121.01045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3948.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53812,0.05609,0.03228],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54686,-0.03359,0.02511],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12549,"object_to_goal_dist_start":0.13211,"object_z_max":0.02513,"peak_contact_force":2.21828,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2631.0,"raw_peak_contact_force":11.53751,"tcp_end":[0.53964,0.00312,0.01994],"tcp_start":[0.53812,0.05609,0.03228],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.53253,-0.13396,0.03084],"object_pos_start":[0.54686,-0.03359,0.02511],"object_to_goal_dist_end":0.03674,"object_to_goal_dist_start":0.12549,"object_z_max":0.03085,"peak_contact_force":116.00048,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3725.0,"raw_peak_contact_force":121.01045,"tcp_end":[0.50771,-0.1036,0.02835],"tcp_start":[0.53964,0.00312,0.01994],"tcp_to_object_dist_end":0.03929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,-0.12797,0.02499],"object_pos_start":[0.53253,-0.13396,0.03084],"object_to_goal_dist_end":0.03457,"object_to_goal_dist_start":0.03674,"object_z_max":0.03399,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3793.0,"raw_peak_contact_force":81.67105,"tcp_end":[0.50021,0.0172,0.08144],"tcp_start":[0.50771,-0.1036,0.02835],"tcp_to_object_dist_end":0.15798,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```