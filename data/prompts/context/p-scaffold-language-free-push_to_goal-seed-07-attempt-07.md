## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2748 | 0.69 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0774 | 0.01 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2790 | 0.71 | ✅ accepted |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0940 | 0.00 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0079 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.275) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
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
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.275
- **task_score** (E): 0.694
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2822 |
| contact_1 | 1.00 | 1.00 | 0.0553 |
| push_1 | 1.00 | 1.00 | 0.1246 |
| retract_1 | 0.00 | 1.00 | 0.1308 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.105, 0.042) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.105, 0.042)→(0.508, 0.055, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 2.333 | 4.369 | 11.934 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.055, 0.021)→(0.501, -0.068, 0.024) | (0.515, 0.018, 0.025)→(0.514, -0.103, 0.029) | 0.171→0.057 | 1.00 / 3.667 | 53.762 | 81.099 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.068, 0.024)→(0.497, 0.046, 0.087) | (0.514, -0.103, 0.029)→(0.511, -0.099, 0.025) | 0.057→0.057 | 1.00 / 4.000 | 0.245 | 46.077 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.857
- lateral_force_integral: None
- approach_alignment: 0.483
- goal_progress: 0.772
- terminal_score: 0.772
- phase_score: 0.801
- phase_breakdown.approach_score: 0.820
- phase_breakdown.contact_score: 0.853
- phase_breakdown.push_score: 0.761

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.789
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.772
- **Median Q (composite search score)**: 0.209
- **K-run variance**: 0.0120
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.534


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47619,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09298,"contact_1.speed":0.03067,"push_1.push_depth":0.09727,"push_1.push_distance":0.07765,"push_1.push_speed":0.07879,"retract_1.speed":0.05274},"optimized_scores":{"best_composite_score":0.20917,"best_fitness_score":0.56917,"best_task_score":0.64805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1770.0,"contact_point_centroid":[0.5237,-0.04517,-0.00021],"force_p95":52.43619,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.16686,"mean_force":35.87121,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.505,0.00948,0.02223]},{"body_a":"push_box","body_b":"link7","contact_count":952.0,"contact_point_centroid":[0.53203,-0.00408,0.05459],"force_p95":58.6086,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.91109,"mean_force":49.44009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50511,0.01252,0.02203]},{"body_a":"attachment","body_b":"push_box","contact_count":951.0,"contact_point_centroid":[0.52411,0.00229,0.05225],"force_p95":55.66846,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.87528,"mean_force":41.59793,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50511,0.01246,0.02204]},{"body_a":"push_box","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53099,-0.07033,0.05491],"force_p95":47.62628,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.06409,"mean_force":23.19238,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50043,-0.04676,0.02442]},{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.52104,-0.05395,0.05581],"force_p95":38.02747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.25213,"mean_force":10.83841,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4996,-0.04416,0.02504]},{"body_a":"world","body_b":"push_box","contact_count":3831.0,"contact_point_centroid":[0.50926,-0.08148,-1e-05],"force_p95":0.24693,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.25196,"mean_force":0.31831,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49698,0.00726,0.0547]},{"body_a":"attachment","body_b":"push_box","contact_count":211.0,"contact_point_centroid":[0.51652,0.06795,0.03609],"force_p95":7.82319,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.21052,"mean_force":3.98103,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51004,0.07978,0.02199]},{"body_a":"world","body_b":"push_box","contact_count":3506.0,"contact_point_centroid":[0.51509,0.04547,-1e-05],"force_p95":2.59585,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.67678,"mean_force":0.48973,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50822,0.10019,0.02785]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50352,0.07634,0.17929]}],"total_contact_groups":9},"final_pose_error":0.11579,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50917,-0.08084,0.02499],"final_tcp_position":[0.49681,0.05445,0.08467],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":69.16686,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50998,0.12517,0.03954],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.51842,0.03802,0.02517],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18892,"object_to_goal_dist_start":0.19823,"object_z_max":0.02517,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3717.0,"raw_peak_contact_force":9.21052,"tcp_end":[0.51054,0.07468,0.02059],"tcp_start":[0.50998,0.12517,0.03954],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.51141,-0.08542,0.02945],"object_pos_start":[0.51842,0.03802,0.02517],"object_to_goal_dist_end":0.06573,"object_to_goal_dist_start":0.18892,"object_z_max":0.02947,"peak_contact_force":54.1669,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3673.0,"raw_peak_contact_force":69.16686,"tcp_end":[0.5012,-0.04802,0.02423],"tcp_start":[0.51054,0.07468,0.02059],"tcp_to_object_dist_end":0.03912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50917,-0.08084,0.02499],"object_pos_start":[0.51141,-0.08542,0.02945],"object_to_goal_dist_end":0.06977,"object_to_goal_dist_start":0.06573,"object_z_max":0.02945,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3909.0,"raw_peak_contact_force":50.06409,"tcp_end":[0.49681,0.05445,0.08467],"tcp_start":[0.5012,-0.04802,0.02423],"tcp_to_object_dist_end":0.14838,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11111,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06842,"contact_1.speed":0.03952,"push_1.push_depth":0.09741,"push_1.push_distance":0.02917,"push_1.push_speed":0.02574,"retract_1.speed":0.08496},"optimized_scores":{"best_composite_score":0.18589,"best_fitness_score":0.54589,"best_task_score":0.66047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1431.0,"contact_point_centroid":[0.49369,-0.03209,-0.0001],"force_p95":44.54382,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.22264,"mean_force":11.55413,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48482,0.01594,0.01986]},{"body_a":"attachment","body_b":"push_box","contact_count":929.0,"contact_point_centroid":[0.49499,0.01115,0.03855],"force_p95":31.8991,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.61475,"mean_force":12.22971,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48384,0.02251,0.01996]},{"body_a":"push_box","body_b":"link7","contact_count":364.0,"contact_point_centroid":[0.50672,0.03653,0.05146],"force_p95":32.79261,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.83997,"mean_force":23.27074,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47809,0.06011,0.02042]},{"body_a":"attachment","body_b":"push_box","contact_count":176.0,"contact_point_centroid":[0.4785,0.07901,0.03151],"force_p95":12.32507,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.33018,"mean_force":6.20751,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47474,0.09082,0.02519]},{"body_a":"world","body_b":"push_box","contact_count":2865.0,"contact_point_centroid":[0.47927,0.05678,-1e-05],"force_p95":3.43855,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.71848,"mean_force":0.6267,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47386,0.10859,0.03633]},{"body_a":"world","body_b":"push_box","contact_count":3984.0,"contact_point_centroid":[0.49789,-0.07893,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17455,"mean_force":0.24695,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49266,0.01959,0.05702]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49498,-0.05327,0.02008],"force_p95":0.826,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86514,"mean_force":0.40564,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4947,-0.04134,0.02014]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48545,0.07849,0.18672]}],"total_contact_groups":8},"final_pose_error":0.09067,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49784,-0.0789,0.02499],"final_tcp_position":[0.4944,0.0773,0.09611],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":50.22264,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47619,0.13309,0.05514],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":779.0,"n_steps_budget":930.0,"object_pos_end":[0.4811,0.04924,0.02503],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20014,"object_to_goal_dist_start":0.2095,"object_z_max":0.0251,"peak_contact_force":7.5008,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3041.0,"raw_peak_contact_force":14.33018,"tcp_end":[0.47508,0.08589,0.02217],"tcp_start":[0.47619,0.13309,0.05514],"tcp_to_object_dist_end":0.03725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.49814,-0.07802,0.02512],"object_pos_start":[0.4811,0.04924,0.02503],"object_to_goal_dist_end":0.072,"object_to_goal_dist_start":0.20014,"object_z_max":0.03053,"peak_contact_force":1.5766,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2724.0,"raw_peak_contact_force":50.22264,"tcp_end":[0.49476,-0.04124,0.02017],"tcp_start":[0.47508,0.08589,0.02217],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49784,-0.0789,0.02499],"object_pos_start":[0.49814,-0.07802,0.02512],"object_to_goal_dist_end":0.07113,"object_to_goal_dist_start":0.072,"object_z_max":0.02512,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":1.17455,"tcp_end":[0.4944,0.0773,0.09611],"tcp_start":[0.49476,-0.04124,0.02017],"tcp_to_object_dist_end":0.17166,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52709,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07005,"contact_1.speed":0.04802,"push_1.push_depth":0.09488,"push_1.push_distance":0.16307,"push_1.push_speed":0.08006,"retract_1.speed":0.04789},"optimized_scores":{"best_composite_score":0.42933,"best_fitness_score":0.78933,"best_task_score":0.77241},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":941.0,"contact_point_centroid":[0.55337,-0.07328,0.05465],"force_p95":105.59291,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.90645,"mean_force":73.39276,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52181,-0.05719,0.02329]},{"body_a":"attachment","body_b":"push_box","contact_count":935.0,"contact_point_centroid":[0.54068,-0.06639,0.05349],"force_p95":85.18284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.19803,"mean_force":52.15671,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52173,-0.05752,0.02334]},{"body_a":"push_box","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.54925,-0.12083,0.05517],"force_p95":81.95004,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.99375,"mean_force":36.1069,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5069,-0.11036,0.02917]},{"body_a":"world","body_b":"push_box","contact_count":1874.0,"contact_point_centroid":[0.54601,-0.10777,-0.00032],"force_p95":71.47219,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.91614,"mean_force":47.09754,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52185,-0.05716,0.02332]},{"body_a":"world","body_b":"push_box","contact_count":3621.0,"contact_point_centroid":[0.52808,-0.13755,-3e-05],"force_p95":0.43619,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.72475,"mean_force":0.57586,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5019,-0.04541,0.05506]},{"body_a":"attachment","body_b":"push_box","contact_count":79.0,"contact_point_centroid":[0.52994,-0.11306,0.05974],"force_p95":61.33354,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.1678,"mean_force":20.46892,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50615,-0.10725,0.0297]},{"body_a":"attachment","body_b":"push_box","contact_count":107.0,"contact_point_centroid":[0.54435,-0.00453,0.03409],"force_p95":10.36209,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.26182,"mean_force":3.63274,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5391,0.00735,0.02048]},{"body_a":"world","body_b":"push_box","contact_count":2421.0,"contact_point_centroid":[0.54454,-0.02686,-1e-05],"force_p95":1.08859,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.58923,"mean_force":0.40914,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53671,0.03098,0.02396]},{"body_a":"world","body_b":"push_box","contact_count":3844.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51724,0.04384,0.17048]}],"total_contact_groups":9},"final_pose_error":0.15892,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52738,-0.13757,0.02499],"final_tcp_position":[0.5004,0.00755,0.07954],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":123.90645,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3844.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5381,0.0561,0.03243],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.54649,-0.03358,0.02506],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12536,"object_to_goal_dist_start":0.13211,"object_z_max":0.02515,"peak_contact_force":5.60587,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2528.0,"raw_peak_contact_force":12.26182,"tcp_end":[0.53962,0.00327,0.01997],"tcp_start":[0.5381,0.0561,0.03243],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":954.0,"n_steps_budget":1000.0,"object_pos_end":[0.5334,-0.14413,0.03104],"object_pos_start":[0.54649,-0.03358,0.02506],"object_to_goal_dist_end":0.03445,"object_to_goal_dist_start":0.12536,"object_z_max":0.03104,"peak_contact_force":105.54291,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3750.0,"raw_peak_contact_force":123.90645,"tcp_end":[0.50787,-0.11436,0.0283],"tcp_start":[0.53962,0.00327,0.01997],"tcp_to_object_dist_end":0.03931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52738,-0.13757,0.02499],"object_pos_start":[0.5334,-0.14413,0.03104],"object_to_goal_dist_end":0.03007,"object_to_goal_dist_start":0.03445,"object_z_max":0.03457,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3756.0,"raw_peak_contact_force":86.99375,"tcp_end":[0.5004,0.00755,0.07954],"tcp_start":[0.50787,-0.11436,0.0283],"tcp_to_object_dist_end":0.15737,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```