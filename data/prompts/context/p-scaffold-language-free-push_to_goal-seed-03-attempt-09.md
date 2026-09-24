## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4570 | 0.64 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4557 | 0.63 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.2069 | 0.41 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.1333 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4639 | 0.71 | ❌ rejected |

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

## Current Skill (Q=0.457) — your mutation base

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

- **Composite score**: 0.457
- **task_score** (E): 0.643
- **fitness_score**: 0.667  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2832 |
| contact_1 | 1.00 | 1.00 | 0.0493 |
| push_1 | 1.00 | 1.00 | 0.1256 |
| retract_1 | 0.00 | 1.00 | 0.1664 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.033) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.033)→(0.509, 0.030, 0.020) | (0.513, 0.002, 0.025)→(0.516, -0.007, 0.025) | 0.160→0.152 | 1.00 / 3.333 | 2.182 | 9.431 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.020)→(0.504, -0.090, 0.026) | (0.516, -0.007, 0.025)→(0.510, -0.113, 0.029) | 0.152→0.057 | 1.00 / 4.000 | 79.396 | 107.625 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.090, 0.026)→(0.497, 0.060, 0.099) | (0.510, -0.113, 0.029)→(0.505, -0.110, 0.025) | 0.057→0.057 | 1.00 / 4.000 | 0.245 | 61.119 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.830
- lateral_force_integral: None
- approach_alignment: 0.431
- goal_progress: 0.639
- terminal_score: 0.639
- phase_score: 0.845
- phase_breakdown.contact_score: 0.883
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.831

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.763
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.663
- **Median Q (composite search score)**: 0.455
- **K-run variance**: 0.0060
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.414


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76647,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07891,"contact_1.speed":0.04186,"push_1.push_depth":0.08796},"optimized_scores":{"best_composite_score":0.55269,"best_fitness_score":0.76269,"best_task_score":0.6393},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1372.0,"contact_point_centroid":[0.45641,-0.10547,-7e-05],"force_p95":38.67097,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.37578,"mean_force":7.29478,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47156,-0.06887,0.01952]},{"body_a":"attachment","body_b":"push_box","contact_count":616.0,"contact_point_centroid":[0.47304,-0.06785,0.03287],"force_p95":29.97191,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.94264,"mean_force":11.31854,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46676,-0.05646,0.0196]},{"body_a":"push_box","body_b":"link7","contact_count":246.0,"contact_point_centroid":[0.48057,-0.04436,0.05072],"force_p95":25.59232,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.30838,"mean_force":18.51955,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45346,-0.02168,0.02006]},{"body_a":"attachment","body_b":"push_box","contact_count":127.0,"contact_point_centroid":[0.45283,-0.0106,0.03267],"force_p95":9.17807,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.40806,"mean_force":3.92755,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44609,0.0013,0.02239]},{"body_a":"world","body_b":"push_box","contact_count":2600.0,"contact_point_centroid":[0.45046,-0.03292,-1e-05],"force_p95":2.02516,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.48213,"mean_force":0.44623,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44575,0.02195,0.02632]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48631,-0.13076,0.02304],"force_p95":7.14873,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.14873,"mean_force":7.14873,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49319,-0.12148,0.01981]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.47647,-0.0143,0.0501],"force_p95":5.45466,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.83419,"mean_force":3.74043,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44625,-0.00251,0.02173]},{"body_a":"world","body_b":"push_box","contact_count":3981.0,"contact_point_centroid":[0.45524,-0.13802,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.00533,"mean_force":0.24743,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49136,-0.04422,0.05214]},{"body_a":"world","body_b":"push_box","contact_count":3484.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47378,0.02259,0.16681]}],"total_contact_groups":9},"final_pose_error":0.13614,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45525,-0.13802,0.02499],"final_tcp_position":[0.49329,0.02929,0.08741],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":52.37578,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3484.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44888,0.04566,0.03431],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":710.0,"n_steps_budget":810.0,"object_pos_end":[0.45147,-0.04021,0.0249],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12003,"object_to_goal_dist_start":0.12843,"object_z_max":0.02508,"peak_contact_force":1.06806,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2739.0,"raw_peak_contact_force":12.40806,"tcp_end":[0.44627,-0.00325,0.0216],"tcp_start":[0.44888,0.04566,0.03431],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45612,-0.13723,0.02496],"object_pos_start":[0.45147,-0.04021,0.0249],"object_to_goal_dist_end":0.0457,"object_to_goal_dist_start":0.12003,"object_z_max":0.03127,"peak_contact_force":1.55086,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2234.0,"raw_peak_contact_force":52.37578,"tcp_end":[0.49325,-0.12136,0.01986],"tcp_start":[0.44627,-0.00325,0.0216],"tcp_to_object_dist_end":0.0407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45525,-0.13802,0.02499],"object_pos_start":[0.45612,-0.13723,0.02496],"object_to_goal_dist_end":0.04633,"object_to_goal_dist_start":0.0457,"object_z_max":0.02511,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3982.0,"raw_peak_contact_force":7.14873,"tcp_end":[0.49329,0.02929,0.08741],"tcp_start":[0.49325,-0.12136,0.01986],"tcp_to_object_dist_end":0.18258,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07587,"contact_1.speed":0.03951,"push_1.push_depth":0.09986},"optimized_scores":{"best_composite_score":0.45504,"best_fitness_score":0.66504,"best_task_score":0.66307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":817.0,"contact_point_centroid":[0.56083,-0.04634,0.05441],"force_p95":120.59295,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.6455,"mean_force":80.77662,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52708,-0.0316,0.02378]},{"body_a":"world","body_b":"push_box","contact_count":1632.0,"contact_point_centroid":[0.55433,-0.08015,-0.00033],"force_p95":89.9724,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.59693,"mean_force":51.56297,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52714,-0.03151,0.0238]},{"body_a":"attachment","body_b":"push_box","contact_count":819.0,"contact_point_centroid":[0.54608,-0.03997,0.05398],"force_p95":84.93687,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.03073,"mean_force":52.74825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52715,-0.03143,0.02377]},{"body_a":"world","body_b":"push_box","contact_count":3678.0,"contact_point_centroid":[0.53553,-0.1089,-3e-05],"force_p95":0.28692,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.97782,"mean_force":0.51746,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5027,-0.00783,0.06641]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.5496,-0.09744,0.05744],"force_p95":68.125,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.55262,"mean_force":28.36429,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50877,-0.08686,0.03081]},{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.53344,-0.08922,0.0618],"force_p95":47.69092,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.92033,"mean_force":17.99692,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50832,-0.08496,0.03124]},{"body_a":"attachment","body_b":"push_box","contact_count":152.0,"contact_point_centroid":[0.55441,0.02191,0.03923],"force_p95":6.41316,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.19795,"mean_force":2.52271,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54767,0.03388,0.02016]},{"body_a":"world","body_b":"push_box","contact_count":2632.0,"contact_point_centroid":[0.5533,-0.00104,-1e-05],"force_p95":1.66304,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.99794,"mean_force":0.39976,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54517,0.05522,0.02305]},{"body_a":"world","body_b":"push_box","contact_count":3916.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03844,0.16445]}],"total_contact_groups":9},"final_pose_error":0.10213,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53501,-0.10882,0.02499],"final_tcp_position":[0.50006,0.06059,0.10064],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":138.6455,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3916.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54661,0.07725,0.03101],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.55547,-0.00756,0.0252],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15286,"object_to_goal_dist_start":0.16043,"object_z_max":0.02519,"peak_contact_force":1.69638,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2784.0,"raw_peak_contact_force":8.19795,"tcp_end":[0.54831,0.02922,0.01963],"tcp_start":[0.54661,0.07725,0.03101],"tcp_to_object_dist_end":0.03788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":834.0,"n_steps_budget":930.0,"object_pos_end":[0.54026,-0.11655,0.03117],"object_pos_start":[0.55547,-0.00756,0.0252],"object_to_goal_dist_end":0.05271,"object_to_goal_dist_start":0.15286,"object_z_max":0.0312,"peak_contact_force":120.67752,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3268.0,"raw_peak_contact_force":138.6455,"tcp_end":[0.50995,-0.09112,0.02974],"tcp_start":[0.54831,0.02922,0.01963],"tcp_to_object_dist_end":0.03959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53501,-0.10882,0.02499],"object_pos_start":[0.54026,-0.11655,0.03117],"object_to_goal_dist_end":0.05405,"object_to_goal_dist_start":0.05271,"object_z_max":0.03483,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3791.0,"raw_peak_contact_force":83.97782,"tcp_end":[0.50006,0.06059,0.10064],"tcp_start":[0.50995,-0.09112,0.02974],"tcp_to_object_dist_end":0.1888,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65363,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08109,"contact_1.speed":0.02883,"push_1.push_depth":0.09999},"optimized_scores":{"best_composite_score":0.36342,"best_fitness_score":0.57342,"best_task_score":0.62529},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":805.0,"contact_point_centroid":[0.55045,-0.01167,0.05441],"force_p95":116.16885,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.85291,"mean_force":76.16882,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51823,0.00429,0.02355]},{"body_a":"attachment","body_b":"push_box","contact_count":801.0,"contact_point_centroid":[0.53695,-0.00475,0.05224],"force_p95":101.47896,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.18275,"mean_force":54.82656,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5182,0.00406,0.02358]},{"body_a":"world","body_b":"push_box","contact_count":1506.0,"contact_point_centroid":[0.54545,-0.04795,-0.00032],"force_p95":79.15915,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.42914,"mean_force":52.5749,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51777,0.00141,0.02389]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54978,-0.06198,0.0558],"force_p95":82.93043,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.23111,"mean_force":39.52335,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50701,-0.05289,0.03037]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.52887,-0.05557,0.06004],"force_p95":61.86201,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.57709,"mean_force":22.29918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50624,-0.04969,0.03137]},{"body_a":"world","body_b":"push_box","contact_count":3686.0,"contact_point_centroid":[0.52579,-0.08321,-3e-05],"force_p95":0.25405,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.02147,"mean_force":0.4965,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50106,0.02341,0.07103]},{"body_a":"attachment","body_b":"push_box","contact_count":227.0,"contact_point_centroid":[0.53839,0.05719,0.03927],"force_p95":5.82393,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.68649,"mean_force":2.65007,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53123,0.06915,0.02092]},{"body_a":"world","body_b":"push_box","contact_count":3316.0,"contact_point_centroid":[0.53682,0.03407,-1e-05],"force_p95":2.09652,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.70266,"mean_force":0.43592,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52899,0.08825,0.0247]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51431,0.05488,0.1655]}],"total_contact_groups":9},"final_pose_error":0.07286,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52523,-0.08322,0.02499],"final_tcp_position":[0.49878,0.08929,0.10973],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":131.85291,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53053,0.10997,0.03388],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.53981,0.02725,0.02506],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18167,"object_to_goal_dist_start":0.1905,"object_z_max":0.02516,"peak_contact_force":3.78222,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3543.0,"raw_peak_contact_force":7.68649,"tcp_end":[0.53187,0.0641,0.01998],"tcp_start":[0.53053,0.10997,0.03388],"tcp_to_object_dist_end":0.03804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.53395,-0.08467,0.03145],"object_pos_start":[0.53981,0.02725,0.02506],"object_to_goal_dist_end":0.07391,"object_to_goal_dist_start":0.18167,"object_z_max":0.03145,"peak_contact_force":115.95962,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3112.0,"raw_peak_contact_force":131.85291,"tcp_end":[0.50785,-0.05604,0.02915],"tcp_start":[0.53187,0.0641,0.01998],"tcp_to_object_dist_end":0.03881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52523,-0.08322,0.02499],"object_pos_start":[0.53395,-0.08467,0.03145],"object_to_goal_dist_end":0.07138,"object_to_goal_dist_start":0.07391,"object_z_max":0.03505,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3793.0,"raw_peak_contact_force":92.23111,"tcp_end":[0.49878,0.08929,0.10973],"tcp_start":[0.50785,-0.05604,0.02915],"tcp_to_object_dist_end":0.19402,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```