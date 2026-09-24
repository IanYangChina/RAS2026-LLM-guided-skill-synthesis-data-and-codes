## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2145 | 0.40 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0434 | 0.00 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0690 | 0.51 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0248 | 0.00 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0363 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.819, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5164354024785746, -0.027625594348335558, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.214) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
    push_speed:
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.214
- **task_score** (E): 0.400
- **fitness_score**: 0.444  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1909 |
| descend_1 | 1.00 | 1.00 | 0.0604 |
| push_1 | 1.00 | 1.00 | 0.0988 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.114) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.001, 0.114)→(0.493, 0.001, 0.053) | (0.496, 0.001, 0.025)→(0.497, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 81.557 | 81.557 |
| push_1 | push | 1.00 / step_budget | (0.493, 0.001, 0.053)→(0.496, -0.097, 0.046) | (0.497, 0.001, 0.025)→(0.498, -0.057, 0.024) | 0.152→0.095 | 1.00 / 3.667 | 0.436 | 132.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.476
- lateral_force_integral: None
- approach_alignment: 0.710
- goal_progress: 0.475
- terminal_score: 0.475
- phase_score: 0.528
- phase_breakdown.push_to_goal_score: 0.474
- phase_breakdown.reach_object_score: 0.653

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.507
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.475
- **Median Q (composite search score)**: 0.261
- **K-run variance**: 0.0060
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.317


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57303,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16633,"descend_1.descend_speed":0.10136,"push_1.push_distance":0.11859,"push_1.push_speed":0.05544},"optimized_scores":{"best_composite_score":0.26119,"best_fitness_score":0.49119,"best_task_score":0.45823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":213.0,"contact_point_centroid":[0.5192,-0.05293,0.05089],"force_p95":117.59452,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.05005,"mean_force":80.31254,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51121,-0.05945,0.05356]},{"body_a":"world","body_b":"push_box","contact_count":585.0,"contact_point_centroid":[0.51524,-0.057,-0.00034],"force_p95":73.52208,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.31486,"mean_force":29.69015,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.509,-0.07072,0.05206]},{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.52304,-0.02731,0.04946],"force_p95":72.99165,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.03087,"mean_force":58.71423,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51202,-0.02727,0.05381]},{"body_a":"world","body_b":"push_box","contact_count":1400.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.16696,"mean_force":0.91786,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51051,-0.02645,0.08123]},{"body_a":"world","body_b":"push_box","contact_count":2176.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50505,-0.01257,0.20694]}],"total_contact_groups":5},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51196,-0.08419,0.02428],"final_tcp_position":[0.4994,-0.12581,0.04598],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":120.05005,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":750.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51183,-0.02563,0.11353],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":350.0,"n_steps_budget":600.0,"object_pos_end":[0.51668,-0.02765,0.02469],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12348,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":74.03087,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1416.0,"raw_peak_contact_force":74.03087,"subtask_id":"reach_object","tcp_end":[0.51256,-0.02732,0.05313],"tcp_start":[0.51183,-0.02563,0.11353],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.51196,-0.08419,0.02428],"object_pos_start":[0.51668,-0.02765,0.02469],"object_to_goal_dist_end":0.06689,"object_to_goal_dist_start":0.12348,"object_z_max":0.03521,"peak_contact_force":0.30172,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":798.0,"raw_peak_contact_force":120.05005,"subtask_id":"push_to_goal","tcp_end":[0.4994,-0.12581,0.04598],"tcp_start":[0.51256,-0.02732,0.05313],"tcp_to_object_dist_end":0.0486,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31132,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13703,"descend_1.descend_speed":0.09606,"push_1.push_distance":0.11343,"push_1.push_speed":0.04216},"optimized_scores":{"best_composite_score":0.10542,"best_fitness_score":0.33542,"best_task_score":0.26747},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":210.0,"contact_point_centroid":[0.50801,0.02816,0.05052],"force_p95":120.62023,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.30469,"mean_force":83.2502,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50007,0.02174,0.05339]},{"body_a":"world","body_b":"push_box","contact_count":571.0,"contact_point_centroid":[0.5023,0.02696,-0.00034],"force_p95":89.76174,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.17821,"mean_force":31.05614,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4995,0.0129,0.05221]},{"body_a":"attachment","body_b":"push_box","contact_count":18.0,"contact_point_centroid":[0.50816,0.05329,0.04943],"force_p95":77.84116,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.10462,"mean_force":61.87476,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49729,0.05307,0.0541]},{"body_a":"world","body_b":"push_box","contact_count":1404.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":5.07899,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.66032,"mean_force":1.04019,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49619,0.05146,0.08139]},{"body_a":"world","body_b":"push_box","contact_count":2384.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49814,0.02455,0.20676]}],"total_contact_groups":5},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50137,-0.00053,0.02423],"final_tcp_position":[0.49715,-0.04029,0.04625],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":122.30469,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":930.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49794,0.05003,0.1134],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":351.0,"n_steps_budget":600.0,"object_pos_end":[0.50169,0.0541,0.02465],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.2041,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":79.10462,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1422.0,"raw_peak_contact_force":79.10462,"subtask_id":"reach_object","tcp_end":[0.49788,0.05318,0.05335],"tcp_start":[0.49794,0.05003,0.1134],"tcp_to_object_dist_end":0.02897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.50137,-0.00053,0.02423],"object_pos_start":[0.50169,0.0541,0.02465],"object_to_goal_dist_end":0.14948,"object_to_goal_dist_start":0.2041,"object_z_max":0.0351,"peak_contact_force":0.62754,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":781.0,"raw_peak_contact_force":122.30469,"subtask_id":"push_to_goal","tcp_end":[0.49715,-0.04029,0.04625],"tcp_start":[0.49788,0.05318,0.05335],"tcp_to_object_dist_end":0.04565,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82192,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.2083,"descend_1.descend_speed":0.05431,"push_1.push_distance":0.12099,"push_1.push_speed":0.09482},"optimized_scores":{"best_composite_score":0.27676,"best_fitness_score":0.50676,"best_task_score":0.4749},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":508.0,"contact_point_centroid":[0.47939,-0.05531,-0.0004],"force_p95":128.57187,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.02008,"mean_force":39.74906,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48019,-0.06955,0.05173]},{"body_a":"attachment","body_b":"push_box","contact_count":213.0,"contact_point_centroid":[0.48618,-0.05311,0.0501],"force_p95":143.22089,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.98067,"mean_force":93.35107,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4787,-0.05936,0.05315]},{"body_a":"attachment","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.47818,-0.02403,0.04935],"force_p95":90.07266,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.53622,"mean_force":72.00601,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4677,-0.02387,0.05475]},{"body_a":"world","body_b":"push_box","contact_count":1496.0,"contact_point_centroid":[0.4714,-0.02418,-1e-05],"force_p95":4.43032,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.6312,"mean_force":1.21097,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46749,-0.02311,0.08254]},{"body_a":"world","body_b":"push_box","contact_count":2032.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48461,-0.011,0.20736]}],"total_contact_groups":5},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48155,-0.08481,0.02435],"final_tcp_position":[0.4906,-0.12424,0.04613],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":154.02008,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":630.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2032.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47018,-0.02238,0.11463],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":374.0,"n_steps_budget":750.0,"object_pos_end":[0.47182,-0.02421,0.02458],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1289,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":91.53622,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1516.0,"raw_peak_contact_force":91.53622,"subtask_id":"reach_object","tcp_end":[0.46833,-0.02392,0.05392],"tcp_start":[0.47018,-0.02238,0.11463],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":810.0,"object_pos_end":[0.48155,-0.08481,0.02435],"object_pos_start":[0.47182,-0.02421,0.02458],"object_to_goal_dist_end":0.06775,"object_to_goal_dist_start":0.1289,"object_z_max":0.03506,"peak_contact_force":0.37897,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":721.0,"raw_peak_contact_force":154.02008,"subtask_id":"push_to_goal","tcp_end":[0.4906,-0.12424,0.04613],"tcp_start":[0.46833,-0.02392,0.05392],"tcp_to_object_dist_end":0.04594,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```