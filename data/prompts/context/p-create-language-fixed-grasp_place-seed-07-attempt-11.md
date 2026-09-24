## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0077 | 0.20 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | time_limit | time_limit | time_limit | time_limit | 9 | -0.0559 | 0.16 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1112 | 0.26 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1982 | 0.27 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2113 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.008) — your mutation base

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
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
    - 0.0
    tolerance: 0.02
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
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
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
    offset_along_axis:
      distance: 0.08
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
  type: descend
  generator: linear_cartesian
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.08, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.008
- **task_score** (E): 0.195
- **fitness_score**: 0.392  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1196 |
| descend_1 | 1.00 | 1.00 | 0.1305 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.0369 |
| transport_to_goal | 1.00 | 1.00 | 0.2052 |
| place_descend | 1.00 | 1.00 | 0.0393 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.016, 0.187) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 10.882 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.016, 0.187)→(0.506, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.056)→(0.498, 0.021, 0.047) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 43.333 | 0.171 | 0.229 |
| lift_1 | lift | 1.00 / step_budget | (0.508, 0.026, 0.180)→(0.509, 0.027, 0.215) | (0.511, 0.021, 0.025)→(0.519, 0.033, 0.052) | 0.274→0.247 | 1.00 / 13.333 | 3249.834 | 1.307 |
| transport_to_goal | approach | 1.00 / step_budget | (0.509, 0.027, 0.215)→(0.595, 0.196, 0.255) | (0.519, 0.033, 0.052)→(0.535, 0.057, 0.016) | 0.247→0.251 | 1.00 / 8.333 | 0.123 | 0.612 |
| place_descend | descend | 1.00 / step_budget | (0.595, 0.196, 0.255)→(0.596, 0.202, 0.216) | (0.535, 0.057, 0.016)→(0.535, 0.057, 0.016) | 0.251→0.251 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.202, 0.216)→(0.591, 0.200, 0.236) | (0.535, 0.057, 0.016)→(0.535, 0.057, 0.016) | 0.251→0.251 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.194
- phase_score: 0.474
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.020
- phase_breakdown.release_1_score: 0.428
- phase_breakdown.transport_arc_score: 0.311
- phase_breakdown.descend_1_score: 0.875
- grasp_place_fitness: 0.559

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.559
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.260
- **Median Q (composite search score)**: -0.061
- **K-run variance**: 0.0145
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.404


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11403,"descend_1.grasp_z_offset":0.01346,"lift_1.lift_height":0.21771,"place_descend.place_z_offset":0.04083,"transport_to_goal.transport_speed":0.12778},"optimized_scores":{"best_composite_score":-0.0614,"best_fitness_score":0.3386,"best_task_score":0.26007},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1789.0,"contact_point_centroid":[0.53125,0.04909,-0.00259],"force_p95":0.2911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9002,"mean_force":0.14565,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50618,0.03807,0.21031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6706.0,"contact_point_centroid":[0.50352,0.01832,0.11396],"force_p95":0.14897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32882,"mean_force":0.08044,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5006,0.03717,0.11465]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7855.0,"contact_point_centroid":[0.50446,0.0555,0.12074],"force_p95":0.11812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28477,"mean_force":0.07182,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50102,0.0372,0.12045]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51262,0.03964,-0.00222],"force_p95":0.18506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2376,"mean_force":0.13848,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50057,0.03725,0.0502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.50003,0.01797,0.04976],"force_p95":0.09303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14205,"mean_force":0.05487,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49944,0.03716,0.04895]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.51251,0.03972,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50352,0.01465,0.23835]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50679,0.03431,0.11514]},{"body_a":"world","body_b":"grasp_target","contact_count":3248.0,"contact_point_centroid":[0.53226,0.0497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5887,0.13045,0.21344]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.53226,0.0497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61366,0.16321,0.18674]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53226,0.0497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60938,0.16212,0.18445]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.50022,0.05621,0.04974],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08107,"mean_force":0.04447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03716,0.04896]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1624.0,"contact_point_centroid":[0.50707,0.03824,0.22038],"force_p95":0.01174,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5067,0.03823,0.21818]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3506.0,"contact_point_centroid":[0.58941,0.13065,0.21571],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01034,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58884,0.13063,0.21343]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1932.0,"contact_point_centroid":[0.61427,0.16325,0.18892],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01043,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61366,0.16321,0.18676]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.6129,0.16301,0.18317],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61201,0.16296,0.18102]}],"total_contact_groups":15},"final_pose_error":0.01491,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53226,0.0497,0.01602],"final_tcp_position":[0.61705,0.16446,0.19267],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9749.24442,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50771,0.031,0.17187],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":852.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50784,0.03778,0.05861],"tcp_start":[0.50771,0.031,0.17187],"tcp_to_object_dist_end":0.03299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51256,0.03803,0.02514],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21374,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18535,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10796.0,"raw_peak_contact_force":0.2376,"subtask_id":"grasp_1","tcp_end":[0.49942,0.03715,0.04892],"tcp_start":[0.50784,0.03778,0.05861],"tcp_to_object_dist_end":0.02718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.53226,0.0497,0.01602],"object_pos_start":[0.51256,0.03803,0.02514],"object_to_goal_dist_end":0.20202,"object_to_goal_dist_start":0.21374,"object_z_max":0.17691,"peak_contact_force":9749.24442,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17974.0,"raw_peak_contact_force":1.9002,"tcp_end":[0.5187,0.04458,0.22194],"tcp_start":[0.51739,0.04364,0.22198],"tcp_to_object_dist_end":0.20643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.53226,0.0497,0.01602],"object_pos_start":[0.53226,0.0497,0.01602],"object_to_goal_dist_end":0.20202,"object_to_goal_dist_start":0.20202,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6754.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.61129,0.15874,0.20832],"tcp_start":[0.5187,0.04458,0.22194],"tcp_to_object_dist_end":0.23477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.53226,0.0497,0.01602],"object_pos_start":[0.53226,0.0497,0.01602],"object_to_goal_dist_end":0.20202,"object_to_goal_dist_start":0.20202,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3740.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61331,0.16333,0.18397],"tcp_start":[0.61129,0.15874,0.20832],"tcp_to_object_dist_end":0.21838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53226,0.0497,0.01602],"object_pos_start":[0.53226,0.0497,0.01602],"object_to_goal_dist_end":0.20202,"object_to_goal_dist_start":0.20202,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60787,0.16162,0.20388],"tcp_start":[0.61331,0.16333,0.18397],"tcp_to_object_dist_end":0.23138,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77922,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16913,"descend_1.grasp_z_offset":0.01018,"lift_1.lift_height":0.15288,"place_descend.place_z_offset":0.01482,"transport_to_goal.transport_speed":0.12637},"optimized_scores":{"best_composite_score":0.15932,"best_fitness_score":0.55932,"best_task_score":0.19369},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3484.0,"contact_point_centroid":[0.53044,0.1194,-0.00229],"force_p95":0.12849,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59189,"mean_force":0.13677,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5569,0.19074,0.26847]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.48115,0.04514,-0.00155],"force_p95":0.379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43246,"mean_force":0.08686,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47041,0.04563,0.04847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2049.0,"contact_point_centroid":[0.49118,0.05133,0.16833],"force_p95":0.15931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29907,"mean_force":0.09575,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4858,0.06992,0.17034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11195.0,"contact_point_centroid":[0.47658,0.0646,0.12251],"force_p95":0.10335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28175,"mean_force":0.06851,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4735,0.04588,0.12177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2512.0,"contact_point_centroid":[0.49214,0.08861,0.17014],"force_p95":0.12525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2486,"mean_force":0.07929,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48619,0.07057,0.17091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10107.0,"contact_point_centroid":[0.47611,0.02702,0.12165],"force_p95":0.12633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24678,"mean_force":0.07582,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47351,0.04588,0.12146]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04856,-0.00224],"force_p95":0.18815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24659,"mean_force":0.13966,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47254,0.04585,0.04791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4603.0,"contact_point_centroid":[0.47068,0.02649,0.04732],"force_p95":0.07682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15818,"mean_force":0.04688,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47146,0.04574,0.0468]},{"body_a":"world","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.4827,0.04873,-0.00174],"force_p95":0.13798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12365,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49359,0.0158,0.26434]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48211,0.04019,0.13992]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.53046,0.11937,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57344,0.22168,0.25372]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53046,0.11937,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57022,0.22052,0.25028]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5567.0,"contact_point_centroid":[0.47076,0.06506,0.04761],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.077,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47147,0.04575,0.0468]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3483.0,"contact_point_centroid":[0.5601,0.19525,0.27436],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55956,0.19522,0.27206]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2019.0,"contact_point_centroid":[0.57404,0.22173,0.25585],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01049,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57343,0.22168,0.2537]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.57286,0.22149,0.24855],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57211,0.22143,0.24644]}],"total_contact_groups":16},"final_pose_error":0.01466,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53046,0.11937,0.01602],"final_tcp_position":[0.5759,0.22309,0.25739],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":32.40177,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28997,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":32.40177,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48634,0.03412,0.2243],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28997,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47952,0.04647,0.05545],"tcp_start":[0.48634,0.03412,0.2243],"tcp_to_object_dist_end":0.02968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04675,0.02515],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29182,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18205,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11970.0,"raw_peak_contact_force":0.24659,"subtask_id":"grasp_1","tcp_end":[0.47143,0.04574,0.04677],"tcp_start":[0.47952,0.04647,0.05545],"tcp_to_object_dist_end":0.0244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":355.0,"n_steps_budget":840.0,"object_pos_end":[0.48073,0.04692,0.12295],"object_pos_start":[0.4827,0.04675,0.02515],"object_to_goal_dist_end":0.23429,"object_to_goal_dist_start":0.29182,"object_z_max":0.13344,"peak_contact_force":0.13548,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21384.0,"raw_peak_contact_force":0.43246,"tcp_end":[0.47403,0.04592,0.15352],"tcp_start":[0.47143,0.04574,0.04677],"tcp_to_object_dist_end":0.03131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.53046,0.11937,0.01602],"object_pos_start":[0.48073,0.04692,0.12295],"object_to_goal_dist_end":0.24622,"object_to_goal_dist_start":0.23429,"object_z_max":0.15736,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11528.0,"raw_peak_contact_force":1.59189,"subtask_id":"transport_arc","tcp_end":[0.57218,0.21767,0.28692],"tcp_start":[0.47403,0.04592,0.15352],"tcp_to_object_dist_end":0.29119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.53046,0.11937,0.01602],"object_pos_start":[0.53046,0.11937,0.01602],"object_to_goal_dist_end":0.24622,"object_to_goal_dist_start":0.24622,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3919.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5731,0.22185,0.24924],"tcp_start":[0.57218,0.21767,0.28692],"tcp_to_object_dist_end":0.25829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.11937,0.01602],"object_pos_start":[0.53046,0.11937,0.01602],"object_to_goal_dist_end":0.24622,"object_to_goal_dist_start":0.24622,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56919,0.21999,0.26997],"tcp_start":[0.5731,0.22185,0.24924],"tcp_to_object_dist_end":0.27589,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72549,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10622,"descend_1.grasp_z_offset":0.0103,"lift_1.lift_height":0.26768,"place_descend.place_z_offset":0.00458,"transport_to_goal.transport_speed":0.17467},"optimized_scores":{"best_composite_score":-0.1211,"best_fitness_score":0.2789,"best_task_score":0.13158},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2353.0,"contact_point_centroid":[0.54264,0.00041,-0.00245],"force_p95":0.20574,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58896,"mean_force":0.14151,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53111,-0.01982,0.25918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8096.0,"contact_point_centroid":[0.52757,-0.00145,0.12002],"force_p95":0.12238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29546,"mean_force":0.07359,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52318,-0.02027,0.11795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7907.0,"contact_point_centroid":[0.52728,-0.03913,0.118],"force_p95":0.12565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27859,"mean_force":0.07532,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5231,-0.02027,0.11623]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02121,-0.00209],"force_p95":0.14701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20367,"mean_force":0.12946,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52346,-0.02027,0.04596]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.53702,-0.02132,-0.00184],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51285,-0.00802,0.23411]},{"body_a":"world","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52814,-0.01863,0.10922]},{"body_a":"world","body_b":"grasp_target","contact_count":3884.0,"contact_point_centroid":[0.54281,0.00111,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58198,0.14719,0.2714]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.54281,0.00111,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60198,0.21867,0.22269]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54281,0.00111,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59817,0.21803,0.21542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4822.0,"contact_point_centroid":[0.5235,-0.00107,0.0472],"force_p95":0.06967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11341,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52228,-0.02025,0.0446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5020.0,"contact_point_centroid":[0.52324,-0.0395,0.04651],"force_p95":0.07079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07284,"mean_force":0.04424,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52228,-0.02025,0.0446]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2226.0,"contact_point_centroid":[0.53178,-0.01976,0.27053],"force_p95":0.01126,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01594,"mean_force":0.01056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53143,-0.01976,0.26818]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2190.0,"contact_point_centroid":[0.60269,0.21872,0.22489],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01033,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60199,0.21868,0.22266]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4153.0,"contact_point_centroid":[0.58234,0.14687,0.27368],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01043,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58188,0.14687,0.27138]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.60111,0.21905,0.21427],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01108,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60039,0.21901,0.21205]}],"total_contact_groups":15},"final_pose_error":0.01492,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54281,0.00111,0.01602],"final_tcp_position":[0.60475,0.22079,0.22394],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273009.92772,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":796.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52724,-0.01692,0.16358],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53101,-0.02038,0.05511],"tcp_start":[0.52724,-0.01692,0.16358],"tcp_to_object_dist_end":0.02972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02056,0.02567],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31633,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14455,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11642.0,"raw_peak_contact_force":0.20367,"subtask_id":"grasp_1","tcp_end":[0.52225,-0.02025,0.04456],"tcp_start":[0.53101,-0.02038,0.05511],"tcp_to_object_dist_end":0.02395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.54281,0.00111,0.01602],"object_pos_start":[0.53696,-0.02056,0.02567],"object_to_goal_dist_end":0.30423,"object_to_goal_dist_start":0.31633,"object_z_max":0.18536,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20582.0,"raw_peak_contact_force":1.58896,"tcp_end":[0.53472,-0.0091,0.27056],"tcp_start":[0.53437,-0.0113,0.27069],"tcp_to_object_dist_end":0.25487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.54281,0.00111,0.01602],"object_pos_start":[0.54281,0.00111,0.01602],"object_to_goal_dist_end":0.30423,"object_to_goal_dist_start":0.30423,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8037.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.60093,0.21058,0.26948],"tcp_start":[0.53472,-0.0091,0.27056],"tcp_to_object_dist_end":0.33391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.54281,0.00111,0.01602],"object_pos_start":[0.54281,0.00111,0.01602],"object_to_goal_dist_end":0.30423,"object_to_goal_dist_start":0.30423,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4218.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60153,0.21946,0.21511],"tcp_start":[0.60093,0.21058,0.26948],"tcp_to_object_dist_end":0.30127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54281,0.00111,0.01602],"object_pos_start":[0.54281,0.00111,0.01602],"object_to_goal_dist_end":0.30423,"object_to_goal_dist_start":0.30423,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59693,0.21746,0.23477],"tcp_start":[0.60153,0.21946,0.21511],"tcp_to_object_dist_end":0.31239,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```