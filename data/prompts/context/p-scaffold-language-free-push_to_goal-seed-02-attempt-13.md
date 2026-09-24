## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.2315 | 0.46 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0808 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | 0.2206 | 0.46 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5971 | 0.76 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5975 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

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
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.232) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.232
- **task_score** (E): 0.461
- **fitness_score**: 0.592  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1056 |
| contact_1 | 1.00 | 1.00 | 0.1532 |
| push_1 | 1.00 | 1.00 | 0.1453 |
| retract_1 | 0.67 | 1.00 | 0.1203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.016, 0.205) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.490, -0.016, 0.205)→(0.488, -0.018, 0.052) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 48.659 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.488, -0.018, 0.052)→(0.497, -0.153, 0.023) | (0.492, -0.018, 0.025)→(0.509, -0.078, 0.025) | 0.139→0.076 | 1.00 / 4.000 | 0.245 | 170.380 |
| retract_1 | retract | 0.67 / step_budget | (0.497, -0.153, 0.023)→(0.495, -0.121, 0.139) | (0.509, -0.078, 0.025)→(0.508, -0.078, 0.025) | 0.076→0.076 | 1.00 / 4.000 | 0.245 | 4.755 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.640
- lateral_force_integral: None
- approach_alignment: 0.803
- goal_progress: 0.550
- terminal_score: 0.550
- phase_score: 0.660
- phase_breakdown.reach_goal_score: 0.876
- phase_breakdown.reach_pre_contact_score: 0.157

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.616
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.550
- **Median Q (composite search score)**: 0.238
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.293


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72014,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15557,"approach_1.pose_tolerance":0.02758,"approach_1.speed":0.01479,"contact_1.contact_force_threshold":3.03227,"contact_1.descend_speed":0.02659,"push_1.push_distance":0.15019,"push_1.push_speed":0.09988,"push_1.push_tolerance":0.02354,"retract_1.arc_height":0.10544,"retract_1.retract_speed":0.06044,"retract_1.retract_tolerance":0.01003},"optimized_scores":{"best_composite_score":0.23801,"best_fitness_score":0.59801,"best_task_score":0.4565},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":786.0,"contact_point_centroid":[0.47926,-0.06605,-0.0005],"force_p95":164.54948,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":202.30514,"mean_force":39.6739,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48567,-0.09055,0.03937]},{"body_a":"attachment","body_b":"push_box","contact_count":247.0,"contact_point_centroid":[0.48841,-0.05386,0.04745],"force_p95":181.39879,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.51617,"mean_force":124.30587,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.481,-0.06152,0.0472]},{"body_a":"world","body_b":"push_box","contact_count":3483.0,"contact_point_centroid":[0.47993,-0.08,-3e-05],"force_p95":0.47443,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.67624,"mean_force":0.2913,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49349,-0.11166,0.07405]},{"body_a":"attachment","body_b":"push_box","contact_count":153.0,"contact_point_centroid":[0.49339,-0.10115,0.04876],"force_p95":1.21902,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.48324,"mean_force":0.63424,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49315,-0.11312,0.04875]},{"body_a":"world","body_b":"push_box","contact_count":1620.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4858,-0.01017,0.24595]},{"body_a":"world","body_b":"push_box","contact_count":3464.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46867,-0.02241,0.11946]}],"total_contact_groups":6},"final_pose_error":0.06086,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47989,-0.08282,0.02499],"final_tcp_position":[0.49367,-0.10839,0.13168],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":202.30514,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.47199,-0.02134,0.1899],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":866.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":45.86179,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3464.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.46787,-0.02355,0.05244],"tcp_start":[0.47199,-0.02134,0.1899],"tcp_to_object_dist_end":0.02768,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":960.0,"object_pos_end":[0.48033,-0.08343,0.02496],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.06941,"object_to_goal_dist_start":0.12903,"object_z_max":0.0348,"peak_contact_force":0.24441,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1033.0,"raw_peak_contact_force":202.30514,"subtask_id":"reach_goal","tcp_end":[0.49701,-0.15238,0.02361],"tcp_start":[0.46787,-0.02355,0.05244],"tcp_to_object_dist_end":0.07095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47989,-0.08282,0.02499],"object_pos_start":[0.48033,-0.08343,0.02496],"object_to_goal_dist_end":0.07013,"object_to_goal_dist_start":0.06941,"object_z_max":0.03024,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3636.0,"raw_peak_contact_force":3.67624,"tcp_end":[0.49367,-0.10839,0.13168],"tcp_start":[0.49701,-0.15238,0.02361],"tcp_to_object_dist_end":0.11058,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14163,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1725,"approach_1.pose_tolerance":0.02303,"approach_1.speed":0.05674,"contact_1.contact_force_threshold":9.05423,"contact_1.descend_speed":0.02383,"push_1.push_distance":0.15383,"push_1.push_speed":0.05818,"push_1.push_tolerance":0.0221,"retract_1.arc_height":0.09626,"retract_1.retract_speed":0.1077,"retract_1.retract_tolerance":0.03337},"optimized_scores":{"best_composite_score":0.25602,"best_fitness_score":0.61602,"best_task_score":0.54971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":694.0,"contact_point_centroid":[0.49117,-0.07674,-0.00061],"force_p95":164.5347,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.9205,"mean_force":48.76027,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47989,-0.10255,0.03765]},{"body_a":"attachment","body_b":"push_box","contact_count":281.0,"contact_point_centroid":[0.47676,-0.06217,0.04722],"force_p95":168.11585,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":176.90788,"mean_force":119.02511,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46905,-0.06947,0.04698]},{"body_a":"attachment","body_b":"push_box","contact_count":25.0,"contact_point_centroid":[0.49899,-0.11197,0.04611],"force_p95":10.10983,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.34324,"mean_force":2.39712,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49699,-0.1234,0.04465]},{"body_a":"world","body_b":"push_box","contact_count":788.0,"contact_point_centroid":[0.50632,-0.08802,-0.00011],"force_p95":0.71608,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39967,"mean_force":0.3845,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4974,-0.12135,0.08658]},{"body_a":"world","body_b":"push_box","contact_count":1440.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47708,-0.01324,0.25343]},{"body_a":"world","body_b":"push_box","contact_count":3760.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44935,-0.02917,0.12734]}],"total_contact_groups":6},"final_pose_error":0.03335,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50558,-0.09244,0.02499],"final_tcp_position":[0.49769,-0.13213,0.15063],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":177.9205,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.45374,-0.02767,0.20579],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":48.97885,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3760.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.44738,-0.03076,0.05239],"tcp_start":[0.45374,-0.02767,0.20579],"tcp_to_object_dist_end":0.02757,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,-0.09268,0.02496],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.05763,"object_to_goal_dist_start":0.12843,"object_z_max":0.03666,"peak_contact_force":0.24473,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":975.0,"raw_peak_contact_force":177.9205,"subtask_id":"reach_goal","tcp_end":[0.4995,-0.15641,0.02342],"tcp_start":[0.44738,-0.03076,0.05239],"tcp_to_object_dist_end":0.06407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":870.0,"object_pos_end":[0.50558,-0.09244,0.02499],"object_pos_start":[0.50593,-0.09268,0.02496],"object_to_goal_dist_end":0.05783,"object_to_goal_dist_start":0.05763,"object_z_max":0.03207,"peak_contact_force":0.24522,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":813.0,"raw_peak_contact_force":10.34324,"tcp_end":[0.49769,-0.13213,0.15063],"tcp_start":[0.4995,-0.15641,0.02342],"tcp_to_object_dist_end":0.132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31579,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19127,"approach_1.pose_tolerance":0.00553,"approach_1.speed":0.05233,"contact_1.contact_force_threshold":8.87077,"contact_1.descend_speed":0.01847,"push_1.push_distance":0.18028,"push_1.push_speed":0.08099,"push_1.push_tolerance":0.01449,"retract_1.arc_height":0.11372,"retract_1.retract_speed":0.08562,"retract_1.retract_tolerance":0.04632},"optimized_scores":{"best_composite_score":0.20053,"best_fitness_score":0.56053,"best_task_score":0.37604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":257.0,"contact_point_centroid":[0.54675,-0.02618,0.04954],"force_p95":129.03893,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.91584,"mean_force":91.31036,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53949,-0.0343,0.04962]},{"body_a":"world","body_b":"push_box","contact_count":1081.0,"contact_point_centroid":[0.54431,-0.04415,-0.00026],"force_p95":85.31484,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.14196,"mean_force":22.11852,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52152,-0.07959,0.03825]},{"body_a":"world","body_b":"push_box","contact_count":1472.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52084,0.00055,0.25989]},{"body_a":"world","body_b":"push_box","contact_count":3708.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54469,0.00116,0.1334]},{"body_a":"world","body_b":"push_box","contact_count":624.0,"contact_point_centroid":[0.53998,-0.05823,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49382,-0.1215,0.07258]}],"total_contact_groups":5},"final_pose_error":0.04632,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53998,-0.05823,0.02499],"final_tcp_position":[0.49471,-0.12315,0.13469],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":130.91584,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.54424,0.00114,0.22073],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.19595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":51.13508,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3708.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.54752,0.00122,0.05239],"tcp_start":[0.54424,0.00114,0.22073],"tcp_to_object_dist_end":0.02797,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.53998,-0.05823,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1001,"object_to_goal_dist_start":0.16043,"object_z_max":0.03493,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1338.0,"raw_peak_contact_force":130.91584,"subtask_id":"reach_goal","tcp_end":[0.49577,-0.14908,0.02306],"tcp_start":[0.54752,0.00122,0.05239],"tcp_to_object_dist_end":0.10105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.53998,-0.05823,0.02499],"object_pos_start":[0.53998,-0.05823,0.02499],"object_to_goal_dist_end":0.1001,"object_to_goal_dist_start":0.1001,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":624.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49471,-0.12315,0.13469],"tcp_start":[0.49577,-0.14908,0.02306],"tcp_to_object_dist_end":0.13527,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```