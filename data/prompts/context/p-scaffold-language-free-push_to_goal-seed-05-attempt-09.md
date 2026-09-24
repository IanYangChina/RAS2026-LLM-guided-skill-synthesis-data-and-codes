## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1492 | 0.31 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4711 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4632 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1477 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4697 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.149) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: 0.149
- **task_score** (E): 0.313
- **fitness_score**: 0.559  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1982 |
| contact_1 | 1.00 | 1.00 | 0.0808 |
| push_1 | 1.00 | 1.00 | 0.1624 |
| retract_1 | 1.00 | 1.00 | 0.0903 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.040, 0.110) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.040, 0.110)→(0.545, 0.004, 0.045) | (0.519, 0.022, 0.025)→(0.525, 0.019, 0.025) | 0.173→0.171 | 1.00 / 3.000 | 188.778 | 234.489 |
| push_1 | push | 1.00 / step_budget | (0.545, 0.004, 0.045)→(0.498, -0.150, 0.022) | (0.525, 0.019, 0.025)→(0.517, -0.030, 0.025) | 0.171→0.121 | 1.00 / 4.000 | 0.245 | 127.192 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.150, 0.022)→(0.495, -0.149, 0.112) | (0.517, -0.030, 0.025)→(0.517, -0.030, 0.025) | 0.121→0.121 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.406
- lateral_force_integral: None
- approach_alignment: 0.788
- goal_progress: 0.405
- terminal_score: 0.405
- phase_score: 0.732
- phase_breakdown.reach_goal_score: 0.939
- phase_breakdown.reach_pre_contact_score: 0.249

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.601
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.405
- **Median Q (composite search score)**: 0.129
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.343


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78177,"average_solve_count":362.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.13667,"approach_1.speed":0.03993,"contact_1.speed":0.02097,"push_1.push_depth":0.01381,"push_1.speed":0.02519,"retract_1.retract_height":0.10093,"retract_1.speed":0.04572},"optimized_scores":{"best_composite_score":0.12719,"best_fitness_score":0.53719,"best_task_score":0.26307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":311.0,"contact_point_centroid":[0.55759,0.02791,0.04634],"force_p95":221.81112,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":233.75733,"mean_force":204.51596,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54777,0.02292,0.04594]},{"body_a":"world","body_b":"push_box","contact_count":1540.0,"contact_point_centroid":[0.5449,0.03328,-0.00041],"force_p95":145.32409,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.4493,"mean_force":41.70324,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53871,0.03242,0.06386]},{"body_a":"attachment","body_b":"push_box","contact_count":263.0,"contact_point_centroid":[0.56101,0.00855,0.04718],"force_p95":118.48388,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.04529,"mean_force":98.92035,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55662,-0.00221,0.04642]},{"body_a":"world","body_b":"push_box","contact_count":1937.0,"contact_point_centroid":[0.53578,-0.0057,-0.00022],"force_p95":98.58469,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.9005,"mean_force":13.81555,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52657,-0.07286,0.03229]},{"body_a":"world","body_b":"push_box","contact_count":2120.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51216,0.06351,0.21967]},{"body_a":"world","body_b":"push_box","contact_count":1108.0,"contact_point_centroid":[0.53201,-0.01331,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49482,-0.14828,0.06077]}],"total_contact_groups":6},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53201,-0.01331,0.02499],"final_tcp_position":[0.49462,-0.14806,0.10288],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":233.75733,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2120.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.53073,0.05391,0.1137],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.54344,0.0344,0.02501],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18945,"object_to_goal_dist_start":0.1905,"object_z_max":0.02541,"peak_contact_force":193.44106,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1851.0,"raw_peak_contact_force":233.75733,"subtask_id":"reach_pre_contact","tcp_end":[0.56033,0.01953,0.04464],"tcp_start":[0.53073,0.05391,0.1137],"tcp_to_object_dist_end":0.02987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.53201,-0.01331,0.02499],"object_pos_start":[0.54344,0.0344,0.02501],"object_to_goal_dist_end":0.14039,"object_to_goal_dist_start":0.18945,"object_z_max":0.0359,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2200.0,"raw_peak_contact_force":121.04529,"subtask_id":"reach_goal","tcp_end":[0.49772,-0.14889,0.02146],"tcp_start":[0.56033,0.01953,0.04464],"tcp_to_object_dist_end":0.1399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.53201,-0.01331,0.02499],"object_pos_start":[0.53201,-0.01331,0.02499],"object_to_goal_dist_end":0.14039,"object_to_goal_dist_start":0.14039,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49462,-0.14806,0.10288],"tcp_start":[0.49772,-0.14889,0.02146],"tcp_to_object_dist_end":0.16007,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.59271,"average_solve_count":329.0,"average_success_count":329.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.11359,"approach_1.speed":0.06378,"contact_1.speed":0.01016,"push_1.push_depth":0.01516,"push_1.speed":0.01736,"retract_1.retract_height":0.08536,"retract_1.speed":0.06991},"optimized_scores":{"best_composite_score":0.1913,"best_fitness_score":0.6013,"best_task_score":0.40546},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":419.0,"contact_point_centroid":[0.52778,-0.02737,0.04629],"force_p95":230.10883,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":238.62475,"mean_force":202.30591,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51974,-0.03422,0.04556]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.51591,-0.02258,-0.00049],"force_p95":145.06153,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.68796,"mean_force":49.93656,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51072,-0.02418,0.05968]},{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.53115,-0.0513,0.04647],"force_p95":129.38139,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.9233,"mean_force":105.67999,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53002,-0.06304,0.04478]},{"body_a":"world","body_b":"push_box","contact_count":1263.0,"contact_point_centroid":[0.5085,-0.05862,-0.00033],"force_p95":115.15195,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.40425,"mean_force":24.38435,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51704,-0.09699,0.03516]},{"body_a":"world","body_b":"push_box","contact_count":2116.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50002,0.04514,0.20265]},{"body_a":"world","body_b":"push_box","contact_count":868.0,"contact_point_centroid":[0.50471,-0.0721,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49573,-0.15,0.0541]}],"total_contact_groups":6},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50471,-0.0721,0.02499],"final_tcp_position":[0.49536,-0.14969,0.08817],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":238.62475,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.50124,0.00063,0.10565],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.51129,-0.02275,0.02444],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12776,"object_to_goal_dist_start":0.13127,"object_z_max":0.0252,"peak_contact_force":188.11187,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2131.0,"raw_peak_contact_force":238.62475,"subtask_id":"reach_pre_contact","tcp_end":[0.53209,-0.03914,0.04449],"tcp_start":[0.50124,0.00063,0.10565],"tcp_to_object_dist_end":0.03322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.50471,-0.0721,0.02499],"object_pos_start":[0.51129,-0.02275,0.02444],"object_to_goal_dist_end":0.07805,"object_to_goal_dist_start":0.12776,"object_z_max":0.03545,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1549.0,"raw_peak_contact_force":134.9233,"subtask_id":"reach_goal","tcp_end":[0.49854,-0.15054,0.02225],"tcp_start":[0.53209,-0.03914,0.04449],"tcp_to_object_dist_end":0.07874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":780.0,"object_pos_end":[0.50471,-0.0721,0.02499],"object_pos_start":[0.50471,-0.0721,0.02499],"object_to_goal_dist_end":0.07805,"object_to_goal_dist_start":0.07805,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":868.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49536,-0.14969,0.08817],"tcp_start":[0.49854,-0.15054,0.02225],"tcp_to_object_dist_end":0.1005,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90208,"average_solve_count":337.0,"average_success_count":337.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.10123,"approach_1.speed":0.06177,"contact_1.speed":0.0054,"push_1.push_depth":0.0146,"push_1.speed":0.03411,"retract_1.retract_height":0.14284,"retract_1.speed":0.09641},"optimized_scores":{"best_composite_score":0.12897,"best_fitness_score":0.53897,"best_task_score":0.26954},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":409.0,"contact_point_centroid":[0.53786,0.0402,0.0464],"force_p95":223.47062,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":231.08368,"mean_force":198.45038,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52947,0.03385,0.04571]},{"body_a":"world","body_b":"push_box","contact_count":1727.0,"contact_point_centroid":[0.52572,0.04416,-0.00046],"force_p95":140.76994,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.77672,"mean_force":47.4046,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52036,0.04293,0.06102]},{"body_a":"attachment","body_b":"push_box","contact_count":275.0,"contact_point_centroid":[0.542,0.01724,0.04702],"force_p95":119.35065,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.60888,"mean_force":96.00763,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53974,0.0057,0.04541]},{"body_a":"world","body_b":"push_box","contact_count":2101.0,"contact_point_centroid":[0.51736,0.00172,-0.00019],"force_p95":105.50615,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.88817,"mean_force":12.93587,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51793,-0.06892,0.03199]},{"body_a":"world","body_b":"push_box","contact_count":2408.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50336,0.08261,0.22552]},{"body_a":"world","body_b":"push_box","contact_count":1528.0,"contact_point_centroid":[0.51499,-0.00597,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,-0.14932,0.08192]}],"total_contact_groups":6},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51499,-0.00597,0.02499],"final_tcp_position":[0.49478,-0.14924,0.14471],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":231.08368,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2408.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.51106,0.06652,0.10976],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.52169,0.045,0.02463],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.1962,"object_to_goal_dist_start":0.19823,"object_z_max":0.0255,"peak_contact_force":184.77989,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2136.0,"raw_peak_contact_force":231.08368,"subtask_id":"reach_pre_contact","tcp_end":[0.54192,0.03063,0.04452],"tcp_start":[0.51106,0.06652,0.10976],"tcp_to_object_dist_end":0.03179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":707.0,"n_steps_budget":1000.0,"object_pos_end":[0.51499,-0.00597,0.02499],"object_pos_start":[0.52169,0.045,0.02463],"object_to_goal_dist_end":0.1448,"object_to_goal_dist_start":0.1962,"object_z_max":0.03541,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2376.0,"raw_peak_contact_force":125.60888,"subtask_id":"reach_goal","tcp_end":[0.49761,-0.15003,0.02141],"tcp_start":[0.54192,0.03063,0.04452],"tcp_to_object_dist_end":0.14514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":930.0,"object_pos_end":[0.51499,-0.00597,0.02499],"object_pos_start":[0.51499,-0.00597,0.02499],"object_to_goal_dist_end":0.1448,"object_to_goal_dist_start":0.1448,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1528.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49478,-0.14924,0.14471],"tcp_start":[0.49761,-0.15003,0.02141],"tcp_to_object_dist_end":0.1878,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```