## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4632 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1477 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4697 | 0.75 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.3815 | 0.00 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.463) — your mutation base

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

- **Composite score**: 0.463
- **task_score** (E): 0.734
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0537 |
| push_1 | 1.00 | 1.00 | 0.1242 |
| retract_1 | 0.00 | 1.00 | 0.1656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 3.000 | 2.945 | 9.354 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.020)→(0.502, -0.073, 0.025) | (0.521, 0.013, 0.025)→(0.517, -0.107, 0.029) | 0.165→0.050 | 1.00 / 3.000 | 62.576 | 97.181 |
| retract_1 | retract | 0.00 / step_budget | (0.502, -0.073, 0.025)→(0.497, 0.072, 0.103) | (0.517, -0.107, 0.029)→(0.513, -0.104, 0.025) | 0.050→0.051 | 1.00 / 4.000 | 0.245 | 57.962 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.424
- goal_progress: 0.963
- terminal_score: 0.963
- phase_score: 0.840
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.831
- phase_breakdown.contact_score: 0.866

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.889
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.963
- **Median Q (composite search score)**: 0.361
- **K-run variance**: 0.0233
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.365


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71779,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03394,"push_1.push_depth":0.09958,"retract_1.retract_height":0.08471},"optimized_scores":{"best_composite_score":0.3606,"best_fitness_score":0.5706,"best_task_score":0.62041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":798.0,"contact_point_centroid":[0.54988,-0.01151,0.05475],"force_p95":114.75371,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.47169,"mean_force":76.51576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51818,0.00405,0.02366]},{"body_a":"attachment","body_b":"push_box","contact_count":802.0,"contact_point_centroid":[0.537,-0.00433,0.05215],"force_p95":100.63065,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.09772,"mean_force":57.09287,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51825,0.00437,0.02364]},{"body_a":"world","body_b":"push_box","contact_count":1528.0,"contact_point_centroid":[0.54461,-0.04705,-0.00032],"force_p95":79.49308,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.09717,"mean_force":51.96062,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51788,0.00214,0.0239]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.5498,-0.0616,0.0558],"force_p95":82.87535,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.42821,"mean_force":38.87031,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50702,-0.0525,0.03038]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.5282,-0.05489,0.05958],"force_p95":60.66898,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.92252,"mean_force":20.9456,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50613,-0.04876,0.03157]},{"body_a":"world","body_b":"push_box","contact_count":3683.0,"contact_point_centroid":[0.52598,-0.08234,-3e-05],"force_p95":0.25624,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.82045,"mean_force":0.4915,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50107,0.0237,0.07106]},{"body_a":"attachment","body_b":"push_box","contact_count":186.0,"contact_point_centroid":[0.53835,0.05725,0.03915],"force_p95":6.2601,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.12882,"mean_force":2.74804,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5313,0.06919,0.02114]},{"body_a":"world","body_b":"push_box","contact_count":3182.0,"contact_point_centroid":[0.5369,0.03462,-1e-05],"force_p95":1.89489,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.07903,"mean_force":0.41406,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52894,0.0909,0.02602]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07276,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52544,-0.08231,0.02499],"final_tcp_position":[0.49878,0.0894,0.10974],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":130.47169,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.53908,0.02727,0.02513],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18153,"object_to_goal_dist_start":0.1905,"object_z_max":0.02519,"peak_contact_force":1.55934,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3368.0,"raw_peak_contact_force":8.12882,"tcp_end":[0.53189,0.06413,0.02006],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.0379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":900.0,"object_pos_end":[0.53404,-0.08427,0.03142],"object_pos_start":[0.53908,0.02727,0.02513],"object_to_goal_dist_end":0.0743,"object_to_goal_dist_start":0.18153,"object_z_max":0.03141,"peak_contact_force":113.44764,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3128.0,"raw_peak_contact_force":130.47169,"tcp_end":[0.50787,-0.05564,0.02917],"tcp_start":[0.53189,0.06413,0.02006],"tcp_to_object_dist_end":0.03885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52544,-0.08231,0.02499],"object_pos_start":[0.53404,-0.08427,0.03142],"object_to_goal_dist_end":0.07231,"object_to_goal_dist_start":0.0743,"object_z_max":0.03496,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3793.0,"raw_peak_contact_force":91.42821,"tcp_end":[0.49878,0.0894,0.10974],"tcp_start":[0.50787,-0.05564,0.02917],"tcp_to_object_dist_end":0.19333,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04755,"push_1.push_depth":0.09903,"retract_1.retract_height":0.15579},"optimized_scores":{"best_composite_score":0.67917,"best_fitness_score":0.88917,"best_task_score":0.96347},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1031.0,"contact_point_centroid":[0.5094,-0.10756,-0.00014],"force_p95":63.39127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.324,"mean_force":23.36777,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49798,-0.0531,0.01992]},{"body_a":"push_box","body_b":"link7","contact_count":490.0,"contact_point_centroid":[0.52525,-0.05259,0.05247],"force_p95":46.52426,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.43402,"mean_force":31.21179,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49888,-0.03066,0.02013]},{"body_a":"attachment","body_b":"push_box","contact_count":736.0,"contact_point_centroid":[0.51215,-0.0628,0.04468],"force_p95":49.53764,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.78627,"mean_force":21.45095,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49801,-0.0515,0.0199]},{"body_a":"push_box","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.52496,-0.13852,0.05033],"force_p95":7.8183,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.32115,"mean_force":5.06991,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49405,-0.11355,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":3847.0,"contact_point_centroid":[0.50086,-0.15431,-2e-05],"force_p95":0.24625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.61476,"mean_force":0.30589,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49323,-0.03877,0.05372]},{"body_a":"attachment","body_b":"push_box","contact_count":106.0,"contact_point_centroid":[0.50637,0.00218,0.03473],"force_p95":9.06577,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.90629,"mean_force":3.7862,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49971,0.01403,0.02135]},{"body_a":"world","body_b":"push_box","contact_count":2531.0,"contact_point_centroid":[0.50466,-0.02011,-1e-05],"force_p95":1.52913,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.72005,"mean_force":0.4081,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49817,0.03741,0.02535]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51019,-0.13052,0.05015],"force_p95":1.13102,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.19055,"mean_force":0.59527,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49581,-0.11868,0.01977]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]}],"total_contact_groups":9},"final_pose_error":0.13249,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50092,-0.15471,0.02499],"final_tcp_position":[0.49447,0.0328,0.08847],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":81.324,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.50568,-0.02703,0.02497],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.1231,"object_to_goal_dist_start":0.13127,"object_z_max":0.02518,"peak_contact_force":6.19481,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2637.0,"raw_peak_contact_force":9.90629,"tcp_end":[0.5001,0.0098,0.02072],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.0375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":776.0,"n_steps_budget":870.0,"object_pos_end":[0.49997,-0.15548,0.0251],"object_pos_start":[0.50568,-0.02703,0.02497],"object_to_goal_dist_end":0.00549,"object_to_goal_dist_start":0.1231,"object_z_max":0.02844,"peak_contact_force":0.1942,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2257.0,"raw_peak_contact_force":81.324,"tcp_end":[0.49583,-0.11863,0.01978],"tcp_start":[0.5001,0.0098,0.02072],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,-0.15471,0.02499],"object_pos_start":[0.49997,-0.15548,0.0251],"object_to_goal_dist_end":0.0048,"object_to_goal_dist_start":0.00549,"object_z_max":0.02729,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3887.0,"raw_peak_contact_force":19.32115,"tcp_end":[0.49447,0.0328,0.08847],"tcp_start":[0.49583,-0.11863,0.01978],"tcp_to_object_dist_end":0.19806,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72956,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03683,"push_1.push_depth":0.09828,"retract_1.retract_height":0.10437},"optimized_scores":{"best_composite_score":0.34973,"best_fitness_score":0.55973,"best_task_score":0.6195},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":776.0,"contact_point_centroid":[0.52353,0.00495,0.0499],"force_p95":72.27771,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.74821,"mean_force":46.11536,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50566,0.01481,0.02234]},{"body_a":"world","body_b":"push_box","contact_count":1400.0,"contact_point_centroid":[0.52569,-0.04369,-0.0002],"force_p95":57.59905,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.73941,"mean_force":40.99441,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50548,0.01033,0.02263]},{"body_a":"push_box","body_b":"link7","contact_count":769.0,"contact_point_centroid":[0.53322,-0.00297,0.05472],"force_p95":72.44302,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.1653,"mean_force":56.84792,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50562,0.01426,0.02236]},{"body_a":"push_box","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53516,-0.06711,0.05522],"force_p95":60.25794,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.138,"mean_force":28.28102,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50183,-0.04459,0.02592]},{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.52286,-0.05093,0.05671],"force_p95":44.38942,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.04491,"mean_force":12.30238,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50106,-0.04184,0.02669]},{"body_a":"world","body_b":"push_box","contact_count":3819.0,"contact_point_centroid":[0.51297,-0.07629,-2e-05],"force_p95":0.25009,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.05633,"mean_force":0.32882,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49786,0.02835,0.06812]},{"body_a":"attachment","body_b":"push_box","contact_count":168.0,"contact_point_centroid":[0.51567,0.06811,0.03394],"force_p95":7.22538,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.0278,"mean_force":3.50283,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51002,0.07996,0.0216]},{"body_a":"world","body_b":"push_box","contact_count":2945.0,"contact_point_centroid":[0.51507,0.0458,-1e-05],"force_p95":2.37177,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51439,"mean_force":0.44856,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50829,0.10091,0.02647]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.06827,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51259,-0.07563,0.02499],"final_tcp_position":[0.49722,0.09459,0.11021],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":79.74821,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":819.0,"n_steps_budget":930.0,"object_pos_end":[0.51723,0.03826,0.02502],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18905,"object_to_goal_dist_start":0.19823,"object_z_max":0.02508,"peak_contact_force":1.08211,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3113.0,"raw_peak_contact_force":10.0278,"tcp_end":[0.51049,0.07507,0.02053],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":870.0,"object_pos_end":[0.51585,-0.08254,0.03008],"object_pos_start":[0.51723,0.03826,0.02502],"object_to_goal_dist_end":0.06948,"object_to_goal_dist_start":0.18905,"object_z_max":0.03012,"peak_contact_force":74.08731,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2945.0,"raw_peak_contact_force":79.74821,"tcp_end":[0.5026,-0.04621,0.02537],"tcp_start":[0.51049,0.07507,0.02053],"tcp_to_object_dist_end":0.03896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51259,-0.07563,0.02499],"object_pos_start":[0.51585,-0.08254,0.03008],"object_to_goal_dist_end":0.07543,"object_to_goal_dist_start":0.06948,"object_z_max":0.03008,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3897.0,"raw_peak_contact_force":63.138,"tcp_end":[0.49722,0.09459,0.11021],"tcp_start":[0.5026,-0.04621,0.02537],"tcp_to_object_dist_end":0.19098,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```