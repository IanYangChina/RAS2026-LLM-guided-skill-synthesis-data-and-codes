## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.1487 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 2 | 0.2823 | 0.23 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 1 | 0.2934 | 0.19 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.4470 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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

## Current Skill (Q=0.149) — your mutation base

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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
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
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.149
- **task_score** (E): 0.220
- **fitness_score**: 0.499  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2454 |
| descend_1 | 1.00 | 1.00 | 0.0142 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1147 |
| transport_to_goal | 0.00 | 1.00 | 0.0000 |
| descend_to_goal | 0.00 | 1.00 | 0.0931 |
| release_1 | 1.00 | 1.00 | 0.0230 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.059) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.019, 0.059)→(0.505, 0.020, 0.044) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.020, 0.044)→(0.496, 0.020, 0.035) | (0.511, 0.022, 0.026)→(0.511, 0.020, 0.025) | 0.273→0.275 | 1.00 / 40.000 | 0.219 | 0.289 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.020, 0.035)→(0.502, 0.020, 0.150) | (0.511, 0.020, 0.025)→(0.515, 0.025, 0.084) | 0.275→0.242 | 1.00 / 16.667 | 0.131 | 0.914 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.519, 0.051, 0.181)→(0.518, 0.051, 0.181) | (0.515, 0.025, 0.084)→(0.541, 0.078, 0.016) | 0.242→0.238 | 1.00 / 8.000 | 3249.699 | 1.212 |
| descend_to_goal | descend | 0.00 / step_budget | (0.518, 0.051, 0.181)→(0.560, 0.132, 0.172) | (0.541, 0.078, 0.016)→(0.541, 0.078, 0.016) | 0.238→0.238 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.560, 0.132, 0.172)→(0.554, 0.130, 0.194) | (0.541, 0.078, 0.016)→(0.541, 0.078, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.332
- phase_score: 0.330
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.556
- phase_breakdown.release_1_score: 0.241
- phase_breakdown.transport_arc_score: 0.059
- phase_breakdown.descend_1_score: 0.835
- grasp_place_fitness: 0.638

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.638
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.332
- **Median Q (composite search score)**: 0.224
- **K-run variance**: 0.0238
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.224


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53896,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_speed":0.05429,"lift_1.lift_height":0.14222,"transport_to_goal.approach_height":0.1085,"transport_to_goal.transport_speed":0.1098},"optimized_scores":{"best_composite_score":0.28792,"best_fitness_score":0.63792,"best_task_score":0.33162},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1377.0,"contact_point_centroid":[0.55153,0.10009,-0.00269],"force_p95":0.35853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62914,"mean_force":0.1623,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52947,0.07161,0.1603]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.5107,0.03447,-0.00163],"force_p95":0.42101,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54086,"mean_force":0.10865,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49692,0.03529,0.03685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":891.0,"contact_point_centroid":[0.51737,0.02955,0.14441],"force_p95":0.20025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3569,"mean_force":0.12328,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51205,0.04747,0.14862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":973.0,"contact_point_centroid":[0.51868,0.06713,0.14529],"force_p95":0.1639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33293,"mean_force":0.11419,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51362,0.04935,0.14991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9624.0,"contact_point_centroid":[0.50696,0.01691,0.1155],"force_p95":0.11745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32075,"mean_force":0.08002,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50209,0.03549,0.11406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9300.0,"contact_point_centroid":[0.506,0.05419,0.10998],"force_p95":0.12063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31131,"mean_force":0.08415,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50164,0.03547,0.10862]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5127,0.03916,-0.00235],"force_p95":0.26383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30273,"mean_force":0.18,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03548,0.03619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3403.0,"contact_point_centroid":[0.50031,0.01615,0.03855],"force_p95":0.11006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17174,"mean_force":0.06978,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49799,0.03539,0.03496]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50347,0.0167,0.18123]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.55159,0.10184,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56501,0.11243,0.14484]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55159,0.10184,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57497,0.12884,0.13736]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50621,0.03503,0.05162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4881.0,"contact_point_centroid":[0.49925,0.05479,0.03663],"force_p95":0.09294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11282,"mean_force":0.0569,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.498,0.03539,0.03497]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1306.0,"contact_point_centroid":[0.52959,0.07158,0.16225],"force_p95":0.01227,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01072,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52932,0.07157,0.16008]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5961.0,"contact_point_centroid":[0.5655,0.11255,0.14709],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5651,0.11252,0.14481]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.57858,0.12962,0.13523],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57799,0.12959,0.13305]}],"total_contact_groups":16},"final_pose_error":0.06035,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55159,0.10184,0.01602],"final_tcp_position":[0.58384,0.13097,0.14331],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.85152,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50768,0.03444,0.0585],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":31.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":124.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.50646,0.03595,0.04444],"tcp_start":[0.50768,0.03444,0.0585],"tcp_to_object_dist_end":0.01975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51255,0.0362,0.02486],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21507,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.23519,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10084.0,"raw_peak_contact_force":0.30273,"subtask_id":"grasp_1","tcp_end":[0.49796,0.03539,0.03492],"tcp_start":[0.50646,0.03595,0.04444],"tcp_to_object_dist_end":0.01774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":374.0,"n_steps_budget":840.0,"object_pos_end":[0.51196,0.03552,0.11879],"object_pos_start":[0.51255,0.0362,0.02486],"object_to_goal_dist_end":0.18117,"object_to_goal_dist_start":0.21507,"object_z_max":0.13173,"peak_contact_force":0.16283,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19013.0,"raw_peak_contact_force":0.54086,"tcp_end":[0.50315,0.0355,0.14218],"tcp_start":[0.49796,0.03539,0.03492],"tcp_to_object_dist_end":0.02499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.55159,0.10184,0.01602],"object_pos_start":[0.51196,0.03552,0.11879],"object_to_goal_dist_end":0.16556,"object_to_goal_dist_start":0.18117,"object_z_max":0.13136,"peak_contact_force":9748.85152,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4547.0,"raw_peak_contact_force":1.62914,"subtask_id":"transport_arc","tcp_end":[0.52922,0.07154,0.1599],"tcp_start":[0.52923,0.07154,0.15993],"tcp_to_object_dist_end":0.14873,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55159,0.10184,0.01602],"object_pos_start":[0.55159,0.10184,0.01602],"object_to_goal_dist_end":0.16556,"object_to_goal_dist_start":0.16556,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57951,0.12994,0.13568],"tcp_start":[0.52922,0.07154,0.1599],"tcp_to_object_dist_end":0.12605,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55159,0.10184,0.01602],"object_pos_start":[0.55159,0.10184,0.01602],"object_to_goal_dist_end":0.16556,"object_to_goal_dist_start":0.16556,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57318,0.12838,0.15736],"tcp_start":[0.57951,0.12994,0.13568],"tcp_to_object_dist_end":0.14543,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56725,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_speed":0.05773,"lift_1.lift_height":0.13906,"transport_to_goal.approach_height":0.20099,"transport_to_goal.transport_speed":0.09606},"optimized_scores":{"best_composite_score":0.22443,"best_fitness_score":0.57443,"best_task_score":0.20068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1233.0,"contact_point_centroid":[0.52238,0.13209,-0.0032],"force_p95":0.48884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88292,"mean_force":0.19032,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50236,0.10226,0.22184]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4806,0.04285,-0.00177],"force_p95":0.46062,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59621,"mean_force":0.12582,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4704,0.0434,0.03846]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4829,0.0482,-0.00243],"force_p95":0.27935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3186,"mean_force":0.18788,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4726,0.04361,0.03755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10988.0,"contact_point_centroid":[0.476,0.06274,0.11072],"force_p95":0.10496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30294,"mean_force":0.06965,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47339,0.04381,0.10895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11006.0,"contact_point_centroid":[0.47647,0.02502,0.11398],"force_p95":0.10618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26061,"mean_force":0.06789,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47353,0.04383,0.1123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2973.0,"contact_point_centroid":[0.48927,0.08453,0.16995],"force_p95":0.14194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24286,"mean_force":0.09408,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48395,0.06585,0.17019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3261.0,"contact_point_centroid":[0.48912,0.04669,0.16858],"force_p95":0.14808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22906,"mean_force":0.08619,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48349,0.06505,0.16896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4979.0,"contact_point_centroid":[0.47125,0.02418,0.03827],"force_p95":0.09221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18,"mean_force":0.04978,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4715,0.04351,0.03644]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49091,0.0205,0.1814]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.52256,0.13653,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.53404,0.15796,0.21708]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52256,0.13653,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54501,0.18266,0.21482]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48013,0.04302,0.05219]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5718.0,"contact_point_centroid":[0.47078,0.06326,0.03739],"force_p95":0.08844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1123,"mean_force":0.05036,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47152,0.04351,0.03646]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1406.0,"contact_point_centroid":[0.50256,0.10225,0.22391],"force_p95":0.01195,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01748,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50227,0.10223,0.22166]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6036.0,"contact_point_centroid":[0.53445,0.15792,0.21942],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.53399,0.15788,0.21708]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.54778,0.18355,0.21244],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01002,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54726,0.18351,0.21028]}],"total_contact_groups":16},"final_pose_error":0.05413,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52256,0.13653,0.01602],"final_tcp_position":[0.55178,0.18507,0.22011],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.88292,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48202,0.04228,0.0589],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":31.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":124.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.47964,0.04415,0.04503],"tcp_start":[0.48202,0.04228,0.0589],"tcp_to_object_dist_end":0.01979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04477,0.02452],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2935,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.25916,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12497.0,"raw_peak_contact_force":0.3186,"subtask_id":"grasp_1","tcp_end":[0.47148,0.04351,0.03642],"tcp_start":[0.47964,0.04415,0.04503],"tcp_to_object_dist_end":0.01641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":342.0,"n_steps_budget":810.0,"object_pos_end":[0.48422,0.04432,0.11834],"object_pos_start":[0.48271,0.04477,0.02452],"object_to_goal_dist_end":0.23699,"object_to_goal_dist_start":0.2935,"object_z_max":0.12928,"peak_contact_force":0.10718,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22082.0,"raw_peak_contact_force":0.59621,"tcp_end":[0.4738,0.04391,0.13923],"tcp_start":[0.47148,0.04351,0.03642],"tcp_to_object_dist_end":0.02335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.52256,0.13653,0.01602],"object_pos_start":[0.48422,0.04432,0.11834],"object_to_goal_dist_end":0.24091,"object_to_goal_dist_start":0.23699,"object_z_max":0.18326,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8873.0,"raw_peak_contact_force":1.88292,"subtask_id":"transport_arc","tcp_end":[0.50213,0.10219,0.22142],"tcp_start":[0.50215,0.10219,0.22145],"tcp_to_object_dist_end":0.20926,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52256,0.13653,0.01602],"object_pos_start":[0.52256,0.13653,0.01602],"object_to_goal_dist_end":0.24091,"object_to_goal_dist_start":0.24091,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11636.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54845,0.18391,0.21282],"tcp_start":[0.50213,0.10219,0.22142],"tcp_to_object_dist_end":0.20407,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52256,0.13653,0.01602],"object_pos_start":[0.52256,0.13653,0.01602],"object_to_goal_dist_end":0.24091,"object_to_goal_dist_start":0.24091,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54372,0.18216,0.23496],"tcp_start":[0.54845,0.18391,0.21282],"tcp_to_object_dist_end":0.22464,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61905,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_speed":0.0655,"lift_1.lift_height":0.16721,"transport_to_goal.approach_height":0.21973,"transport_to_goal.transport_speed":0.0656},"optimized_scores":{"best_composite_score":-0.06621,"best_fitness_score":0.28379,"best_task_score":0.12851},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1534.0,"contact_point_centroid":[0.54758,-0.00585,-0.00255],"force_p95":0.33829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60533,"mean_force":0.14859,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52788,-0.01943,0.16039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4881.0,"contact_point_centroid":[0.52837,-0.0008,0.09507],"force_p95":0.1449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36497,"mean_force":0.09279,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52295,-0.01936,0.09382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4891.0,"contact_point_centroid":[0.52808,-0.03789,0.09274],"force_p95":0.15018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35802,"mean_force":0.09378,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52272,-0.01935,0.09168]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5371,-0.02104,-0.00219],"force_p95":0.17271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24454,"mean_force":0.13662,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52081,-0.01933,0.03504]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3690.0,"contact_point_centroid":[0.52222,-0.00038,0.03719],"force_p95":0.10194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15084,"mean_force":0.05723,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51961,-0.01931,0.0337]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51378,-0.00899,0.18114]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.54814,-0.0051,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52465,-0.01936,0.16196]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.54814,-0.0051,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54315,0.04837,0.1659]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54814,-0.0051,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54749,0.08024,0.16902]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52759,-0.01892,0.05117]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4085.0,"contact_point_centroid":[0.52257,-0.03833,0.03604],"force_p95":0.09666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09982,"mean_force":0.05439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51962,-0.01931,0.03371]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1258.0,"contact_point_centroid":[0.52854,-0.01944,0.1698],"force_p95":0.01273,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01575,"mean_force":0.01073,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52824,-0.01943,0.16742]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5938.0,"contact_point_centroid":[0.54358,0.04855,0.16817],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54321,0.04855,0.16592]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1700.0,"contact_point_centroid":[0.525,-0.01937,0.1642],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52464,-0.01936,0.16195]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.55069,0.08069,0.16643],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55022,0.08069,0.1641]}],"total_contact_groups":15},"final_pose_error":0.15983,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54814,-0.0051,0.01602],"final_tcp_position":[0.55561,0.08151,0.17328],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.60533,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52888,-0.01855,0.05827],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":31.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":124.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.52846,-0.0194,0.04398],"tcp_start":[0.52888,-0.01855,0.05827],"tcp_to_object_dist_end":0.01999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5372,-0.01961,0.02533],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31573,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.16124,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9575.0,"raw_peak_contact_force":0.24454,"subtask_id":"grasp_1","tcp_end":[0.51958,-0.01931,0.03366],"tcp_start":[0.52846,-0.0194,0.04398],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":478.0,"n_steps_budget":990.0,"object_pos_end":[0.54814,-0.0051,0.01602],"object_pos_start":[0.5372,-0.01961,0.02533],"object_to_goal_dist_end":0.30776,"object_to_goal_dist_start":0.31573,"object_z_max":0.1387,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12564.0,"raw_peak_contact_force":1.60533,"tcp_end":[0.52816,-0.01943,0.1673],"tcp_start":[0.51958,-0.01931,0.03366],"tcp_to_object_dist_end":0.15326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54814,-0.0051,0.01602],"object_pos_start":[0.54814,-0.0051,0.01602],"object_to_goal_dist_end":0.30776,"object_to_goal_dist_start":0.30776,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3308.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.52413,-0.01935,0.16117],"tcp_start":[0.52415,-0.01935,0.1612],"tcp_to_object_dist_end":0.14781,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54814,-0.0051,0.01602],"object_pos_start":[0.54814,-0.0051,0.01602],"object_to_goal_dist_end":0.30776,"object_to_goal_dist_start":0.30776,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11538.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55163,0.0809,0.16647],"tcp_start":[0.52413,-0.01935,0.16117],"tcp_to_object_dist_end":0.17333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54814,-0.0051,0.01602],"object_pos_start":[0.54814,-0.0051,0.01602],"object_to_goal_dist_end":0.30776,"object_to_goal_dist_start":0.30776,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54589,0.07997,0.18943],"tcp_start":[0.55163,0.0809,0.16647],"tcp_to_object_dist_end":0.19317,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```