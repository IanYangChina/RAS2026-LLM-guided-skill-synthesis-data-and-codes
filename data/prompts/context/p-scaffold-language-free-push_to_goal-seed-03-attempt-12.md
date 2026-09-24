## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4501 | 0.63 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4593 | 0.65 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4794 | 0.72 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4570 | 0.64 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4557 | 0.63 | ❌ rejected |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.450) — your mutation base

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

- **Composite score**: 0.450
- **task_score** (E): 0.634
- **fitness_score**: 0.660  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2803 |
| contact_1 | 1.00 | 1.00 | 0.0496 |
| push_1 | 1.00 | 1.00 | 0.1260 |
| retract_1 | 0.00 | 1.00 | 0.1666 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.077, 0.036) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.077, 0.036)→(0.509, 0.030, 0.021) | (0.513, 0.002, 0.025)→(0.515, -0.007, 0.025) | 0.160→0.152 | 1.00 / 3.333 | 2.994 | 10.160 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.021)→(0.504, -0.090, 0.026) | (0.515, -0.007, 0.025)→(0.510, -0.113, 0.029) | 0.152→0.058 | 1.00 / 4.000 | 82.035 | 107.062 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.090, 0.026)→(0.497, 0.060, 0.099) | (0.510, -0.113, 0.029)→(0.505, -0.108, 0.025) | 0.058→0.059 | 1.00 / 4.000 | 0.245 | 59.219 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.831
- lateral_force_integral: None
- approach_alignment: 0.434
- goal_progress: 0.638
- terminal_score: 0.638
- phase_score: 0.850
- phase_breakdown.contact_score: 0.885
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.841

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.765
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.640
- **Median Q (composite search score)**: 0.429
- **K-run variance**: 0.0062
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.228


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28497,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05911,"contact_1.speed":0.03821,"push_1.push_depth":0.08968},"optimized_scores":{"best_composite_score":0.55515,"best_fitness_score":0.76515,"best_task_score":0.63833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1382.0,"contact_point_centroid":[0.45701,-0.10817,-6e-05],"force_p95":33.73365,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.84584,"mean_force":5.84964,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47199,-0.07152,0.01939]},{"body_a":"attachment","body_b":"push_box","contact_count":598.0,"contact_point_centroid":[0.47067,-0.06817,0.03007],"force_p95":26.84247,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.07673,"mean_force":9.52538,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46619,-0.05676,0.0194]},{"body_a":"push_box","body_b":"link7","contact_count":203.0,"contact_point_centroid":[0.47909,-0.04224,0.05043],"force_p95":22.94048,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.19386,"mean_force":16.39278,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45191,-0.0193,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":139.0,"contact_point_centroid":[0.45463,-0.01083,0.03541],"force_p95":9.14613,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.01372,"mean_force":3.87417,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4461,0.00106,0.02237]},{"body_a":"world","body_b":"push_box","contact_count":2796.0,"contact_point_centroid":[0.45045,-0.03297,-1e-05],"force_p95":2.15353,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.75657,"mean_force":0.44134,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44574,0.02173,0.02634]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.47635,-0.01488,0.05009],"force_p95":3.1132,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.38361,"mean_force":1.13083,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44626,-0.00303,0.02164]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48612,-0.13251,0.02306],"force_p95":3.1684,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.1684,"mean_force":3.1684,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4931,-0.12334,0.01978]},{"body_a":"world","body_b":"push_box","contact_count":3997.0,"contact_point_centroid":[0.45506,-0.13826,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76443,"mean_force":0.24594,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49136,-0.04602,0.05193]},{"body_a":"world","body_b":"push_box","contact_count":3692.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47373,0.02261,0.1667]}],"total_contact_groups":9},"final_pose_error":0.13706,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45506,-0.13824,0.02499],"final_tcp_position":[0.49328,0.0283,0.08732],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":47.84584,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3692.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44889,0.04563,0.03444],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":764.0,"n_steps_budget":870.0,"object_pos_end":[0.45128,-0.04046,0.02485],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11989,"object_to_goal_dist_start":0.12843,"object_z_max":0.02508,"peak_contact_force":5.34568,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2941.0,"raw_peak_contact_force":12.01372,"tcp_end":[0.44626,-0.00349,0.02156],"tcp_start":[0.44889,0.04563,0.03444],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45533,-0.13809,0.02491],"object_pos_start":[0.45128,-0.04046,0.02485],"object_to_goal_dist_end":0.04623,"object_to_goal_dist_start":0.11989,"object_z_max":0.02935,"peak_contact_force":0.37709,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2183.0,"raw_peak_contact_force":47.84584,"tcp_end":[0.49325,-0.12324,0.01985],"tcp_start":[0.44626,-0.00349,0.02156],"tcp_to_object_dist_end":0.04104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45506,-0.13824,0.02499],"object_pos_start":[0.45533,-0.13809,0.02491],"object_to_goal_dist_end":0.04645,"object_to_goal_dist_start":0.04623,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3998.0,"raw_peak_contact_force":3.1684,"tcp_end":[0.49328,0.0283,0.08732],"tcp_start":[0.49325,-0.12324,0.01985],"tcp_to_object_dist_end":0.18188,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26636,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01578,"contact_1.speed":0.03552,"push_1.push_depth":0.09985},"optimized_scores":{"best_composite_score":0.4292,"best_fitness_score":0.6392,"best_task_score":0.64009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":815.0,"contact_point_centroid":[0.56088,-0.04617,0.05466],"force_p95":123.39795,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.49477,"mean_force":81.09904,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52703,-0.03201,0.02409]},{"body_a":"world","body_b":"push_box","contact_count":1632.0,"contact_point_centroid":[0.55468,-0.07936,-0.00034],"force_p95":90.87038,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.15633,"mean_force":51.86793,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52716,-0.0317,0.02409]},{"body_a":"attachment","body_b":"push_box","contact_count":821.0,"contact_point_centroid":[0.54614,-0.03995,0.05401],"force_p95":83.91185,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.7022,"mean_force":53.33337,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52719,-0.03155,0.02407]},{"body_a":"world","body_b":"push_box","contact_count":3653.0,"contact_point_centroid":[0.53565,-0.1043,-3e-05],"force_p95":0.299,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.4298,"mean_force":0.53336,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50269,-0.00751,0.06665]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.55028,-0.09609,0.05722],"force_p95":67.68975,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.53854,"mean_force":29.20104,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50879,-0.08701,0.03089]},{"body_a":"attachment","body_b":"push_box","contact_count":71.0,"contact_point_centroid":[0.53267,-0.08851,0.06143],"force_p95":47.11432,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.71611,"mean_force":15.95702,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50807,-0.08387,0.03162]},{"body_a":"attachment","body_b":"push_box","contact_count":168.0,"contact_point_centroid":[0.55413,0.02188,0.04126],"force_p95":7.64537,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.34771,"mean_force":3.43488,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54735,0.03387,0.02196]},{"body_a":"world","body_b":"push_box","contact_count":2769.0,"contact_point_centroid":[0.55325,-0.00119,-1e-05],"force_p95":2.27438,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.54493,"mean_force":0.4635,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54426,0.05256,0.02893]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52126,0.03684,0.16994]}],"total_contact_groups":9},"final_pose_error":0.10216,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53514,-0.10418,0.02499],"final_tcp_position":[0.50006,0.06054,0.10066],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":142.49477,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54466,0.07412,0.04176],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":789.0,"n_steps_budget":900.0,"object_pos_end":[0.55571,-0.00793,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1526,"object_to_goal_dist_start":0.16043,"object_z_max":0.02514,"peak_contact_force":2.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2937.0,"raw_peak_contact_force":9.34771,"tcp_end":[0.54826,0.02893,0.02021],"tcp_start":[0.54466,0.07412,0.04176],"tcp_to_object_dist_end":0.03791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":930.0,"object_pos_end":[0.54076,-0.11602,0.03119],"object_pos_start":[0.55571,-0.00793,0.02499],"object_to_goal_dist_end":0.05342,"object_to_goal_dist_start":0.1526,"object_z_max":0.0312,"peak_contact_force":121.76732,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3268.0,"raw_peak_contact_force":142.49477,"tcp_end":[0.50996,-0.09126,0.02979],"tcp_start":[0.54826,0.02893,0.02021],"tcp_to_object_dist_end":0.03955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53514,-0.10418,0.02499],"object_pos_start":[0.54076,-0.11602,0.03119],"object_to_goal_dist_end":0.05774,"object_to_goal_dist_start":0.05342,"object_z_max":0.03465,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3776.0,"raw_peak_contact_force":83.4298,"tcp_end":[0.50006,0.06054,0.10066],"tcp_start":[0.50996,-0.09126,0.02979],"tcp_to_object_dist_end":0.18464,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7764,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08949,"contact_1.speed":0.04286,"push_1.push_depth":0.1},"optimized_scores":{"best_composite_score":0.36589,"best_fitness_score":0.57589,"best_task_score":0.62507},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":798.0,"contact_point_centroid":[0.54929,-0.01143,0.05466],"force_p95":113.25952,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.84527,"mean_force":74.86586,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51797,0.00436,0.02344]},{"body_a":"attachment","body_b":"push_box","contact_count":792.0,"contact_point_centroid":[0.5365,-0.00494,0.05188],"force_p95":101.56168,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.31483,"mean_force":55.41244,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51789,0.00394,0.02348]},{"body_a":"world","body_b":"push_box","contact_count":1510.0,"contact_point_centroid":[0.54416,-0.04715,-0.00031],"force_p95":76.67218,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.20353,"mean_force":51.32296,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51762,0.00208,0.02371]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54855,-0.06245,0.05577],"force_p95":81.78612,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.05911,"mean_force":39.84517,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50651,-0.05195,0.03006]},{"body_a":"world","body_b":"push_box","contact_count":3690.0,"contact_point_centroid":[0.52457,-0.08276,-3e-05],"force_p95":0.25232,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.7381,"mean_force":0.49644,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5008,0.02394,0.07085]},{"body_a":"attachment","body_b":"push_box","contact_count":65.0,"contact_point_centroid":[0.52783,-0.05494,0.05947],"force_p95":63.76826,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.28235,"mean_force":22.49262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50571,-0.04857,0.03114]},{"body_a":"attachment","body_b":"push_box","contact_count":139.0,"contact_point_centroid":[0.53834,0.05753,0.03877],"force_p95":8.03769,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.1181,"mean_force":2.84034,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53125,0.06948,0.02055]},{"body_a":"world","body_b":"push_box","contact_count":2304.0,"contact_point_centroid":[0.53662,0.03459,-1e-05],"force_p95":1.67048,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.63649,"mean_force":0.42576,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52916,0.08976,0.02357]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51447,0.05539,0.16429]}],"total_contact_groups":9},"final_pose_error":0.07255,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52402,-0.08274,0.02499],"final_tcp_position":[0.49865,0.08967,0.10973],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":130.84527,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53083,0.111,0.03141],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53878,0.02788,0.02507],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18206,"object_to_goal_dist_start":0.1905,"object_z_max":0.02511,"peak_contact_force":1.63638,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2443.0,"raw_peak_contact_force":9.1181,"tcp_end":[0.53182,0.06479,0.01995],"tcp_start":[0.53083,0.111,0.03141],"tcp_to_object_dist_end":0.03791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":900.0,"object_pos_end":[0.53247,-0.08478,0.03123],"object_pos_start":[0.53878,0.02788,0.02507],"object_to_goal_dist_end":0.07312,"object_to_goal_dist_start":0.18206,"object_z_max":0.03126,"peak_contact_force":123.9607,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3100.0,"raw_peak_contact_force":130.84527,"tcp_end":[0.50742,-0.05528,0.0288],"tcp_start":[0.53182,0.06479,0.01995],"tcp_to_object_dist_end":0.03878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52402,-0.08274,0.02499],"object_pos_start":[0.53247,-0.08478,0.03123],"object_to_goal_dist_end":0.07142,"object_to_goal_dist_start":0.07312,"object_z_max":0.03472,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3800.0,"raw_peak_contact_force":91.05911,"tcp_end":[0.49865,0.08967,0.10973],"tcp_start":[0.50742,-0.05528,0.0288],"tcp_to_object_dist_end":0.19378,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```