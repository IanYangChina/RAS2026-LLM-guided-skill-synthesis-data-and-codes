## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0902 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0459 | 0.17 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 4 | -0.0250 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3627 | 0.36 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3628 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.090) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_timeout:
      type: scalar
      range:
      - 20.0
      - 100.0
      default: 50
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: transport_arc
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_timeout:
      type: scalar
      range:
      - 10.0
      - 60.0
      default: 20
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: release_1

```

## Design Metrics

- **Composite score**: 0.090
- **task_score** (E): 0.392
- **fitness_score**: 0.660  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0770 |
| descend_1 | 1.00 | 1.00 | 0.1823 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1944 |
| transport_1 | 1.00 | 1.00 | 0.2359 |
| release_1 | 1.00 | 1.00 | 0.0200 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.011, 0.236) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.508, -0.011, 0.236)→(0.510, -0.016, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.054)→(0.502, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 48.000 | 0.138 | 0.177 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.045)→(0.511, -0.017, 0.239) | (0.515, -0.017, 0.026)→(0.523, -0.017, 0.216) | 0.270→0.234 | 1.00 / 38.000 | 0.079 | 0.459 |
| transport_1 | approach | 1.00 / step_budget | (0.511, -0.017, 0.239)→(0.615, 0.179, 0.187) | (0.523, -0.017, 0.216)→(0.610, 0.180, 0.156) | 0.234→0.016 | 1.00 / 22.667 | 0.125 | 0.251 |
| release_1 | release | 1.00 / step_budget | (0.615, 0.179, 0.187)→(0.609, 0.178, 0.206) | (0.610, 0.180, 0.156)→(0.604, 0.176, 0.025) | 0.016→0.145 | 1.00 / 4.000 | 0.093 | 1.450 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.526
- phase_score: 0.678
- phase_breakdown.transport_arc_score: 0.673
- phase_breakdown.descend_1_score: 0.880
- phase_breakdown.release_1_score: 0.452
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.038
- grasp_place_fitness: 0.726

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.726
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.526
- **Median Q (composite search score)**: 0.075
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.300


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81325,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29995,"approach_1.approach_speed":0.09375,"descend_1.descend_speed":0.01893,"grasp_1.grasp_timeout":21.02487,"lift_1.lift_height":0.21134,"lift_1.lift_speed":0.08538,"release_1.release_timeout":13.13308,"transport_1.arc_height":0.16439,"transport_1.transport_speed":0.0182},"optimized_scores":{"best_composite_score":0.03935,"best_fitness_score":0.60935,"best_task_score":0.28952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.59328,0.21346,-0.00774],"force_p95":1.07048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57036,"mean_force":0.37182,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59968,0.21584,0.2351]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.53427,-0.0207,-0.00137],"force_p95":0.40386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48115,"mean_force":0.10094,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52153,-0.02062,0.04496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":608.0,"contact_point_centroid":[0.59902,0.23599,0.21616],"force_p95":0.12548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39705,"mean_force":0.08699,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60267,0.21717,0.21806]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12968.0,"contact_point_centroid":[0.52658,-0.0017,0.12896],"force_p95":0.07569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31071,"mean_force":0.04926,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52542,-0.02079,0.12657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11320.0,"contact_point_centroid":[0.52593,-0.04002,0.13274],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30982,"mean_force":0.05467,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52563,-0.0208,0.12922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":794.0,"contact_point_centroid":[0.60861,0.20004,0.21277],"force_p95":0.10231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30928,"mean_force":0.06854,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60269,0.21718,0.21809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14309.0,"contact_point_centroid":[0.5592,0.09444,0.27854],"force_p95":0.09665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23163,"mean_force":0.05962,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56087,0.07565,0.27763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15068.0,"contact_point_centroid":[0.56564,0.06256,0.2777],"force_p95":0.08887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22475,"mean_force":0.05775,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56263,0.08129,0.27729]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02138,-0.00207],"force_p95":0.14126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18325,"mean_force":0.12779,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52384,-0.02065,0.04505]},{"body_a":"world","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.53702,-0.02132,-0.00156],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12456,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50882,-0.00544,0.29953]},{"body_a":"world","body_b":"grasp_target","contact_count":2960.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5244,-0.01642,0.17451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5804.0,"contact_point_centroid":[0.52312,-0.00147,0.04659],"force_p95":0.06341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10249,"mean_force":0.03801,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5226,-0.02063,0.0436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4667.0,"contact_point_centroid":[0.52282,-0.03995,0.04731],"force_p95":0.07403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07854,"mean_force":0.04687,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5226,-0.02063,0.0436]}],"total_contact_groups":13},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59504,0.21309,0.02269],"final_tcp_position":[0.60474,0.21758,0.22336],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.57036,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":73.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02592],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12255,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":288.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.51972,-0.01213,0.29774],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02592],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31677,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2960.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.53123,-0.02074,0.0538],"tcp_start":[0.51972,-0.01213,0.29774],"tcp_to_object_dist_end":0.02838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02112,0.02575],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31673,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14083,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12271.0,"raw_peak_contact_force":0.18325,"subtask_id":"grasp_1","tcp_end":[0.52257,-0.02063,0.04356],"tcp_start":[0.53123,-0.02074,0.0538],"tcp_to_object_dist_end":0.02291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.5447,-0.02152,0.19615],"object_pos_start":[0.53696,-0.02112,0.02575],"object_to_goal_dist_end":0.25801,"object_to_goal_dist_start":0.31673,"object_z_max":0.19589,"peak_contact_force":0.07724,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24367.0,"raw_peak_contact_force":0.48115,"tcp_end":[0.53276,-0.02102,0.21756],"tcp_start":[0.52257,-0.02063,0.04356],"tcp_to_object_dist_end":0.02452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.60063,0.21849,0.19257],"object_pos_start":[0.5447,-0.02152,0.19615],"object_to_goal_dist_end":0.02,"object_to_goal_dist_start":0.25801,"object_z_max":0.28271,"peak_contact_force":0.12206,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29377.0,"raw_peak_contact_force":0.23163,"subtask_id":"transport_arc","tcp_end":[0.60474,0.21758,0.22336],"tcp_start":[0.53276,-0.02102,0.21756],"tcp_to_object_dist_end":0.03108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59504,0.21309,0.02269],"object_pos_start":[0.60063,0.21849,0.19257],"object_to_goal_dist_end":0.18593,"object_to_goal_dist_start":0.02,"object_z_max":0.19257,"peak_contact_force":0.07552,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1595.0,"raw_peak_contact_force":1.57036,"subtask_id":"release_1","tcp_end":[0.59964,0.21583,0.24248],"tcp_start":[0.60474,0.21758,0.22336],"tcp_to_object_dist_end":0.21986,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06918,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2004,"approach_1.approach_speed":0.04317,"descend_1.descend_speed":0.02728,"grasp_1.grasp_timeout":50.1246,"lift_1.lift_height":0.26592,"lift_1.lift_speed":0.06026,"release_1.release_timeout":24.84732,"transport_1.arc_height":0.13397,"transport_1.transport_speed":0.05891},"optimized_scores":{"best_composite_score":0.07541,"best_fitness_score":0.64541,"best_task_score":0.3614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":230.0,"contact_point_centroid":[0.61557,0.15854,-0.00632],"force_p95":0.99777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64,"mean_force":0.30649,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62444,0.16361,0.20643]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54344,-0.02856,-0.00137],"force_p95":0.41931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49181,"mean_force":0.08612,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53022,-0.02856,0.04502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16461.0,"contact_point_centroid":[0.53576,-0.00954,0.15403],"force_p95":0.07881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31563,"mean_force":0.0503,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53428,-0.02866,0.15192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15553.0,"contact_point_centroid":[0.53487,-0.04785,0.15723],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31145,"mean_force":0.05246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53442,-0.02866,0.15431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.63087,0.14618,0.18581],"force_p95":0.11111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30868,"mean_force":0.07292,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62786,0.16461,0.1908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.62395,0.18292,0.18812],"force_p95":0.09791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27682,"mean_force":0.06405,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62793,0.16463,0.19094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12489.0,"contact_point_centroid":[0.58337,0.08534,0.29414],"force_p95":0.09862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24034,"mean_force":0.05806,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58511,0.06669,0.29393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11006.0,"contact_point_centroid":[0.58721,0.04816,0.29295],"force_p95":0.11453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2254,"mean_force":0.06604,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58535,0.06717,0.2932]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02926,-0.00206],"force_p95":0.14062,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17719,"mean_force":0.12753,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53261,-0.02862,0.04514]},{"body_a":"world","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.5456,-0.02923,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52037,-0.01401,0.26246]},{"body_a":"world","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53738,-0.0272,0.13495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5800.0,"contact_point_centroid":[0.53192,-0.00934,0.04653],"force_p95":0.06704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11431,"mean_force":0.03814,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53136,-0.02859,0.04365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5141.0,"contact_point_centroid":[0.53151,-0.04788,0.04694],"force_p95":0.0709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07769,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53136,-0.02859,0.04365]}],"total_contact_groups":13},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61645,0.16001,0.02522],"final_tcp_position":[0.63021,0.16534,0.19663],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.64,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":772.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53739,-0.02567,0.21824],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54007,-0.02881,0.05416],"tcp_start":[0.53739,-0.02567,0.21824],"tcp_to_object_dist_end":0.02869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02897,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2609,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14015,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12741.0,"raw_peak_contact_force":0.17719,"subtask_id":"grasp_1","tcp_end":[0.53133,-0.02859,0.04361],"tcp_start":[0.54007,-0.02881,0.05416],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.55372,-0.0295,0.24968],"object_pos_start":[0.54554,-0.02897,0.02576],"object_to_goal_dist_end":0.22216,"object_to_goal_dist_start":0.2609,"object_z_max":0.24942,"peak_contact_force":0.08309,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32095.0,"raw_peak_contact_force":0.49181,"tcp_end":[0.54214,-0.02886,0.27223],"tcp_start":[0.53133,-0.02859,0.04361],"tcp_to_object_dist_end":0.02536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.62553,0.166,0.16515],"object_pos_start":[0.55372,-0.0295,0.24968],"object_to_goal_dist_end":0.0139,"object_to_goal_dist_start":0.22216,"object_z_max":0.29439,"peak_contact_force":0.12024,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23495.0,"raw_peak_contact_force":0.24034,"subtask_id":"transport_arc","tcp_end":[0.63021,0.16534,0.19663],"tcp_start":[0.54214,-0.02886,0.27223],"tcp_to_object_dist_end":0.03183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61645,0.16001,0.02522],"object_pos_start":[0.62553,0.166,0.16515],"object_to_goal_dist_end":0.15266,"object_to_goal_dist_start":0.0139,"object_z_max":0.16515,"peak_contact_force":0.0814,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1774.0,"raw_peak_contact_force":1.64,"subtask_id":"release_1","tcp_end":[0.62439,0.1636,0.21511],"tcp_start":[0.63021,0.16534,0.19663],"tcp_to_object_dist_end":0.19009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2349,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17435,"approach_1.approach_speed":0.06166,"descend_1.descend_speed":0.06275,"grasp_1.grasp_timeout":42.39394,"lift_1.lift_height":0.2203,"lift_1.lift_speed":0.04657,"release_1.release_timeout":53.25287,"transport_1.arc_height":0.11392,"transport_1.transport_speed":0.04191},"optimized_scores":{"best_composite_score":0.15571,"best_fitness_score":0.72571,"best_task_score":0.52608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":305.0,"contact_point_centroid":[0.59993,0.15477,-0.00439],"force_p95":0.69983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14029,"mean_force":0.22037,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60278,0.15337,0.14995]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.46019,9e-05,-0.00134],"force_p95":0.37502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40406,"mean_force":0.08732,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44973,0.00024,0.0483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":597.0,"contact_point_centroid":[0.60452,0.17342,0.13368],"force_p95":0.12568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31675,"mean_force":0.08499,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60682,0.15443,0.13632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12524.0,"contact_point_centroid":[0.53319,0.05614,0.25036],"force_p95":0.10281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28156,"mean_force":0.06265,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53098,0.07479,0.25133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":785.0,"contact_point_centroid":[0.61063,0.13676,0.13103],"force_p95":0.0992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2805,"mean_force":0.06778,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60687,0.15444,0.13639]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11204.0,"contact_point_centroid":[0.52731,0.09169,0.25235],"force_p95":0.11255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2708,"mean_force":0.06811,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52902,0.0728,0.25251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12356.0,"contact_point_centroid":[0.45349,-0.01889,0.13566],"force_p95":0.07335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26799,"mean_force":0.0487,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45288,0.0002,0.13411]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10370.0,"contact_point_centroid":[0.45354,0.01943,0.13737],"force_p95":0.08014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26181,"mean_force":0.05629,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45298,0.0002,0.13551]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46286,-2e-05,-0.00204],"force_p95":0.13384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17167,"mean_force":0.12582,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45191,0.00029,0.04806]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.46286,-7e-05,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48374,0.00796,0.24828]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46159,0.00322,0.12306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5049.0,"contact_point_centroid":[0.45099,0.01957,0.04889],"force_p95":0.06552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08471,"mean_force":0.04336,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45076,0.00027,0.04693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5612.0,"contact_point_centroid":[0.45101,-0.01894,0.04857],"force_p95":0.06095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07628,"mean_force":0.03949,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45076,0.00027,0.04693]}],"total_contact_groups":13},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59979,0.15469,0.02642],"final_tcp_position":[0.60959,0.15528,0.1418],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.14029,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":848.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46687,0.00605,0.19287],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45877,0.00042,0.05488],"tcp_start":[0.46687,0.00605,0.19287],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,0.00023,0.02584],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23302,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.13283,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12461.0,"raw_peak_contact_force":0.17167,"subtask_id":"grasp_1","tcp_end":[0.45073,0.00027,0.0469],"tcp_start":[0.45877,0.00042,0.05488],"tcp_to_object_dist_end":0.02426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.47016,0.00017,0.20274],"object_pos_start":[0.46277,0.00023,0.02584],"object_to_goal_dist_end":0.22227,"object_to_goal_dist_start":0.23302,"object_z_max":0.20246,"peak_contact_force":0.07808,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22798.0,"raw_peak_contact_force":0.40406,"tcp_end":[0.45897,0.0002,0.22666],"tcp_start":[0.45073,0.00027,0.0469],"tcp_to_object_dist_end":0.0264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.6049,0.15638,0.11029],"object_pos_start":[0.47016,0.00017,0.20274],"object_to_goal_dist_end":0.01347,"object_to_goal_dist_start":0.22227,"object_z_max":0.25542,"peak_contact_force":0.13348,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23728.0,"raw_peak_contact_force":0.28156,"subtask_id":"transport_arc","tcp_end":[0.60959,0.15528,0.1418],"tcp_start":[0.45897,0.0002,0.22666],"tcp_to_object_dist_end":0.03188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59979,0.15469,0.02642],"object_pos_start":[0.6049,0.15638,0.11029],"object_to_goal_dist_end":0.09634,"object_to_goal_dist_start":0.01347,"object_z_max":0.11029,"peak_contact_force":0.12064,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1687.0,"raw_peak_contact_force":1.14029,"subtask_id":"release_1","tcp_end":[0.60267,0.15335,0.16119],"tcp_start":[0.60959,0.15528,0.1418],"tcp_to_object_dist_end":0.13481,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```