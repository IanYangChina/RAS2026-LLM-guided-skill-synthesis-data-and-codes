## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0332 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1436 | 0.17 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

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

## Current Skill (Q=0.033) — your mutation base

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

- **Composite score**: 0.033
- **task_score** (E): 0.168
- **fitness_score**: 0.563  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre | 1.00 | 1.00 | 0.1731 |
| descend_grasp | 1.00 | 1.00 | 0.0973 |
| grasp_hold | 1.00 | 1.00 | 0.0115 |
| lift_up | 1.00 | 1.00 | 0.1328 |
| transport_arc | 0.00 | 1.00 | 0.1321 |
| descend_place | 0.00 | 1.00 | 0.0385 |
| release_object | 1.00 | 0.67 | 0.0243 |
| retract_away | 0.00 | 0.67 | 0.0943 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.023, 0.132) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.496, 0.023, 0.132)→(0.495, 0.024, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_hold | grasp | 1.00 / step_budget | (0.495, 0.024, 0.035)→(0.487, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.143 | 0.210 |
| lift_up | lift | 1.00 / step_budget | (0.487, 0.023, 0.026)→(0.495, 0.023, 0.159) | (0.500, 0.024, 0.026)→(0.510, 0.023, 0.143) | 0.272→0.210 | 1.00 / 20.000 | 0.170 | 0.651 |
| transport_arc | approach | 0.00 / step_budget | (0.495, 0.023, 0.159)→(0.478, 0.060, 0.072) | (0.510, 0.023, 0.143)→(0.461, 0.086, -5.356) | 0.210→5.597 | 1.00 / 8.667 | 75.950 | 1428.193 |
| descend_place | descend | 0.00 / step_budget | (0.478, 0.060, 0.072)→(0.497, 0.085, 0.090) | (0.461, 0.086, -5.356)→(0.355, 0.125, -23.721) | 5.597→23.959 | 1.00 / 8.000 | 0.179 | 227.219 |
| release_object | release | 1.00 / step_budget | (0.497, 0.085, 0.090)→(0.492, 0.084, 0.114) | (0.355, 0.125, -23.721)→(0.332, 0.131, -28.962) | 23.959→29.202 | 0.67 / 2.667 | 0.159 | 2.184 |
| retract_away | retract | 0.00 / step_budget | (0.492, 0.084, 0.114)→(0.528, 0.136, 0.179) | (0.332, 0.131, -28.962)→(0.227, 0.164, -63.027) | 29.202→63.266 | 0.67 / 2.667 | 0.082 | 0.222 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.356
- phase_score: 0.402
- phase_breakdown.place_at_goal_score: 0.018
- phase_breakdown.lift_clearance_score: 0.607
- phase_breakdown.reach_pre_contact_score: 0.905
- grasp_place_fitness: 0.657

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.657
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.356
- **Median Q (composite search score)**: 0.023
- **K-run variance**: 0.0053
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.276


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":31.0,"average_failure_rate":0.1694,"average_mean_iterations":37.51366,"average_solve_count":183.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.10931,"descend_grasp.descend_speed":0.06695,"descend_place.descend_place_speed":0.0493,"lift_up.lift_height":0.18891,"retract_away.retract_speed":0.15184,"transport_arc.arc_height":0.03453,"transport_arc.transport_speed":0.10834},"optimized_scores":{"best_composite_score":0.02349,"best_fitness_score":0.55349,"best_task_score":0.14809},"replay_outcomes":[{"contacts":{"omitted_contact_groups":15,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":51.0,"contact_point_centroid":[0.54709,-0.08194,-0.0041],"force_p95":833.42928,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1011.24323,"mean_force":288.6887,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49985,-0.01528,-0.01113]},{"body_a":"world","body_b":"link6","contact_count":543.0,"contact_point_centroid":[0.66366,0.01485,-0.00026],"force_p95":220.31858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.1444,"mean_force":204.48636,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.42848,-0.00627,0.05536]},{"body_a":"world","body_b":"link7","contact_count":352.0,"contact_point_centroid":[0.59926,-0.00809,-0.00015],"force_p95":259.73651,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.63551,"mean_force":187.55651,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47471,-0.01404,0.01376]},{"body_a":"world","body_b":"link6","contact_count":196.0,"contact_point_centroid":[0.6752,0.04125,-5e-05],"force_p95":108.02939,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.99603,"mean_force":50.33082,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.42658,0.0014,0.06724]},{"body_a":"world","body_b":"left_finger","contact_count":1979.0,"contact_point_centroid":[0.49448,-0.02686,-0.00459],"force_p95":8.4401,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.34191,"mean_force":2.57228,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49269,-0.01575,-0.00033]},{"body_a":"world","body_b":"right_finger","contact_count":1888.0,"contact_point_centroid":[0.49366,-0.0043,-0.00468],"force_p95":8.47012,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.17006,"mean_force":2.58807,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49318,-0.01573,-0.00072]},{"body_a":"grasp_target","body_b":"hand","contact_count":930.0,"contact_point_centroid":[0.54502,-0.01323,0.02719],"force_p95":1.55302,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.88677,"mean_force":0.98286,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.44955,-0.00963,0.03716]},{"body_a":"world","body_b":"grasp_target","contact_count":2617.0,"contact_point_centroid":[0.55199,-0.00654,-0.0092],"force_p95":0.86604,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.49864,"mean_force":0.60585,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.45819,-0.01103,0.02957]},{"body_a":"grasp_target","body_b":"link7","contact_count":822.0,"contact_point_centroid":[0.55845,0.0001,0.02166],"force_p95":0.80567,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.53058,"mean_force":0.5872,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.44285,-0.00885,0.04212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":422.0,"contact_point_centroid":[0.53168,-0.03193,0.16624],"force_p95":0.62092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.03068,"mean_force":0.27276,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5317,-0.01645,0.17124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":233.0,"contact_point_centroid":[0.52527,0.00025,0.15971],"force_p95":0.49445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.78574,"mean_force":0.21534,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52308,-0.01629,0.16619]},{"body_a":"world","body_b":"grasp_target","contact_count":3456.0,"contact_point_centroid":[0.53837,0.01208,-0.00522],"force_p95":0.70222,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78443,"mean_force":0.3362,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43535,0.01471,0.07633]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.53977,-0.00159,0.03928],"force_p95":0.69398,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.75105,"mean_force":0.58487,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43424,0.01309,0.07517]},{"body_a":"grasp_target","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.54494,0.00845,0.03488],"force_p95":0.53486,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.70167,"mean_force":0.36833,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43424,0.01309,0.07517]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.50121,-0.01535,-0.00109],"force_p95":0.48625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66282,"mean_force":0.07533,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48953,-0.01546,0.02736]},{"body_a":"grasp_target","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.55334,-0.00161,0.04353],"force_p95":0.42515,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60903,"mean_force":0.31969,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.44133,0.02635,0.09094]}],"total_contact_groups":31},"final_pose_error":0.24733,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53347,0.01455,0.02602],"final_tcp_position":[0.47465,0.06622,0.16407],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1011.24323,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_contact","tcp_end":[0.49956,-0.01489,0.13241],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2676.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49878,-0.01558,0.03402],"tcp_start":[0.49956,-0.01489,0.13241],"tcp_to_object_dist_end":0.00946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01533,0.0259],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31214,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12884,"phase_name":"grasp_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.154,"tcp_end":[0.49081,-0.01548,0.02562],"tcp_start":[0.49878,-0.01558,0.03402],"tcp_to_object_dist_end":0.01287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51102,-0.01521,0.16671],"object_pos_start":[0.50367,-0.01533,0.0259],"object_to_goal_dist_end":0.23121,"object_to_goal_dist_start":0.31214,"object_z_max":0.16655,"peak_contact_force":0.23002,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28381.0,"raw_peak_contact_force":0.66282,"subtask_id":"lift_clearance","tcp_end":[0.49855,-0.01528,0.18847],"tcp_start":[0.49081,-0.01548,0.02562],"tcp_to_object_dist_end":0.02508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53287,0.00108,0.01507],"object_pos_start":[0.51102,-0.01521,0.16671],"object_to_goal_dist_end":0.30325,"object_to_goal_dist_start":0.23121,"object_z_max":0.16696,"peak_contact_force":93.20023,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12340.0,"raw_peak_contact_force":1011.24323,"subtask_id":"place_at_goal","tcp_end":[0.42467,-0.00126,0.06523],"tcp_start":[0.49855,-0.01528,0.18847],"tcp_to_object_dist_end":0.11928,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53578,0.01361,0.02371],"object_pos_start":[0.53287,0.00108,0.01507],"object_to_goal_dist_end":0.28843,"object_to_goal_dist_start":0.30325,"object_z_max":0.02371,"peak_contact_force":0.34554,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9911.0,"raw_peak_contact_force":169.99603,"tcp_end":[0.44537,0.02678,0.08714],"tcp_start":[0.42467,-0.00126,0.06523],"tcp_to_object_dist_end":0.11123,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52965,0.01342,0.02898],"object_pos_start":[0.53578,0.01361,0.02371],"object_to_goal_dist_end":0.28563,"object_to_goal_dist_start":0.28843,"object_z_max":0.02893,"peak_contact_force":0.35214,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1362.0,"raw_peak_contact_force":0.60903,"tcp_end":[0.43968,0.02614,0.11182],"tcp_start":[0.44537,0.02678,0.08714],"tcp_to_object_dist_end":0.12295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.53347,0.01455,0.02602],"object_pos_start":[0.52965,0.01342,0.02898],"object_to_goal_dist_end":0.28649,"object_to_goal_dist_start":0.28563,"object_z_max":0.029,"peak_contact_force":0.12267,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1327.0,"raw_peak_contact_force":0.5417,"tcp_end":[0.47465,0.06622,0.16407],"tcp_start":[0.43968,0.02614,0.11182],"tcp_to_object_dist_end":0.15871,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":10.0,"average_failure_rate":0.05952,"average_mean_iterations":16.3631,"average_solve_count":168.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.14819,"descend_grasp.descend_speed":0.06738,"descend_place.descend_place_speed":0.05191,"lift_up.lift_height":0.14223,"retract_away.retract_speed":0.09659,"transport_arc.arc_height":0.09731,"transport_arc.transport_speed":0.09704},"optimized_scores":{"best_composite_score":0.12693,"best_fitness_score":0.65693,"best_task_score":0.35552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":473.0,"contact_point_centroid":[0.66776,0.04308,-0.00083],"force_p95":257.58297,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1817.22447,"mean_force":258.40377,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57114,0.03428,0.02943]},{"body_a":"world","body_b":"link6","contact_count":383.0,"contact_point_centroid":[0.61785,0.24513,-0.00023],"force_p95":247.61003,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":669.36077,"mean_force":124.70935,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56255,0.00389,0.07245]},{"body_a":"world","body_b":"link7","contact_count":414.0,"contact_point_centroid":[0.65853,0.10472,-0.00024],"force_p95":248.57018,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.74955,"mean_force":149.45274,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56183,0.0033,0.07055]},{"body_a":"world","body_b":"link6","contact_count":343.0,"contact_point_centroid":[0.62596,0.2417,-3e-05],"force_p95":101.56025,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.48808,"mean_force":54.58513,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55832,0.00453,0.07603]},{"body_a":"world","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.65663,0.0973,-4e-05],"force_p95":89.19663,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.00321,"mean_force":35.29943,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55609,-0.00197,0.07525]},{"body_a":"world","body_b":"left_finger","contact_count":633.0,"contact_point_centroid":[0.57804,0.07022,-0.00786],"force_p95":10.60349,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.26418,"mean_force":5.0197,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56712,0.07759,-0.00409]},{"body_a":"world","body_b":"right_finger","contact_count":466.0,"contact_point_centroid":[0.55537,0.09109,-0.00497],"force_p95":8.12632,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.1344,"mean_force":3.44061,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56664,0.07949,-0.00721]},{"body_a":"world","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.63388,0.27266,-3e-05],"force_p95":5.85307,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.9325,"mean_force":4.44661,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56616,0.03645,0.07886]},{"body_a":"world","body_b":"grasp_target","contact_count":3376.0,"contact_point_centroid":[0.57434,0.12398,-0.00416],"force_p95":0.54808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.63935,"mean_force":0.26932,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5668,0.01793,0.05222]},{"body_a":"grasp_target","body_b":"hand","contact_count":571.0,"contact_point_centroid":[0.59099,0.10665,0.03306],"force_p95":0.76759,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.53128,"mean_force":0.26767,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56587,0.02247,0.05245]},{"body_a":"grasp_target","body_b":"link7","contact_count":496.0,"contact_point_centroid":[0.59183,0.13435,0.02168],"force_p95":0.81106,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.69589,"mean_force":0.58999,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56393,0.00497,0.06924]},{"body_a":"grasp_target","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.59245,0.13004,0.02379],"force_p95":0.4721,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.7136,"mean_force":0.34917,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56215,0.01719,0.07835]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.51043,0.03771,-0.00117],"force_p95":0.50795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69057,"mean_force":0.07848,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.49815,0.03846,0.02595]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":445.0,"contact_point_centroid":[0.54533,0.04726,0.139],"force_p95":0.41337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56786,"mean_force":0.23859,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5377,0.06384,0.14353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":365.0,"contact_point_centroid":[0.53556,0.0796,0.14313],"force_p95":0.46587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52903,"mean_force":0.21132,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53501,0.06118,0.14643]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56104,0.11815,-0.00337],"force_p95":0.40618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51387,"mean_force":0.20884,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56215,0.01719,0.07835]}],"total_contact_groups":30},"final_pose_error":0.06423,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55964,0.11954,0.01602],"final_tcp_position":[0.60767,0.14024,0.19318],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1817.22447,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3272.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_contact","tcp_end":[0.50787,0.03798,0.1305],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3220.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50747,0.03927,0.03278],"tcp_start":[0.50787,0.03798,0.1305],"tcp_to_object_dist_end":0.00844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03852,0.02566],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21325,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14589,"phase_name":"grasp_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.23695,"tcp_end":[0.49942,0.03859,0.02409],"tcp_start":[0.50747,0.03927,0.03278],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":814.0,"n_steps_budget":900.0,"object_pos_end":[0.52601,0.03829,0.14254],"object_pos_start":[0.51238,0.03852,0.02566],"object_to_goal_dist_end":0.16834,"object_to_goal_dist_start":0.21325,"object_z_max":0.14246,"peak_contact_force":0.17853,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25045.0,"raw_peak_contact_force":0.69057,"subtask_id":"lift_clearance","tcp_end":[0.50789,0.03821,0.15553],"tcp_start":[0.49942,0.03859,0.02409],"tcp_to_object_dist_end":0.0223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56519,0.11601,0.01206],"object_pos_start":[0.52601,0.03829,0.14254],"object_to_goal_dist_end":0.15737,"object_to_goal_dist_start":0.16834,"object_z_max":0.14256,"peak_contact_force":134.64828,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10932.0,"raw_peak_contact_force":1817.22447,"subtask_id":"place_at_goal","tcp_end":[0.55571,-0.00277,0.0749],"tcp_start":[0.50789,0.03821,0.15553],"tcp_to_object_dist_end":0.13471,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56039,0.12099,0.01535],"object_pos_start":[0.56519,0.11601,0.01206],"object_to_goal_dist_end":0.15487,"object_to_goal_dist_start":0.15737,"object_z_max":0.01534,"peak_contact_force":0.19278,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9694.0,"raw_peak_contact_force":193.48808,"tcp_end":[0.56931,0.03693,0.08417],"tcp_start":[0.55571,-0.00277,0.0749],"tcp_to_object_dist_end":0.10901,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55966,0.11948,0.01601],"object_pos_start":[0.56039,0.12099,0.01535],"object_to_goal_dist_end":0.15514,"object_to_goal_dist_start":0.15487,"object_z_max":0.01675,"peak_contact_force":0.12591,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1276.0,"raw_peak_contact_force":5.9325,"tcp_end":[0.56521,0.036,0.10704],"tcp_start":[0.56931,0.03693,0.08417],"tcp_to_object_dist_end":0.12364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.55964,0.11954,0.01602],"object_pos_start":[0.55966,0.11948,0.01601],"object_to_goal_dist_end":0.15513,"object_to_goal_dist_start":0.15514,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3732.0,"raw_peak_contact_force":0.12578,"tcp_end":[0.60767,0.14024,0.19318],"tcp_start":[0.56521,0.036,0.10704],"tcp_to_object_dist_end":0.18472,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24516,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.15521,"descend_grasp.descend_speed":0.07819,"descend_place.descend_place_speed":0.04242,"lift_up.lift_height":0.11826,"retract_away.retract_speed":0.02678,"transport_arc.arc_height":0.05899,"transport_arc.transport_speed":0.08606},"optimized_scores":{"best_composite_score":-0.05071,"best_fitness_score":0.47929,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":633.0,"contact_point_centroid":[0.57981,0.16524,-0.0006],"force_p95":330.63533,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1456.11262,"mean_force":151.27131,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49206,0.12419,0.03188]},{"body_a":"world","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.58792,0.07297,-0.00044],"force_p95":558.75793,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":623.60961,"mean_force":215.19731,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.45828,0.12145,0.03847]},{"body_a":"world","body_b":"link6","contact_count":556.0,"contact_point_centroid":[0.65603,0.04174,-0.00022],"force_p95":220.27673,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.50071,"mean_force":175.85428,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4492,0.15116,0.05838]},{"body_a":"world","body_b":"link6","contact_count":130.0,"contact_point_centroid":[0.65492,0.02686,-4e-05],"force_p95":55.19427,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.17202,"mean_force":26.40294,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.45628,0.1842,0.07779]},{"body_a":"world","body_b":"hand","contact_count":115.0,"contact_point_centroid":[0.56772,0.17993,-8e-05],"force_p95":34.52831,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.13325,"mean_force":24.97857,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.45591,0.18398,0.07762]},{"body_a":"world","body_b":"left_finger","contact_count":2572.0,"contact_point_centroid":[0.54073,0.05255,-0.00847],"force_p95":8.33337,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.23711,"mean_force":5.3558,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54592,0.07303,-0.00744]},{"body_a":"world","body_b":"right_finger","contact_count":3100.0,"contact_point_centroid":[0.5507,0.09462,-0.00785],"force_p95":8.55509,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.46533,"mean_force":5.07793,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54296,0.07622,-0.00552]},{"body_a":"world","body_b":"grasp_target","contact_count":178.0,"contact_point_centroid":[0.57418,0.05266,-0.03015],"force_p95":3.77134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.18754,"mean_force":0.83188,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56093,0.05602,-0.01765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1046.0,"contact_point_centroid":[0.54529,0.06433,0.0674],"force_p95":0.683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.10485,"mean_force":0.25288,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53725,0.04632,0.06826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1029.0,"contact_point_centroid":[0.54163,0.02725,0.06229],"force_p95":0.62509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88411,"mean_force":0.23434,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53918,0.04668,0.06346]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.48079,0.04657,-0.00119],"force_p95":0.42716,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59992,"mean_force":0.06733,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.469,0.04718,0.03108]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10875.0,"contact_point_centroid":[0.47353,0.06599,0.07549],"force_p95":0.10398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29945,"mean_force":0.06313,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.4715,0.04701,0.07377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10733.0,"contact_point_centroid":[0.47412,0.02816,0.07804],"force_p95":0.09934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27263,"mean_force":0.06309,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.47176,0.04701,0.07631]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.0485,-0.00213],"force_p95":0.15893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24028,"mean_force":0.13247,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.4713,0.04745,0.03031]},{"body_a":"world","body_b":"grasp_target","contact_count":2852.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.48861,0.02306,0.21437]},{"body_a":"world","body_b":"grasp_target","contact_count":2280.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47712,0.04702,0.08177]}],"total_contact_groups":21},"final_pose_error":0.17207,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[-0.41136,0.3582,-189.12403],"final_tcp_position":[0.50276,0.20249,0.17997],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1456.11262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2852.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_contact","tcp_end":[0.47948,0.04614,0.13268],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47785,0.0481,0.03698],"tcp_start":[0.47948,0.04614,0.13268],"tcp_to_object_dist_end":0.012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.0475,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2911,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15294,"phase_name":"grasp_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12321.0,"raw_peak_contact_force":0.24028,"tcp_end":[0.47014,0.04733,0.02914],"tcp_start":[0.47785,0.0481,0.03698],"tcp_to_object_dist_end":0.01297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.49442,0.04735,0.1199],"object_pos_start":[0.4826,0.0475,0.02556],"object_to_goal_dist_end":0.22983,"object_to_goal_dist_start":0.2911,"object_z_max":0.11979,"peak_contact_force":0.10122,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21750.0,"raw_peak_contact_force":0.59992,"subtask_id":"lift_clearance","tcp_end":[0.47796,0.04711,0.13235],"tcp_start":[0.47014,0.04733,0.02914],"tcp_to_object_dist_end":0.02064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.28584,0.14184,-16.09639],"object_pos_start":[0.49442,0.04735,0.1199],"object_to_goal_dist_end":16.32979,"object_to_goal_dist_start":0.22983,"object_z_max":0.11994,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11189.0,"raw_peak_contact_force":1456.11262,"subtask_id":"place_at_goal","tcp_end":[0.45476,0.18394,0.07663],"tcp_start":[0.47796,0.04711,0.13235],"tcp_to_object_dist_end":16.17396,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[-0.03107,0.24019,-71.20132],"object_pos_start":[0.28584,0.14184,-16.09639],"object_to_goal_dist_end":71.43443,"object_to_goal_dist_start":16.32979,"object_z_max":-16.09639,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4516.0,"raw_peak_contact_force":318.17202,"tcp_end":[0.4753,0.19172,0.09901],"tcp_start":[0.45476,0.18394,0.07663],"tcp_to_object_dist_end":71.30214,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[-0.09445,0.25985,-86.9311],"object_pos_start":[-0.03107,0.24019,-71.20132],"object_to_goal_dist_end":87.16422,"object_to_goal_dist_start":71.43443,"object_z_max":-71.20132,"peak_contact_force":0.0,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":230.0,"raw_peak_contact_force":0.01096,"tcp_end":[0.47069,0.19112,0.12275],"tcp_start":[0.4753,0.19172,0.09901],"tcp_to_object_dist_end":87.05571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[-0.41136,0.3582,-189.12403],"object_pos_start":[-0.09445,0.25985,-86.9311],"object_to_goal_dist_end":189.35716,"object_to_goal_dist_start":87.16422,"object_z_max":-86.9311,"peak_contact_force":0.0,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50276,0.20249,0.17997],"tcp_start":[0.47069,0.19112,0.12275],"tcp_to_object_dist_end":189.30627,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```