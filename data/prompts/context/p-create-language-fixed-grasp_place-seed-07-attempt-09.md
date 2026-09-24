## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1112 | 0.26 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1982 | 0.27 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2113 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2167 | 0.25 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0953 | 0.17 | ❌ rejected |

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

## Current Skill (Q=0.111) — your mutation base

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

- **Composite score**: 0.111
- **task_score** (E): 0.264
- **fitness_score**: 0.511  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1123 |
| descend_1 | 1.00 | 1.00 | 0.1400 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.0822 |
| transport_to_goal | 1.00 | 1.00 | 0.2213 |
| place_descend | 1.00 | 1.00 | 0.0568 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.014, 0.195) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.508, 0.014, 0.195)→(0.506, 0.021, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.055)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 42.000 | 0.184 | 0.235 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.025, 0.128)→(0.504, 0.026, 0.209) | (0.511, 0.021, 0.025)→(0.511, 0.030, 0.097) | 0.274→0.236 | 1.00 / 18.000 | 0.117 | 0.898 |
| transport_to_goal | approach | 1.00 / step_budget | (0.504, 0.026, 0.209)→(0.597, 0.198, 0.292) | (0.511, 0.030, 0.097)→(0.569, 0.138, 0.016) | 0.236→0.216 | 1.00 / 8.000 | 0.123 | 1.391 |
| place_descend | descend | 1.00 / step_budget | (0.597, 0.198, 0.292)→(0.598, 0.203, 0.236) | (0.569, 0.138, 0.016)→(0.569, 0.138, 0.016) | 0.216→0.216 | 1.00 / 8.667 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.598, 0.203, 0.236)→(0.594, 0.202, 0.255) | (0.569, 0.138, 0.016)→(0.569, 0.138, 0.016) | 0.216→0.216 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.420
- phase_score: 0.372
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.088
- phase_breakdown.release_1_score: 0.364
- phase_breakdown.transport_arc_score: 0.140
- phase_breakdown.descend_1_score: 0.862
- grasp_place_fitness: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.672
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.420
- **Median Q (composite search score)**: 0.180
- **K-run variance**: 0.0280
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.356


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07092,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09312,"descend_1.grasp_z_offset":0.01043,"lift_1.lift_height":0.1671,"place_descend.place_z_offset":0.02364,"transport_to_goal.transport_speed":0.16153},"optimized_scores":{"best_composite_score":0.27249,"best_fitness_score":0.67249,"best_task_score":0.41981},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1983.0,"contact_point_centroid":[0.61015,0.17357,-0.00254],"force_p95":0.21464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73795,"mean_force":0.14855,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61354,0.1608,0.24322]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.51073,0.03641,-0.00154],"force_p95":0.36963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40789,"mean_force":0.07994,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49821,0.03702,0.04727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11725.0,"contact_point_centroid":[0.50676,0.05602,0.13018],"force_p95":0.10622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29357,"mean_force":0.07148,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50241,0.03721,0.12902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11361.0,"contact_point_centroid":[0.50667,0.01841,0.13266],"force_p95":0.1077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27733,"mean_force":0.07186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50259,0.03722,0.13207]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3637.0,"contact_point_centroid":[0.5431,0.05784,0.18773],"force_p95":0.137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25394,"mean_force":0.09615,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53748,0.07628,0.1907]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51259,0.03955,-0.00221],"force_p95":0.18107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23911,"mean_force":0.13789,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,0.03722,0.04691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3879.0,"contact_point_centroid":[0.54442,0.09594,0.18871],"force_p95":0.12959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20047,"mean_force":0.09025,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53875,0.07768,0.19164]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4125.0,"contact_point_centroid":[0.49994,0.01791,0.04762],"force_p95":0.08167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15968,"mean_force":0.05169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03712,0.04566]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.51251,0.03972,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50354,0.01518,0.22803]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50681,0.03474,0.10334]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.61006,0.17371,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61722,0.16699,0.18336]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61006,0.17371,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61282,0.1662,0.17303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5130.0,"contact_point_centroid":[0.50031,0.05634,0.04779],"force_p95":0.07686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0798,"mean_force":0.04364,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03713,0.04567]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1892.0,"contact_point_centroid":[0.61522,0.16227,0.24583],"force_p95":0.01163,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61468,0.16224,0.24355]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2273.0,"contact_point_centroid":[0.61781,0.16702,0.18561],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01047,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61721,0.16698,0.18339]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.61621,0.16713,0.17189],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61557,0.16708,0.16968]}],"total_contact_groups":16},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61006,0.17371,0.01602],"final_tcp_position":[0.62078,0.16865,0.18145],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.73795,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":852.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50781,0.03188,0.15141],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":724.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5077,0.03775,0.0553],"tcp_start":[0.50781,0.03188,0.15141],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03793,0.02525],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21377,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17527,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11055.0,"raw_peak_contact_force":0.23911,"subtask_id":"grasp_1","tcp_end":[0.49926,0.03712,0.04563],"tcp_start":[0.5077,0.03775,0.0553],"tcp_to_object_dist_end":0.02432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":421.0,"n_steps_budget":930.0,"object_pos_end":[0.51137,0.0376,0.13722],"object_pos_start":[0.51251,0.03793,0.02525],"object_to_goal_dist_end":0.17823,"object_to_goal_dist_start":0.21377,"object_z_max":0.1474,"peak_contact_force":0.09247,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23169.0,"raw_peak_contact_force":0.40789,"tcp_end":[0.5038,0.03726,0.16731],"tcp_start":[0.49926,0.03712,0.04563],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.61006,0.17371,0.01602],"object_pos_start":[0.51137,0.0376,0.13722],"object_to_goal_dist_end":0.13019,"object_to_goal_dist_start":0.17823,"object_z_max":0.18147,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11391.0,"raw_peak_contact_force":1.73795,"subtask_id":"transport_arc","tcp_end":[0.61446,0.16243,0.24199],"tcp_start":[0.5038,0.03726,0.16731],"tcp_to_object_dist_end":0.2263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.61006,0.17371,0.01602],"object_pos_start":[0.61006,0.17371,0.01602],"object_to_goal_dist_end":0.13019,"object_to_goal_dist_start":0.13019,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4409.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61691,0.16747,0.17266],"tcp_start":[0.61446,0.16243,0.24199],"tcp_to_object_dist_end":0.15691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61006,0.17371,0.01602],"object_pos_start":[0.61006,0.17371,0.01602],"object_to_goal_dist_end":0.13019,"object_to_goal_dist_start":0.13019,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61123,0.16567,0.19242],"tcp_start":[0.61691,0.16747,0.17266],"tcp_to_object_dist_end":0.17658,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37719,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22553,"descend_1.grasp_z_offset":0.01044,"lift_1.lift_height":0.16871,"place_descend.place_z_offset":0.04747,"transport_to_goal.transport_speed":0.05225},"optimized_scores":{"best_composite_score":0.18049,"best_fitness_score":0.58049,"best_task_score":0.23663},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1999.0,"contact_point_centroid":[0.55549,0.23456,-0.00275],"force_p95":0.18339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.31134,"mean_force":0.15851,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57296,0.21713,0.32666]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.48071,0.04446,-0.0016],"force_p95":0.36078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44961,"mean_force":0.09116,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47063,0.04518,0.04881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10527.0,"contact_point_centroid":[0.47639,0.02668,0.12994],"force_p95":0.13635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29447,"mean_force":0.07779,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47371,0.04551,0.13011]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12028.0,"contact_point_centroid":[0.47687,0.06414,0.13267],"force_p95":0.10461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29305,"mean_force":0.06774,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47373,0.04551,0.13192]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04851,-0.00226],"force_p95":0.24825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26052,"mean_force":0.17397,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4728,0.0454,0.0482]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5697.0,"contact_point_centroid":[0.51695,0.09595,0.22819],"force_p95":0.13794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23787,"mean_force":0.10869,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51231,0.1141,0.23192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3840.0,"contact_point_centroid":[0.47154,0.02607,0.04837],"force_p95":0.09414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19624,"mean_force":0.06346,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47172,0.0453,0.04709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6339.0,"contact_point_centroid":[0.51331,0.12577,0.22272],"force_p95":0.13629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17232,"mean_force":0.09959,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50859,0.10772,0.22584]},{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.4827,0.04873,-0.00148],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1248,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49535,0.01116,0.28813]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12371,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48399,0.03584,0.16431]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.55525,0.23467,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57487,0.22255,0.28812]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55525,0.23467,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5722,0.22157,0.28368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5134.0,"contact_point_centroid":[0.47173,0.06454,0.0484],"force_p95":0.08547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09612,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47173,0.0453,0.0471]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2049.0,"contact_point_centroid":[0.57363,0.21773,0.32937],"force_p95":0.01176,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01557,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57327,0.2177,0.32701]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2069.0,"contact_point_centroid":[0.57532,0.2226,0.29038],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01045,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57487,0.22254,0.28815]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.5743,0.22245,0.28212],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.00995,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57376,0.22239,0.2799]}],"total_contact_groups":16},"final_pose_error":0.01472,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55525,0.23467,0.01602],"final_tcp_position":[0.57698,0.22387,0.29092],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.31134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02587],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.29008,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.1239,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":248.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48967,0.0259,0.27277],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02587],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.29008,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.12371,"subtask_id":"descend_1","tcp_end":[0.47977,0.04599,0.05575],"tcp_start":[0.48967,0.0259,0.27277],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.0464,0.02508],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29209,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.23343,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10774.0,"raw_peak_contact_force":0.26052,"subtask_id":"grasp_1","tcp_end":[0.47169,0.04529,0.04706],"tcp_start":[0.47977,0.04599,0.05575],"tcp_to_object_dist_end":0.02461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":403.0,"n_steps_budget":930.0,"object_pos_end":[0.4806,0.04725,0.13779],"object_pos_start":[0.4827,0.0464,0.02508],"object_to_goal_dist_end":0.22766,"object_to_goal_dist_start":0.29209,"object_z_max":0.14834,"peak_contact_force":0.13636,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22637.0,"raw_peak_contact_force":0.44961,"tcp_end":[0.47444,0.0456,0.16942],"tcp_start":[0.47169,0.04529,0.04706],"tcp_to_object_dist_end":0.03227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.55525,0.23467,0.01602],"object_pos_start":[0.4806,0.04725,0.13779],"object_to_goal_dist_end":0.21619,"object_to_goal_dist_start":0.22766,"object_z_max":0.25422,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16084.0,"raw_peak_contact_force":2.31134,"subtask_id":"transport_arc","tcp_end":[0.57351,0.21862,0.32593],"tcp_start":[0.47444,0.0456,0.16942],"tcp_to_object_dist_end":0.31087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.55525,0.23467,0.01602],"object_pos_start":[0.55525,0.23467,0.01602],"object_to_goal_dist_end":0.21619,"object_to_goal_dist_start":0.21619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4009.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57461,0.22277,0.28272],"tcp_start":[0.57351,0.21862,0.32593],"tcp_to_object_dist_end":0.26767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55525,0.23467,0.01602],"object_pos_start":[0.55525,0.23467,0.01602],"object_to_goal_dist_end":0.21619,"object_to_goal_dist_start":0.21619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57139,0.2211,0.30333],"tcp_start":[0.57461,0.22277,0.28272],"tcp_to_object_dist_end":0.28809,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64754,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10277,"descend_1.grasp_z_offset":0.01023,"lift_1.lift_height":0.28708,"place_descend.place_z_offset":0.04009,"transport_to_goal.transport_speed":0.07536},"optimized_scores":{"best_composite_score":-0.11935,"best_fitness_score":0.28065,"best_task_score":0.13459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2623.0,"contact_point_centroid":[0.54065,0.00557,-0.0024],"force_p95":0.16158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83744,"mean_force":0.14009,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53146,-0.01961,0.2757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7921.0,"contact_point_centroid":[0.52696,-0.0015,0.1186],"force_p95":0.12575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27936,"mean_force":0.07553,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52283,-0.02027,0.11663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7612.0,"contact_point_centroid":[0.52692,-0.03911,0.11788],"force_p95":0.12839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27887,"mean_force":0.07799,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52282,-0.02027,0.1163]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02121,-0.00209],"force_p95":0.14685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20388,"mean_force":0.12944,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52351,-0.02028,0.04578]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.53702,-0.02132,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51291,-0.00807,0.23238]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52822,-0.01867,0.10743]},{"body_a":"world","body_b":"grasp_target","contact_count":4224.0,"contact_point_centroid":[0.54073,0.00634,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58138,0.14564,0.30404]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.54073,0.00634,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60324,0.21936,0.25915]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54073,0.00634,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60006,0.21888,0.25137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4973.0,"contact_point_centroid":[0.52335,-0.00108,0.04731],"force_p95":0.06774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11346,"mean_force":0.04348,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52233,-0.02025,0.04442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.52338,-0.03953,0.0462],"force_p95":0.07119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07318,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52233,-0.02025,0.04442]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2512.0,"contact_point_centroid":[0.5322,-0.01952,0.28748],"force_p95":0.01132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53184,-0.01952,0.28514]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4495.0,"contact_point_centroid":[0.58186,0.14579,0.30635],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58143,0.14578,0.30406]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2205.0,"contact_point_centroid":[0.60392,0.2194,0.26125],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01033,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60323,0.21937,0.25902]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.6028,0.2198,0.24999],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01252,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60193,0.21976,0.24811]}],"total_contact_groups":15},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54073,0.00634,0.01602],"final_tcp_position":[0.60561,0.22134,0.26001],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.83744,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":812.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52737,-0.017,0.16024],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":784.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53107,-0.02038,0.05493],"tcp_start":[0.52737,-0.017,0.16024],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.0206,0.02567],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31637,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14347,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11724.0,"raw_peak_contact_force":0.20388,"subtask_id":"grasp_1","tcp_end":[0.5223,-0.02025,0.04438],"tcp_start":[0.53107,-0.02038,0.05493],"tcp_to_object_dist_end":0.02377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.54073,0.00634,0.01602],"object_pos_start":[0.53696,-0.0206,0.02567],"object_to_goal_dist_end":0.30083,"object_to_goal_dist_start":0.31637,"object_z_max":0.18613,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20668.0,"raw_peak_contact_force":1.83744,"tcp_end":[0.53438,-0.00494,0.29023],"tcp_start":[0.53428,-0.00737,0.29046],"tcp_to_object_dist_end":0.27452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":656.0,"n_steps_budget":1000.0,"object_pos_end":[0.54073,0.00634,0.01602],"object_pos_start":[0.54073,0.00634,0.01602],"object_to_goal_dist_end":0.30083,"object_to_goal_dist_start":0.30083,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8719.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.60205,0.21159,0.30782],"tcp_start":[0.53438,-0.00494,0.29023],"tcp_to_object_dist_end":0.36199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.54073,0.00634,0.01602],"object_pos_start":[0.54073,0.00634,0.01602],"object_to_goal_dist_end":0.30083,"object_to_goal_dist_start":0.30083,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4245.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60289,0.22016,0.25113],"tcp_start":[0.60205,0.21159,0.30782],"tcp_to_object_dist_end":0.32382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54073,0.00634,0.01602],"object_pos_start":[0.54073,0.00634,0.01602],"object_to_goal_dist_end":0.30083,"object_to_goal_dist_start":0.30083,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59906,0.21837,0.27068],"tcp_start":[0.60289,0.22016,0.25113],"tcp_to_object_dist_end":0.33647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```