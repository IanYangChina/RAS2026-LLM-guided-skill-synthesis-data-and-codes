## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | 0.2042 | 0.54 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | -0.3527 | 0.00 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.1999 | 0.52 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | 0.7074 | 0.47 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5  | 0.2061 | 0.55 | ✅ accepted |

**Proposal policy**: task_score is 0.55 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.206) — your mutation base

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

- **Composite score**: 0.206
- **task_score** (E): 0.550
- **fitness_score**: 0.416  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1849 |
| align_1 | 1.00 | 1.00 | 0.1928 |
| push_1 | 0.67 | 1.00 | 0.1685 |
| align_2 | 1.00 | 1.00 | 0.0600 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.086, 0.137) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.086, 0.137)→(0.473, 0.069, 0.030) | (0.474, -0.001, 0.025)→(0.475, 0.009, 0.028) | 0.154→0.163 | 1.00 / 4.000 | 13.603 | 60.704 |
| push_1 | push | 0.67 / step_budget | (0.473, 0.069, 0.030)→(0.494, -0.097, 0.022) | (0.475, 0.009, 0.028)→(0.472, -0.115, 0.028) | 0.163→0.053 | 1.00 / 3.000 | 9.436 | 45.644 |
| align_2 | align | 1.00 / step_budget | (0.494, -0.097, 0.022)→(0.470, -0.043, 0.023) | (0.472, -0.115, 0.028)→(0.463, -0.103, 0.025) | 0.053→0.069 | 1.00 / 4.000 | 0.246 | 28.521 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.640
- goal_progress: 0.916
- terminal_score: 0.916
- phase_score: 0.430
- phase_breakdown.push_score: 0.838
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.056

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.625
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.916
- **Median Q (composite search score)**: 0.122
- **K-run variance**: 0.0220
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78767,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01,"align_2.lateral_offset_x":-8e-05,"push_1.push_distance":0.19892},"optimized_scores":{"best_composite_score":0.08176,"best_fitness_score":0.29176,"best_task_score":0.56901},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.51033,0.08541,0.04646],"force_p95":154.66051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.6215,"mean_force":112.54583,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50235,0.09183,0.04903]},{"body_a":"world","body_b":"push_box","contact_count":3422.0,"contact_point_centroid":[0.50174,0.05825,-9e-05],"force_p95":81.58625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76933,"mean_force":9.73416,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49612,0.00715,0.08615]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.50364,0.03211,0.03085],"force_p95":74.06286,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.22896,"mean_force":53.54407,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50163,0.04338,0.03146]},{"body_a":"world","body_b":"push_box","contact_count":1907.0,"contact_point_centroid":[0.4965,-0.00306,-0.00016],"force_p95":57.93259,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.88233,"mean_force":39.53586,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50167,0.04635,0.03163]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.5216,0.00879,0.06802],"force_p95":30.9763,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.8641,"mean_force":28.13285,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50162,0.04386,0.03147]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52838,0.09012,0.06853],"force_p95":39.95326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.31824,"mean_force":36.49581,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50206,0.12188,0.0353]},{"body_a":"world","body_b":"push_box","contact_count":332.0,"contact_point_centroid":[0.47089,-0.07322,-0.00025],"force_p95":17.07191,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.32496,"mean_force":3.69803,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.48746,-0.02146,0.02607]},{"body_a":"push_box","body_b":"link7","contact_count":104.0,"contact_point_centroid":[0.50495,-0.07027,0.06612],"force_p95":28.5156,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.54213,"mean_force":10.03872,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49404,-0.03409,0.02509]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.49826,-0.05444,0.02581],"force_p95":3.34019,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.46622,"mean_force":1.08691,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49899,-0.04262,0.0254]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]}],"total_contact_groups":10},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47916,-0.06456,0.02487],"final_tcp_position":[0.48175,-0.00986,0.02743],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":181.6215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17934,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.08175,0.03419],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.23196,"object_to_goal_dist_start":0.20406,"object_z_max":0.03486,"peak_contact_force":40.31824,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3711.0,"raw_peak_contact_force":181.6215,"tcp_end":[0.50193,0.12221,0.03486],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48244,-0.08201,0.03351],"object_pos_start":[0.50341,0.08175,0.03419],"object_to_goal_dist_end":0.07074,"object_to_goal_dist_start":0.23196,"object_z_max":0.0343,"peak_contact_force":28.06237,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3901.0,"raw_peak_contact_force":79.22896,"tcp_end":[0.49924,-0.04248,0.0255],"tcp_start":[0.50193,0.12221,0.03486],"tcp_to_object_dist_end":0.04369,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":189.0,"n_steps_budget":600.0,"object_pos_end":[0.47916,-0.06456,0.02487],"object_pos_start":[0.48244,-0.08201,0.03351],"object_to_goal_dist_end":0.08795,"object_to_goal_dist_start":0.07074,"object_z_max":0.03351,"peak_contact_force":0.24605,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":446.0,"raw_peak_contact_force":32.32496,"tcp_end":[0.48175,-0.00986,0.02743],"tcp_start":[0.49924,-0.04248,0.0255],"tcp_to_object_dist_end":0.05482,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00409,"align_2.lateral_offset_x":0.00289,"push_1.push_distance":0.11697},"optimized_scores":{"best_composite_score":0.41465,"best_fitness_score":0.62465,"best_task_score":0.91607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":729.0,"contact_point_centroid":[0.48408,-0.06766,0.0259],"force_p95":18.2253,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.89636,"mean_force":4.5935,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48195,-0.05569,0.02153]},{"body_a":"push_box","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.52053,-0.14965,0.05214],"force_p95":28.48455,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.97051,"mean_force":23.40145,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49169,-0.11273,0.01914]},{"body_a":"world","body_b":"push_box","contact_count":598.0,"contact_point_centroid":[0.49477,-0.15117,-0.00015],"force_p95":20.02952,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.02515,"mean_force":3.56938,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49133,-0.10258,0.01925]},{"body_a":"world","body_b":"push_box","contact_count":2115.0,"contact_point_centroid":[0.47921,-0.0737,-4e-05],"force_p95":6.84199,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.4367,"mean_force":1.86142,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4775,-0.02713,0.02233]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48142,-0.0196,0.08025]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.4928,-0.13448,0.02028],"force_p95":0.23162,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23162,"mean_force":0.23162,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49298,-0.12251,0.02026]}],"total_contact_groups":7},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49487,-0.15954,0.02498],"final_tcp_position":[0.49086,-0.08644,0.01953],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":29.89636,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13033,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46892,0.04665,0.02746],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49529,-0.15951,0.02504],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01062,"object_to_goal_dist_start":0.12903,"object_z_max":0.02543,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2844.0,"raw_peak_contact_force":29.89636,"tcp_end":[0.49298,-0.12251,0.02026],"tcp_start":[0.46892,0.04665,0.02746],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":600.0,"object_pos_end":[0.49487,-0.15954,0.02498],"object_pos_start":[0.49529,-0.15951,0.02504],"object_to_goal_dist_end":0.01083,"object_to_goal_dist_start":0.01062,"object_z_max":0.02921,"peak_contact_force":0.24531,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":681.0,"raw_peak_contact_force":28.97051,"tcp_end":[0.49086,-0.08644,0.01953],"tcp_start":[0.49298,-0.12251,0.02026],"tcp_to_object_dist_end":0.07341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91429,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00128,"align_2.lateral_offset_x":-0.00013,"push_1.push_distance":0.11438},"optimized_scores":{"best_composite_score":0.12174,"best_fitness_score":0.33174,"best_task_score":0.16551},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":403.0,"contact_point_centroid":[0.46397,-0.05028,0.02427],"force_p95":14.1771,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.80762,"mean_force":3.50717,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46693,-0.03909,0.02255]},{"body_a":"attachment","body_b":"push_box","contact_count":112.0,"contact_point_centroid":[0.45846,-0.08454,0.02305],"force_p95":13.84607,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.26727,"mean_force":4.09775,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4676,-0.08848,0.01781]},{"body_a":"world","body_b":"push_box","contact_count":2825.0,"contact_point_centroid":[0.44247,-0.07281,-2e-05],"force_p95":3.50828,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.44363,"mean_force":0.77567,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4693,-0.04704,0.02255]},{"body_a":"world","body_b":"push_box","contact_count":1311.0,"contact_point_centroid":[0.42187,-0.09282,-3e-05],"force_p95":3.42012,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.32356,"mean_force":0.63838,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46151,-0.07652,0.01882]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2388.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47184,-0.02372,0.08098]}],"total_contact_groups":6},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.41395,-0.08611,0.02499],"final_tcp_position":[0.43784,-0.03229,0.02055],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":27.80762,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13281,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2388.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44945,0.03913,0.0283],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43701,-0.10349,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.0783,"object_to_goal_dist_start":0.12843,"object_z_max":0.02539,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3228.0,"raw_peak_contact_force":27.80762,"tcp_end":[0.49036,-0.12527,0.02035],"tcp_start":[0.44945,0.03913,0.0283],"tcp_to_object_dist_end":0.05781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":750.0,"object_pos_end":[0.41395,-0.08611,0.02499],"object_pos_start":[0.43701,-0.10349,0.02499],"object_to_goal_dist_end":0.10718,"object_to_goal_dist_start":0.0783,"object_z_max":0.02524,"peak_contact_force":0.24525,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1423.0,"raw_peak_contact_force":24.26727,"tcp_end":[0.43784,-0.03229,0.02055],"tcp_start":[0.49036,-0.12527,0.02035],"tcp_to_object_dist_end":0.05905,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```