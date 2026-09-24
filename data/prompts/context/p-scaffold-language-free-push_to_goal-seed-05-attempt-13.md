## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4719 | 0.75 | ❌ rejected |
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.2080 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4762 | 0.76 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4729 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1492 | 0.31 | ❌ rejected |

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

## Current Skill (Q=0.472) — your mutation base

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

- **Composite score**: 0.472
- **task_score** (E): 0.748
- **fitness_score**: 0.682  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0538 |
| push_1 | 1.00 | 1.00 | 0.1260 |
| retract_1 | 0.00 | 1.00 | 0.1658 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 3.667 | 3.360 | 9.692 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.020)→(0.501, -0.075, 0.024) | (0.521, 0.013, 0.025)→(0.514, -0.110, 0.028) | 0.165→0.048 | 1.00 / 3.667 | 54.180 | 91.925 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.075, 0.024)→(0.497, 0.071, 0.102) | (0.514, -0.110, 0.028)→(0.511, -0.107, 0.025) | 0.048→0.048 | 1.00 / 4.000 | 0.245 | 52.929 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.425
- goal_progress: 0.958
- terminal_score: 0.958
- phase_score: 0.849
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.847
- phase_breakdown.contact_score: 0.870

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.893
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.958
- **Median Q (composite search score)**: 0.370
- **K-run variance**: 0.0222
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.467


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70482,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03129,"push_1.push_depth":0.0998,"retract_1.retract_height":0.1507},"optimized_scores":{"best_composite_score":0.3629,"best_fitness_score":0.5729,"best_task_score":0.62309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":799.0,"contact_point_centroid":[0.55033,-0.01158,0.05466],"force_p95":115.20258,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.81759,"mean_force":77.46287,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51829,0.00384,0.0237]},{"body_a":"attachment","body_b":"push_box","contact_count":801.0,"contact_point_centroid":[0.53702,-0.00468,0.05219],"force_p95":102.0058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.3307,"mean_force":56.80334,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51832,0.00399,0.02369]},{"body_a":"world","body_b":"push_box","contact_count":1540.0,"contact_point_centroid":[0.54433,-0.04736,-0.00031],"force_p95":80.15123,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.8052,"mean_force":51.91658,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51803,0.00223,0.0239]},{"body_a":"push_box","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.55037,-0.06199,0.05577],"force_p95":77.66002,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.52302,"mean_force":37.90584,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50725,-0.05336,0.0305]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.52858,-0.0558,0.05982],"force_p95":59.10578,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.35576,"mean_force":20.64542,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5064,-0.04985,0.03159]},{"body_a":"world","body_b":"push_box","contact_count":3676.0,"contact_point_centroid":[0.52662,-0.08306,-3e-05],"force_p95":0.38795,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.41503,"mean_force":0.48236,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50123,0.02332,0.07124]},{"body_a":"attachment","body_b":"push_box","contact_count":208.0,"contact_point_centroid":[0.53795,0.05708,0.03818],"force_p95":6.32877,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.18062,"mean_force":2.48668,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5313,0.06904,0.02109]},{"body_a":"world","body_b":"push_box","contact_count":3487.0,"contact_point_centroid":[0.53691,0.03467,-1e-05],"force_p95":1.81171,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.54878,"mean_force":0.40082,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52895,0.09065,0.02594]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07292,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.526,-0.08307,0.02499],"final_tcp_position":[0.49886,0.08918,0.10979],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":125.81759,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.53989,0.02704,0.02503],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18148,"object_to_goal_dist_start":0.1905,"object_z_max":0.02509,"peak_contact_force":4.22911,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3695.0,"raw_peak_contact_force":7.18062,"tcp_end":[0.53191,0.06392,0.02001],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.03807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":900.0,"object_pos_end":[0.53477,-0.08471,0.03141],"object_pos_start":[0.53989,0.02704,0.02503],"object_to_goal_dist_end":0.07425,"object_to_goal_dist_start":0.18148,"object_z_max":0.03143,"peak_contact_force":110.96803,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3140.0,"raw_peak_contact_force":125.81759,"tcp_end":[0.50813,-0.05642,0.02936],"tcp_start":[0.53191,0.06392,0.02001],"tcp_to_object_dist_end":0.03891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.526,-0.08307,0.02499],"object_pos_start":[0.53477,-0.08471,0.03141],"object_to_goal_dist_end":0.0718,"object_to_goal_dist_start":0.07425,"object_z_max":0.0349,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3783.0,"raw_peak_contact_force":89.52302,"tcp_end":[0.49886,0.08918,0.10979],"tcp_start":[0.50813,-0.05642,0.02936],"tcp_to_object_dist_end":0.1939,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72258,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03901,"push_1.push_depth":0.09996,"retract_1.retract_height":0.08441},"optimized_scores":{"best_composite_score":0.6825,"best_fitness_score":0.8925,"best_task_score":0.95833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1101.0,"contact_point_centroid":[0.5088,-0.10918,-0.00012],"force_p95":58.85892,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.9788,"mean_force":22.02501,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49805,-0.05414,0.01989]},{"body_a":"push_box","body_b":"link7","contact_count":478.0,"contact_point_centroid":[0.52533,-0.05079,0.05252],"force_p95":46.24589,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.27531,"mean_force":31.42234,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49907,-0.02918,0.02012]},{"body_a":"attachment","body_b":"push_box","contact_count":740.0,"contact_point_centroid":[0.51175,-0.06366,0.04377],"force_p95":48.97195,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.13892,"mean_force":21.84801,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49807,-0.05237,0.01985]},{"body_a":"world","body_b":"push_box","contact_count":3942.0,"contact_point_centroid":[0.50073,-0.15533,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.82806,"mean_force":0.2765,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49325,-0.04141,0.05294]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.52538,-0.1402,0.05031],"force_p95":24.68153,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.20959,"mean_force":7.79625,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49529,-0.11936,0.01982]},{"body_a":"attachment","body_b":"push_box","contact_count":147.0,"contact_point_centroid":[0.5067,0.00186,0.03528],"force_p95":7.44943,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.43239,"mean_force":3.28261,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49974,0.01373,0.02131]},{"body_a":"world","body_b":"push_box","contact_count":2965.0,"contact_point_centroid":[0.50465,-0.02057,-1e-05],"force_p95":1.67818,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1286,"mean_force":0.41279,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.03696,0.02523]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51017,-0.13188,0.05011],"force_p95":0.78093,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.78093,"mean_force":0.78093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49587,-0.12001,0.01979]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]}],"total_contact_groups":9},"final_pose_error":0.13301,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5008,-0.15541,0.02499],"final_tcp_position":[0.49449,0.0322,0.08847],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75.9788,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":930.0,"object_pos_end":[0.50643,-0.0276,0.02507],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12257,"object_to_goal_dist_start":0.13127,"object_z_max":0.02514,"peak_contact_force":4.82094,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3112.0,"raw_peak_contact_force":9.43239,"tcp_end":[0.50013,0.00923,0.02063],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":781.0,"n_steps_budget":870.0,"object_pos_end":[0.50099,-0.15691,0.025],"object_pos_start":[0.50643,-0.0276,0.02507],"object_to_goal_dist_end":0.00699,"object_to_goal_dist_start":0.12257,"object_z_max":0.02807,"peak_contact_force":2.22396,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2319.0,"raw_peak_contact_force":75.9788,"tcp_end":[0.49587,-0.12001,0.01979],"tcp_start":[0.50013,0.00923,0.02063],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5008,-0.15541,0.02499],"object_pos_start":[0.50099,-0.15691,0.025],"object_to_goal_dist_end":0.00547,"object_to_goal_dist_start":0.00699,"object_z_max":0.02528,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3957.0,"raw_peak_contact_force":28.82806,"tcp_end":[0.49449,0.0322,0.08847],"tcp_start":[0.49587,-0.12001,0.01979],"tcp_to_object_dist_end":0.19816,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76471,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.0465,"push_1.push_depth":0.09948,"retract_1.retract_height":0.13395},"optimized_scores":{"best_composite_score":0.37027,"best_fitness_score":0.58027,"best_task_score":0.66173},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1352.0,"contact_point_centroid":[0.5234,-0.04284,-0.00014],"force_p95":59.99243,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.97993,"mean_force":35.33709,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50482,0.01123,0.02188]},{"body_a":"push_box","body_b":"link7","contact_count":768.0,"contact_point_centroid":[0.53182,-0.00456,0.05424],"force_p95":58.0052,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.10111,"mean_force":46.5207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50486,0.01326,0.02172]},{"body_a":"attachment","body_b":"push_box","contact_count":776.0,"contact_point_centroid":[0.52223,0.00365,0.04926],"force_p95":58.0177,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.07888,"mean_force":39.47197,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50491,0.01391,0.02171]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52783,-0.07394,0.05458],"force_p95":39.49217,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.43456,"mean_force":22.78225,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4996,-0.04929,0.02318]},{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.5191,-0.05643,0.05523],"force_p95":31.00651,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.99747,"mean_force":6.70878,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49859,-0.0461,0.02399]},{"body_a":"world","body_b":"push_box","contact_count":3863.0,"contact_point_centroid":[0.50517,-0.08365,-2e-05],"force_p95":0.24564,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.2827,"mean_force":0.28473,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49624,0.02397,0.06526]},{"body_a":"attachment","body_b":"push_box","contact_count":120.0,"contact_point_centroid":[0.51656,0.06849,0.03614],"force_p95":7.48044,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.46167,"mean_force":2.9432,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.08033,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":2352.0,"contact_point_centroid":[0.5152,0.04612,-1e-05],"force_p95":1.65642,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77995,"mean_force":0.40194,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50825,0.10195,0.02677]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.07295,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50515,-0.08314,0.02499],"final_tcp_position":[0.49647,0.09068,0.10769],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":73.97993,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":660.0,"n_steps_budget":750.0,"object_pos_end":[0.51706,0.03872,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18949,"object_to_goal_dist_start":0.19823,"object_z_max":0.02511,"peak_contact_force":1.02954,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2472.0,"raw_peak_contact_force":12.46167,"tcp_end":[0.51039,0.07559,0.02061],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":870.0,"object_pos_end":[0.50707,-0.0871,0.02871],"object_pos_start":[0.51706,0.03872,0.02494],"object_to_goal_dist_end":0.06341,"object_to_goal_dist_start":0.18949,"object_z_max":0.02929,"peak_contact_force":49.34656,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2896.0,"raw_peak_contact_force":73.97993,"tcp_end":[0.49999,-0.04956,0.02308],"tcp_start":[0.51039,0.07559,0.02061],"tcp_to_object_dist_end":0.03861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50515,-0.08314,0.02499],"object_pos_start":[0.50707,-0.0871,0.02871],"object_to_goal_dist_end":0.06706,"object_to_goal_dist_start":0.06341,"object_z_max":0.02871,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3914.0,"raw_peak_contact_force":40.43456,"tcp_end":[0.49647,0.09068,0.10769],"tcp_start":[0.49999,-0.04956,0.02308],"tcp_to_object_dist_end":0.19269,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```