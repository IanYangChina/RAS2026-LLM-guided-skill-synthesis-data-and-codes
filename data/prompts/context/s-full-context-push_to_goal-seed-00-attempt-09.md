## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0690 | 0.51 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0248 | 0.00 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0363 | 0.00 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2595 | 0.00 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1678 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.51 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.069) — your mutation base

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

- **Composite score**: 0.069
- **task_score** (E): 0.512
- **fitness_score**: 0.429  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1739 |
| descend_1 | 1.00 | 1.00 | 0.0893 |
| push_1 | 0.67 | 1.00 | 0.3271 |
| retract_1 | 1.00 | 1.00 | 0.1718 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.028, 0.134) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.028, 0.134)→(0.509, 0.028, 0.046) | (0.496, 0.001, 0.025)→(0.500, 0.001, 0.025) | 0.152→0.153 | 1.00 / 3.333 | 242.150 | 251.905 |
| push_1 | push | 0.67 / step_budget | (0.509, 0.028, 0.046)→(0.502, -0.294, 0.021) | (0.500, 0.001, 0.025)→(0.512, -0.074, 0.025) | 0.153→0.077 | 1.00 / 4.000 | 0.245 | 195.593 |
| retract_1 | retract | 1.00 / step_budget | (0.502, -0.294, 0.021)→(0.497, -0.159, 0.123) | (0.512, -0.074, 0.025)→(0.512, -0.074, 0.025) | 0.077→0.077 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.593
- lateral_force_integral: None
- approach_alignment: 0.831
- goal_progress: 0.592
- terminal_score: 0.592
- phase_score: 0.434
- phase_breakdown.push_to_goal_score: 0.592
- phase_breakdown.reach_object_score: 0.067

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.497
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.592
- **Median Q (composite search score)**: 0.094
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.343


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72078,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11258,"descend_1.descend_speed":0.04282,"push_1.push_distance":0.15605,"push_1.push_speed":0.13439,"retract_1.retract_height":0.19877,"retract_1.retract_speed":0.17679},"optimized_scores":{"best_composite_score":0.13738,"best_fitness_score":0.49738,"best_task_score":0.59188},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":356.0,"contact_point_centroid":[0.53303,-0.00276,0.04583],"force_p95":232.66268,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":233.73011,"mean_force":181.21712,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52204,-0.0007,0.04855]},{"body_a":"world","body_b":"push_box","contact_count":2842.0,"contact_point_centroid":[0.51943,-0.02423,-0.00023],"force_p95":177.80417,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":224.14311,"mean_force":23.05639,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51397,4e-05,0.07747]},{"body_a":"world","body_b":"push_box","contact_count":2441.0,"contact_point_centroid":[0.51312,-0.08145,-0.00035],"force_p95":159.6399,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":184.93584,"mean_force":30.68275,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50505,-0.14646,0.03537]},{"body_a":"attachment","body_b":"push_box","contact_count":479.0,"contact_point_centroid":[0.53818,-0.05268,0.04624],"force_p95":178.25008,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":183.58811,"mean_force":154.03032,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52788,-0.05558,0.04832]},{"body_a":"world","body_b":"push_box","contact_count":2092.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50497,0.00102,0.21733]},{"body_a":"world","body_b":"push_box","contact_count":2288.0,"contact_point_centroid":[0.50387,-0.09976,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48036,-0.23624,0.08358]}],"total_contact_groups":6},"final_pose_error":0.01305,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50387,-0.09976,0.02499],"final_tcp_position":[0.49464,-0.16089,0.12021],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":233.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":990.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5119,0.00211,0.13386],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.51971,-0.02813,0.02512],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12345,"object_to_goal_dist_start":0.12347,"object_z_max":0.0251,"peak_contact_force":228.64575,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3198.0,"raw_peak_contact_force":233.73011,"subtask_id":"reach_object","tcp_end":[0.53136,-0.00032,0.04533],"tcp_start":[0.5119,0.00211,0.13386],"tcp_to_object_dist_end":0.0363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":866.0,"n_steps_budget":1000.0,"object_pos_end":[0.50387,-0.09976,0.02499],"object_pos_start":[0.51971,-0.02813,0.02512],"object_to_goal_dist_end":0.05039,"object_to_goal_dist_start":0.12345,"object_z_max":0.03489,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2920.0,"raw_peak_contact_force":184.93584,"subtask_id":"push_to_goal","tcp_end":[0.47453,-0.28491,0.02028],"tcp_start":[0.53136,-0.00032,0.04533],"tcp_to_object_dist_end":0.18752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50387,-0.09976,0.02499],"object_pos_start":[0.50387,-0.09976,0.02499],"object_to_goal_dist_end":0.05039,"object_to_goal_dist_start":0.05039,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2288.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49464,-0.16089,0.12021],"tcp_start":[0.47453,-0.28491,0.02028],"tcp_to_object_dist_end":0.11354,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05147,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.21867,"descend_1.descend_speed":0.09769,"push_1.push_distance":0.19308,"push_1.push_speed":0.10438,"retract_1.retract_height":0.12967,"retract_1.retract_speed":0.12017},"optimized_scores":{"best_composite_score":-0.02456,"best_fitness_score":0.33544,"best_task_score":0.40352},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":168.0,"contact_point_centroid":[0.5151,0.07889,0.04617],"force_p95":248.43836,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":249.45418,"mean_force":189.36473,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50416,0.08028,0.04928]},{"body_a":"world","body_b":"push_box","contact_count":2063.0,"contact_point_centroid":[0.50361,0.05612,-0.00014],"force_p95":139.9292,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":242.28104,"mean_force":15.77095,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49786,0.07839,0.08184]},{"body_a":"attachment","body_b":"push_box","contact_count":482.0,"contact_point_centroid":[0.5271,0.03524,0.04658],"force_p95":166.51494,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.21991,"mean_force":148.27313,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51672,0.03283,0.04944]},{"body_a":"world","body_b":"push_box","contact_count":2686.0,"contact_point_centroid":[0.52068,-0.00612,-0.00032],"force_p95":145.11933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":167.85852,"mean_force":27.43147,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50553,-0.08589,0.03673]},{"body_a":"push_box","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.52831,-0.01087,0.08161],"force_p95":28.20768,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.03157,"mean_force":14.8602,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50713,-0.05144,0.03834]},{"body_a":"world","body_b":"push_box","contact_count":2104.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49829,0.03843,0.21545]},{"body_a":"world","body_b":"push_box","contact_count":2768.0,"contact_point_centroid":[0.52247,-0.03037,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49294,-0.21778,0.08306]}],"total_contact_groups":7},"final_pose_error":0.01016,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52247,-0.03037,0.02499],"final_tcp_position":[0.49624,-0.15808,0.12012],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":249.45418,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49806,0.07789,0.1319],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":560.0,"n_steps_budget":690.0,"object_pos_end":[0.50588,0.0556,0.02456],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20569,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":240.8232,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2231.0,"raw_peak_contact_force":249.45418,"subtask_id":"reach_object","tcp_end":[0.51308,0.08237,0.0458],"tcp_start":[0.49806,0.07789,0.1319],"tcp_to_object_dist_end":0.03492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52247,-0.03037,0.02499],"object_pos_start":[0.50588,0.0556,0.02456],"object_to_goal_dist_end":0.12172,"object_to_goal_dist_start":0.20569,"object_z_max":0.0432,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3230.0,"raw_peak_contact_force":182.21991,"subtask_id":"push_to_goal","tcp_end":[0.49482,-0.24543,0.02426],"tcp_start":[0.51308,0.08237,0.0458],"tcp_to_object_dist_end":0.21683,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.52247,-0.03037,0.02499],"object_pos_start":[0.52247,-0.03037,0.02499],"object_to_goal_dist_end":0.12172,"object_to_goal_dist_start":0.12172,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2768.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49624,-0.15808,0.12012],"tcp_start":[0.49482,-0.24543,0.02426],"tcp_to_object_dist_end":0.16139,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.39098,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13022,"descend_1.descend_speed":0.11974,"push_1.push_distance":0.23388,"push_1.push_speed":0.14956,"retract_1.retract_height":0.15043,"retract_1.retract_speed":0.1516},"optimized_scores":{"best_composite_score":0.09405,"best_fitness_score":0.45405,"best_task_score":0.53997},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":143.0,"contact_point_centroid":[0.48496,0.00138,0.04592],"force_p95":265.54428,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":272.53145,"mean_force":204.75095,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47442,0.0029,0.04978]},{"body_a":"world","body_b":"push_box","contact_count":2021.0,"contact_point_centroid":[0.47327,-0.02269,-0.00013],"force_p95":125.30445,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":260.49199,"mean_force":14.84359,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46912,0.00353,0.08475]},{"body_a":"attachment","body_b":"push_box","contact_count":384.0,"contact_point_centroid":[0.50429,-0.03903,0.04642],"force_p95":195.72375,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":219.62218,"mean_force":124.7417,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49868,-0.04626,0.04782]},{"body_a":"world","body_b":"push_box","contact_count":2933.0,"contact_point_centroid":[0.50651,-0.08036,-0.0002],"force_p95":106.44176,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.40409,"mean_force":16.69137,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5146,-0.1975,0.03178]},{"body_a":"world","body_b":"push_box","contact_count":2004.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48486,0.00255,0.21803]},{"body_a":"world","body_b":"push_box","contact_count":3664.0,"contact_point_centroid":[0.51046,-0.09157,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52152,-0.28325,0.11364]}],"total_contact_groups":6},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51046,-0.09157,0.02499],"final_tcp_position":[0.49875,-0.15919,0.12833],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":272.53145,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":870.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47056,0.00526,0.13484],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":539.0,"n_steps_budget":600.0,"object_pos_end":[0.47527,-0.02348,0.0245],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12892,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":256.98049,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2164.0,"raw_peak_contact_force":272.53145,"subtask_id":"reach_object","tcp_end":[0.48311,0.00336,0.04607],"tcp_start":[0.47056,0.00526,0.13484],"tcp_to_object_dist_end":0.03532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51046,-0.09157,0.02499],"object_pos_start":[0.47527,-0.02348,0.0245],"object_to_goal_dist_end":0.05936,"object_to_goal_dist_start":0.12892,"object_z_max":0.03543,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3317.0,"raw_peak_contact_force":219.62218,"subtask_id":"push_to_goal","tcp_end":[0.53697,-0.35273,0.01979],"tcp_start":[0.48311,0.00336,0.04607],"tcp_to_object_dist_end":0.26255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":916.0,"n_steps_budget":960.0,"object_pos_end":[0.51046,-0.09157,0.02499],"object_pos_start":[0.51046,-0.09157,0.02499],"object_to_goal_dist_end":0.05936,"object_to_goal_dist_start":0.05936,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3664.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49875,-0.15919,0.12833],"tcp_start":[0.53697,-0.35273,0.01979],"tcp_to_object_dist_end":0.12405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```