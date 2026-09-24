## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.4376 | 0.18 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.438) — your mutation base

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

- **Composite score**: -0.438
- **task_score** (E): 0.182
- **fitness_score**: 0.292  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0965 |
| descend_to_grasp | 1.00 | 1.00 | 0.1469 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift_off | 0.00 | 1.00 | 0.0001 |
| transport_to_goal | 0.00 | 1.00 | 0.1066 |
| descend_to_place | 0.33 | 1.00 | 0.0873 |
| release_object | 1.00 | 1.00 | 0.0235 |
| retract | 0.33 | 1.00 | 0.1431 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.020, 0.211) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.497, 0.020, 0.211)→(0.495, 0.024, 0.065) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 29.000 | 0.146 | 0.186 |
| grasp | grasp | 1.00 / step_budget | (0.495, 0.024, 0.065)→(0.487, 0.023, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 29.000 | 0.236 | 0.247 |
| lift_off | lift | 0.00 / guard_failure | (0.487, 0.023, 0.055)→(0.486, 0.023, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.272→0.272 | 1.00 / 8.333 | 6499.269 | 0.758 |
| transport_to_goal | approach | 0.00 / step_budget | (0.486, 0.023, 0.055)→(0.510, 0.063, 0.151) | (0.500, 0.024, 0.026)→(0.491, 0.060, 0.016) | 0.272→0.261 | 1.00 / 8.667 | 182002.248 | 0.123 |
| descend_to_place | descend | 0.33 / step_budget | (0.510, 0.063, 0.151)→(0.555, 0.132, 0.170) | (0.491, 0.060, 0.016)→(0.491, 0.060, 0.016) | 0.261→0.261 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.555, 0.132, 0.170)→(0.549, 0.130, 0.193) | (0.491, 0.060, 0.016)→(0.491, 0.060, 0.016) | 0.261→0.261 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 0.33 / step_budget | (0.549, 0.130, 0.193)→(0.582, 0.174, 0.324) | (0.491, 0.060, 0.016)→(0.491, 0.060, 0.016) | 0.261→0.261 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.258
- phase_score: 0.192
- phase_breakdown.grasp_lift_score: 0.080
- phase_breakdown.transport_approach_score: 0.018
- phase_breakdown.pre_grasp_approach_score: 0.268
- phase_breakdown.final_place_score: 0.369
- grasp_place_fitness: 0.330

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.330
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.258
- **Median Q (composite search score)**: -0.453
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51282,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_z":0.14638,"approach_object.speed":0.13136,"descend_to_grasp.descent_speed":0.06589,"descend_to_place.descend_place_speed":0.05574,"lift_off.lift_height":0.19567,"lift_off.lift_speed":0.0424,"release_object.release_duration":0.45597,"retract.retract_height":0.1639,"retract.retract_speed":0.09653,"transport_to_goal.arc_height":0.02055,"transport_to_goal.transport_speed":0.10885},"optimized_scores":{"best_composite_score":-0.46015,"best_fitness_score":0.26985,"best_task_score":0.13647},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1577.0,"contact_point_centroid":[0.49921,0.01658,-0.0022],"force_p95":0.26161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99739,"mean_force":0.14199,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49999,0.01289,0.12]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7042.0,"contact_point_centroid":[0.49165,-0.02229,0.07709],"force_p95":0.12574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29447,"mean_force":0.08439,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49177,-0.00368,0.08086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6830.0,"contact_point_centroid":[0.49149,0.01472,0.07661],"force_p95":0.12392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24968,"mean_force":0.08503,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49174,-0.00379,0.08059]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50385,-0.01567,-0.00208],"force_p95":0.23013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23314,"mean_force":0.20168,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49048,-0.01537,0.05527]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01567,-0.00203],"force_p95":0.13182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15482,"mean_force":0.12503,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49172,-0.01538,0.05664]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49905,-0.00666,0.24309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":39.0,"contact_point_centroid":[0.49036,0.00334,0.05206],"force_p95":0.12326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12863,"mean_force":0.08325,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49048,-0.01537,0.05527]},{"body_a":"world","body_b":"grasp_target","contact_count":1576.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49795,-0.01461,0.12437]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5002,0.02052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51922,0.05911,0.16096]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5002,0.02052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53033,0.08847,0.18252]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5002,0.02052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54623,0.12178,0.26863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":39.0,"contact_point_centroid":[0.48979,-0.03411,0.05228],"force_p95":0.11525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12083,"mean_force":0.08275,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49048,-0.01537,0.05527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3157.0,"contact_point_centroid":[0.49042,0.00345,0.05212],"force_p95":0.09153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10289,"mean_force":0.06585,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49053,-0.01537,0.05534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3176.0,"contact_point_centroid":[0.48983,-0.03422,0.05234],"force_p95":0.09036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0906,"mean_force":0.06552,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49054,-0.01537,0.05534]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1153.0,"contact_point_centroid":[0.50277,0.0181,0.13429],"force_p95":0.01217,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01543,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50224,0.0181,0.13201]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4309.0,"contact_point_centroid":[0.51964,0.05905,0.16326],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51919,0.05905,0.16092]}],"total_contact_groups":17},"final_pose_error":0.08383,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5002,0.02052,0.01602],"final_tcp_position":[0.56623,0.15494,0.33757],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.14191,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1576.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp_approach","tcp_end":[0.49986,-0.01383,0.18509],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13138,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8133.0,"raw_peak_contact_force":0.15482,"subtask_id":"pre_grasp_approach","tcp_end":[0.49875,-0.01543,0.06452],"tcp_start":[0.49986,-0.01383,0.18509],"tcp_to_object_dist_end":0.03883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01554,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31226,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.22267,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":90.0,"raw_peak_contact_force":0.23314,"tcp_end":[0.49051,-0.01537,0.0553],"tcp_start":[0.49875,-0.01543,0.06452],"tcp_to_object_dist_end":0.03227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,-0.01554,0.02585],"object_pos_start":[0.50375,-0.01554,0.02588],"object_to_goal_dist_end":0.31229,"object_to_goal_dist_start":0.31226,"object_z_max":0.02588,"peak_contact_force":9748.92172,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16602.0,"raw_peak_contact_force":0.99739,"subtask_id":"grasp_lift","tcp_end":[0.49041,-0.01537,0.05517],"tcp_start":[0.49045,-0.01537,0.05523],"tcp_to_object_dist_end":0.03221,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5002,0.02052,0.01602],"object_pos_start":[0.5037,-0.01554,0.02575],"object_to_goal_dist_end":0.29875,"object_to_goal_dist_start":0.31237,"object_z_max":0.06845,"peak_contact_force":273005.14191,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8309.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_approach","tcp_end":[0.50496,0.02354,0.14381],"tcp_start":[0.49041,-0.01537,0.05517],"tcp_to_object_dist_end":0.12791,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5002,0.02052,0.01602],"object_pos_start":[0.5002,0.02052,0.01602],"object_to_goal_dist_end":0.29875,"object_to_goal_dist_start":0.29875,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_place","tcp_end":[0.53423,0.08905,0.17949],"tcp_start":[0.50496,0.02354,0.14381],"tcp_to_object_dist_end":0.18049,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5002,0.02052,0.01602],"object_pos_start":[0.5002,0.02052,0.01602],"object_to_goal_dist_end":0.29875,"object_to_goal_dist_start":0.29875,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52882,0.08819,0.20313],"tcp_start":[0.53423,0.08905,0.17949],"tcp_to_object_dist_end":0.20102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5002,0.02052,0.01602],"object_pos_start":[0.5002,0.02052,0.01602],"object_to_goal_dist_end":0.29875,"object_to_goal_dist_start":0.29875,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56623,0.15494,0.33757],"tcp_start":[0.52882,0.08819,0.20313],"tcp_to_object_dist_end":0.35471,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47742,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_z":0.18252,"approach_object.speed":0.17119,"descend_to_grasp.descent_speed":0.05885,"descend_to_place.descend_place_speed":0.07371,"lift_off.lift_height":0.19769,"lift_off.lift_speed":0.02312,"release_object.release_duration":0.11084,"retract.retract_height":0.14352,"retract.retract_speed":0.1035,"transport_to_goal.arc_height":0.02018,"transport_to_goal.transport_speed":0.12869},"optimized_scores":{"best_composite_score":-0.39952,"best_fitness_score":0.33048,"best_task_score":0.25751},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2668.0,"contact_point_centroid":[0.50447,0.07065,-0.00208],"force_p95":0.19592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65136,"mean_force":0.13009,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51733,0.06114,0.11354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4179.0,"contact_point_centroid":[0.50185,0.0259,0.0655],"force_p95":0.1232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27207,"mean_force":0.07892,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50095,0.04403,0.06926]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3644.0,"contact_point_centroid":[0.49958,0.06229,0.06492],"force_p95":0.14963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26557,"mean_force":0.09274,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50068,0.04369,0.06833]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.51269,0.0397,-0.0022],"force_p95":0.25017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25394,"mean_force":0.21012,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.4991,0.0382,0.05484]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03971,-0.0021],"force_p95":0.15318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19957,"mean_force":0.13037,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50034,0.0383,0.05626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3134.0,"contact_point_centroid":[0.4996,0.0195,0.05149],"force_p95":0.10026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17228,"mean_force":0.06605,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49915,0.0382,0.05491]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5028,0.01641,0.25937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":39.0,"contact_point_centroid":[0.49951,0.01962,0.05145],"force_p95":0.12779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13415,"mean_force":0.08238,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.4991,0.0382,0.05484]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50617,0.03635,0.14087]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50398,0.07507,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5638,0.11158,0.13923]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50398,0.07507,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58668,0.13823,0.13946]},{"body_a":"world","body_b":"grasp_target","contact_count":3132.0,"contact_point_centroid":[0.50398,0.07507,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60255,0.15383,0.21466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.4983,0.05696,0.05231],"force_p95":0.11783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1205,"mean_force":0.09008,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.4991,0.0382,0.05484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2997.0,"contact_point_centroid":[0.49829,0.05712,0.05239],"force_p95":0.10003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10057,"mean_force":0.06964,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49916,0.0382,0.05492]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2246.0,"contact_point_centroid":[0.52112,0.06478,0.12508],"force_p95":0.01118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01596,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5207,0.0648,0.1228]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.58975,0.13884,0.13752],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01035,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58967,0.13897,0.13519]}],"total_contact_groups":17},"final_pose_error":0.0155,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50398,0.07507,0.01602],"final_tcp_position":[0.6229,0.17009,0.27397],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.76291,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp_approach","tcp_end":[0.50759,0.03405,0.21882],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15048,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7931.0,"raw_peak_contact_force":0.19957,"subtask_id":"pre_grasp_approach","tcp_end":[0.5074,0.03886,0.06437],"tcp_start":[0.50759,0.03405,0.21882],"tcp_to_object_dist_end":0.0387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51254,0.03904,0.02564],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21284,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.24399,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":87.0,"raw_peak_contact_force":0.25394,"tcp_end":[0.49912,0.0382,0.05488],"tcp_start":[0.5074,0.03886,0.06437],"tcp_to_object_dist_end":0.03218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51254,0.03904,0.02561],"object_pos_start":[0.51254,0.03904,0.02564],"object_to_goal_dist_end":0.21286,"object_to_goal_dist_start":0.21284,"object_z_max":0.02564,"peak_contact_force":9748.76291,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12737.0,"raw_peak_contact_force":0.65136,"subtask_id":"grasp_lift","tcp_end":[0.49902,0.03819,0.05474],"tcp_start":[0.49907,0.0382,0.0548],"tcp_to_object_dist_end":0.03213,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50398,0.07507,0.01602],"object_pos_start":[0.5125,0.03904,0.0255],"object_to_goal_dist_end":0.2035,"object_to_goal_dist_start":0.21295,"object_z_max":0.04764,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8305.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_approach","tcp_end":[0.53111,0.07543,0.14646],"tcp_start":[0.49902,0.03819,0.05474],"tcp_to_object_dist_end":0.13323,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50398,0.07507,0.01602],"object_pos_start":[0.50398,0.07507,0.01602],"object_to_goal_dist_end":0.2035,"object_to_goal_dist_start":0.2035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_place","tcp_end":[0.59117,0.13926,0.13783],"tcp_start":[0.53111,0.07543,0.14646],"tcp_to_object_dist_end":0.16297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50398,0.07507,0.01602],"object_pos_start":[0.50398,0.07507,0.01602],"object_to_goal_dist_end":0.2035,"object_to_goal_dist_start":0.2035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3132.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58491,0.13779,0.15945],"tcp_start":[0.59117,0.13926,0.13783],"tcp_to_object_dist_end":0.17622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50398,0.07507,0.01602],"object_pos_start":[0.50398,0.07507,0.01602],"object_to_goal_dist_end":0.2035,"object_to_goal_dist_start":0.2035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.6229,0.17009,0.27397],"tcp_start":[0.58491,0.13779,0.15945],"tcp_to_object_dist_end":0.29951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89542,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_z":0.19373,"approach_object.speed":0.10188,"descend_to_grasp.descent_speed":0.08154,"descend_to_place.descend_place_speed":0.0733,"lift_off.lift_height":0.19639,"lift_off.lift_speed":0.08041,"release_object.release_duration":0.27579,"retract.retract_height":0.28623,"retract.retract_speed":0.09305,"transport_to_goal.arc_height":0.02174,"transport_to_goal.transport_speed":0.14173},"optimized_scores":{"best_composite_score":-0.45313,"best_fitness_score":0.27687,"best_task_score":0.15238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2907.0,"contact_point_centroid":[0.47076,0.07974,-0.00208],"force_p95":0.18986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62588,"mean_force":0.13034,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48246,0.07307,0.12278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3131.0,"contact_point_centroid":[0.4708,0.03457,0.06593],"force_p95":0.13314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31144,"mean_force":0.08405,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47005,0.05275,0.0704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2968.0,"contact_point_centroid":[0.46824,0.07092,0.0654],"force_p95":0.14154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2947,"mean_force":0.09051,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46984,0.05233,0.06924]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.48291,0.04864,-0.00222],"force_p95":0.2503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25479,"mean_force":0.20715,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.47005,0.04691,0.05595]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04869,-0.00212],"force_p95":0.15789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20474,"mean_force":0.13148,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47125,0.04703,0.05723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2891.0,"contact_point_centroid":[0.47051,0.02822,0.05186],"force_p95":0.10853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17489,"mean_force":0.07112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4701,0.04692,0.05601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.47045,0.02835,0.05183],"force_p95":0.13455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13917,"mean_force":0.08753,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.47005,0.04691,0.05595]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.4827,0.04873,-0.00187],"force_p95":0.13652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49063,0.01962,0.2651]},{"body_a":"world","body_b":"grasp_target","contact_count":2104.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47896,0.04426,0.14677]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47009,0.08342,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51665,0.13151,0.17758]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47009,0.08342,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53532,0.1653,0.19639]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47009,0.08342,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5439,0.18051,0.28726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.46853,0.06558,0.05261],"force_p95":0.11323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11705,"mean_force":0.08918,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.47005,0.04691,0.05595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2998.0,"contact_point_centroid":[0.46849,0.06577,0.0527],"force_p95":0.1021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10265,"mean_force":0.06963,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4701,0.04692,0.05602]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2497.0,"contact_point_centroid":[0.48517,0.0767,0.13407],"force_p95":0.01122,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01072,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48459,0.07669,0.13193]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4294.0,"contact_point_centroid":[0.5169,0.13135,0.17994],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51657,0.13139,0.17753]}],"total_contact_groups":17},"final_pose_error":0.16069,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47009,0.08342,0.01602],"final_tcp_position":[0.55649,0.19658,0.36136],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273001.48018,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp_approach","tcp_end":[0.48223,0.04108,0.23],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15479,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7689.0,"raw_peak_contact_force":0.20474,"subtask_id":"pre_grasp_approach","tcp_end":[0.47811,0.04769,0.06461],"tcp_start":[0.48223,0.04108,0.23],"tcp_to_object_dist_end":0.03887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48278,0.04784,0.02558],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29081,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.24272,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":84.0,"raw_peak_contact_force":0.25479,"tcp_end":[0.47007,0.04691,0.05598],"tcp_start":[0.47811,0.04769,0.06461],"tcp_to_object_dist_end":0.03296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48278,0.04784,0.02555],"object_pos_start":[0.48278,0.04784,0.02558],"object_to_goal_dist_end":0.29083,"object_to_goal_dist_start":0.29081,"object_z_max":0.02558,"peak_contact_force":0.12263,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11503.0,"raw_peak_contact_force":0.62588,"subtask_id":"grasp_lift","tcp_end":[0.46997,0.04691,0.05586],"tcp_start":[0.47002,0.04691,0.05591],"tcp_to_object_dist_end":0.03291,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47009,0.08342,0.01602],"object_pos_start":[0.48273,0.04784,0.02545],"object_to_goal_dist_end":0.28221,"object_to_goal_dist_start":0.29092,"object_z_max":0.04702,"peak_contact_force":273001.48018,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8294.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_approach","tcp_end":[0.49329,0.09035,0.16305],"tcp_start":[0.46997,0.04691,0.05586],"tcp_to_object_dist_end":0.14901,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47009,0.08342,0.01602],"object_pos_start":[0.47009,0.08342,0.01602],"object_to_goal_dist_end":0.28221,"object_to_goal_dist_start":0.28221,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_place","tcp_end":[0.53899,0.16632,0.19377],"tcp_start":[0.49329,0.09035,0.16305],"tcp_to_object_dist_end":0.20788,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47009,0.08342,0.01602],"object_pos_start":[0.47009,0.08342,0.01602],"object_to_goal_dist_end":0.28221,"object_to_goal_dist_start":0.28221,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53392,0.16484,0.2168],"tcp_start":[0.53899,0.16632,0.19377],"tcp_to_object_dist_end":0.22587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47009,0.08342,0.01602],"object_pos_start":[0.47009,0.08342,0.01602],"object_to_goal_dist_end":0.28221,"object_to_goal_dist_start":0.28221,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1040.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.55649,0.19658,0.36136],"tcp_start":[0.53392,0.16484,0.2168],"tcp_to_object_dist_end":0.37354,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```