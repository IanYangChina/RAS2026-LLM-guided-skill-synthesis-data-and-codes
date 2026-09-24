## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

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
| `object` | offset from object initial position (0.5014185949640309, 0.05405564355911223, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.202) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.202
- **task_score** (E): 0.531
- **fitness_score**: 0.412  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1849 |
| align_1 | 1.00 | 1.00 | 0.1928 |
| push_1 | 0.67 | 1.00 | 0.1681 |
| align_2 | 1.00 | 1.00 | 0.0633 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.086, 0.137) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.086, 0.137)→(0.473, 0.069, 0.030) | (0.474, -0.001, 0.025)→(0.475, 0.009, 0.028) | 0.154→0.163 | 1.00 / 4.000 | 13.603 | 60.704 |
| push_1 | push | 0.67 / step_budget | (0.473, 0.069, 0.030)→(0.495, -0.096, 0.022) | (0.475, 0.009, 0.028)→(0.472, -0.111, 0.028) | 0.163→0.057 | 1.00 / 3.000 | 11.590 | 44.186 |
| align_2 | align | 1.00 / step_budget | (0.495, -0.096, 0.022)→(0.470, -0.039, 0.023) | (0.472, -0.111, 0.028)→(0.463, -0.100, 0.025) | 0.057→0.071 | 1.00 / 4.000 | 0.246 | 30.088 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.643
- goal_progress: 0.909
- terminal_score: 0.909
- phase_score: 0.420
- phase_breakdown.approach_score: 0.054
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.616
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.909
- **Median Q (composite search score)**: 0.118
- **K-run variance**: 0.0210
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.206


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78767,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00748,"align_2.lateral_offset_x":0.00314,"push_1.push_distance":0.1835},"optimized_scores":{"best_composite_score":0.08207,"best_fitness_score":0.29207,"best_task_score":0.57061},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.51033,0.08541,0.04646],"force_p95":154.66051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.6215,"mean_force":112.54583,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50235,0.09183,0.04903]},{"body_a":"world","body_b":"push_box","contact_count":3422.0,"contact_point_centroid":[0.50174,0.05825,-9e-05],"force_p95":81.58625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76933,"mean_force":9.73416,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49612,0.00715,0.08615]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.50377,0.03236,0.0308],"force_p95":75.51006,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.66939,"mean_force":55.02047,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50176,0.04362,0.0314]},{"body_a":"world","body_b":"push_box","contact_count":1915.0,"contact_point_centroid":[0.49646,-0.00303,-0.00017],"force_p95":59.63881,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.04368,"mean_force":40.75732,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5018,0.04634,0.03157]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.52172,0.00903,0.06799],"force_p95":32.01275,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.8641,"mean_force":29.58462,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50176,0.04409,0.03142]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52838,0.09012,0.06853],"force_p95":39.95326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.31824,"mean_force":36.49581,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50206,0.12188,0.0353]},{"body_a":"world","body_b":"push_box","contact_count":327.0,"contact_point_centroid":[0.47162,-0.07273,-0.00025],"force_p95":16.48165,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.53843,"mean_force":3.68699,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.48759,-0.02131,0.02589]},{"body_a":"push_box","body_b":"link7","contact_count":105.0,"contact_point_centroid":[0.50486,-0.06993,0.06599],"force_p95":27.76136,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.74488,"mean_force":9.72391,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4941,-0.0337,0.02486]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.49829,-0.05416,0.02562],"force_p95":3.5889,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.69043,"mean_force":1.28294,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49917,-0.04232,0.02516]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]}],"total_contact_groups":10},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47949,-0.06481,0.02489],"final_tcp_position":[0.48169,-0.00945,0.02732],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":181.6215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17934,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.08175,0.03419],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.23196,"object_to_goal_dist_start":0.20406,"object_z_max":0.03486,"peak_contact_force":40.31824,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3711.0,"raw_peak_contact_force":181.6215,"tcp_end":[0.50193,0.12221,0.03486],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48234,-0.0816,0.03342],"object_pos_start":[0.50341,0.08175,0.03419],"object_to_goal_dist_end":0.07114,"object_to_goal_dist_start":0.23196,"object_z_max":0.03428,"peak_contact_force":34.52442,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3909.0,"raw_peak_contact_force":80.66939,"tcp_end":[0.49943,-0.04215,0.02525],"tcp_start":[0.50193,0.12221,0.03486],"tcp_to_object_dist_end":0.04377,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":600.0,"object_pos_end":[0.47949,-0.06481,0.02489],"object_pos_start":[0.48234,-0.0816,0.03342],"object_to_goal_dist_end":0.08762,"object_to_goal_dist_start":0.07114,"object_z_max":0.03342,"peak_contact_force":0.24865,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":442.0,"raw_peak_contact_force":31.53843,"tcp_end":[0.48169,-0.00945,0.02732],"tcp_start":[0.49943,-0.04215,0.02525],"tcp_to_object_dist_end":0.05546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00017,"align_2.lateral_offset_x":-0.00205,"push_1.push_distance":0.13411},"optimized_scores":{"best_composite_score":0.40562,"best_fitness_score":0.61562,"best_task_score":0.90883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.52138,-0.15491,0.05293],"force_p95":36.22817,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.59876,"mean_force":27.77501,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49114,-0.11514,0.01999]},{"body_a":"attachment","body_b":"push_box","contact_count":748.0,"contact_point_centroid":[0.48482,-0.06806,0.03004],"force_p95":16.79903,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.44612,"mean_force":4.21974,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48057,-0.05608,0.02165]},{"body_a":"world","body_b":"push_box","contact_count":569.0,"contact_point_centroid":[0.49572,-0.14999,-0.00017],"force_p95":30.3972,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.05666,"mean_force":5.71297,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49123,-0.10414,0.01972]},{"body_a":"world","body_b":"push_box","contact_count":2033.0,"contact_point_centroid":[0.47863,-0.074,-4e-05],"force_p95":7.61644,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.23361,"mean_force":1.84207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47642,-0.02674,0.02244]},{"body_a":"push_box","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52121,-0.1365,0.05032],"force_p95":2.6685,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.69606,"mean_force":1.1134,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49043,-0.12033,0.02057]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48142,-0.0196,0.08025]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49091,-0.13668,0.02048],"force_p95":0.12864,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13541,"mean_force":0.0677,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49106,-0.1247,0.02048]}],"total_contact_groups":8},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4954,-0.16083,0.02496],"final_tcp_position":[0.49162,-0.08836,0.01966],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":36.59876,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13033,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46892,0.04665,0.02746],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49651,-0.16162,0.02507],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01214,"object_to_goal_dist_start":0.12903,"object_z_max":0.02548,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2800.0,"raw_peak_contact_force":33.44612,"tcp_end":[0.49107,-0.12465,0.02049],"tcp_start":[0.46892,0.04665,0.02746],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":600.0,"object_pos_end":[0.4954,-0.16083,0.02496],"object_pos_start":[0.49651,-0.16162,0.02507],"object_to_goal_dist_end":0.01176,"object_to_goal_dist_start":0.01214,"object_z_max":0.02935,"peak_contact_force":0.24535,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":680.0,"raw_peak_contact_force":36.59876,"tcp_end":[0.49162,-0.08836,0.01966],"tcp_start":[0.49107,-0.12465,0.02049],"tcp_to_object_dist_end":0.07275,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91429,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00182,"align_2.lateral_offset_x":-0.00139,"push_1.push_distance":0.09683},"optimized_scores":{"best_composite_score":0.11758,"best_fitness_score":0.32758,"best_task_score":0.1127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":96.0,"contact_point_centroid":[0.46048,-0.07557,0.02263],"force_p95":12.10111,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.12574,"mean_force":4.51833,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46935,-0.08064,0.01752]},{"body_a":"attachment","body_b":"push_box","contact_count":344.0,"contact_point_centroid":[0.46412,-0.04419,0.02447],"force_p95":13.02044,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.44221,"mean_force":3.61531,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46737,-0.03315,0.02253]},{"body_a":"world","body_b":"push_box","contact_count":1553.0,"contact_point_centroid":[0.42319,-0.08191,-3e-05],"force_p95":2.75826,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.9591,"mean_force":0.55404,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46343,-0.06857,0.01859]},{"body_a":"world","body_b":"push_box","contact_count":2953.0,"contact_point_centroid":[0.44163,-0.06745,-2e-05],"force_p95":3.34445,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.3839,"mean_force":0.69427,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47156,-0.04645,0.02235]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2388.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47184,-0.02372,0.08098]}],"total_contact_groups":6},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.41454,-0.07461,0.02499],"final_tcp_position":[0.43787,-0.01945,0.02058],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":22.12574,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13281,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2388.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44945,0.03913,0.0283],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.43721,-0.09066,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.08639,"object_to_goal_dist_start":0.12843,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3297.0,"raw_peak_contact_force":18.44221,"tcp_end":[0.49384,-0.12146,0.02008],"tcp_start":[0.44945,0.03913,0.0283],"tcp_to_object_dist_end":0.06465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":780.0,"object_pos_end":[0.41454,-0.07461,0.02499],"object_pos_start":[0.43721,-0.09066,0.02499],"object_to_goal_dist_end":0.11396,"object_to_goal_dist_start":0.08639,"object_z_max":0.02531,"peak_contact_force":0.24525,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1649.0,"raw_peak_contact_force":22.12574,"tcp_end":[0.43787,-0.01945,0.02058],"tcp_start":[0.49384,-0.12146,0.02008],"tcp_to_object_dist_end":0.06005,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```