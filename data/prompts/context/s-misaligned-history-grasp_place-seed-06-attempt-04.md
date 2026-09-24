## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.1415 | 0.25 | ✅ accepted |
| 3 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.5159 | 0.15 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.1417 | 0.25 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.1416 | 0.25 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.2456 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=-0.246) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    yaw_angle:
      type: angle
      range:
      - 0.1
      - 1.57

```

## Design Metrics

- **Composite score**: -0.246
- **task_score** (E): 0.167
- **fitness_score**: 0.284  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1476 |
| descend_to_grasp | 1.00 | 1.00 | 0.0939 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.33 | 1.00 | 0.1590 |
| transport_to_goal | 0.33 | 1.00 | 0.1824 |
| place | 1.00 | 1.00 | 0.0878 |
| release_object | 1.00 | 1.00 | 0.0217 |
| retract | 1.00 | 1.00 | 0.1054 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.026, 0.158) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.026, 0.158)→(0.495, 0.024, 0.065) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 8.136 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.065)→(0.487, 0.024, 0.056) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 28.333 | 0.145 | 0.193 |
| lift_object | lift | 0.33 / step_budget | (0.483, 0.024, 0.163)→(0.481, 0.024, 0.322) | (0.500, 0.024, 0.026)→(0.480, 0.040, 0.019) | 0.272→0.275 | 1.00 / 8.333 | 94251.279 | 0.777 |
| transport_to_goal | approach | 0.33 / step_budget | (0.481, 0.024, 0.322)→(0.567, 0.144, 0.265) | (0.480, 0.040, 0.019)→(0.480, 0.040, 0.019) | 0.275→0.275 | 1.00 / 8.667 | 94251.824 | 0.123 |
| place | descend | 1.00 / step_budget | (0.567, 0.144, 0.265)→(0.593, 0.191, 0.209) | (0.480, 0.040, 0.019)→(0.480, 0.040, 0.019) | 0.275→0.275 | 1.00 / 8.333 | 91005.979 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.593, 0.191, 0.209)→(0.588, 0.189, 0.230) | (0.480, 0.040, 0.019)→(0.480, 0.040, 0.019) | 0.275→0.275 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.588, 0.189, 0.230)→(0.596, 0.195, 0.335) | (0.480, 0.040, 0.019)→(0.480, 0.040, 0.019) | 0.275→0.275 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.233
- phase_score: 0.115
- phase_breakdown.place_at_goal_score: 0.000
- phase_breakdown.lift_object_score: 0.011
- phase_breakdown.reach_object_score: 0.560
- grasp_place_fitness: 0.318

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.318
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.233
- **Median Q (composite search score)**: -0.255
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.320


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12027,"average_solve_count":291.0,"average_success_count":291.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.appr_speed":0.0801,"descend_to_grasp.desc_speed":0.06651,"lift_object.lift_hgt":0.10615,"lift_object.lift_spd":0.02007,"place.plc_spd":0.04945,"retract.retr_spd":0.06409,"transport_to_goal.trn_spd":0.09073},"optimized_scores":{"best_composite_score":-0.27047,"best_fitness_score":0.25953,"best_task_score":0.11711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5079.0,"contact_point_centroid":[0.48139,-0.00886,-0.00203],"force_p95":0.12321,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83637,"mean_force":0.12611,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48484,-0.01462,0.15006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6055.0,"contact_point_centroid":[0.48662,0.00397,0.07038],"force_p95":0.12909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23594,"mean_force":0.0875,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48693,-0.01468,0.07442]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01564,-0.00207],"force_p95":0.14452,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18781,"mean_force":0.1279,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49213,-0.01476,0.05716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6846.0,"contact_point_centroid":[0.48698,-0.03314,0.07122],"force_p95":0.10498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16954,"mean_force":0.07726,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48692,-0.01468,0.07517]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.499,0.0029,0.22779]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49803,-0.01237,0.11057]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48055,-0.00827,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5055,0.03343,0.25299]},{"body_a":"world","body_b":"grasp_target","contact_count":3548.0,"contact_point_centroid":[0.48055,-0.00827,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.55672,0.13542,0.25582]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48055,-0.00827,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5784,0.18109,0.24303]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48055,-0.00827,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57922,0.18268,0.31232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2906.0,"contact_point_centroid":[0.49115,0.00409,0.05236],"force_p95":0.093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10721,"mean_force":0.07091,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49101,-0.01474,0.05592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.49082,-0.03353,0.05281],"force_p95":0.08894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08916,"mean_force":0.06488,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49101,-0.01474,0.05593]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4647.0,"contact_point_centroid":[0.48451,-0.01461,0.16165],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01072,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48445,-0.01461,0.15937]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4221.0,"contact_point_centroid":[0.5055,0.03359,0.25534],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50558,0.03358,0.25309]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3776.0,"contact_point_centroid":[0.5567,0.13551,0.25809],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01047,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.55676,0.1355,0.2558]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.58028,0.18193,0.24117],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58044,0.18191,0.23885]}],"total_contact_groups":16},"final_pose_error":0.034,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48055,-0.00827,0.01602],"final_tcp_position":[0.58344,0.18542,0.36436],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273006.29954,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49975,-0.01001,0.15696],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49886,-0.01483,0.06466],"tcp_start":[0.49975,-0.01001,0.15696],"tcp_to_object_dist_end":0.03896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.0151,0.02575],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14319,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7918.0,"raw_peak_contact_force":0.18781,"tcp_end":[0.49098,-0.01474,0.05589],"tcp_start":[0.49886,-0.01483,0.06466],"tcp_to_object_dist_end":0.03274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1814.0,"n_steps_budget":1000.0,"object_pos_end":[0.48055,-0.00827,0.01602],"object_pos_start":[0.50376,-0.0151,0.02575],"object_to_goal_dist_end":0.32169,"object_to_goal_dist_start":0.31207,"object_z_max":0.05693,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22627.0,"raw_peak_contact_force":0.83637,"subtask_id":"lift_object","tcp_end":[0.48375,-0.01458,0.22326],"tcp_start":[0.48692,-0.01467,0.12657],"tcp_to_object_dist_end":0.20737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48055,-0.00827,0.01602],"object_pos_start":[0.48055,-0.00827,0.01602],"object_to_goal_dist_end":0.32169,"object_to_goal_dist_start":0.32169,"object_z_max":0.01602,"peak_contact_force":273006.29954,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8221.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.53019,0.08138,0.27765],"tcp_start":[0.48375,-0.01458,0.22326],"tcp_to_object_dist_end":0.28099,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":887.0,"n_steps_budget":1000.0,"object_pos_end":[0.48055,-0.00827,0.01602],"object_pos_start":[0.48055,-0.00827,0.01602],"object_to_goal_dist_end":0.32169,"object_to_goal_dist_start":0.32169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7324.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58157,0.18213,0.24161],"tcp_start":[0.53019,0.08138,0.27765],"tcp_to_object_dist_end":0.312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48055,-0.00827,0.01602],"object_pos_start":[0.48055,-0.00827,0.01602],"object_to_goal_dist_end":0.32169,"object_to_goal_dist_start":0.32169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57725,0.18061,0.26293],"tcp_start":[0.58157,0.18213,0.24161],"tcp_to_object_dist_end":0.32557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48055,-0.00827,0.01602],"object_pos_start":[0.48055,-0.00827,0.01602],"object_to_goal_dist_end":0.32169,"object_to_goal_dist_start":0.32169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58344,0.18542,0.36436],"tcp_start":[0.57725,0.18061,0.26293],"tcp_to_object_dist_end":0.41163,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41121,"average_solve_count":321.0,"average_success_count":321.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.appr_speed":0.05343,"descend_to_grasp.desc_speed":0.03154,"lift_object.lift_hgt":0.21775,"lift_object.lift_spd":0.08924,"place.plc_spd":0.03477,"retract.retr_spd":0.06329,"transport_to_goal.trn_spd":0.09897},"optimized_scores":{"best_composite_score":-0.21163,"best_fitness_score":0.31837,"best_task_score":0.23349},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5232.0,"contact_point_centroid":[0.49381,0.05812,-0.00211],"force_p95":0.12338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99256,"mean_force":0.12689,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49442,0.03838,0.25999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7338.0,"contact_point_centroid":[0.49549,0.05691,0.09234],"force_p95":0.10931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31841,"mean_force":0.07778,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4955,0.03846,0.09608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6316.0,"contact_point_centroid":[0.49498,0.01978,0.0899],"force_p95":0.1371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28093,"mean_force":0.08954,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49552,0.03846,0.09377]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03969,-0.00207],"force_p95":0.14367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18792,"mean_force":0.12799,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50059,0.03888,0.05657]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50241,0.02722,0.23244]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50613,0.03982,0.11128]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49335,0.05873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55969,0.10551,0.32273]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.49335,0.05873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.61838,0.16628,0.18279]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49335,0.05873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61744,0.16811,0.15314]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49335,0.05873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61834,0.16888,0.22185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2998.0,"contact_point_centroid":[0.49953,0.02001,0.05237],"force_p95":0.09146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10615,"mean_force":0.06845,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03878,0.05529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2968.0,"contact_point_centroid":[0.49968,0.05759,0.05201],"force_p95":0.09349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09385,"mean_force":0.07014,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49946,0.03878,0.05529]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4990.0,"contact_point_centroid":[0.49385,0.03838,0.27665],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01067,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49422,0.03837,0.27442]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4277.0,"contact_point_centroid":[0.55911,0.10571,0.32453],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01043,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55989,0.10572,0.32246]},{"body_a":"left_finger","body_b":"right_finger","contact_count":814.0,"contact_point_centroid":[0.61774,0.16628,0.18513],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.0103,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.61838,0.16628,0.18278]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.61911,0.16897,0.1514],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62002,0.16896,0.14889]}],"total_contact_groups":16},"final_pose_error":0.02192,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.49335,0.05873,0.01602],"final_tcp_position":[0.62363,0.17102,0.27351],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9749.04994,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50765,0.04039,0.15858],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":24.16288,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50738,0.03944,0.06434],"tcp_start":[0.50765,0.04039,0.15858],"tcp_to_object_dist_end":0.03867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03917,0.02575],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21275,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14194,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7766.0,"raw_peak_contact_force":0.18792,"tcp_end":[0.49942,0.03878,0.05525],"tcp_start":[0.50738,0.03944,0.06434],"tcp_to_object_dist_end":0.03226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1916.0,"n_steps_budget":1000.0,"object_pos_end":[0.49335,0.05873,0.01602],"object_pos_start":[0.51246,0.03917,0.02575],"object_to_goal_dist_end":0.21819,"object_to_goal_dist_start":0.21275,"object_z_max":0.10002,"peak_contact_force":9748.97659,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23876.0,"raw_peak_contact_force":0.99256,"subtask_id":"lift_object","tcp_end":[0.49457,0.03841,0.40556],"tcp_start":[0.49598,0.03851,0.20059],"tcp_to_object_dist_end":0.39008,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49335,0.05873,0.01602],"object_pos_start":[0.49335,0.05873,0.01602],"object_to_goal_dist_end":0.21819,"object_to_goal_dist_start":0.21819,"object_z_max":0.01602,"peak_contact_force":9749.04994,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8277.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.61709,0.16397,0.21332],"tcp_start":[0.49457,0.03841,0.40556],"tcp_to_object_dist_end":0.25557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.49335,0.05873,0.01602],"object_pos_start":[0.49335,0.05873,0.01602],"object_to_goal_dist_end":0.21819,"object_to_goal_dist_start":0.21819,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1566.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62173,0.16944,0.15248],"tcp_start":[0.61709,0.16397,0.21332],"tcp_to_object_dist_end":0.21762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49335,0.05873,0.01602],"object_pos_start":[0.49335,0.05873,0.01602],"object_to_goal_dist_end":0.21819,"object_to_goal_dist_start":0.21819,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6159,0.16759,0.17302],"tcp_start":[0.62173,0.16944,0.15248],"tcp_to_object_dist_end":0.22698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49335,0.05873,0.01602],"object_pos_start":[0.49335,0.05873,0.01602],"object_to_goal_dist_end":0.21819,"object_to_goal_dist_start":0.21819,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62363,0.17102,0.27351],"tcp_start":[0.6159,0.16759,0.17302],"tcp_to_object_dist_end":0.30966,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40625,"average_solve_count":288.0,"average_success_count":288.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.appr_speed":0.10082,"descend_to_grasp.desc_speed":0.05601,"lift_object.lift_hgt":0.18644,"lift_object.lift_spd":0.06334,"place.plc_spd":0.02504,"retract.retr_spd":0.08004,"transport_to_goal.trn_spd":0.07201},"optimized_scores":{"best_composite_score":-0.2546,"best_fitness_score":0.2754,"best_task_score":0.1505},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6628.0,"contact_point_centroid":[0.46741,0.0671,-0.00207],"force_p95":0.1914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50062,"mean_force":0.12803,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46549,0.04702,0.19116]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2640.0,"contact_point_centroid":[0.46699,0.06565,0.06338],"force_p95":0.11338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27832,"mean_force":0.07596,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46742,0.0472,0.06721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2232.0,"contact_point_centroid":[0.46605,0.02847,0.06272],"force_p95":0.13079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27604,"mean_force":0.08921,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46744,0.0472,0.06682]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48273,0.04867,-0.00209],"force_p95":0.15072,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20235,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47177,0.04763,0.05797]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49019,0.03095,0.23377]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47833,0.04825,0.11204]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46718,0.06843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50786,0.11639,0.32726]},{"body_a":"world","body_b":"grasp_target","contact_count":1340.0,"contact_point_centroid":[0.46718,0.06843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.56269,0.20305,0.26718]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46718,0.06843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57197,0.22055,0.23427]},{"body_a":"world","body_b":"grasp_target","contact_count":3600.0,"contact_point_centroid":[0.46718,0.06843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5742,0.22328,0.30878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2660.0,"contact_point_centroid":[0.46982,0.0287,0.05311],"force_p95":0.09826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11059,"mean_force":0.07672,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47069,0.04753,0.05683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3234.0,"contact_point_centroid":[0.47083,0.06623,0.05338],"force_p95":0.0887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08903,"mean_force":0.06437,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4707,0.04753,0.05683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6483.0,"contact_point_centroid":[0.4652,0.04702,0.20127],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01631,"mean_force":0.01073,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46534,0.047,0.19906]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4253.0,"contact_point_centroid":[0.50734,0.11652,0.32947],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01048,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50794,0.11652,0.32721]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1429.0,"contact_point_centroid":[0.5621,0.203,0.26963],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01045,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.56265,0.20299,0.26732]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.57337,0.22155,0.23198],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57389,0.22153,0.22975]}],"total_contact_groups":16},"final_pose_error":0.01329,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.46718,0.06843,0.02602],"final_tcp_position":[0.57989,0.22759,0.3674],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273017.69272,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4809,0.04846,0.15976],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47826,0.04828,0.06492],"tcp_start":[0.4809,0.04846,0.15976],"tcp_to_object_dist_end":0.03915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04789,0.02567],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29076,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14942,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7694.0,"raw_peak_contact_force":0.20235,"tcp_end":[0.47067,0.04752,0.0568],"tcp_start":[0.47826,0.04828,0.06492],"tcp_to_object_dist_end":0.03336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1902.0,"n_steps_budget":1000.0,"object_pos_end":[0.46718,0.06843,0.02602],"object_pos_start":[0.48265,0.04789,0.02567],"object_to_goal_dist_end":0.28407,"object_to_goal_dist_start":0.29076,"object_z_max":0.04238,"peak_contact_force":273004.7381,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17983.0,"raw_peak_contact_force":0.50062,"subtask_id":"lift_object","tcp_end":[0.46494,0.04697,0.33771],"tcp_start":[0.467,0.04717,0.16251],"tcp_to_object_dist_end":0.31244,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46718,0.06843,0.02602],"object_pos_start":[0.46718,0.06843,0.02602],"object_to_goal_dist_end":0.28407,"object_to_goal_dist_start":0.28407,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8253.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.55241,0.18574,0.30437],"tcp_start":[0.46494,0.04697,0.33771],"tcp_to_object_dist_end":0.31386,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.46718,0.06843,0.02602],"object_pos_start":[0.46718,0.06843,0.02602],"object_to_goal_dist_end":0.28407,"object_to_goal_dist_start":0.28407,"object_z_max":0.02602,"peak_contact_force":273017.69272,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2769.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57516,0.22191,0.23288],"tcp_start":[0.55241,0.18574,0.30437],"tcp_to_object_dist_end":0.2793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46718,0.06843,0.02602],"object_pos_start":[0.46718,0.06843,0.02602],"object_to_goal_dist_end":0.28407,"object_to_goal_dist_start":0.28407,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57086,0.21997,0.25435],"tcp_start":[0.57516,0.22191,0.23288],"tcp_to_object_dist_end":0.293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":900.0,"n_steps_budget":990.0,"object_pos_end":[0.46718,0.06843,0.02602],"object_pos_start":[0.46718,0.06843,0.02602],"object_to_goal_dist_end":0.28407,"object_to_goal_dist_start":0.28407,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3600.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57989,0.22759,0.3674],"tcp_start":[0.57086,0.21997,0.25435],"tcp_to_object_dist_end":0.39317,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```