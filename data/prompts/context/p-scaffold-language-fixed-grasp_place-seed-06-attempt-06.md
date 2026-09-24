## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0057 | 0.26 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0328 | 0.18 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0095 | 0.37 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0159 | 0.28 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0726 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.006) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
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
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_arc
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.006
- **task_score** (E): 0.257
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1774 |
| descend_1 | 1.00 | 1.00 | 0.0866 |
| grasp_1 | 1.00 | 1.00 | 0.0114 |
| lift_1 | 0.33 | 1.00 | 0.0976 |
| transport_approach | 0.00 | 0.67 | 0.0015 |
| place_descend | 1.00 | 1.00 | 0.1155 |
| release_1 | 1.00 | 1.00 | 0.0212 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.127) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.127)→(0.495, 0.024, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.041)→(0.487, 0.023, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.333 | 0.145 | 0.206 |
| lift_1 | lift | 0.33 / step_budget | (0.487, 0.023, 0.032)→(0.483, 0.023, 0.130) | (0.500, 0.024, 0.026)→(0.492, 0.023, 0.115) | 0.272→0.229 | 1.00 / 37.333 | 55983.956 | 0.581 |
| transport_approach | approach | 0.00 / guard_failure | (0.535, 0.105, 0.255)→(0.535, 0.106, 0.256) | (0.492, 0.023, 0.115)→(0.509, 0.058, 0.168) | 0.229→0.176 | 0.67 / 2.333 | 0.006 | 0.312 |
| place_descend | descend | 1.00 / step_budget | (0.535, 0.106, 0.256)→(0.592, 0.190, 0.202) | (0.548, 0.109, 0.225)→(0.559, 0.129, 0.016) | 0.104→0.209 | 1.00 / 8.333 | 91001.889 | 2.089 |
| release_1 | release | 1.00 / step_budget | (0.592, 0.190, 0.202)→(0.587, 0.188, 0.223) | (0.559, 0.129, 0.016)→(0.559, 0.129, 0.016) | 0.209→0.209 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.357
- phase_score: 0.366
- phase_breakdown.descend_1_score: 0.852
- phase_breakdown.transport_arc_score: 0.066
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.057
- phase_breakdown.release_1_score: 0.610
- grasp_place_fitness: 0.653

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.653
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.357
- **Median Q (composite search score)**: -0.005
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16733,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0656,"approach_1.speed":0.05097,"descend_1.grasp_z_offset":0.01883,"descend_1.speed":0.09185,"lift_1.lift_height":0.19836,"lift_1.speed":0.05779,"place_descend.speed":0.05988,"transport_approach.speed":0.01943,"transport_approach.transport_z_offset":0.2277},"optimized_scores":{"best_composite_score":-0.03123,"best_fitness_score":0.56877,"best_task_score":0.18399},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2809.0,"contact_point_centroid":[0.54578,0.09295,-0.00249],"force_p95":0.13568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.30513,"mean_force":0.14495,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56097,0.14197,0.25879]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.49953,-0.01511,-0.00115],"force_p95":0.37644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55723,"mean_force":0.09454,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48931,-0.01544,0.03469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19350.0,"contact_point_centroid":[0.48708,0.00374,0.08435],"force_p95":0.07728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31755,"mean_force":0.05215,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4868,-0.01539,0.08229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19920.0,"contact_point_centroid":[0.48708,-0.03449,0.08268],"force_p95":0.07507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29483,"mean_force":0.05098,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4868,-0.01539,0.08083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9244.0,"contact_point_centroid":[0.50755,0.00704,0.1942],"force_p95":0.12676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25035,"mean_force":0.0707,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50416,0.02569,0.19404]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8289.0,"contact_point_centroid":[0.50855,0.04631,0.19772],"force_p95":0.1303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23291,"mean_force":0.07806,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50503,0.02747,0.19703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.54022,0.10015,0.28281],"force_p95":0.16886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18305,"mean_force":0.07677,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53274,0.08275,0.29009]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01557,-0.00203],"force_p95":0.1325,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1549,"mean_force":0.12523,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4922,-0.01548,0.0344]},{"body_a":"world","body_b":"grasp_target","contact_count":2596.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49864,-0.00714,0.20188]},{"body_a":"world","body_b":"grasp_target","contact_count":2220.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49781,-0.01514,0.06485]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54579,0.09299,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57829,0.18072,0.24315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.49144,0.00382,0.03593],"force_p95":0.07649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10469,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49103,-0.01546,0.03315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5363.0,"contact_point_centroid":[0.49078,-0.03451,0.03584],"force_p95":0.06364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08224,"mean_force":0.04081,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49103,-0.01546,0.03315]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2855.0,"contact_point_centroid":[0.56261,0.14424,0.25999],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01568,"mean_force":0.01051,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56213,0.14423,0.25782]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.58089,0.18155,0.24155],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01105,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58032,0.18153,0.23916]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54579,0.09299,0.01602],"final_tcp_position":[0.58146,0.18172,0.24204],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.30513,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2596.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49951,-0.01452,0.10444],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49886,-0.01557,0.04152],"tcp_start":[0.49951,-0.01452,0.10444],"tcp_to_object_dist_end":0.01627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01529,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31211,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13135,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11282.0,"raw_peak_contact_force":0.1549,"subtask_id":"grasp_1","tcp_end":[0.491,-0.01546,0.03312],"tcp_start":[0.49886,-0.01557,0.04152],"tcp_to_object_dist_end":0.01463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49461,-0.01534,0.11349],"object_pos_start":[0.5037,-0.01529,0.02588],"object_to_goal_dist_end":0.26032,"object_to_goal_dist_start":0.31211,"object_z_max":0.11339,"peak_contact_force":0.06847,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39445.0,"raw_peak_contact_force":0.55723,"tcp_end":[0.48688,-0.01539,0.12858],"tcp_start":[0.491,-0.01546,0.03312],"tcp_to_object_dist_end":0.01695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.54175,0.08233,0.26304],"object_pos_start":[0.49461,-0.01534,0.11349],"object_to_goal_dist_end":0.11538,"object_to_goal_dist_start":0.26032,"object_z_max":0.26326,"peak_contact_force":0.0109,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17533.0,"raw_peak_contact_force":0.25035,"subtask_id":"transport_arc","tcp_end":[0.53272,0.08268,0.29008],"tcp_start":[0.53268,0.08243,0.28989],"tcp_to_object_dist_end":0.02851,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":803.0,"n_steps_budget":1000.0,"object_pos_end":[0.54579,0.09299,0.01602],"object_pos_start":[0.54216,0.08384,0.26067],"object_to_goal_dist_end":0.25393,"object_to_goal_dist_start":0.11356,"object_z_max":0.26067,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5672.0,"raw_peak_contact_force":2.30513,"subtask_id":"release_1","tcp_end":[0.58146,0.18172,0.24204],"tcp_start":[0.53272,0.08268,0.29008],"tcp_to_object_dist_end":0.24542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54579,0.09299,0.01602],"object_pos_start":[0.54579,0.09299,0.01602],"object_to_goal_dist_end":0.25393,"object_to_goal_dist_start":0.25393,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57717,0.18025,0.26293],"tcp_start":[0.58146,0.18172,0.24204],"tcp_to_object_dist_end":0.26375,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22368,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13522,"approach_1.speed":0.03877,"descend_1.grasp_z_offset":0.02155,"descend_1.speed":0.04265,"lift_1.lift_height":0.17754,"lift_1.speed":0.0636,"place_descend.speed":0.06809,"transport_approach.speed":0.09273,"transport_approach.transport_z_offset":0.22765},"optimized_scores":{"best_composite_score":0.05346,"best_fitness_score":0.65346,"best_task_score":0.35696},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3681.0,"contact_point_centroid":[0.57563,0.10515,-0.00228],"force_p95":0.1249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80637,"mean_force":0.13529,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58749,0.13603,0.16462]},{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.50918,0.03785,-0.0012],"force_p95":0.35922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56256,"mean_force":0.08702,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49797,0.03846,0.03679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2493.0,"contact_point_centroid":[0.51792,0.0396,0.16642],"force_p95":0.17152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31461,"mean_force":0.09232,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51299,0.05816,0.1661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17478.0,"contact_point_centroid":[0.49704,0.05728,0.08498],"force_p95":0.08612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31399,"mean_force":0.05832,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49545,0.03826,0.08341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2773.0,"contact_point_centroid":[0.52034,0.07888,0.16932],"force_p95":0.14275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31073,"mean_force":0.08487,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51518,0.06045,0.16933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17154.0,"contact_point_centroid":[0.49704,0.01926,0.08674],"force_p95":0.0873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29006,"mean_force":0.05893,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49544,0.03826,0.08486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5.0,"contact_point_centroid":[0.54903,0.10189,0.20199],"force_p95":0.1967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22154,"mean_force":0.0833,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54235,0.08885,0.20937]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03952,-0.0021],"force_p95":0.15266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2198,"mean_force":0.13053,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5009,0.03871,0.03634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.50015,0.01934,0.03785],"force_p95":0.08108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14754,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49971,0.03861,0.03504]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.01724,0.2364]},{"body_a":"world","body_b":"grasp_target","contact_count":3912.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50625,0.03765,0.0951]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57564,0.10516,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6126,0.16401,0.14136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5454.0,"contact_point_centroid":[0.49945,0.05771,0.03767],"force_p95":0.06794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07797,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49972,0.03861,0.03504]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3693.0,"contact_point_centroid":[0.59012,0.1382,0.16507],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01539,"mean_force":0.01055,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58965,0.13818,0.16284]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.61612,0.16499,0.1403],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61567,0.16496,0.13793]}],"total_contact_groups":15},"final_pose_error":0.0133,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57564,0.10516,0.01602],"final_tcp_position":[0.61717,0.16532,0.14092],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273005.42181,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50764,0.03556,0.1728],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3912.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5076,0.03926,0.04372],"tcp_start":[0.50764,0.03556,0.1728],"tcp_to_object_dist_end":0.01838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03865,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21314,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14758,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11337.0,"raw_peak_contact_force":0.2198,"subtask_id":"grasp_1","tcp_end":[0.49968,0.03861,0.03501],"tcp_start":[0.5076,0.03926,0.04372],"tcp_to_object_dist_end":0.01582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.03812,0.12106],"object_pos_start":[0.51243,0.03865,0.02565],"object_to_goal_dist_end":0.18285,"object_to_goal_dist_start":0.21314,"object_z_max":0.12094,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34809.0,"raw_peak_contact_force":0.56256,"tcp_end":[0.49552,0.03828,0.13981],"tcp_start":[0.49968,0.03861,0.03501],"tcp_to_object_dist_end":0.02144,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.03824,0.12121],"object_pos_start":[0.50592,0.03812,0.12106],"object_to_goal_dist_end":0.18262,"object_to_goal_dist_start":0.18285,"object_z_max":0.18101,"peak_contact_force":0.00654,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5266.0,"raw_peak_contact_force":0.31461,"subtask_id":"transport_arc","tcp_end":[0.54233,0.08878,0.20935],"tcp_start":[0.5407,0.08671,0.20722],"tcp_to_object_dist_end":0.10786,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57564,0.10516,0.01602],"object_pos_start":[0.55626,0.09155,0.17764],"object_to_goal_dist_end":0.15452,"object_to_goal_dist_start":0.11272,"object_z_max":0.17764,"peak_contact_force":273005.42181,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7379.0,"raw_peak_contact_force":1.80637,"subtask_id":"release_1","tcp_end":[0.61717,0.16532,0.14092],"tcp_start":[0.54233,0.08878,0.20935],"tcp_to_object_dist_end":0.14472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57564,0.10516,0.01602],"object_pos_start":[0.57564,0.10516,0.01602],"object_to_goal_dist_end":0.15452,"object_to_goal_dist_start":0.15452,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61082,0.16345,0.16081],"tcp_start":[0.61717,0.16532,0.14092],"tcp_to_object_dist_end":0.16,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73713,"average_solve_count":369.0,"average_success_count":369.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06616,"approach_1.speed":0.01009,"descend_1.grasp_z_offset":0.01025,"descend_1.speed":0.01151,"lift_1.lift_height":0.10125,"lift_1.speed":0.0489,"place_descend.speed":0.03216,"transport_approach.speed":0.13761,"transport_approach.transport_z_offset":0.19928},"optimized_scores":{"best_composite_score":-0.00514,"best_fitness_score":0.59486,"best_task_score":0.23133},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2468.0,"contact_point_centroid":[0.55694,0.18891,-0.00252],"force_p95":0.13798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15574,"mean_force":0.14525,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55748,0.19367,0.23934]},{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.47744,0.046,-0.00124],"force_p95":0.49811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62325,"mean_force":0.11586,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46854,0.04702,0.03115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5329.0,"contact_point_centroid":[0.4913,0.06614,0.17689],"force_p95":0.14296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37023,"mean_force":0.07811,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48843,0.08501,0.17566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20561.0,"contact_point_centroid":[0.46587,0.06596,0.07725],"force_p95":0.07162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3109,"mean_force":0.04937,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46604,0.04678,0.07557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6243.0,"contact_point_centroid":[0.4938,0.10677,0.18061],"force_p95":0.12367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29558,"mean_force":0.07043,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.49043,0.08806,0.18015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20437.0,"contact_point_centroid":[0.46589,0.02762,0.07894],"force_p95":0.07224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2689,"mean_force":0.04886,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46604,0.04678,0.07684]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04848,-0.00214],"force_p95":0.16259,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24344,"mean_force":0.13339,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4713,0.0473,0.0305]},{"body_a":"world","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48889,0.02215,0.20206]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47714,0.0464,0.06842]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55692,0.18886,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57289,0.22212,0.22523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5021.0,"contact_point_centroid":[0.47001,0.02795,0.0324],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11308,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47017,0.04719,0.02936]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5509.0,"contact_point_centroid":[0.46983,0.06652,0.03177],"force_p95":0.06996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08025,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47017,0.04719,0.02936]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2509.0,"contact_point_centroid":[0.55927,0.19555,0.24052],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55864,0.19552,0.23837]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.57541,0.22318,0.22382],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57501,0.22314,0.22137]}],"total_contact_groups":14},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55692,0.18886,0.01602],"final_tcp_position":[0.57619,0.22346,0.22431],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.15574,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2672.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47984,0.04505,0.10496],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47784,0.04796,0.03716],"tcp_start":[0.47984,0.04505,0.10496],"tcp_to_object_dist_end":0.01218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04738,0.02552],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2912,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15597,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12330.0,"raw_peak_contact_force":0.24344,"subtask_id":"grasp_1","tcp_end":[0.47014,0.04719,0.02933],"tcp_start":[0.47784,0.04796,0.03716],"tcp_to_object_dist_end":0.01303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.47489,0.04681,0.11009],"object_pos_start":[0.4826,0.04738,0.02552],"object_to_goal_dist_end":0.24306,"object_to_goal_dist_start":0.2912,"object_z_max":0.11002,"peak_contact_force":0.06879,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41172.0,"raw_peak_contact_force":0.62325,"tcp_end":[0.46613,0.0468,0.12146],"tcp_start":[0.47014,0.04719,0.02933],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.47884,0.05436,0.12042],"object_pos_start":[0.47489,0.04681,0.11009],"object_to_goal_dist_end":0.2306,"object_to_goal_dist_start":0.24306,"object_z_max":0.23917,"peak_contact_force":0.0,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11572.0,"raw_peak_contact_force":0.37023,"subtask_id":"transport_arc","tcp_end":[0.53088,0.1478,0.26912],"tcp_start":[0.53059,0.14724,0.26848],"tcp_to_object_dist_end":0.18316,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.55692,0.18886,0.01602],"object_pos_start":[0.54457,0.15214,0.23572],"object_to_goal_dist_end":0.21958,"object_to_goal_dist_start":0.08546,"object_z_max":0.23572,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4977.0,"raw_peak_contact_force":2.15574,"subtask_id":"release_1","tcp_end":[0.57619,0.22346,0.22431],"tcp_start":[0.53088,0.1478,0.26912],"tcp_to_object_dist_end":0.21203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55692,0.18886,0.01602],"object_pos_start":[0.55692,0.18886,0.01602],"object_to_goal_dist_end":0.21958,"object_to_goal_dist_start":0.21958,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5717,0.22153,0.24493],"tcp_start":[0.57619,0.22346,0.22431],"tcp_to_object_dist_end":0.2317,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```