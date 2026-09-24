## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1410 | 0.18 | ❌ rejected |
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
- Frozen object start: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5038164351471943, -0.015672913018666156, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5038164351471943, -0.015672913018666156, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | approach/contact targets near object start |
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

## Current Skill (Q=0.141) — your mutation base

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

- **Composite score**: 0.141
- **task_score** (E): 0.184
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1181 |
| descend_grasp | 1.00 | 1.00 | 0.1521 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 0.00 | 1.00 | 0.1623 |
| transport_to_goal | 0.00 | 1.00 | 0.0963 |
| descend_place | 1.00 | 1.00 | 0.1201 |
| release_1 | 1.00 | 1.00 | 0.0212 |
| retract_1 | 1.00 | 1.00 | 0.0713 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.188) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 10.961 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.496, 0.022, 0.188)→(0.495, 0.024, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.036)→(0.487, 0.023, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.148 | 0.220 |
| lift_1 | lift | 0.00 / step_budget | (0.487, 0.023, 0.027)→(0.489, 0.023, 0.190) | (0.500, 0.023, 0.026)→(0.501, 0.023, 0.168) | 0.272→0.209 | 1.00 / 16.000 | 0.513 | 0.657 |
| transport_to_goal | approach | 0.00 / step_budget | (0.489, 0.023, 0.190)→(0.533, 0.095, 0.232) | (0.501, 0.023, 0.168)→(0.495, 0.058, 0.016) | 0.209→0.262 | 1.00 / 8.000 | 6499.316 | 1.730 |
| descend_place | descend | 1.00 / step_budget | (0.533, 0.095, 0.232)→(0.592, 0.190, 0.203) | (0.495, 0.058, 0.016)→(0.495, 0.058, 0.016) | 0.262→0.262 | 1.00 / 8.333 | 91002.257 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.592, 0.190, 0.203)→(0.587, 0.188, 0.223) | (0.495, 0.058, 0.016)→(0.495, 0.058, 0.016) | 0.262→0.262 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.587, 0.188, 0.223)→(0.596, 0.195, 0.293) | (0.495, 0.058, 0.016)→(0.495, 0.058, 0.016) | 0.262→0.262 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.268
- phase_score: 0.677
- phase_breakdown.lift_clearance_score: 0.760
- phase_breakdown.reach_object_score: 0.822
- phase_breakdown.transport_accuracy_score: 0.110
- phase_breakdown.grasp_success_score: 0.867
- phase_breakdown.place_accuracy_score: 0.829
- grasp_place_fitness: 0.613

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.613
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.268
- **Median Q (composite search score)**: 0.129
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.189


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
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89349,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.05002,"descend_grasp.grasp_z_offset":0.00534,"descend_place.place_z_offset":0.00905,"lift_1.lift_height":0.17052,"transport_to_goal.transport_speed":0.09728},"optimized_scores":{"best_composite_score":0.11111,"best_fitness_score":0.54111,"best_task_score":0.12656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3488.0,"contact_point_centroid":[0.50526,-0.00123,-0.00229],"force_p95":0.12436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78943,"mean_force":0.13573,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51416,0.03589,0.2261]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.50127,-0.0153,-0.0011],"force_p95":0.4222,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58192,"mean_force":0.0714,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48949,-0.01533,0.03297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13271.0,"contact_point_centroid":[0.49311,0.00352,0.1003],"force_p95":0.12339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32425,"mean_force":0.0751,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48977,-0.01525,0.09907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14023.0,"contact_point_centroid":[0.49296,-0.03398,0.09886],"force_p95":0.12058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29416,"mean_force":0.07183,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48973,-0.01525,0.0978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":246.0,"contact_point_centroid":[0.49998,0.00539,0.18848],"force_p95":0.21389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22355,"mean_force":0.14785,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4943,-0.01262,0.19351]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":379.0,"contact_point_centroid":[0.49937,-0.02905,0.18865],"force_p95":0.14633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21289,"mean_force":0.09968,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49442,-0.01174,0.19375]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01553,-0.00203],"force_p95":0.13287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1597,"mean_force":0.12554,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49203,-0.01536,0.03248]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49913,-0.00661,0.24489]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4982,-0.01456,0.11365]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50523,-0.00122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55658,0.12985,0.24784]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50523,-0.00122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57723,0.17787,0.25011]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.50523,-0.00122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57926,0.18144,0.30008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49132,0.00386,0.03402],"force_p95":0.07619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11868,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49086,-0.01535,0.03126]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.49139,-0.03442,0.0331],"force_p95":0.06848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08944,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49086,-0.01535,0.03126]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3493.0,"contact_point_centroid":[0.51557,0.03816,0.23011],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01046,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51521,0.03816,0.22781]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4267.0,"contact_point_centroid":[0.55711,0.13,0.25009],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55666,0.12999,0.24785]}],"total_contact_groups":17},"final_pose_error":0.01392,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50523,-0.00122,0.01602],"final_tcp_position":[0.58436,0.18599,0.33451],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273006.52714,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":32.63675,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5,-0.01374,0.18883],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.49898,-0.01544,0.03993],"tcp_start":[0.5,-0.01374,0.18883],"tcp_to_object_dist_end":0.01473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01522,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1306,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.1597,"tcp_end":[0.49083,-0.01534,0.03122],"tcp_start":[0.49898,-0.01544,0.03993],"tcp_to_object_dist_end":0.01393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50391,-0.01524,0.17047],"object_pos_start":[0.50369,-0.01522,0.02587],"object_to_goal_dist_end":0.23238,"object_to_goal_dist_start":0.31208,"object_z_max":0.17029,"peak_contact_force":0.13737,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27426.0,"raw_peak_contact_force":0.58192,"subtask_id":"lift_clearance","tcp_end":[0.49398,-0.01521,0.1927],"tcp_start":[0.49083,-0.01534,0.03122],"tcp_to_object_dist_end":0.02435,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50523,-0.00122,0.01602],"object_pos_start":[0.50391,-0.01524,0.17047],"object_to_goal_dist_end":0.31006,"object_to_goal_dist_start":0.23238,"object_z_max":0.17075,"peak_contact_force":9749.02263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7606.0,"raw_peak_contact_force":1.78943,"subtask_id":"transport_accuracy","tcp_end":[0.53014,0.07001,0.25197],"tcp_start":[0.49398,-0.01521,0.1927],"tcp_to_object_dist_end":0.24773,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50523,-0.00122,0.01602],"object_pos_start":[0.50523,-0.00122,0.01602],"object_to_goal_dist_end":0.31006,"object_to_goal_dist_start":0.31006,"object_z_max":0.01602,"peak_contact_force":273006.52714,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8267.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.58027,0.17886,0.24889],"tcp_start":[0.53014,0.07001,0.25197],"tcp_to_object_dist_end":0.30379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50523,-0.00122,0.01602],"object_pos_start":[0.50523,-0.00122,0.01602],"object_to_goal_dist_end":0.31006,"object_to_goal_dist_start":0.31006,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57614,0.17742,0.2699],"tcp_start":[0.58027,0.17886,0.24889],"tcp_to_object_dist_end":0.31843,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50523,-0.00122,0.01602],"object_pos_start":[0.50523,-0.00122,0.01602],"object_to_goal_dist_end":0.31006,"object_to_goal_dist_start":0.31006,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58436,0.18599,0.33451],"tcp_start":[0.57614,0.17742,0.2699],"tcp_to_object_dist_end":0.37782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71006,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.07307,"descend_grasp.grasp_z_offset":0.00043,"descend_place.place_z_offset":0.00095,"lift_1.lift_height":0.19767,"transport_to_goal.transport_speed":0.05979},"optimized_scores":{"best_composite_score":0.18277,"best_fitness_score":0.61277,"best_task_score":0.26761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3552.0,"contact_point_centroid":[0.50558,0.08529,-0.00227],"force_p95":0.12954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7345,"mean_force":0.13846,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53306,0.07464,0.19783]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.50969,0.03712,-0.0012],"force_p95":0.49121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6808,"mean_force":0.08677,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49778,0.03813,0.02791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13337.0,"contact_point_centroid":[0.50103,0.01922,0.09622],"force_p95":0.13278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31981,"mean_force":0.07546,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49794,0.03793,0.09537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14049.0,"contact_point_centroid":[0.50097,0.05667,0.09501],"force_p95":0.13233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31879,"mean_force":0.07323,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49793,0.03793,0.0944]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":234.0,"contact_point_centroid":[0.50646,0.05501,0.18275],"force_p95":0.24005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28046,"mean_force":0.13759,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50275,0.03919,0.1884]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03938,-0.00213],"force_p95":0.16139,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24546,"mean_force":0.13308,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50044,0.03837,0.02732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.50848,0.02051,0.18242],"force_p95":0.19129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19957,"mean_force":0.13958,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50214,0.03813,0.1887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4054.0,"contact_point_centroid":[0.49987,0.01907,0.02885],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14616,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03827,0.02605]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50283,0.01705,0.24363]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50628,0.03697,0.11039]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.5056,0.08545,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59202,0.13882,0.16544]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5056,0.08545,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6169,0.16818,0.13887]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.5056,0.08545,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61782,0.16894,0.19178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5004.0,"contact_point_centroid":[0.49983,0.05744,0.02786],"force_p95":0.07344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08676,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03827,0.02605]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3598.0,"contact_point_centroid":[0.53456,0.07586,0.20054],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53418,0.07584,0.19829]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3514.0,"contact_point_centroid":[0.59257,0.13895,0.16758],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59212,0.13893,0.16534]}],"total_contact_groups":17},"final_pose_error":0.01561,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.5056,0.08545,0.01602],"final_tcp_position":[0.6236,0.17116,0.22999],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.80348,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50768,0.03519,0.18723],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.50752,0.03895,0.03504],"tcp_start":[0.50768,0.03519,0.18723],"tcp_to_object_dist_end":0.01034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03825,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21346,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15271,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10858.0,"raw_peak_contact_force":0.24546,"tcp_end":[0.49922,0.03827,0.02601],"tcp_start":[0.50752,0.03895,0.03504],"tcp_to_object_dist_end":0.01318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51319,0.03805,0.16574],"object_pos_start":[0.51239,0.03825,0.02556],"object_to_goal_dist_end":0.17775,"object_to_goal_dist_start":0.21346,"object_z_max":0.16571,"peak_contact_force":1.23495,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27527.0,"raw_peak_contact_force":0.6808,"subtask_id":"lift_clearance","tcp_end":[0.50189,0.03796,0.18855],"tcp_start":[0.49922,0.03827,0.02601],"tcp_to_object_dist_end":0.02546,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5056,0.08545,0.01602],"object_pos_start":[0.51319,0.03805,0.16574],"object_to_goal_dist_end":0.19774,"object_to_goal_dist_start":0.17775,"object_z_max":0.16574,"peak_contact_force":9748.80348,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7435.0,"raw_peak_contact_force":1.7345,"subtask_id":"transport_accuracy","tcp_end":[0.55514,0.09805,0.20713],"tcp_start":[0.50189,0.03796,0.18855],"tcp_to_object_dist_end":0.19783,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.5056,0.08545,0.01602],"object_pos_start":[0.5056,0.08545,0.01602],"object_to_goal_dist_end":0.19774,"object_to_goal_dist_start":0.19774,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6826.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.6215,0.16953,0.13856],"tcp_start":[0.55514,0.09805,0.20713],"tcp_to_object_dist_end":0.18846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5056,0.08545,0.01602],"object_pos_start":[0.5056,0.08545,0.01602],"object_to_goal_dist_end":0.19774,"object_to_goal_dist_start":0.19774,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6151,0.1676,0.15825],"tcp_start":[0.6215,0.16953,0.13856],"tcp_to_object_dist_end":0.1974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5056,0.08545,0.01602],"object_pos_start":[0.5056,0.08545,0.01602],"object_to_goal_dist_end":0.19774,"object_to_goal_dist_start":0.19774,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6236,0.17116,0.22999],"tcp_start":[0.6151,0.1676,0.15825],"tcp_to_object_dist_end":0.25895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8011,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.05084,"descend_grasp.grasp_z_offset":-0.00182,"descend_place.place_z_offset":-0.00299,"lift_1.lift_height":0.21612,"transport_to_goal.transport_speed":0.06354},"optimized_scores":{"best_composite_score":0.12918,"best_fitness_score":0.55918,"best_task_score":0.15773},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3549.0,"contact_point_centroid":[0.47325,0.09126,-0.00226],"force_p95":0.12769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66624,"mean_force":0.13633,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4949,0.08923,0.21593]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.47994,0.04569,-0.00121],"force_p95":0.54255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70803,"mean_force":0.08629,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46894,0.04688,0.02695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14408.0,"contact_point_centroid":[0.47164,0.0655,0.09424],"force_p95":0.13111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31218,"mean_force":0.07174,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46884,0.04668,0.09343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.47611,0.02999,0.18291],"force_p95":0.21955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29491,"mean_force":0.13123,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47259,0.04785,0.18826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14010.0,"contact_point_centroid":[0.47171,0.02794,0.09584],"force_p95":0.12669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28869,"mean_force":0.07237,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46888,0.04668,0.09488]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.0484,-0.00216],"force_p95":0.16717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25567,"mean_force":0.13484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47145,0.04715,0.02614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":339.0,"contact_point_centroid":[0.47638,0.06586,0.18293],"force_p95":0.21348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2555,"mean_force":0.11133,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4728,0.04881,0.18845]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4995.0,"contact_point_centroid":[0.47013,0.0278,0.02795],"force_p95":0.07036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1485,"mean_force":0.04307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47032,0.04704,0.025]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49005,0.02082,0.24413]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47846,0.04535,0.10973]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47316,0.09126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54601,0.17532,0.22588]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47316,0.09126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57123,0.21958,0.22117]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.47316,0.09126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5735,0.22269,0.27637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5531.0,"contact_point_centroid":[0.46994,0.06639,0.02729],"force_p95":0.07032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08416,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47033,0.04704,0.02501]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3545.0,"contact_point_centroid":[0.49658,0.09132,0.21974],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49616,0.09131,0.21751]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4305.0,"contact_point_centroid":[0.54665,0.17556,0.22813],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01036,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54614,0.17554,0.22585]}],"total_contact_groups":17},"final_pose_error":0.01491,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47316,0.09126,0.01602],"final_tcp_position":[0.57913,0.22719,0.31592],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.66624,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48128,0.04311,0.18793],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.47821,0.04782,0.03301],"tcp_start":[0.48128,0.04311,0.18793],"tcp_to_object_dist_end":0.00836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04715,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29138,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15942,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12326.0,"raw_peak_contact_force":0.25567,"tcp_end":[0.4703,0.04704,0.02497],"tcp_start":[0.47821,0.04782,0.03301],"tcp_to_object_dist_end":0.0123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48481,0.04673,0.16645],"object_pos_start":[0.48259,0.04715,0.02547],"object_to_goal_dist_end":0.21608,"object_to_goal_dist_start":0.29138,"object_z_max":0.16629,"peak_contact_force":0.16647,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28554.0,"raw_peak_contact_force":0.70803,"subtask_id":"lift_clearance","tcp_end":[0.4723,0.04674,0.18786],"tcp_start":[0.4703,0.04704,0.02497],"tcp_to_object_dist_end":0.02479,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47316,0.09126,0.01602],"object_pos_start":[0.48481,0.04673,0.16645],"object_to_goal_dist_end":0.27703,"object_to_goal_dist_start":0.21608,"object_z_max":0.16652,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7605.0,"raw_peak_contact_force":1.66624,"subtask_id":"transport_accuracy","tcp_end":[0.51271,0.11836,0.23835],"tcp_start":[0.4723,0.04674,0.18786],"tcp_to_object_dist_end":0.22744,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47316,0.09126,0.01602],"object_pos_start":[0.47316,0.09126,0.01602],"object_to_goal_dist_end":0.27703,"object_to_goal_dist_start":0.27703,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8305.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.57452,0.22093,0.22008],"tcp_start":[0.51271,0.11836,0.23835],"tcp_to_object_dist_end":0.26216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47316,0.09126,0.01602],"object_pos_start":[0.47316,0.09126,0.01602],"object_to_goal_dist_end":0.27703,"object_to_goal_dist_start":0.27703,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57,0.21898,0.2409],"tcp_start":[0.57452,0.22093,0.22008],"tcp_to_object_dist_end":0.27616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.47316,0.09126,0.01602],"object_pos_start":[0.47316,0.09126,0.01602],"object_to_goal_dist_end":0.27703,"object_to_goal_dist_start":0.27703,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57913,0.22719,0.31592],"tcp_start":[0.57,0.21898,0.2409],"tcp_to_object_dist_end":0.3459,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```