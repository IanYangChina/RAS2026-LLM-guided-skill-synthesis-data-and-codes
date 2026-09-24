## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4639 | 0.71 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0256 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.1426 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.729, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.464) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  generator: linear_cartesian
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

```

## Design Metrics

- **Composite score**: 0.464
- **task_score** (E): 0.706
- **fitness_score**: 0.674  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2802 |
| contact_1 | 1.00 | 1.00 | 0.0451 |
| push_1 | 1.00 | 1.00 | 0.1282 |
| retract_1 | 0.00 | 1.00 | 0.1665 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.077, 0.036) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.077, 0.036)→(0.509, 0.034, 0.021) | (0.513, 0.002, 0.025)→(0.515, -0.004, 0.025) | 0.160→0.154 | 1.00 / 3.000 | 1.019 | 5.614 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.034, 0.021)→(0.504, -0.088, 0.026) | (0.515, -0.004, 0.025)→(0.518, -0.117, 0.029) | 0.154→0.050 | 1.00 / 3.333 | 83.654 | 101.117 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.088, 0.026)→(0.497, 0.061, 0.100) | (0.518, -0.117, 0.029)→(0.514, -0.114, 0.025) | 0.050→0.049 | 1.00 / 4.000 | 0.245 | 58.053 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.981
- lateral_force_integral: None
- approach_alignment: 0.424
- goal_progress: 0.845
- terminal_score: 0.845
- phase_score: 0.782
- phase_breakdown.contact_score: 0.703
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.814

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.807
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.845
- **Median Q (composite search score)**: 0.433
- **K-run variance**: 0.0098
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.305,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06336,"contact_1.speed":0.01945,"push_1.push_depth":0.09437},"optimized_scores":{"best_composite_score":0.59746,"best_fitness_score":0.80746,"best_task_score":0.84501},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":679.0,"contact_point_centroid":[0.46824,-0.0669,0.02158],"force_p95":16.72647,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.98098,"mean_force":4.45806,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46822,-0.05501,0.02026]},{"body_a":"world","body_b":"push_box","contact_count":1585.0,"contact_point_centroid":[0.46651,-0.09451,-5e-05],"force_p95":6.88816,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.0609,"mean_force":2.17975,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46774,-0.05333,0.02045]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.4786,-0.02065,0.0501],"force_p95":7.42419,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.58213,"mean_force":1.90132,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45006,-0.00867,0.02061]},{"body_a":"world","body_b":"push_box","contact_count":3998.0,"contact_point_centroid":[0.48047,-0.15389,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97014,"mean_force":0.24603,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49155,-0.04166,0.05266]},{"body_a":"world","body_b":"push_box","contact_count":3600.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47372,0.02263,0.1666]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44552,0.02638,0.02701]}],"total_contact_groups":6},"final_pose_error":0.13256,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48048,-0.1539,0.02499],"final_tcp_position":[0.49345,0.0327,0.08859],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":30.98098,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3600.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44886,0.04566,0.03428],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44575,0.01045,0.02399],"tcp_start":[0.44886,0.04566,0.03428],"tcp_to_object_dist_end":0.04229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":837.0,"n_steps_budget":930.0,"object_pos_end":[0.48064,-0.15352,0.025],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01968,"object_to_goal_dist_start":0.12843,"object_z_max":0.02543,"peak_contact_force":1.62881,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2275.0,"raw_peak_contact_force":30.98098,"tcp_end":[0.49346,-0.11886,0.02001],"tcp_start":[0.44575,0.01045,0.02399],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48048,-0.1539,0.02499],"object_pos_start":[0.48064,-0.15352,0.025],"object_to_goal_dist_end":0.01991,"object_to_goal_dist_start":0.01968,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3998.0,"raw_peak_contact_force":0.97014,"tcp_end":[0.49345,0.0327,0.08859],"tcp_start":[0.49346,-0.11886,0.02001],"tcp_to_object_dist_end":0.19757,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26291,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03116,"contact_1.speed":0.03633,"push_1.push_depth":0.09935},"optimized_scores":{"best_composite_score":0.43282,"best_fitness_score":0.64282,"best_task_score":0.6538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":786.0,"contact_point_centroid":[0.56114,-0.0461,0.05448],"force_p95":122.85402,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.64627,"mean_force":80.50181,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52699,-0.03179,0.02403]},{"body_a":"world","body_b":"push_box","contact_count":1576.0,"contact_point_centroid":[0.55513,-0.07894,-0.00034],"force_p95":91.64233,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.98682,"mean_force":51.51647,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52716,-0.03137,0.02403]},{"body_a":"attachment","body_b":"push_box","contact_count":799.0,"contact_point_centroid":[0.54619,-0.03932,0.05406],"force_p95":85.35063,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.453,"mean_force":52.00401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52731,-0.03082,0.02395]},{"body_a":"world","body_b":"push_box","contact_count":3693.0,"contact_point_centroid":[0.53577,-0.10722,-3e-05],"force_p95":0.25303,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.78183,"mean_force":0.51694,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50281,-0.00778,0.06634]},{"body_a":"push_box","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.55002,-0.09645,0.05741],"force_p95":67.17869,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.46637,"mean_force":29.65214,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50895,-0.0866,0.03085]},{"body_a":"attachment","body_b":"push_box","contact_count":60.0,"contact_point_centroid":[0.53381,-0.08886,0.06208],"force_p95":47.04672,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.44617,"mean_force":18.27159,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50851,-0.08476,0.03126]},{"body_a":"attachment","body_b":"push_box","contact_count":168.0,"contact_point_centroid":[0.55413,0.02188,0.04126],"force_p95":7.64537,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.34771,"mean_force":3.43488,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54735,0.03387,0.02196]},{"body_a":"world","body_b":"push_box","contact_count":2769.0,"contact_point_centroid":[0.55325,-0.00119,-1e-05],"force_p95":2.27438,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.54493,"mean_force":0.4635,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54426,0.05256,0.02893]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52126,0.03684,0.16994]}],"total_contact_groups":9},"final_pose_error":0.10196,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53525,-0.10708,0.02499],"final_tcp_position":[0.50011,0.06077,0.10068],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":141.64627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54466,0.07412,0.04176],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":789.0,"n_steps_budget":900.0,"object_pos_end":[0.55571,-0.00793,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1526,"object_to_goal_dist_start":0.16043,"object_z_max":0.02514,"peak_contact_force":2.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2937.0,"raw_peak_contact_force":9.34771,"tcp_end":[0.54826,0.02893,0.02021],"tcp_start":[0.54466,0.07412,0.04176],"tcp_to_object_dist_end":0.03791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":900.0,"object_pos_end":[0.54095,-0.11561,0.03119],"object_pos_start":[0.55571,-0.00793,0.02499],"object_to_goal_dist_end":0.05383,"object_to_goal_dist_start":0.1526,"object_z_max":0.03121,"peak_contact_force":122.05353,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3161.0,"raw_peak_contact_force":141.64627,"tcp_end":[0.5101,-0.09064,0.02983],"tcp_start":[0.54826,0.02893,0.02021],"tcp_to_object_dist_end":0.03972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53525,-0.10708,0.02499],"object_pos_start":[0.54095,-0.11561,0.03119],"object_to_goal_dist_end":0.05554,"object_to_goal_dist_start":0.05383,"object_z_max":0.0347,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3803.0,"raw_peak_contact_force":82.78183,"tcp_end":[0.50011,0.06077,0.10068],"tcp_start":[0.5101,-0.09064,0.02983],"tcp_to_object_dist_end":0.18745,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72941,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08756,"contact_1.speed":0.03036,"push_1.push_depth":0.09852},"optimized_scores":{"best_composite_score":0.36142,"best_fitness_score":0.57142,"best_task_score":0.61817},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":763.0,"contact_point_centroid":[0.54944,-0.01092,0.05497],"force_p95":116.26104,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.72484,"mean_force":78.35984,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51819,0.00433,0.02368]},{"body_a":"attachment","body_b":"push_box","contact_count":767.0,"contact_point_centroid":[0.53682,-0.00412,0.05199],"force_p95":101.85948,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.37393,"mean_force":57.85933,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51826,0.00464,0.02366]},{"body_a":"world","body_b":"push_box","contact_count":1515.0,"contact_point_centroid":[0.54325,-0.04497,-0.0003],"force_p95":81.16283,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.35513,"mean_force":51.19289,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51829,0.00457,0.0237]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54935,-0.06031,0.05579],"force_p95":81.2704,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.40757,"mean_force":39.12291,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50685,-0.05074,0.03027]},{"body_a":"world","body_b":"push_box","contact_count":3689.0,"contact_point_centroid":[0.52551,-0.08166,-3e-05],"force_p95":0.25467,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.88635,"mean_force":0.49529,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50099,0.02487,0.07108]},{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.53047,-0.05425,0.06112],"force_p95":65.30791,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.81254,"mean_force":25.13402,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50638,-0.04884,0.03086]},{"body_a":"attachment","body_b":"push_box","contact_count":211.0,"contact_point_centroid":[0.53776,0.0571,0.03716],"force_p95":6.24167,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.2494,"mean_force":2.7546,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53129,0.06905,0.02056]},{"body_a":"world","body_b":"push_box","contact_count":3153.0,"contact_point_centroid":[0.53699,0.03426,-1e-05],"force_p95":2.07524,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.45458,"mean_force":0.43646,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52919,0.08853,0.02354]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51443,0.05528,0.16455]}],"total_contact_groups":9},"final_pose_error":0.07202,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52496,-0.08168,0.02499],"final_tcp_position":[0.49874,0.0902,0.10988],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":130.72484,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5308,0.11083,0.03182],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.5396,0.02732,0.02514],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18169,"object_to_goal_dist_start":0.1905,"object_z_max":0.02517,"peak_contact_force":0.8129,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3364.0,"raw_peak_contact_force":7.2494,"tcp_end":[0.53194,0.06402,0.01989],"tcp_start":[0.5308,0.11083,0.03182],"tcp_to_object_dist_end":0.03785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":870.0,"object_pos_end":[0.5335,-0.0829,0.03128],"object_pos_start":[0.5396,0.02732,0.02514],"object_to_goal_dist_end":0.07526,"object_to_goal_dist_start":0.18169,"object_z_max":0.03134,"peak_contact_force":127.27944,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3045.0,"raw_peak_contact_force":130.72484,"tcp_end":[0.50775,-0.05401,0.02902],"tcp_start":[0.53194,0.06402,0.01989],"tcp_to_object_dist_end":0.03877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52496,-0.08168,0.02499],"object_pos_start":[0.5335,-0.0829,0.03128],"object_to_goal_dist_end":0.07274,"object_to_goal_dist_start":0.07526,"object_z_max":0.03492,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3789.0,"raw_peak_contact_force":90.40757,"tcp_end":[0.49874,0.0902,0.10988],"tcp_start":[0.50775,-0.05401,0.02902],"tcp_to_object_dist_end":0.19348,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```