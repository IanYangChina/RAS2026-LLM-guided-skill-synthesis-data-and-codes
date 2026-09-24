## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0953 | 0.17 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0966 | 0.24 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.1487 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 2 | 0.2823 | 0.23 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 1 | 0.2934 | 0.19 | ❌ rejected |

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

## Current Skill (Q=0.095) — your mutation base

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
      - 0.05
      - 0.25
      default: 0.18
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
    transport_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
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
- id: descend_to_goal
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
    tolerance: 0.02
    orientation:
      mode: keep_current
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
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.095
- **task_score** (E): 0.172
- **fitness_score**: 0.545  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1063 |
| descend_1 | 1.00 | 1.00 | 0.1422 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1150 |
| transport_to_goal | 0.67 | 1.00 | 0.2655 |
| descend_to_goal | 1.00 | 1.00 | 0.1729 |
| release_1 | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.017, 0.200) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.017, 0.200)→(0.506, 0.021, 0.058) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.058)→(0.498, 0.021, 0.048) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 40.667 | 0.172 | 0.231 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.048)→(0.502, 0.021, 0.163) | (0.511, 0.021, 0.025)→(0.509, 0.019, 0.128) | 0.274→0.228 | 1.00 / 15.000 | 0.108 | 0.381 |
| transport_to_goal | approach | 0.67 / step_budget | (0.502, 0.021, 0.163)→(0.585, 0.162, 0.368) | (0.509, 0.019, 0.128)→(0.517, 0.028, 0.016) | 0.228→0.274 | 1.00 / 8.333 | 0.123 | 1.538 |
| descend_to_goal | descend | 1.00 / step_budget | (0.585, 0.162, 0.368)→(0.598, 0.202, 0.203) | (0.517, 0.028, 0.016)→(0.517, 0.028, 0.016) | 0.274→0.274 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.598, 0.202, 0.203)→(0.593, 0.200, 0.223) | (0.517, 0.028, 0.016)→(0.517, 0.028, 0.016) | 0.274→0.274 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.263
- phase_score: 0.330
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.017
- phase_breakdown.release_1_score: 0.503
- phase_breakdown.transport_arc_score: 0.046
- phase_breakdown.descend_1_score: 0.790
- grasp_place_fitness: 0.588

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.588
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.263
- **Median Q (composite search score)**: 0.080
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13836,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17676,"descend_1.grasp_z_offset":0.01556,"lift_1.lift_height":0.14886,"transport_to_goal.arc_height":0.20143,"transport_to_goal.transport_height":0.16457,"transport_to_goal.transport_speed":0.13041},"optimized_scores":{"best_composite_score":0.13782,"best_fitness_score":0.58782,"best_task_score":0.26327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3940.0,"contact_point_centroid":[0.51784,0.06575,-0.00224],"force_p95":0.12399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46696,"mean_force":0.13275,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57277,0.11486,0.28661]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.51113,0.03624,-0.00155],"force_p95":0.29471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33626,"mean_force":0.05958,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49858,0.03696,0.05277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6759.0,"contact_point_centroid":[0.50628,0.01872,0.12026],"force_p95":0.13932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32976,"mean_force":0.10234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50259,0.03706,0.12326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":901.0,"contact_point_centroid":[0.5057,0.05332,0.15905],"force_p95":0.18519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31928,"mean_force":0.10363,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49982,0.0355,0.16349]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8454.0,"contact_point_centroid":[0.50547,0.05532,0.11509],"force_p95":0.13489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31027,"mean_force":0.08724,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50223,0.03705,0.117]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":706.0,"contact_point_centroid":[0.50579,0.01727,0.15658],"force_p95":0.15548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28156,"mean_force":0.11429,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5,0.0356,0.16117]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51261,0.03953,-0.00222],"force_p95":0.18449,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23707,"mean_force":0.13826,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50076,0.03715,0.05229]},{"body_a":"world","body_b":"grasp_target","contact_count":424.0,"contact_point_centroid":[0.51251,0.03972,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1238,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50324,0.01208,0.26876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2895.0,"contact_point_centroid":[0.50214,0.01803,0.04967],"force_p95":0.10955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13793,"mean_force":0.07037,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49963,0.03706,0.05105]},{"body_a":"world","body_b":"grasp_target","contact_count":1292.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50657,0.03191,0.14666]},{"body_a":"world","body_b":"grasp_target","contact_count":2536.0,"contact_point_centroid":[0.51788,0.06576,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61702,0.16586,0.18373]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51788,0.06576,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61296,0.16621,0.15511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4900.0,"contact_point_centroid":[0.50031,0.05582,0.05119],"force_p95":0.08401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08744,"mean_force":0.04593,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49964,0.03706,0.05106]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4002.0,"contact_point_centroid":[0.57683,0.1188,0.29248],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01514,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5764,0.11878,0.29021]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2712.0,"contact_point_centroid":[0.61764,0.16591,0.18575],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61704,0.16587,0.18359]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.61651,0.16718,0.15392],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61587,0.16713,0.15171]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51788,0.06576,0.01602],"final_tcp_position":[0.6214,0.16878,0.16349],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.46696,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12236,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50691,0.0263,0.23294],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.508,0.03767,0.06072],"tcp_start":[0.50691,0.0263,0.23294],"tcp_to_object_dist_end":0.03505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51254,0.03773,0.02517],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21393,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18163,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9595.0,"raw_peak_contact_force":0.23707,"subtask_id":"grasp_1","tcp_end":[0.49961,0.03706,0.05101],"tcp_start":[0.508,0.03767,0.06072],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":344.0,"n_steps_budget":780.0,"object_pos_end":[0.50826,0.03719,0.11246],"object_pos_start":[0.51254,0.03773,0.02517],"object_to_goal_dist_end":0.18333,"object_to_goal_dist_start":0.21393,"object_z_max":0.1228,"peak_contact_force":0.11388,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15299.0,"raw_peak_contact_force":0.33626,"tcp_end":[0.50333,0.03704,0.14915],"tcp_start":[0.49961,0.03706,0.05101],"tcp_to_object_dist_end":0.03702,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":766.0,"n_steps_budget":1000.0,"object_pos_end":[0.51788,0.06576,0.01602],"object_pos_start":[0.50826,0.03719,0.11246],"object_to_goal_dist_end":0.20018,"object_to_goal_dist_start":0.18333,"object_z_max":0.14016,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9549.0,"raw_peak_contact_force":1.46696,"subtask_id":"transport_arc","tcp_end":[0.61165,0.15769,0.29772],"tcp_start":[0.50333,0.03704,0.14915],"tcp_to_object_dist_end":0.31081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.51788,0.06576,0.01602],"object_pos_start":[0.51788,0.06576,0.01602],"object_to_goal_dist_end":0.20018,"object_to_goal_dist_start":0.20018,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5248.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6173,0.16755,0.15471],"tcp_start":[0.61165,0.15769,0.29772],"tcp_to_object_dist_end":0.1987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51788,0.06576,0.01602],"object_pos_start":[0.51788,0.06576,0.01602],"object_to_goal_dist_end":0.20018,"object_to_goal_dist_start":0.20018,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61127,0.16566,0.1745],"tcp_start":[0.6173,0.16755,0.15471],"tcp_to_object_dist_end":0.20933,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13095,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08142,"descend_1.grasp_z_offset":0.01011,"lift_1.lift_height":0.17751,"transport_to_goal.arc_height":0.2224,"transport_to_goal.transport_height":0.17044,"transport_to_goal.transport_speed":0.16896},"optimized_scores":{"best_composite_score":0.08025,"best_fitness_score":0.53025,"best_task_score":0.13626},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4540.0,"contact_point_centroid":[0.48564,0.04412,-0.00223],"force_p95":0.12389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65603,"mean_force":0.13301,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52738,0.13741,0.36844]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.48091,0.04485,-0.0016],"force_p95":0.37842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43155,"mean_force":0.08771,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47018,0.04544,0.04858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1067.0,"contact_point_centroid":[0.47578,0.05859,0.19155],"force_p95":0.17005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42295,"mean_force":0.0907,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46953,0.04044,0.19292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":961.0,"contact_point_centroid":[0.4754,0.02198,0.19043],"force_p95":0.16856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30711,"mean_force":0.09765,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46956,0.04049,0.19271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12143.0,"contact_point_centroid":[0.47707,0.06454,0.13646],"force_p95":0.10355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28727,"mean_force":0.06995,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47358,0.04577,0.13581]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04857,-0.00225],"force_p95":0.19226,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25242,"mean_force":0.14066,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47234,0.04567,0.04802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11306.0,"contact_point_centroid":[0.47692,0.02693,0.13728],"force_p95":0.11814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24823,"mean_force":0.07407,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47364,0.04577,0.13703]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.4827,0.04873,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49188,0.01902,0.2221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4595.0,"contact_point_centroid":[0.47051,0.02631,0.04755],"force_p95":0.07712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13745,"mean_force":0.04699,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47126,0.04556,0.04691]},{"body_a":"world","body_b":"grasp_target","contact_count":644.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48051,0.04295,0.09769]},{"body_a":"world","body_b":"grasp_target","contact_count":2592.0,"contact_point_centroid":[0.48565,0.0441,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5751,0.22132,0.27283]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48565,0.0441,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57229,0.22217,0.24248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5576.0,"contact_point_centroid":[0.47059,0.06489,0.04785],"force_p95":0.07378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07811,"mean_force":0.04069,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47126,0.04556,0.04692]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4608.0,"contact_point_centroid":[0.53097,0.14266,0.37581],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01619,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53051,0.14264,0.37358]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2794.0,"contact_point_centroid":[0.57566,0.22138,0.27494],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57511,0.22133,0.27271]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.57516,0.22319,0.24093],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57426,0.22313,0.23873]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48565,0.0441,0.01602],"final_tcp_position":[0.57815,0.22483,0.24968],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.65603,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48348,0.0398,0.13964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":644.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47932,0.04628,0.05557],"tcp_start":[0.48348,0.0398,0.13964],"tcp_to_object_dist_end":0.02985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04666,0.0251],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29191,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18596,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11971.0,"raw_peak_contact_force":0.25242,"subtask_id":"grasp_1","tcp_end":[0.47123,0.04556,0.04688],"tcp_start":[0.47932,0.04628,0.05557],"tcp_to_object_dist_end":0.02465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":431.0,"n_steps_budget":990.0,"object_pos_end":[0.48111,0.04672,0.14653],"object_pos_start":[0.48271,0.04666,0.0251],"object_to_goal_dist_end":0.22444,"object_to_goal_dist_start":0.29191,"object_z_max":0.1566,"peak_contact_force":0.12664,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23530.0,"raw_peak_contact_force":0.43155,"tcp_end":[0.47458,0.04587,0.17802],"tcp_start":[0.47123,0.04556,0.04688],"tcp_to_object_dist_end":0.03217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.48565,0.0441,0.01602],"object_pos_start":[0.48111,0.04672,0.14653],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.22444,"object_z_max":0.18004,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11176.0,"raw_peak_contact_force":1.65603,"subtask_id":"transport_arc","tcp_end":[0.57092,0.2111,0.39122],"tcp_start":[0.47458,0.04587,0.17802],"tcp_to_object_dist_end":0.41945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.48565,0.0441,0.01602],"object_pos_start":[0.48565,0.0441,0.01602],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.29898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5386.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57527,0.22355,0.24149],"tcp_start":[0.57092,0.2111,0.39122],"tcp_to_object_dist_end":0.30178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48565,0.0441,0.01602],"object_pos_start":[0.48565,0.0441,0.01602],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.29898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57122,0.22161,0.26215],"tcp_start":[0.57527,0.22355,0.24149],"tcp_to_object_dist_end":0.3153,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92268,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17178,"descend_1.grasp_z_offset":0.01278,"lift_1.lift_height":0.16257,"transport_to_goal.arc_height":0.10304,"transport_to_goal.transport_height":0.22942,"transport_to_goal.transport_speed":0.11631},"optimized_scores":{"best_composite_score":0.06795,"best_fitness_score":0.51795,"best_task_score":0.11558},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5320.0,"contact_point_centroid":[0.54753,-0.02565,-0.00215],"force_p95":0.12361,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49004,"mean_force":0.13159,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54913,0.04852,0.34646]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.53531,-0.02006,-0.00139],"force_p95":0.32095,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37515,"mean_force":0.0715,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52151,-0.02019,0.04879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9574.0,"contact_point_centroid":[0.53116,-0.00152,0.12711],"force_p95":0.1344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26779,"mean_force":0.08284,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52632,-0.02031,0.12654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11159.0,"contact_point_centroid":[0.5312,-0.03883,0.12935],"force_p95":0.10767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26574,"mean_force":0.07291,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52645,-0.02031,0.12906]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02124,-0.00209],"force_p95":0.14953,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20257,"mean_force":0.12978,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52376,-0.02023,0.04873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4342.0,"contact_point_centroid":[0.52361,-0.00102,0.04866],"force_p95":0.07466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14288,"mean_force":0.0495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52258,-0.02021,0.04737]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.53702,-0.02132,-0.00173],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12369,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51129,-0.00674,0.2658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11.0,"contact_point_centroid":[0.53414,-0.0329,0.15569],"force_p95":0.12177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13219,"mean_force":0.0596,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52776,-0.02035,0.16282]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52668,-0.01744,0.14227]},{"body_a":"world","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.54755,-0.0256,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5942,0.18899,0.26575]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54755,-0.0256,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59703,0.21205,0.21271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4950.0,"contact_point_centroid":[0.52351,-0.03937,0.04858],"force_p95":0.07117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07289,"mean_force":0.04438,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52258,-0.02021,0.04737]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5424.0,"contact_point_centroid":[0.55069,0.05176,0.35559],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55027,0.05176,0.35326]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3456.0,"contact_point_centroid":[0.59476,0.18911,0.26784],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59422,0.18909,0.26556]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.60025,0.21305,0.21134],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00983,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59931,0.21302,0.20931]}],"total_contact_groups":15},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54755,-0.0256,0.01602],"final_tcp_position":[0.60372,0.21477,0.221],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.49004,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12249,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52399,-0.01458,0.22726],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53129,-0.02034,0.05792],"tcp_start":[0.52399,-0.01458,0.22726],"tcp_to_object_dist_end":0.03243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02055,0.02565],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31634,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14727,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11092.0,"raw_peak_contact_force":0.20257,"subtask_id":"grasp_1","tcp_end":[0.52255,-0.02021,0.04733],"tcp_start":[0.53129,-0.02034,0.05792],"tcp_to_object_dist_end":0.02604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":417.0,"n_steps_budget":900.0,"object_pos_end":[0.53625,-0.02563,0.12471],"object_pos_start":[0.53697,-0.02055,0.02565],"object_to_goal_dist_end":0.27664,"object_to_goal_dist_start":0.31634,"object_z_max":0.14159,"peak_contact_force":0.08381,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20815.0,"raw_peak_contact_force":0.37515,"tcp_end":[0.52789,-0.02035,0.16285],"tcp_start":[0.52255,-0.02021,0.04733],"tcp_to_object_dist_end":0.0394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54755,-0.0256,0.01602],"object_pos_start":[0.53625,-0.02563,0.12471],"object_to_goal_dist_end":0.32367,"object_to_goal_dist_start":0.27664,"object_z_max":0.12471,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10755.0,"raw_peak_contact_force":1.49004,"subtask_id":"transport_arc","tcp_end":[0.57283,0.11786,0.41388],"tcp_start":[0.52789,-0.02035,0.16285],"tcp_to_object_dist_end":0.42369,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.54755,-0.0256,0.01602],"object_pos_start":[0.54755,-0.0256,0.01602],"object_to_goal_dist_end":0.32367,"object_to_goal_dist_start":0.32367,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6668.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60045,0.21346,0.21228],"tcp_start":[0.57283,0.11786,0.41388],"tcp_to_object_dist_end":0.31379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54755,-0.0256,0.01602],"object_pos_start":[0.54755,-0.0256,0.01602],"object_to_goal_dist_end":0.32367,"object_to_goal_dist_start":0.32367,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59576,0.21147,0.23211],"tcp_start":[0.60045,0.21346,0.21228],"tcp_to_object_dist_end":0.32439,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```