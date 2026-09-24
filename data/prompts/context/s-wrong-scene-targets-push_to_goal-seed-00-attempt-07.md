## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | impedance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.4578 | 0.25 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | arc_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.3383 | 0.00 | ❌ rejected |
| 5 | approach → push → retract | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1819 | 0.00 | ❌ rejected |
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1312 | 0.00 | ❌ rejected |
| 3 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2384 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5164354024785746, -0.027625594348335558, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5164354024785746, -0.027625594348335558, 0.025]
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.806, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.458) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: -0.458
- **task_score** (E): 0.251
- **fitness_score**: 0.112  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 1.00 | 1.00 | 0.2600 |
| approach_1 | 1.00 | 0.67 | 0.1587 |
| push_1 | 1.00 | 1.00 | 0.1258 |
| retract_1 | 1.00 | 1.00 | 0.1220 |
| lift_1 | 1.00 | 1.00 | 0.0803 |
| insert_2 | 1.00 | 1.00 | 0.1813 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.137, 0.080) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 1.00 / step_budget | (0.497, -0.137, 0.080)→(0.502, 0.016, 0.042) | (0.496, 0.001, 0.025)→(0.501, 0.027, 0.025) | 0.152→0.178 | 0.67 / 2.667 | 128.449 | 153.734 |
| push_1 | push | 1.00 / step_budget | (0.502, 0.016, 0.042)→(0.501, -0.107, 0.023) | (0.501, 0.027, 0.025)→(0.510, -0.013, 0.025) | 0.178→0.138 | 1.00 / 4.000 | 0.245 | 108.386 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.107, 0.023)→(0.499, -0.092, 0.144) | (0.510, -0.013, 0.025)→(0.510, -0.013, 0.025) | 0.138→0.138 | 1.00 / 4.000 | 0.245 | 0.974 |
| lift_1 | lift | 1.00 / step_budget | (0.499, -0.092, 0.144)→(0.496, -0.092, 0.224) | (0.510, -0.013, 0.025)→(0.510, -0.013, 0.025) | 0.138→0.138 | 1.00 / 4.000 | 0.245 | 0.245 |
| insert_2 | insert | 1.00 / step_budget | (0.496, -0.092, 0.224)→(0.496, -0.143, 0.062) | (0.510, -0.013, 0.025)→(0.510, -0.013, 0.025) | 0.138→0.138 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.519
- lateral_force_integral: None
- approach_alignment: 0.762
- goal_progress: 0.451
- terminal_score: 0.451
- phase_score: 0.025
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.083

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.195
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.451
- **Median Q (composite search score)**: -0.432
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.314


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51644,-0.02763,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09547,"average_solve_count":419.0,"average_success_count":419.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06958,"insert_1.insert_speed":0.07921,"insert_2.final_insert_speed":0.06254,"lift_1.lift_speed":0.02217,"push_1.push_distance":0.1402,"push_1.push_speed":0.02765,"retract_1.retract_arc_height":0.05076,"retract_1.retract_height":0.13474,"retract_1.retract_speed":0.06115},"optimized_scores":{"best_composite_score":-0.4323,"best_fitness_score":0.1377,"best_task_score":0.30329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":292.0,"contact_point_centroid":[0.53039,-0.03442,0.04766],"force_p95":199.7202,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":210.73207,"mean_force":164.08496,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51903,-0.03549,0.04837]},{"body_a":"attachment","body_b":"push_box","contact_count":322.0,"contact_point_centroid":[0.53621,-0.03733,0.04714],"force_p95":160.74719,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.97942,"mean_force":130.14848,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52791,-0.04407,0.04688]},{"body_a":"world","body_b":"push_box","contact_count":1845.0,"contact_point_centroid":[0.51934,-0.02155,-0.00023],"force_p95":92.39634,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":121.96247,"mean_force":26.32612,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51102,-0.06318,0.05501]},{"body_a":"world","body_b":"push_box","contact_count":982.0,"contact_point_centroid":[0.52082,-0.04532,-0.00055],"force_p95":116.64133,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.48026,"mean_force":43.187,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52148,-0.06302,0.04129]},{"body_a":"world","body_b":"push_box","contact_count":1651.0,"contact_point_centroid":[0.51148,-0.06205,-4e-05],"force_p95":0.47768,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43138,"mean_force":0.28418,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49777,-0.09723,0.08435]},{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.50094,-0.08233,0.05025],"force_p95":1.83775,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.00261,"mean_force":0.70137,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49739,-0.09377,0.04824]},{"body_a":"world","body_b":"push_box","contact_count":2116.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49775,-0.06716,0.19023]},{"body_a":"world","body_b":"push_box","contact_count":1156.0,"contact_point_centroid":[0.51088,-0.06467,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49585,-0.1156,0.18337]},{"body_a":"world","body_b":"push_box","contact_count":1336.0,"contact_point_centroid":[0.51088,-0.06467,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.49536,-0.12929,0.14634]}],"total_contact_groups":9},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51088,-0.06467,0.02499],"final_tcp_position":[0.49627,-0.14467,0.06388],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":210.73207,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49691,-0.13683,0.07967],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.52291,-0.01247,0.02407],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.13943,"object_to_goal_dist_start":0.12347,"object_z_max":0.02501,"peak_contact_force":196.88077,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2137.0,"raw_peak_contact_force":210.73207,"subtask_id":"push_to_goal","tcp_end":[0.529,-0.01175,0.04664],"tcp_start":[0.49691,-0.13683,0.07967],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.51208,-0.06404,0.02492],"object_pos_start":[0.52291,-0.01247,0.02407],"object_to_goal_dist_end":0.0868,"object_to_goal_dist_start":0.13943,"object_z_max":0.03589,"peak_contact_force":0.24396,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1304.0,"raw_peak_contact_force":161.97942,"subtask_id":"push_to_goal","tcp_end":[0.5008,-0.13085,0.02367],"tcp_start":[0.529,-0.01175,0.04664],"tcp_to_object_dist_end":0.06777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.51088,-0.06467,0.02499],"object_pos_start":[0.51208,-0.06404,0.02492],"object_to_goal_dist_end":0.08603,"object_to_goal_dist_start":0.0868,"object_z_max":0.02985,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1691.0,"raw_peak_contact_force":2.43138,"subtask_id":"push_to_goal","tcp_end":[0.49805,-0.1159,0.14542],"tcp_start":[0.5008,-0.13085,0.02367],"tcp_to_object_dist_end":0.1315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.51088,-0.06467,0.02499],"object_pos_start":[0.51088,-0.06467,0.02499],"object_to_goal_dist_end":0.08603,"object_to_goal_dist_start":0.08603,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49574,-0.11541,0.22559],"tcp_start":[0.49805,-0.1159,0.14542],"tcp_to_object_dist_end":0.20747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.51088,-0.06467,0.02499],"object_pos_start":[0.51088,-0.06467,0.02499],"object_to_goal_dist_end":0.08603,"object_to_goal_dist_start":0.08603,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49627,-0.14467,0.06388],"tcp_start":[0.49574,-0.11541,0.22559],"tcp_to_object_dist_end":0.09015,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50142,0.05406,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0279,"average_solve_count":466.0,"average_success_count":466.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07182,"insert_1.insert_speed":0.05331,"insert_2.final_insert_speed":0.05785,"lift_1.lift_speed":0.03573,"push_1.push_distance":0.12622,"push_1.push_speed":0.02642,"retract_1.retract_arc_height":0.03944,"retract_1.retract_height":0.12822,"retract_1.retract_speed":0.03004},"optimized_scores":{"best_composite_score":-0.56645,"best_fitness_score":0.00355,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.50001,0.05039,0.04789],"force_p95":44.12131,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.06572,"mean_force":11.45086,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49731,0.03869,0.03949]},{"body_a":"world","body_b":"push_box","contact_count":1631.0,"contact_point_centroid":[0.50187,0.05656,-1e-05],"force_p95":1.08274,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.203,"mean_force":0.71584,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49556,-0.05228,0.05827]},{"body_a":"world","body_b":"push_box","contact_count":739.0,"contact_point_centroid":[0.51025,0.10616,-4e-05],"force_p95":0.30245,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82516,"mean_force":0.26727,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49734,0.02986,0.027]},{"body_a":"world","body_b":"push_box","contact_count":2204.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49774,-0.0671,0.19033]},{"body_a":"world","body_b":"push_box","contact_count":1760.0,"contact_point_centroid":[0.51019,0.10581,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49612,0.02047,0.07519]},{"body_a":"world","body_b":"push_box","contact_count":1084.0,"contact_point_centroid":[0.51019,0.10581,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49405,0.00667,0.17436]},{"body_a":"world","body_b":"push_box","contact_count":1876.0,"contact_point_centroid":[0.51019,0.10581,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.49412,-0.06221,0.13621]}],"total_contact_groups":7},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51019,0.10581,0.02499],"final_tcp_position":[0.49606,-0.13419,0.05655],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":52.06572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49687,-0.13682,0.07967],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.19861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.50855,0.10133,0.02593],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.25148,"object_to_goal_dist_start":0.20406,"object_z_max":0.02623,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1695.0,"raw_peak_contact_force":52.06572,"subtask_id":"push_to_goal","tcp_end":[0.49785,0.06469,0.03414],"tcp_start":[0.49687,-0.13682,0.07967],"tcp_to_object_dist_end":0.03905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.51019,0.10581,0.02499],"object_pos_start":[0.50855,0.10133,0.02593],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.25148,"object_z_max":0.02593,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":739.0,"raw_peak_contact_force":1.82516,"subtask_id":"push_to_goal","tcp_end":[0.49918,-0.00584,0.02266],"tcp_start":[0.49785,0.06469,0.03414],"tcp_to_object_dist_end":0.11221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.51019,0.10581,0.02499],"object_pos_start":[0.51019,0.10581,0.02499],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.25601,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49625,0.00688,0.13574],"tcp_start":[0.49918,-0.00584,0.02266],"tcp_to_object_dist_end":0.14915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.51019,0.10581,0.02499],"object_pos_start":[0.51019,0.10581,0.02499],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.25601,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49386,0.00681,0.21596],"tcp_start":[0.49625,0.00688,0.13574],"tcp_to_object_dist_end":0.21573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.51019,0.10581,0.02499],"object_pos_start":[0.51019,0.10581,0.02499],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.25601,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49606,-0.13419,0.05655],"tcp_start":[0.49386,0.00681,0.21596],"tcp_to_object_dist_end":0.24248,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47139,-0.02418,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35294,"average_solve_count":374.0,"average_success_count":374.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06436,"insert_1.insert_speed":0.06998,"insert_2.final_insert_speed":0.06887,"lift_1.lift_speed":0.05316,"push_1.push_distance":0.1974,"push_1.push_speed":0.0351,"retract_1.retract_arc_height":0.06961,"retract_1.retract_height":0.13787,"retract_1.retract_speed":0.0878},"optimized_scores":{"best_composite_score":-0.37462,"best_fitness_score":0.19538,"best_task_score":0.45096},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":306.0,"contact_point_centroid":[0.48817,-0.02887,0.04763],"force_p95":194.49025,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.40441,"mean_force":160.8765,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4768,-0.0296,0.04826]},{"body_a":"world","body_b":"push_box","contact_count":1050.0,"contact_point_centroid":[0.50256,-0.05623,-0.00047],"force_p95":153.92975,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":161.35331,"mean_force":36.74058,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49521,-0.1052,0.03437]},{"body_a":"attachment","body_b":"push_box","contact_count":284.0,"contact_point_centroid":[0.49765,-0.032,0.04678],"force_p95":157.72072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":160.44248,"mean_force":131.34353,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49028,-0.04022,0.04652]},{"body_a":"world","body_b":"push_box","contact_count":1907.0,"contact_point_centroid":[0.47202,-0.01767,-0.00024],"force_p95":90.63683,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.11128,"mean_force":26.17788,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48039,-0.05799,0.05464]},{"body_a":"push_box","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.50625,-0.0622,0.0836],"force_p95":20.92806,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.57144,"mean_force":11.01967,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49426,-0.10628,0.03384]},{"body_a":"world","body_b":"push_box","contact_count":2140.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49772,-0.06731,0.18998]},{"body_a":"world","body_b":"push_box","contact_count":2112.0,"contact_point_centroid":[0.50884,-0.07971,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50097,-0.1376,0.08213]},{"body_a":"world","body_b":"push_box","contact_count":1104.0,"contact_point_centroid":[0.50884,-0.07971,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49917,-0.16631,0.18915]},{"body_a":"world","body_b":"push_box","contact_count":1320.0,"contact_point_centroid":[0.50884,-0.07971,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.49736,-0.15881,0.14916]}],"total_contact_groups":9},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50884,-0.07971,0.02499],"final_tcp_position":[0.49666,-0.15128,0.06436],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":198.40441,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2140.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49689,-0.13695,0.07949],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.47205,-0.00888,0.02411],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.12903,"object_z_max":0.02503,"peak_contact_force":188.46696,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2213.0,"raw_peak_contact_force":198.40441,"subtask_id":"push_to_goal","tcp_end":[0.4792,-0.00598,0.04644],"tcp_start":[0.49689,-0.13695,0.07949],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.50884,-0.07971,0.02499],"object_pos_start":[0.47205,-0.00888,0.02411],"object_to_goal_dist_end":0.07084,"object_to_goal_dist_start":0.14386,"object_z_max":0.04326,"peak_contact_force":0.24524,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1392.0,"raw_peak_contact_force":161.35331,"subtask_id":"push_to_goal","tcp_end":[0.50398,-0.18392,0.02193],"tcp_start":[0.4792,-0.00598,0.04644],"tcp_to_object_dist_end":0.10437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":990.0,"object_pos_end":[0.50884,-0.07971,0.02499],"object_pos_start":[0.50884,-0.07971,0.02499],"object_to_goal_dist_end":0.07084,"object_to_goal_dist_start":0.07084,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.50131,-0.1668,0.15012],"tcp_start":[0.50398,-0.18392,0.02193],"tcp_to_object_dist_end":0.15264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50884,-0.07971,0.02499],"object_pos_start":[0.50884,-0.07971,0.02499],"object_to_goal_dist_end":0.07084,"object_to_goal_dist_start":0.07084,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49908,-0.16611,0.23051],"tcp_start":[0.50131,-0.1668,0.15012],"tcp_to_object_dist_end":0.22316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.50884,-0.07971,0.02499],"object_pos_start":[0.50884,-0.07971,0.02499],"object_to_goal_dist_end":0.07084,"object_to_goal_dist_start":0.07084,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49666,-0.15128,0.06436],"tcp_start":[0.49908,-0.16611,0.23051],"tcp_to_object_dist_end":0.08258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```