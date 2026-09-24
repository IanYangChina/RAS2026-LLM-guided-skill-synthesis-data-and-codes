## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4480 | 0.64 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4803 | 0.41 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4501 | 0.63 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4593 | 0.65 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4794 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.64 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.448) — your mutation base

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

- **Composite score**: 0.448
- **task_score** (E): 0.636
- **fitness_score**: 0.658  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2842 |
| contact_1 | 1.00 | 1.00 | 0.0491 |
| push_1 | 1.00 | 1.00 | 0.1261 |
| retract_1 | 0.00 | 1.00 | 0.1658 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.030, 0.020) | (0.513, 0.002, 0.025)→(0.515, -0.006, 0.025) | 0.160→0.152 | 1.00 / 3.667 | 2.962 | 9.722 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.020)→(0.504, -0.090, 0.026) | (0.515, -0.006, 0.025)→(0.510, -0.114, 0.029) | 0.152→0.059 | 1.00 / 4.333 | 76.534 | 108.491 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.090, 0.026)→(0.497, 0.059, 0.099) | (0.510, -0.114, 0.029)→(0.505, -0.111, 0.025) | 0.059→0.059 | 1.00 / 4.000 | 0.245 | 61.553 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.918
- lateral_force_integral: None
- approach_alignment: 0.451
- goal_progress: 0.661
- terminal_score: 0.661
- phase_score: 0.832
- phase_breakdown.contact_score: 0.878
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.808

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.764
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.661
- **Median Q (composite search score)**: 0.446
- **K-run variance**: 0.0073
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.467


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27619,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04844,"contact_1.speed":0.04896,"push_1.push_depth":0.09891},"optimized_scores":{"best_composite_score":0.55369,"best_fitness_score":0.76369,"best_task_score":0.66124},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1369.0,"contact_point_centroid":[0.46071,-0.11623,-9e-05],"force_p95":44.05054,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.54597,"mean_force":8.96953,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47279,-0.07726,0.01955]},{"body_a":"attachment","body_b":"push_box","contact_count":656.0,"contact_point_centroid":[0.47511,-0.07212,0.03543],"force_p95":30.26128,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.99509,"mean_force":12.61009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46691,-0.06067,0.01973]},{"body_a":"push_box","body_b":"link7","contact_count":284.0,"contact_point_centroid":[0.48147,-0.04753,0.05076],"force_p95":28.62562,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.91481,"mean_force":21.69517,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.454,-0.02373,0.02028]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48676,-0.14104,0.02293],"force_p95":11.22149,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.22149,"mean_force":11.22149,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49341,-0.13156,0.01982]},{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.45283,-0.0104,0.03273],"force_p95":9.90777,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.50958,"mean_force":3.80418,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44607,0.00149,0.02242]},{"body_a":"world","body_b":"push_box","contact_count":2211.0,"contact_point_centroid":[0.45045,-0.03274,-1e-05],"force_p95":1.61283,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.60698,"mean_force":0.41731,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44577,0.02253,0.02647]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.45653,-0.14936,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.9477,"mean_force":0.24861,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49142,-0.054,0.05094]},{"body_a":"world","body_b":"push_box","contact_count":3716.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.1668]}],"total_contact_groups":8},"final_pose_error":0.1454,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4565,-0.14933,0.02499],"final_tcp_position":[0.49323,0.02003,0.08518],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":58.54597,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3716.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44887,0.04566,0.03431],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.45167,-0.03962,0.02495],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.1205,"object_to_goal_dist_start":0.12843,"object_z_max":0.02511,"peak_contact_force":1.03912,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2309.0,"raw_peak_contact_force":10.50958,"tcp_end":[0.44621,-0.00277,0.02167],"tcp_start":[0.44887,0.04566,0.03431],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.45696,-0.14862,0.02494],"object_pos_start":[0.45167,-0.03962,0.02495],"object_to_goal_dist_end":0.04307,"object_to_goal_dist_start":0.1205,"object_z_max":0.03231,"peak_contact_force":1.41458,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2309.0,"raw_peak_contact_force":58.54597,"tcp_end":[0.49341,-0.13156,0.01982],"tcp_start":[0.44621,-0.00277,0.02167],"tcp_to_object_dist_end":0.04057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4565,-0.14933,0.02499],"object_pos_start":[0.45696,-0.14862,0.02494],"object_to_goal_dist_end":0.04351,"object_to_goal_dist_start":0.04307,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":11.22149,"tcp_end":[0.49323,0.02003,0.08518],"tcp_start":[0.49341,-0.13156,0.01982],"tcp_to_object_dist_end":0.18346,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77564,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09154,"contact_1.speed":0.04634,"push_1.push_depth":0.09919},"optimized_scores":{"best_composite_score":0.44555,"best_fitness_score":0.65555,"best_task_score":0.65333},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":799.0,"contact_point_centroid":[0.56156,-0.04498,0.05419],"force_p95":123.17714,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.96419,"mean_force":79.77725,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52734,-0.02985,0.02375]},{"body_a":"world","body_b":"push_box","contact_count":1556.0,"contact_point_centroid":[0.55634,-0.07821,-0.00035],"force_p95":91.30013,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.76294,"mean_force":52.35893,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52705,-0.03094,0.02391]},{"body_a":"attachment","body_b":"push_box","contact_count":792.0,"contact_point_centroid":[0.54617,-0.03876,0.05369],"force_p95":85.07471,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.64081,"mean_force":51.99678,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52722,-0.03028,0.02381]},{"body_a":"world","body_b":"push_box","contact_count":3688.0,"contact_point_centroid":[0.53508,-0.10658,-3e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.3151,"mean_force":0.51555,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50275,-0.00673,0.06639]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.54967,-0.09571,0.05743],"force_p95":68.2997,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.23644,"mean_force":28.66735,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50882,-0.0851,0.03083]},{"body_a":"attachment","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.53328,-0.08732,0.06164],"force_p95":49.30251,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.63328,"mean_force":18.19197,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50832,-0.08298,0.03133]},{"body_a":"attachment","body_b":"push_box","contact_count":116.0,"contact_point_centroid":[0.55407,0.02222,0.03857],"force_p95":9.65035,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.94932,"mean_force":3.28525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54763,0.03418,0.02023]},{"body_a":"world","body_b":"push_box","contact_count":2269.0,"contact_point_centroid":[0.55329,-0.00037,-1e-05],"force_p95":1.81879,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.98342,"mean_force":0.41834,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54526,0.05484,0.02315]},{"body_a":"world","body_b":"push_box","contact_count":3836.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03846,0.16441]}],"total_contact_groups":9},"final_pose_error":0.10139,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53455,-0.10642,0.02499],"final_tcp_position":[0.50008,0.06139,0.10072],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":140.96419,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":959.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3836.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54658,0.07721,0.03115],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.55556,-0.00706,0.02501],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15336,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":4.37561,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2385.0,"raw_peak_contact_force":11.94932,"tcp_end":[0.54828,0.0298,0.01975],"tcp_start":[0.54658,0.07721,0.03115],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":808.0,"n_steps_budget":900.0,"object_pos_end":[0.54016,-0.11466,0.03118],"object_pos_start":[0.55556,-0.00706,0.02501],"object_to_goal_dist_end":0.05385,"object_to_goal_dist_start":0.15336,"object_z_max":0.03119,"peak_contact_force":117.02911,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3147.0,"raw_peak_contact_force":140.96419,"tcp_end":[0.51002,-0.08939,0.02972],"tcp_start":[0.54828,0.0298,0.01975],"tcp_to_object_dist_end":0.03936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53455,-0.10642,0.02499],"object_pos_start":[0.54016,-0.11466,0.03118],"object_to_goal_dist_end":0.05561,"object_to_goal_dist_start":0.05385,"object_z_max":0.03487,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3802.0,"raw_peak_contact_force":84.3151,"tcp_end":[0.50008,0.06139,0.10072],"tcp_start":[0.51002,-0.08939,0.02972],"tcp_to_object_dist_end":0.18731,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64848,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09568,"contact_1.speed":0.02963,"push_1.push_depth":0.0925},"optimized_scores":{"best_composite_score":0.34484,"best_fitness_score":0.55484,"best_task_score":0.59257},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":743.0,"contact_point_centroid":[0.54952,-0.00823,0.05457],"force_p95":113.15427,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.96424,"mean_force":74.72576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51811,0.00784,0.02339]},{"body_a":"attachment","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.53667,-0.00106,0.05208],"force_p95":99.59318,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.14227,"mean_force":54.39418,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51813,0.00793,0.02339]},{"body_a":"world","body_b":"push_box","contact_count":1431.0,"contact_point_centroid":[0.54357,-0.04325,-0.00031],"force_p95":76.17648,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.59385,"mean_force":50.35651,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5179,0.00648,0.02359]},{"body_a":"world","body_b":"push_box","contact_count":3693.0,"contact_point_centroid":[0.52422,-0.07613,-3e-05],"force_p95":0.24996,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.12307,"mean_force":0.47575,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50073,0.02975,0.07179]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.5275,-0.04834,0.05894],"force_p95":57.32093,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.48663,"mean_force":21.14675,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50567,-0.04181,0.03111]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54809,-0.05599,0.05588],"force_p95":78.72587,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.46688,"mean_force":38.11704,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50647,-0.0451,0.03001]},{"body_a":"attachment","body_b":"push_box","contact_count":213.0,"contact_point_centroid":[0.53798,0.05721,0.03764],"force_p95":5.66093,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.70647,"mean_force":2.36267,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53128,0.06917,0.02041]},{"body_a":"world","body_b":"push_box","contact_count":3244.0,"contact_point_centroid":[0.53693,0.03423,-1e-05],"force_p95":1.88372,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.13388,"mean_force":0.40842,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52918,0.08902,0.02302]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.05554,0.16393]}],"total_contact_groups":9},"final_pose_error":0.06741,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52371,-0.07609,0.02499],"final_tcp_position":[0.49855,0.09466,0.11153],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":125.96424,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3988.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53087,0.11123,0.03085],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.53927,0.02725,0.02506],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18155,"object_to_goal_dist_start":0.1905,"object_z_max":0.02512,"peak_contact_force":3.47241,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3457.0,"raw_peak_contact_force":6.70647,"tcp_end":[0.53187,0.06414,0.01981],"tcp_start":[0.53087,0.11123,0.03085],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":750.0,"n_steps_budget":840.0,"object_pos_end":[0.53208,-0.07814,0.03122],"object_pos_start":[0.53927,0.02725,0.02506],"object_to_goal_dist_end":0.07894,"object_to_goal_dist_start":0.18155,"object_z_max":0.03125,"peak_contact_force":111.15799,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2918.0,"raw_peak_contact_force":125.96424,"tcp_end":[0.50739,-0.04832,0.02874],"tcp_start":[0.53187,0.06414,0.01981],"tcp_to_object_dist_end":0.03879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52371,-0.07609,0.02499],"object_pos_start":[0.53208,-0.07814,0.03122],"object_to_goal_dist_end":0.07762,"object_to_goal_dist_start":0.07894,"object_z_max":0.03448,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3801.0,"raw_peak_contact_force":89.12307,"tcp_end":[0.49855,0.09466,0.11153],"tcp_start":[0.50739,-0.04832,0.02874],"tcp_to_object_dist_end":0.19308,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```