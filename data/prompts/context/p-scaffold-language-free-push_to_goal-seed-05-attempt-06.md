## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1477 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4697 | 0.75 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.3815 | 0.00 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.76 | ✅ accepted |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4735 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.148) — your mutation base

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

- **Composite score**: 0.148
- **task_score** (E): 0.001
- **fitness_score**: 0.208  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1727 |
| contact_1 | 1.00 | 1.00 | 0.0783 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.2911 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.024, 0.133) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.514, 0.024, 0.133)→(0.513, 0.022, 0.055) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 25329.673 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.513, 0.022, 0.054)→(0.513, 0.022, 0.054) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 3.000 | 20.771 | 53.471 |
| retract_1 | retract | 1.00 / step_budget | (0.513, 0.022, 0.054)→(0.512, 0.022, 0.345) | (0.519, 0.022, 0.025)→(0.518, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 36.503 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.002
- lateral_force_integral: None
- approach_alignment: 0.056
- goal_progress: 0.001
- terminal_score: 0.001
- phase_score: 0.347
- phase_breakdown.push_progress_score: 0.000
- phase_breakdown.contact_alignment_score: 0.609
- phase_breakdown.approach_pre_contact_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.209
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.148
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.243


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72072,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.12765,"contact_1.contact_threshold":3.37203,"contact_1.speed":0.02603,"push_1.push_depth":0.20182,"retract_1.retract_height":0.11832},"optimized_scores":{"best_composite_score":0.14864,"best_fitness_score":0.20864,"best_task_score":0.00076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5419,0.03703,0.04988],"force_p95":49.23837,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.45099,"mean_force":29.61988,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53069,0.03697,0.05401]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.54125,0.03698,0.05019],"force_p95":35.98548,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.81454,"mean_force":11.36528,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53005,0.0369,0.0542]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.52409,0.03695,-1e-05],"force_p95":27.92005,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.0008,"mean_force":11.37369,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5307,0.03697,0.05403]},{"body_a":"world","body_b":"push_box","contact_count":3037.0,"contact_point_centroid":[0.53588,0.0368,-2e-05],"force_p95":0.24629,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.17319,"mean_force":0.29218,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52795,0.03671,0.17941]},{"body_a":"world","body_b":"push_box","contact_count":2052.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51376,0.02843,0.21892]},{"body_a":"world","body_b":"push_box","contact_count":1808.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52928,0.03748,0.09149]}],"total_contact_groups":6},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53632,0.03686,0.02499],"final_tcp_position":[0.52887,0.03679,0.30225],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":52.45099,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.53059,0.03824,0.1326],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":47.15334,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1808.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_alignment","tcp_end":[0.53074,0.03697,0.0541],"tcp_start":[0.53059,0.03824,0.1326],"tcp_to_object_dist_end":0.02969,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53655,0.03695,0.02502],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19049,"object_to_goal_dist_start":0.1905,"object_z_max":0.02504,"peak_contact_force":20.32479,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":52.45099,"subtask_id":"push_progress","tcp_end":[0.53059,0.03695,0.05384],"tcp_start":[0.53064,0.03696,0.05392],"tcp_to_object_dist_end":0.02943,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.53632,0.03686,0.02499],"object_pos_start":[0.53647,0.03694,0.02504],"object_to_goal_dist_end":0.19036,"object_to_goal_dist_start":0.19046,"object_z_max":0.0261,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3048.0,"raw_peak_contact_force":37.81454,"tcp_end":[0.52887,0.03679,0.30225],"tcp_start":[0.53059,0.03695,0.05384],"tcp_to_object_dist_end":0.27736,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85385,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05987,"contact_1.contact_threshold":4.04389,"contact_1.speed":0.03539,"push_1.push_depth":0.16424,"retract_1.retract_height":0.20581},"optimized_scores":{"best_composite_score":0.14673,"best_fitness_score":0.20673,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51033,-0.0172,0.04987],"force_p95":45.68696,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.68778,"mean_force":27.1759,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49946,-0.01715,0.0548]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.50965,-0.01721,0.05019],"force_p95":32.45418,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.28987,"mean_force":9.7576,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49879,-0.01716,0.05501]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.49207,-0.01881,-1e-05],"force_p95":24.9989,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.64079,"mean_force":10.45989,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49948,-0.01715,0.05482]},{"body_a":"world","body_b":"push_box","contact_count":3944.0,"contact_point_centroid":[0.50396,-0.0188,-1e-05],"force_p95":0.2454,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.46508,"mean_force":0.27609,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49709,-0.01713,0.22113]},{"body_a":"world","body_b":"push_box","contact_count":2132.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49968,0.00302,0.21537]},{"body_a":"world","body_b":"push_box","contact_count":1660.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49893,-0.01517,0.09221]}],"total_contact_groups":6},"final_pose_error":0.02514,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50432,-0.0188,0.02499],"final_tcp_position":[0.49834,-0.01713,0.38531],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":930.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.50096,-0.01318,0.13223],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":415.0,"n_steps_budget":900.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_alignment","tcp_end":[0.49952,-0.01714,0.05489],"tcp_start":[0.50096,-0.01318,0.13223],"tcp_to_object_dist_end":0.03038,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50453,-0.01881,0.02502],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02503,"peak_contact_force":18.67953,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":48.68778,"subtask_id":"push_progress","tcp_end":[0.49934,-0.01716,0.05463],"tcp_start":[0.4994,-0.01715,0.05471],"tcp_to_object_dist_end":0.0301,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,-0.0188,0.02499],"object_pos_start":[0.50445,-0.01881,0.02504],"object_to_goal_dist_end":0.13128,"object_to_goal_dist_start":0.13127,"object_z_max":0.02601,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3955.0,"raw_peak_contact_force":34.28987,"tcp_end":[0.49834,-0.01713,0.38531],"tcp_start":[0.49934,-0.01716,0.05463],"tcp_to_object_dist_end":0.36037,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00943,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.15585,"contact_1.contact_threshold":3.35173,"contact_1.speed":0.04753,"push_1.push_depth":0.24871,"retract_1.retract_height":0.16411},"optimized_scores":{"best_composite_score":0.14775,"best_fitness_score":0.20775,"best_task_score":0.00075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5207,0.04753,0.04988],"force_p95":55.84358,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.27525,"mean_force":35.84733,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50969,0.04737,0.05452]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.51995,0.04746,0.05031],"force_p95":35.34341,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.40589,"mean_force":10.58969,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50897,0.04728,0.0548]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.5025,0.04766,-1e-05],"force_p95":31.60953,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.41315,"mean_force":13.71095,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50971,0.04737,0.05454]},{"body_a":"world","body_b":"push_box","contact_count":3498.0,"contact_point_centroid":[0.51434,0.04746,-2e-05],"force_p95":0.24573,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.88909,"mean_force":0.287,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50718,0.04708,0.20315]},{"body_a":"world","body_b":"push_box","contact_count":2008.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50417,0.03289,0.22035]},{"body_a":"world","body_b":"push_box","contact_count":1612.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50882,0.04759,0.09262]}],"total_contact_groups":6},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5147,0.04754,0.02499],"final_tcp_position":[0.50828,0.0472,0.34852],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":59.27525,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.51055,0.04809,0.1337],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":403.0,"n_steps_budget":690.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":48.32768,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_alignment","tcp_end":[0.50974,0.04738,0.05463],"tcp_start":[0.51055,0.04809,0.1337],"tcp_to_object_dist_end":0.03011,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51496,0.04766,0.02502],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19822,"object_to_goal_dist_start":0.19823,"object_z_max":0.02505,"peak_contact_force":23.30822,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":59.27525,"subtask_id":"push_progress","tcp_end":[0.50958,0.04735,0.05432],"tcp_start":[0.50964,0.04736,0.05441],"tcp_to_object_dist_end":0.02979,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.5147,0.04754,0.02499],"object_pos_start":[0.51484,0.04764,0.02507],"object_to_goal_dist_end":0.19809,"object_to_goal_dist_start":0.1982,"object_z_max":0.02624,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3510.0,"raw_peak_contact_force":37.40589,"tcp_end":[0.50828,0.0472,0.34852],"tcp_start":[0.50958,0.04735,0.05432],"tcp_to_object_dist_end":0.32359,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```