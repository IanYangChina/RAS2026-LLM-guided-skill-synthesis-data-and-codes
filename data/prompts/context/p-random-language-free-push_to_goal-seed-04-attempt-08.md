## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1413 | 0.37 | ❌ rejected |
| 7 | approach → push → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 4 | -0.0682 | 0.00 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1801 | 0.00 | ❌ rejected |
| 5 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4202 | 0.80 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | -0.0657 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
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
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.810, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5531667326686841, 0.0013593063377233885, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.141) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.141
- **task_score** (E): 0.372
- **fitness_score**: 0.421  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2572 |
| push_1 | 1.00 | 1.00 | 0.1424 |
| retract_1 | 0.00 | 1.00 | 0.4542 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.533, 0.006, 0.047) | (0.531, 0.007, 0.025)→(0.534, 0.007, 0.024) | 0.161→0.161 | 1.00 / 5.000 | 276.674 | 307.194 |
| push_1 | push | 1.00 / step_budget | (0.533, 0.006, 0.047)→(0.500, -0.132, 0.044) | (0.534, 0.007, 0.024)→(0.525, -0.052, 0.025) | 0.161→0.102 | 1.00 / 4.000 | 0.253 | 162.282 |
| retract_1 | retract | 0.00 / step_budget | (0.500, -0.132, 0.044)→(0.106, -0.028, 0.244) | (0.525, -0.052, 0.025)→(0.525, -0.052, 0.025) | 0.102→0.102 | 1.00 / 4.000 | 0.245 | 0.253 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.429
- lateral_force_integral: None
- approach_alignment: 0.549
- goal_progress: 0.429
- terminal_score: 0.429
- phase_score: 0.492
- phase_breakdown.push_to_goal_score: 0.431
- phase_breakdown.reach_pre_contact_score: 0.633

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.467
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.429
- **Median Q (composite search score)**: 0.157
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.293


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1465,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.178,"push_1.push_distance":0.14871,"push_1.push_speed":0.12666,"push_1.push_tolerance":0.03808,"retract_1.retract_speed":0.05941},"optimized_scores":{"best_composite_score":0.15715,"best_fitness_score":0.43715,"best_task_score":0.38948},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":34.0,"contact_point_centroid":[0.55906,0.00114,0.04719],"force_p95":301.41772,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":302.5037,"mean_force":270.1985,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54764,0.00112,0.04911]},{"body_a":"attachment","body_b":"push_box","contact_count":247.0,"contact_point_centroid":[0.55287,-0.02525,0.04956],"force_p95":140.76892,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.03354,"mean_force":96.28283,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54411,-0.03153,0.05106]},{"body_a":"world","body_b":"push_box","contact_count":1972.0,"contact_point_centroid":[0.55323,0.00136,-3e-05],"force_p95":21.00842,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.73997,"mean_force":4.93532,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52244,0.00057,0.16914]},{"body_a":"world","body_b":"push_box","contact_count":837.0,"contact_point_centroid":[0.54758,-0.03616,-0.00036],"force_p95":80.40964,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.05614,"mean_force":28.87285,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53243,-0.05615,0.04797]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53922,-0.06025,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24526,"mean_force":0.24524,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.30694,-0.07305,0.14018]}],"total_contact_groups":5},"final_pose_error":0.12448,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53922,-0.06025,0.02499],"final_tcp_position":[0.10783,-0.02558,0.24331],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":302.5037,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":493.0,"n_steps_budget":990.0,"object_pos_end":[0.556,0.00136,0.02369],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16139,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":273.93824,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2006.0,"raw_peak_contact_force":302.5037,"subtask_id":"reach_pre_contact","tcp_end":[0.55289,0.00114,0.04687],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":750.0,"object_pos_end":[0.53921,-0.06026,0.02497],"object_pos_start":[0.556,0.00136,0.02369],"object_to_goal_dist_end":0.09793,"object_to_goal_dist_start":0.16139,"object_z_max":0.03524,"peak_contact_force":0.24526,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1084.0,"raw_peak_contact_force":150.03354,"subtask_id":"push_to_goal","tcp_end":[0.50459,-0.11966,0.04298],"tcp_start":[0.55289,0.00114,0.04687],"tcp_to_object_dist_end":0.07107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53922,-0.06025,0.02499],"object_pos_start":[0.53921,-0.06026,0.02497],"object_to_goal_dist_end":0.09794,"object_to_goal_dist_start":0.09793,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24526,"tcp_end":[0.10783,-0.02558,0.24331],"tcp_start":[0.50459,-0.11966,0.04298],"tcp_to_object_dist_end":0.48473,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22024,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1524,"push_1.push_distance":0.21121,"push_1.push_speed":0.14394,"push_1.push_tolerance":0.03084,"retract_1.retract_speed":0.07699},"optimized_scores":{"best_composite_score":0.08017,"best_fitness_score":0.36017,"best_task_score":0.29742},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.54432,0.03304,0.04715],"force_p95":302.7057,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":307.40622,"mean_force":262.66273,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53304,0.03298,0.04947]},{"body_a":"attachment","body_b":"push_box","contact_count":202.0,"contact_point_centroid":[0.5435,0.00996,0.04924],"force_p95":150.10355,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.72605,"mean_force":98.73491,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53517,0.00345,0.05088]},{"body_a":"world","body_b":"push_box","contact_count":2008.0,"contact_point_centroid":[0.53666,0.03697,-3e-05],"force_p95":20.276,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.35087,"mean_force":5.25093,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51487,0.01696,0.16872]},{"body_a":"world","body_b":"push_box","contact_count":1415.0,"contact_point_centroid":[0.53318,-0.00879,-0.00021],"force_p95":86.99989,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.14064,"mean_force":14.43533,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51548,-0.06833,0.04554]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53101,-0.0198,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.30117,-0.09377,0.14035]}],"total_contact_groups":5},"final_pose_error":0.12437,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53101,-0.0198,0.02499],"final_tcp_position":[0.10576,-0.03283,0.24338],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":307.40622,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.5393,0.03728,0.02367],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19136,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":272.19948,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2046.0,"raw_peak_contact_force":307.40622,"subtask_id":"reach_pre_contact","tcp_end":[0.5384,0.03384,0.04713],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":930.0,"object_pos_end":[0.53101,-0.0198,0.02499],"object_pos_start":[0.5393,0.03728,0.02367],"object_to_goal_dist_end":0.13384,"object_to_goal_dist_start":0.19136,"object_z_max":0.0352,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1617.0,"raw_peak_contact_force":153.72605,"subtask_id":"push_to_goal","tcp_end":[0.49515,-0.15366,0.04321],"tcp_start":[0.5384,0.03384,0.04713],"tcp_to_object_dist_end":0.13978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53101,-0.0198,0.02499],"object_pos_start":[0.53101,-0.0198,0.02499],"object_to_goal_dist_end":0.13384,"object_to_goal_dist_start":0.13384,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.10576,-0.03283,0.24338],"tcp_start":[0.49515,-0.15366,0.04321],"tcp_to_object_dist_end":0.47822,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13208,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.18599,"push_1.push_distance":0.12328,"push_1.push_speed":0.09418,"push_1.push_tolerance":0.04244,"retract_1.retract_speed":0.08277},"optimized_scores":{"best_composite_score":0.18652,"best_fitness_score":0.46652,"best_task_score":0.42881},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.51463,-0.01694,0.04702],"force_p95":309.62853,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":311.67151,"mean_force":281.09255,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50367,-0.01689,0.05005]},{"body_a":"attachment","body_b":"push_box","contact_count":222.0,"contact_point_centroid":[0.51827,-0.04383,0.04882],"force_p95":171.29224,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":183.08661,"mean_force":114.15817,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50946,-0.04917,0.05118]},{"body_a":"world","body_b":"push_box","contact_count":1883.0,"contact_point_centroid":[0.50464,-0.0188,-3e-05],"force_p95":19.39326,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.16634,"mean_force":5.05637,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50005,-0.00864,0.1699]},{"body_a":"world","body_b":"push_box","contact_count":681.0,"contact_point_centroid":[0.50713,-0.0485,-0.00049],"force_p95":118.31466,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.54312,"mean_force":37.72623,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50718,-0.06257,0.04952]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50398,-0.07512,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26899,"mean_force":0.24506,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.30187,-0.07365,0.14202]}],"total_contact_groups":5},"final_pose_error":0.11964,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50398,-0.07512,0.02499],"final_tcp_position":[0.10338,-0.02515,0.2453],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":311.67151,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":471.0,"n_steps_budget":930.0,"object_pos_end":[0.50682,-0.01899,0.02362],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.1312,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":283.88292,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1915.0,"raw_peak_contact_force":311.67151,"subtask_id":"reach_pre_contact","tcp_end":[0.50763,-0.0173,0.04764],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":840.0,"object_pos_end":[0.50393,-0.07548,0.0245],"object_pos_start":[0.50682,-0.01899,0.02362],"object_to_goal_dist_end":0.07462,"object_to_goal_dist_start":0.1312,"object_z_max":0.03515,"peak_contact_force":0.26824,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":903.0,"raw_peak_contact_force":183.08661,"subtask_id":"push_to_goal","tcp_end":[0.49917,-0.12137,0.04441],"tcp_start":[0.50763,-0.0173,0.04764],"tcp_to_object_dist_end":0.05025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50398,-0.07512,0.02499],"object_pos_start":[0.50393,-0.07548,0.0245],"object_to_goal_dist_end":0.07498,"object_to_goal_dist_start":0.07462,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.26899,"tcp_end":[0.10338,-0.02515,0.2453],"tcp_start":[0.49917,-0.12137,0.04441],"tcp_to_object_dist_end":0.4599,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```