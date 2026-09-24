## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1238 | 0.01 | ❌ rejected |
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2063 | 0.55 | ✅ accepted |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.4501 | 0.00 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.2057 | 0.53 | ✅ accepted |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2056 | 0.54 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

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
| `object` | offset from object initial position (0.5014185949640309, 0.05405564355911223, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.124) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
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

```

## Design Metrics

- **Composite score**: -0.124
- **task_score** (E): 0.008
- **fitness_score**: 0.056  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1759 |
| descend_1 | 1.00 | 1.00 | 0.0854 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.473, -0.001, 0.132) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.473, -0.001, 0.132)→(0.488, -0.001, 0.048) | (0.474, -0.001, 0.025)→(0.479, -0.001, 0.024) | 0.154→0.153 | 1.00 / 4.667 | 257.907 | 280.876 |
| push_1 | push | 0.00 / guard_failure | (0.488, -0.001, 0.048)→(0.488, -0.001, 0.048) | (0.479, -0.001, 0.024)→(0.479, -0.001, 0.024) | 0.153→0.153 | 1.00 / 4.667 | 115.578 | 115.578 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.035
- lateral_force_integral: None
- approach_alignment: 0.531
- goal_progress: 0.015
- terminal_score: 0.015
- phase_score: 0.107
- phase_breakdown.goal_reach_score: 0.082
- phase_breakdown.pre_contact_score: 0.209

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.070
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.015
- **Median Q (composite search score)**: -0.114
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 2.7
- **Final σ (mean)**: 0.275


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22727,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31714,"push_1.push_distance":0.14562,"push_1.push_speed":0.2665},"optimized_scores":{"best_composite_score":-0.14732,"best_fitness_score":0.03268,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":169.0,"contact_point_centroid":[0.51555,0.05365,0.04687],"force_p95":258.77117,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":265.1493,"mean_force":203.85943,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50454,0.05347,0.04996]},{"body_a":"world","body_b":"push_box","contact_count":2241.0,"contact_point_centroid":[0.50202,0.05426,-0.00015],"force_p95":116.71204,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.14736,"mean_force":15.68698,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49843,0.0518,0.07955]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52517,0.0548,0.04534],"force_p95":110.15062,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.15062,"mean_force":110.15062,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.514,0.05473,0.04749]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50489,0.05459,-0.00062],"force_p95":36.72912,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.53881,"mean_force":27.77458,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.514,0.05473,0.04749]},{"body_a":"world","body_b":"push_box","contact_count":2256.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49821,0.02386,0.2182]}],"total_contact_groups":5},"final_pose_error":0.14796,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50607,0.05463,0.02373],"final_tcp_position":[0.51407,0.05474,0.04752],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":265.1493,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49801,0.05012,0.13176],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":563.0,"n_steps_budget":690.0,"object_pos_end":[0.50607,0.05463,0.02373],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20473,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":247.15228,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2410.0,"raw_peak_contact_force":265.1493,"subtask_id":"pre_contact","tcp_end":[0.514,0.05473,0.04749],"tcp_start":[0.49801,0.05012,0.13176],"tcp_to_object_dist_end":0.02506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50607,0.05463,0.02373],"object_pos_start":[0.50607,0.05463,0.02373],"object_to_goal_dist_end":0.20473,"object_to_goal_dist_start":0.20473,"object_z_max":0.02373,"peak_contact_force":110.15062,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":110.15062,"subtask_id":"goal_reach","tcp_end":[0.51407,0.05474,0.04752],"tcp_start":[0.514,0.05473,0.04749],"tcp_to_object_dist_end":0.0251,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22727,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.2555,"push_1.push_distance":0.16905,"push_1.push_speed":0.18022},"optimized_scores":{"best_composite_score":-0.11441,"best_fitness_score":0.06559,"best_task_score":0.00906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":172.0,"contact_point_centroid":[0.48582,-0.0242,0.04664],"force_p95":272.6828,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":283.6557,"mean_force":216.45641,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47519,-0.02409,0.05037]},{"body_a":"world","body_b":"push_box","contact_count":2271.0,"contact_point_centroid":[0.472,-0.0244,-0.00016],"force_p95":123.13751,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.6333,"mean_force":16.70495,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46959,-0.02333,0.08029]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.4956,-0.0248,0.04505],"force_p95":116.31948,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.31948,"mean_force":116.31948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48477,-0.02468,0.04785]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47463,-0.02441,-0.00065],"force_p95":40.03083,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.39852,"mean_force":29.3235,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48477,-0.02468,0.04785]},{"body_a":"world","body_b":"push_box","contact_count":2248.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48483,-0.01076,0.2181]}],"total_contact_groups":5},"final_pose_error":0.16884,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47589,-0.02444,0.02367],"final_tcp_position":[0.48484,-0.02469,0.04788],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":283.6557,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":562.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47004,-0.02252,0.13217],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":572.0,"n_steps_budget":690.0,"object_pos_end":[0.47589,-0.02444,0.02367],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12786,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":259.39632,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2443.0,"raw_peak_contact_force":283.6557,"subtask_id":"pre_contact","tcp_end":[0.48477,-0.02468,0.04785],"tcp_start":[0.47004,-0.02252,0.13217],"tcp_to_object_dist_end":0.02577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.47589,-0.02444,0.02367],"object_pos_start":[0.47589,-0.02444,0.02367],"object_to_goal_dist_end":0.12786,"object_to_goal_dist_start":0.12786,"object_z_max":0.02367,"peak_contact_force":116.31948,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":116.31948,"subtask_id":"goal_reach","tcp_end":[0.48484,-0.02469,0.04788],"tcp_start":[0.48477,-0.02468,0.04785],"tcp_to_object_dist_end":0.02581,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26087,"average_solve_count":46.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.18197,"push_1.push_distance":0.17379,"push_1.push_speed":0.18585},"optimized_scores":{"best_composite_score":-0.10972,"best_fitness_score":0.07028,"best_task_score":0.0147},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":175.0,"contact_point_centroid":[0.46489,-0.0317,0.04648],"force_p95":281.23966,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":293.8227,"mean_force":225.32709,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45453,-0.03149,0.0506]},{"body_a":"world","body_b":"push_box","contact_count":2296.0,"contact_point_centroid":[0.45081,-0.03176,-0.00017],"force_p95":126.09593,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.45346,"mean_force":17.48569,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44925,-0.03054,0.08016]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.47487,-0.03249,0.04486],"force_p95":120.26286,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.26286,"mean_force":120.26286,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46429,-0.03229,0.04805]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.4615,-0.04022,-0.0009],"force_p95":53.36343,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.59336,"mean_force":40.41514,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46429,-0.03229,0.04805]},{"body_a":"world","body_b":"push_box","contact_count":2480.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47506,-0.01424,0.21709]}],"total_contact_groups":5},"final_pose_error":0.17163,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4545,-0.03193,0.02363],"final_tcp_position":[0.46435,-0.0323,0.04808],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":293.8227,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":620.0,"n_steps_budget":660.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2480.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.4501,-0.02959,0.13134],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":577.0,"n_steps_budget":690.0,"object_pos_end":[0.45451,-0.03193,0.02363],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12654,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":267.17363,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2471.0,"raw_peak_contact_force":293.8227,"subtask_id":"pre_contact","tcp_end":[0.46429,-0.03229,0.04805],"tcp_start":[0.4501,-0.02959,0.13134],"tcp_to_object_dist_end":0.02631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.4545,-0.03193,0.02363],"object_pos_start":[0.45451,-0.03193,0.02363],"object_to_goal_dist_end":0.12655,"object_to_goal_dist_start":0.12654,"object_z_max":0.02363,"peak_contact_force":120.26286,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":120.26286,"subtask_id":"goal_reach","tcp_end":[0.46435,-0.0323,0.04808],"tcp_start":[0.46429,-0.03229,0.04805],"tcp_to_object_dist_end":0.02637,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```