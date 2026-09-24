## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4711 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4632 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1477 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4697 | 0.75 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.3815 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.763, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.471) — your mutation base

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

- **Composite score**: 0.471
- **task_score** (E): 0.746
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0540 |
| push_1 | 1.00 | 1.00 | 0.1258 |
| retract_1 | 0.00 | 1.00 | 0.1658 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.049, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.164 | 1.00 / 3.000 | 0.723 | 8.817 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.049, 0.020)→(0.501, -0.075, 0.024) | (0.521, 0.013, 0.025)→(0.513, -0.110, 0.028) | 0.164→0.047 | 1.00 / 3.333 | 55.450 | 96.780 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.075, 0.024)→(0.497, 0.071, 0.102) | (0.513, -0.110, 0.028)→(0.509, -0.108, 0.025) | 0.047→0.048 | 1.00 / 4.000 | 0.245 | 45.421 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.425
- goal_progress: 0.942
- terminal_score: 0.942
- phase_score: 0.847
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.843
- phase_breakdown.contact_score: 0.871

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.885
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.942
- **Median Q (composite search score)**: 0.377
- **K-run variance**: 0.0207
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.433


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03742,"push_1.push_depth":0.09969,"retract_1.retract_height":0.14946},"optimized_scores":{"best_composite_score":0.3615,"best_fitness_score":0.5715,"best_task_score":0.62384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":796.0,"contact_point_centroid":[0.54949,-0.01166,0.05473],"force_p95":114.42437,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.72566,"mean_force":75.35542,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.518,0.00403,0.02356]},{"body_a":"attachment","body_b":"push_box","contact_count":799.0,"contact_point_centroid":[0.53682,-0.00454,0.05232],"force_p95":99.79805,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.73446,"mean_force":55.04949,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51806,0.00427,0.02355]},{"body_a":"world","body_b":"push_box","contact_count":1512.0,"contact_point_centroid":[0.54409,-0.04788,-0.00031],"force_p95":77.89804,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.34293,"mean_force":51.41484,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51764,0.00179,0.02383]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54921,-0.06211,0.05572],"force_p95":81.31952,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.11236,"mean_force":39.85977,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50676,-0.05226,0.03017]},{"body_a":"world","body_b":"push_box","contact_count":3687.0,"contact_point_centroid":[0.52526,-0.08274,-3e-05],"force_p95":0.25161,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.79876,"mean_force":0.49187,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50094,0.02378,0.07092]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.52834,-0.05504,0.05972],"force_p95":62.81671,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.41209,"mean_force":22.46642,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50597,-0.04897,0.0312]},{"body_a":"attachment","body_b":"push_box","contact_count":162.0,"contact_point_centroid":[0.53792,0.0574,0.03815],"force_p95":6.73281,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.60136,"mean_force":2.77549,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53127,0.06934,0.02116]},{"body_a":"world","body_b":"push_box","contact_count":2906.0,"contact_point_centroid":[0.53689,0.03479,-1e-05],"force_p95":1.78946,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.39139,"mean_force":0.40773,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52894,0.09108,0.02608]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07273,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52472,-0.08274,0.02499],"final_tcp_position":[0.49872,0.08947,0.10969],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":128.72566,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":930.0,"object_pos_end":[0.53929,0.02761,0.02502],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1819,"object_to_goal_dist_start":0.1905,"object_z_max":0.02512,"peak_contact_force":1.02004,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3068.0,"raw_peak_contact_force":8.60136,"tcp_end":[0.53188,0.06442,0.02013],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.03787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":900.0,"object_pos_end":[0.53323,-0.08456,0.03139],"object_pos_start":[0.53929,0.02761,0.02502],"object_to_goal_dist_end":0.07368,"object_to_goal_dist_start":0.1819,"object_z_max":0.03139,"peak_contact_force":113.91952,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3107.0,"raw_peak_contact_force":128.72566,"tcp_end":[0.50766,-0.05539,0.02899],"tcp_start":[0.53188,0.06442,0.02013],"tcp_to_object_dist_end":0.03886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52472,-0.08274,0.02499],"object_pos_start":[0.53323,-0.08456,0.03139],"object_to_goal_dist_end":0.07166,"object_to_goal_dist_start":0.07368,"object_z_max":0.03483,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3795.0,"raw_peak_contact_force":90.11236,"tcp_end":[0.49872,0.08947,0.10969],"tcp_start":[0.50766,-0.05539,0.02899],"tcp_to_object_dist_end":0.19367,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71795,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03771,"push_1.push_depth":0.09942,"retract_1.retract_height":0.09046},"optimized_scores":{"best_composite_score":0.67464,"best_fitness_score":0.88464,"best_task_score":0.94164},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1042.0,"contact_point_centroid":[0.50818,-0.10772,-0.00012],"force_p95":64.17701,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.61434,"mean_force":20.73205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49765,-0.05597,0.01961]},{"body_a":"attachment","body_b":"push_box","contact_count":721.0,"contact_point_centroid":[0.51063,-0.06411,0.04247],"force_p95":46.87529,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.24661,"mean_force":19.64151,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49775,-0.05273,0.0196]},{"body_a":"push_box","body_b":"link7","contact_count":440.0,"contact_point_centroid":[0.52532,-0.0484,0.05211],"force_p95":46.60857,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.96442,"mean_force":30.16078,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49881,-0.02648,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.50737,0.00196,0.03669],"force_p95":7.25954,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.38855,"mean_force":3.1073,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49973,0.01382,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":3047.0,"contact_point_centroid":[0.50492,-0.02076,-1e-05],"force_p95":1.76698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39551,"mean_force":0.40954,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.03694,0.02522]},{"body_a":"world","body_b":"push_box","contact_count":3965.0,"contact_point_centroid":[0.49795,-0.15729,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80239,"mean_force":0.24765,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49325,-0.0417,0.05267]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50071,-0.1316,0.02987],"force_p95":0.06289,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06988,"mean_force":0.02329,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49584,-0.11968,0.01978]}],"total_contact_groups":8},"final_pose_error":0.13304,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49807,-0.15741,0.02499],"final_tcp_position":[0.49449,0.03221,0.08839],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":78.61434,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":850.0,"n_steps_budget":960.0,"object_pos_end":[0.50686,-0.02771,0.02498],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12249,"object_to_goal_dist_start":0.13127,"object_z_max":0.02515,"peak_contact_force":0.00036,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3202.0,"raw_peak_contact_force":9.38855,"tcp_end":[0.50011,0.00908,0.02058],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":776.0,"n_steps_budget":870.0,"object_pos_end":[0.49825,-0.15646,0.0251],"object_pos_start":[0.50686,-0.02771,0.02498],"object_to_goal_dist_end":0.00669,"object_to_goal_dist_start":0.12249,"object_z_max":0.02799,"peak_contact_force":1.58374,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2203.0,"raw_peak_contact_force":78.61434,"tcp_end":[0.49588,-0.1196,0.0198],"tcp_start":[0.50011,0.00908,0.02058],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49807,-0.15741,0.02499],"object_pos_start":[0.49825,-0.15646,0.0251],"object_to_goal_dist_end":0.00766,"object_to_goal_dist_start":0.00669,"object_z_max":0.0251,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3968.0,"raw_peak_contact_force":0.80239,"tcp_end":[0.49449,0.03221,0.08839],"tcp_start":[0.49588,-0.1196,0.0198],"tcp_to_object_dist_end":0.19997,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70303,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03048,"push_1.push_depth":0.09994,"retract_1.retract_height":0.18316},"optimized_scores":{"best_composite_score":0.37725,"best_fitness_score":0.58725,"best_task_score":0.67152},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1340.0,"contact_point_centroid":[0.5229,-0.04522,-0.00015],"force_p95":59.24031,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.00017,"mean_force":35.72288,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50491,0.01009,0.02178]},{"body_a":"push_box","body_b":"link7","contact_count":769.0,"contact_point_centroid":[0.53183,-0.00642,0.05418],"force_p95":58.58631,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.9323,"mean_force":45.92948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50496,0.01209,0.02162]},{"body_a":"attachment","body_b":"push_box","contact_count":775.0,"contact_point_centroid":[0.52264,0.00231,0.05],"force_p95":60.16965,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.46008,"mean_force":40.20684,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.505,0.01256,0.02161]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52733,-0.07609,0.0547],"force_p95":43.22924,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.34762,"mean_force":22.44998,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49951,-0.05084,0.02306]},{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.51829,-0.05803,0.05406],"force_p95":34.08709,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.22318,"mean_force":6.7061,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49849,-0.04763,0.02386]},{"body_a":"world","body_b":"push_box","contact_count":3848.0,"contact_point_centroid":[0.50441,-0.08551,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.48051,"mean_force":0.28394,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49616,0.02322,0.06534]},{"body_a":"attachment","body_b":"push_box","contact_count":208.0,"contact_point_centroid":[0.51556,0.06787,0.03364],"force_p95":6.83193,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.46092,"mean_force":2.75072,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51001,0.07975,0.02154]},{"body_a":"world","body_b":"push_box","contact_count":3500.0,"contact_point_centroid":[0.51532,0.04579,-1e-05],"force_p95":1.85651,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.09435,"mean_force":0.41271,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50828,0.10047,0.02633]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.07335,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50445,-0.08504,0.02499],"final_tcp_position":[0.49644,0.09021,0.10765],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":83.00017,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.51699,0.03777,0.02505],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18854,"object_to_goal_dist_start":0.19823,"object_z_max":0.02509,"peak_contact_force":1.14923,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3708.0,"raw_peak_contact_force":8.46092,"tcp_end":[0.51048,0.0745,0.02037],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":780.0,"n_steps_budget":870.0,"object_pos_end":[0.50643,-0.0891,0.02899],"object_pos_start":[0.51699,0.03777,0.02505],"object_to_goal_dist_end":0.06137,"object_to_goal_dist_start":0.18854,"object_z_max":0.0294,"peak_contact_force":50.84585,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2884.0,"raw_peak_contact_force":83.00017,"tcp_end":[0.49988,-0.05118,0.02295],"tcp_start":[0.51048,0.0745,0.02037],"tcp_to_object_dist_end":0.03895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50445,-0.08504,0.02499],"object_pos_start":[0.50643,-0.0891,0.02899],"object_to_goal_dist_end":0.06512,"object_to_goal_dist_start":0.06137,"object_z_max":0.02901,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3899.0,"raw_peak_contact_force":45.34762,"tcp_end":[0.49644,0.09021,0.10765],"tcp_start":[0.49988,-0.05118,0.02295],"tcp_to_object_dist_end":0.19393,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```