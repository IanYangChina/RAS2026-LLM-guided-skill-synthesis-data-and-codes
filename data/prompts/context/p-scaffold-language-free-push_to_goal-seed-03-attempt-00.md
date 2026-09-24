## Search State

- **Seed**: 3
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4526 | 0.63 | ✅ accepted |

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

## Current Skill (Q=0.453) — your mutation base

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

- **Composite score**: 0.453
- **task_score** (E): 0.629
- **fitness_score**: 0.663  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2837 |
| contact_1 | 1.00 | 1.00 | 0.0495 |
| push_1 | 1.00 | 1.00 | 0.1258 |
| retract_1 | 0.00 | 1.00 | 0.1666 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.033) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.033)→(0.509, 0.030, 0.020) | (0.513, 0.002, 0.025)→(0.516, -0.007, 0.025) | 0.160→0.152 | 1.00 / 2.667 | 4.662 | 9.014 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.020)→(0.504, -0.090, 0.026) | (0.516, -0.007, 0.025)→(0.510, -0.112, 0.029) | 0.152→0.059 | 1.00 / 4.333 | 77.496 | 108.985 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.090, 0.026)→(0.497, 0.060, 0.099) | (0.510, -0.112, 0.029)→(0.505, -0.108, 0.025) | 0.059→0.059 | 1.00 / 4.000 | 0.245 | 61.644 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.833
- lateral_force_integral: None
- approach_alignment: 0.434
- goal_progress: 0.630
- terminal_score: 0.630
- phase_score: 0.851
- phase_breakdown.contact_score: 0.886
- phase_breakdown.approach_score: 0.819
- phase_breakdown.push_score: 0.842

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.763
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.633
- **Median Q (composite search score)**: 0.440
- **K-run variance**: 0.0059
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53591,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06783,"contact_1.speed":0.03694,"push_1.push_depth":0.09032},"optimized_scores":{"best_composite_score":0.55252,"best_fitness_score":0.76252,"best_task_score":0.63009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1345.0,"contact_point_centroid":[0.45768,-0.11168,-7e-05],"force_p95":42.69416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.33488,"mean_force":7.52489,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47346,-0.07501,0.01947]},{"body_a":"attachment","body_b":"push_box","contact_count":612.0,"contact_point_centroid":[0.4726,-0.06733,0.03327],"force_p95":30.20777,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.44423,"mean_force":11.27446,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46615,-0.05596,0.01961]},{"body_a":"push_box","body_b":"link7","contact_count":235.0,"contact_point_centroid":[0.48095,-0.0459,0.05052],"force_p95":28.30246,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.91211,"mean_force":20.21982,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45319,-0.02078,0.02025]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48644,-0.13295,0.02307],"force_p95":12.01569,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.01569,"mean_force":12.01569,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49327,-0.12363,0.01986]},{"body_a":"attachment","body_b":"push_box","contact_count":151.0,"contact_point_centroid":[0.45532,-0.01099,0.03646],"force_p95":7.81629,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.08622,"mean_force":3.50981,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44609,0.00092,0.02234]},{"body_a":"world","body_b":"push_box","contact_count":2850.0,"contact_point_centroid":[0.4505,-0.03324,-1e-05],"force_p95":2.03848,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.31472,"mean_force":0.46408,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44575,0.02186,0.02639]},{"body_a":"push_box","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.47668,-0.02226,0.04999],"force_p95":4.85238,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.96639,"mean_force":4.35639,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44628,-0.00286,0.02169]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.45368,-0.13847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.57159,"mean_force":0.25048,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49138,-0.0456,0.05224]},{"body_a":"world","body_b":"push_box","contact_count":3584.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47376,0.02259,0.1668]}],"total_contact_groups":9},"final_pose_error":0.13721,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45392,-0.13845,0.02499],"final_tcp_position":[0.4933,0.02812,0.08733],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":58.33488,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44892,0.04563,0.0345],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":789.0,"n_steps_budget":900.0,"object_pos_end":[0.45186,-0.04027,0.02505],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11983,"object_to_goal_dist_start":0.12843,"object_z_max":0.02508,"peak_contact_force":8.06724,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3025.0,"raw_peak_contact_force":10.08622,"tcp_end":[0.44635,-0.00345,0.02162],"tcp_start":[0.44892,0.04563,0.0345],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.4544,-0.13788,0.0249],"object_pos_start":[0.45186,-0.04027,0.02505],"object_to_goal_dist_end":0.04718,"object_to_goal_dist_start":0.11983,"object_z_max":0.03051,"peak_contact_force":1.15484,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2192.0,"raw_peak_contact_force":58.33488,"tcp_end":[0.49327,-0.12363,0.01986],"tcp_start":[0.44635,-0.00345,0.02162],"tcp_to_object_dist_end":0.04171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45392,-0.13845,0.02499],"object_pos_start":[0.4544,-0.13788,0.0249],"object_to_goal_dist_end":0.04751,"object_to_goal_dist_start":0.04718,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3961.0,"raw_peak_contact_force":12.01569,"tcp_end":[0.4933,0.02812,0.08733],"tcp_start":[0.49327,-0.12363,0.01986],"tcp_to_object_dist_end":0.18216,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75152,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08658,"contact_1.speed":0.03803,"push_1.push_depth":0.09915},"optimized_scores":{"best_composite_score":0.4396,"best_fitness_score":0.6496,"best_task_score":0.63252},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":796.0,"contact_point_centroid":[0.56257,-0.04527,0.05406],"force_p95":125.46131,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.60578,"mean_force":82.83535,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52751,-0.03058,0.02391]},{"body_a":"world","body_b":"push_box","contact_count":1573.0,"contact_point_centroid":[0.55669,-0.07843,-0.00035],"force_p95":93.16076,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.65517,"mean_force":53.18407,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52745,-0.03095,0.024]},{"body_a":"attachment","body_b":"push_box","contact_count":798.0,"contact_point_centroid":[0.54637,-0.03892,0.05367],"force_p95":84.98295,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.25661,"mean_force":51.21991,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52757,-0.03043,0.0239]},{"body_a":"world","body_b":"push_box","contact_count":3647.0,"contact_point_centroid":[0.5356,-0.10264,-3e-05],"force_p95":0.36711,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.17001,"mean_force":0.53596,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5028,-0.00649,0.06682]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.55083,-0.09407,0.05711],"force_p95":67.79245,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.24905,"mean_force":28.82077,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50896,-0.08584,0.03095]},{"body_a":"attachment","body_b":"push_box","contact_count":70.0,"contact_point_centroid":[0.53296,-0.08735,0.06157],"force_p95":46.44843,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.71701,"mean_force":16.10975,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50826,-0.0828,0.03167]},{"body_a":"attachment","body_b":"push_box","contact_count":157.0,"contact_point_centroid":[0.55407,0.02191,0.03851],"force_p95":5.95249,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.26168,"mean_force":2.31017,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54765,0.03388,0.02016]},{"body_a":"world","body_b":"push_box","contact_count":2697.0,"contact_point_centroid":[0.55338,-0.00095,-1e-05],"force_p95":1.6528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.01037,"mean_force":0.38836,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.05483,0.02305]},{"body_a":"world","body_b":"push_box","contact_count":3864.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03846,0.16439]}],"total_contact_groups":9},"final_pose_error":0.10158,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53502,-0.10257,0.02499],"final_tcp_position":[0.50013,0.06114,0.10077],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":142.60578,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3864.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54659,0.07722,0.0311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":772.0,"n_steps_budget":870.0,"object_pos_end":[0.55636,-0.00776,0.02503],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.153,"object_to_goal_dist_start":0.16043,"object_z_max":0.02511,"peak_contact_force":0.79096,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2854.0,"raw_peak_contact_force":8.26168,"tcp_end":[0.5483,0.02909,0.0196],"tcp_start":[0.54659,0.07722,0.0311],"tcp_to_object_dist_end":0.03811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":808.0,"n_steps_budget":900.0,"object_pos_end":[0.54123,-0.11428,0.03118],"object_pos_start":[0.55636,-0.00776,0.02503],"object_to_goal_dist_end":0.0549,"object_to_goal_dist_start":0.153,"object_z_max":0.0312,"peak_contact_force":122.28295,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3167.0,"raw_peak_contact_force":142.60578,"tcp_end":[0.51014,-0.09006,0.02986],"tcp_start":[0.5483,0.02909,0.0196],"tcp_to_object_dist_end":0.03943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53502,-0.10257,0.02499],"object_pos_start":[0.54123,-0.11428,0.03118],"object_to_goal_dist_end":0.05895,"object_to_goal_dist_start":0.0549,"object_z_max":0.03457,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3769.0,"raw_peak_contact_force":84.17001,"tcp_end":[0.50013,0.06114,0.10077],"tcp_start":[0.51014,-0.09006,0.02986],"tcp_to_object_dist_end":0.18375,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74556,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08731,"contact_1.speed":0.03374,"push_1.push_depth":0.0996},"optimized_scores":{"best_composite_score":0.36582,"best_fitness_score":0.57582,"best_task_score":0.62455},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":808.0,"contact_point_centroid":[0.54998,-0.01072,0.05465],"force_p95":114.36627,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.01567,"mean_force":75.62883,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51833,0.00489,0.02355]},{"body_a":"attachment","body_b":"push_box","contact_count":808.0,"contact_point_centroid":[0.53706,-0.00395,0.05247],"force_p95":100.54953,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.05778,"mean_force":56.09644,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51834,0.0049,0.02355]},{"body_a":"world","body_b":"push_box","contact_count":1549.0,"contact_point_centroid":[0.54441,-0.04601,-0.00031],"force_p95":78.16872,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.03925,"mean_force":51.26341,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51806,0.00314,0.02376]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54955,-0.06184,0.0558],"force_p95":78.87608,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.74757,"mean_force":37.77158,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50693,-0.05249,0.03034]},{"body_a":"world","body_b":"push_box","contact_count":3689.0,"contact_point_centroid":[0.52577,-0.08306,-3e-05],"force_p95":0.25341,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.80794,"mean_force":0.48602,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50105,0.02368,0.07107]},{"body_a":"attachment","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.52872,-0.05538,0.05993],"force_p95":60.4446,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.47095,"mean_force":21.77713,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50619,-0.04938,0.03132]},{"body_a":"attachment","body_b":"push_box","contact_count":186.0,"contact_point_centroid":[0.53825,0.05726,0.03857],"force_p95":6.7673,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.69446,"mean_force":2.96367,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53128,0.06922,0.02063]},{"body_a":"world","body_b":"push_box","contact_count":2868.0,"contact_point_centroid":[0.5368,0.03448,-1e-05],"force_p95":2.12698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.64123,"mean_force":0.445,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5292,0.08844,0.02373]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51443,0.05525,0.16462]}],"total_contact_groups":9},"final_pose_error":0.0726,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52522,-0.08307,0.02499],"final_tcp_position":[0.49877,0.08954,0.10983],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":126.01567,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53078,0.11071,0.03211],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":817.0,"n_steps_budget":930.0,"object_pos_end":[0.54033,0.02746,0.02507],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18198,"object_to_goal_dist_start":0.1905,"object_z_max":0.02513,"peak_contact_force":5.12651,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3054.0,"raw_peak_contact_force":8.69446,"tcp_end":[0.53192,0.06422,0.01994],"tcp_start":[0.53078,0.11071,0.03211],"tcp_to_object_dist_end":0.03806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.53381,-0.08453,0.03129],"object_pos_start":[0.54033,0.02746,0.02507],"object_to_goal_dist_end":0.07395,"object_to_goal_dist_start":0.18198,"object_z_max":0.03141,"peak_contact_force":109.04958,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3165.0,"raw_peak_contact_force":126.01567,"tcp_end":[0.50785,-0.05574,0.02914],"tcp_start":[0.53192,0.06422,0.01994],"tcp_to_object_dist_end":0.03883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52522,-0.08307,0.02499],"object_pos_start":[0.53381,-0.08453,0.03129],"object_to_goal_dist_end":0.07152,"object_to_goal_dist_start":0.07395,"object_z_max":0.0349,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3795.0,"raw_peak_contact_force":88.74757,"tcp_end":[0.49877,0.08954,0.10983],"tcp_start":[0.50785,-0.05574,0.02914],"tcp_to_object_dist_end":0.19414,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```