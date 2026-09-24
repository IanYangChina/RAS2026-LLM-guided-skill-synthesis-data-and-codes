## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0966 | 0.24 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.1487 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 2 | 0.2823 | 0.23 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 1 | 0.2934 | 0.19 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.4470 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.097) — your mutation base

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

- **Composite score**: 0.097
- **task_score** (E): 0.238
- **fitness_score**: 0.497  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0766 |
| descend_1 | 1.00 | 1.00 | 0.1746 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.0931 |
| transport_to_goal | 1.00 | 1.00 | 0.2998 |
| descend_to_goal | 1.00 | 1.00 | 0.1506 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.011, 0.231) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.126 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.011, 0.231)→(0.506, 0.021, 0.057) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.126 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.057)→(0.498, 0.021, 0.047) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 42.333 | 0.172 | 0.235 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.047)→(0.501, 0.021, 0.140) | (0.511, 0.021, 0.025)→(0.508, 0.021, 0.110) | 0.274→0.233 | 1.00 / 26.000 | 0.121 | 0.391 |
| transport_to_goal | approach | 1.00 / step_budget | (0.501, 0.021, 0.140)→(0.599, 0.199, 0.355) | (0.508, 0.021, 0.110)→(0.563, 0.082, 0.016) | 0.233→0.228 | 1.00 / 8.333 | 0.123 | 1.559 |
| descend_to_goal | descend | 1.00 / step_budget | (0.599, 0.199, 0.355)→(0.599, 0.206, 0.205) | (0.563, 0.082, 0.016)→(0.563, 0.082, 0.016) | 0.228→0.228 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.599, 0.206, 0.205)→(0.595, 0.204, 0.225) | (0.563, 0.082, 0.016)→(0.563, 0.082, 0.016) | 0.228→0.228 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.196
- phase_score: 0.347
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.028
- phase_breakdown.release_1_score: 0.507
- phase_breakdown.transport_arc_score: 0.059
- phase_breakdown.descend_1_score: 0.873
- grasp_place_fitness: 0.560

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.560
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.372
- **Median Q (composite search score)**: 0.133
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.500


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82081,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24938,"descend_1.grasp_z_offset":0.01206,"lift_1.lift_height":0.07673,"transport_to_goal.transport_height":0.19761,"transport_to_goal.transport_speed":0.14431},"optimized_scores":{"best_composite_score":-0.00349,"best_fitness_score":0.39651,"best_task_score":0.37225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3492.0,"contact_point_centroid":[0.58512,0.11318,-0.0023],"force_p95":0.12706,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55915,"mean_force":0.13668,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60416,0.1495,0.28808]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.51137,0.03617,-0.00163],"force_p95":0.3026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35718,"mean_force":0.07794,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49886,0.03627,0.04895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10068.0,"contact_point_centroid":[0.50239,0.05545,0.07578],"force_p95":0.08591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2776,"mean_force":0.05512,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50138,0.03657,0.07475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4798.0,"contact_point_centroid":[0.52519,0.04409,0.12282],"force_p95":0.14057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26423,"mean_force":0.08601,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52225,0.06277,0.12466]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51262,0.03954,-0.00226],"force_p95":0.19563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25352,"mean_force":0.14143,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5006,0.03641,0.04864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9245.0,"contact_point_centroid":[0.5019,0.01748,0.07563],"force_p95":0.10281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24664,"mean_force":0.06136,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50138,0.03657,0.075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6094.0,"contact_point_centroid":[0.52743,0.0822,0.12691],"force_p95":0.10925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22003,"mean_force":0.06843,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52336,0.06397,0.12693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4084.0,"contact_point_centroid":[0.50005,0.01715,0.04863],"force_p95":0.08148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1534,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49947,0.03632,0.04739]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.51251,0.03972,-0.00108],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12245,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50128,0.00507,0.29666]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.51251,0.03972,-0.002],"force_p95":0.12457,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1336,"mean_force":0.12292,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50502,0.02521,0.17377]},{"body_a":"world","body_b":"grasp_target","contact_count":2616.0,"contact_point_centroid":[0.58513,0.11312,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61945,0.1684,0.1889]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58513,0.11312,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61429,0.16762,0.1557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4917.0,"contact_point_centroid":[0.50032,0.05563,0.04862],"force_p95":0.08104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08519,"mean_force":0.04567,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49948,0.03632,0.0474]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3495.0,"contact_point_centroid":[0.607,0.15201,0.29489],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01563,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60652,0.15199,0.29267]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2792.0,"contact_point_centroid":[0.62003,0.16844,0.19133],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61945,0.1684,0.18913]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.61788,0.16858,0.15467],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61717,0.16853,0.15228]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.58513,0.11312,0.01602],"final_tcp_position":[0.62272,0.1702,0.16418],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.55915,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":37.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02615],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21214,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.13411,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":144.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50369,0.01371,0.29052],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02615],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21214,"object_z_max":0.02615,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.1336,"subtask_id":"descend_1","tcp_end":[0.50784,0.0369,0.05701],"tcp_start":[0.50369,0.01371,0.29052],"tcp_to_object_dist_end":0.03147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51253,0.03752,0.02507],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21412,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1887,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10801.0,"raw_peak_contact_force":0.25352,"subtask_id":"grasp_1","tcp_end":[0.49944,0.03632,0.04736],"tcp_start":[0.50784,0.0369,0.05701],"tcp_to_object_dist_end":0.02587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":140.0,"n_steps_budget":600.0,"object_pos_end":[0.50694,0.03776,0.05002],"object_pos_start":[0.51253,0.03752,0.02507],"object_to_goal_dist_end":0.2043,"object_to_goal_dist_start":0.21412,"object_z_max":0.06,"peak_contact_force":0.11284,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19413.0,"raw_peak_contact_force":0.35718,"tcp_end":[0.50075,0.03654,0.07794],"tcp_start":[0.49944,0.03632,0.04736],"tcp_to_object_dist_end":0.02863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58513,0.11312,0.01602],"object_pos_start":[0.50694,0.03776,0.05002],"object_to_goal_dist_end":0.14823,"object_to_goal_dist_start":0.2043,"object_z_max":0.15178,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17879.0,"raw_peak_contact_force":1.55915,"subtask_id":"transport_arc","tcp_end":[0.61836,0.16506,0.31354],"tcp_start":[0.50075,0.03654,0.07794],"tcp_to_object_dist_end":0.30384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.58513,0.11312,0.01602],"object_pos_start":[0.58513,0.11312,0.01602],"object_to_goal_dist_end":0.14823,"object_to_goal_dist_start":0.14823,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5408.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61862,0.16896,0.15535],"tcp_start":[0.61836,0.16506,0.31354],"tcp_to_object_dist_end":0.15379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58513,0.11312,0.01602],"object_pos_start":[0.58513,0.11312,0.01602],"object_to_goal_dist_end":0.14823,"object_to_goal_dist_start":0.14823,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6126,0.16706,0.17507],"tcp_start":[0.61862,0.16896,0.15535],"tcp_to_object_dist_end":0.17018,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48498,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15229,"descend_1.grasp_z_offset":0.01006,"lift_1.lift_height":0.18306,"transport_to_goal.transport_height":0.16855,"transport_to_goal.transport_speed":0.05705},"optimized_scores":{"best_composite_score":0.16018,"best_fitness_score":0.56018,"best_task_score":0.19569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.54664,0.11642,-0.00236],"force_p95":0.12558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59705,"mean_force":0.1369,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5612,0.1958,0.35042]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.4806,0.04509,-0.00159],"force_p95":0.39141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43368,"mean_force":0.08971,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47033,0.04565,0.04851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.49788,0.09724,0.21637],"force_p95":0.14153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3017,"mean_force":0.08848,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49171,0.07903,0.21812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12353.0,"contact_point_centroid":[0.47716,0.06471,0.13925],"force_p95":0.10415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28434,"mean_force":0.07012,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47366,0.04593,0.1386]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04857,-0.00224],"force_p95":0.1884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24946,"mean_force":0.13976,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47249,0.04587,0.04799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11625.0,"contact_point_centroid":[0.477,0.02709,0.14024],"force_p95":0.1152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24854,"mean_force":0.0736,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47372,0.04593,0.13999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3859.0,"contact_point_centroid":[0.49824,0.06242,0.21715],"force_p95":0.12733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18527,"mean_force":0.09459,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49272,0.08072,0.2201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4605.0,"contact_point_centroid":[0.47064,0.02652,0.04741],"force_p95":0.07677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13957,"mean_force":0.0469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47141,0.04577,0.04688]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.4827,0.04873,-0.00177],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49318,0.01662,0.25656]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48172,0.04096,0.13212]},{"body_a":"world","body_b":"grasp_target","contact_count":2448.0,"contact_point_centroid":[0.54666,0.11645,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57593,0.22343,0.26661]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54666,0.11645,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5726,0.22302,0.24258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5579.0,"contact_point_centroid":[0.47072,0.06509,0.04772],"force_p95":0.07283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07699,"mean_force":0.04058,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47142,0.04577,0.04688]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3612.0,"contact_point_centroid":[0.5632,0.19835,0.35544],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5627,0.19832,0.35321]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2612.0,"contact_point_centroid":[0.57649,0.22348,0.26874],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57593,0.22343,0.26657]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.57519,0.22403,0.24111],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57454,0.22396,0.23876]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54666,0.11645,0.01602],"final_tcp_position":[0.57845,0.22568,0.24983],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.59705,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48563,0.03563,0.20854],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47947,0.04649,0.05554],"tcp_start":[0.48563,0.03563,0.20854],"tcp_to_object_dist_end":0.02978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04678,0.02515],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2918,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18235,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11984.0,"raw_peak_contact_force":0.24946,"subtask_id":"grasp_1","tcp_end":[0.47139,0.04577,0.04685],"tcp_start":[0.47947,0.04649,0.05554],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.48126,0.04685,0.15212],"object_pos_start":[0.48271,0.04678,0.02515],"object_to_goal_dist_end":0.22224,"object_to_goal_dist_start":0.2918,"object_z_max":0.16214,"peak_contact_force":0.12338,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24058.0,"raw_peak_contact_force":0.43368,"tcp_end":[0.47472,0.04601,0.18359],"tcp_start":[0.47139,0.04577,0.04685],"tcp_to_object_dist_end":0.03216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54666,0.11645,0.01602],"object_pos_start":[0.48126,0.04685,0.15212],"object_to_goal_dist_end":0.24469,"object_to_goal_dist_start":0.22224,"object_z_max":0.22647,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15241.0,"raw_peak_contact_force":1.59705,"subtask_id":"transport_arc","tcp_end":[0.57396,0.21769,0.37139],"tcp_start":[0.47472,0.04601,0.18359],"tcp_to_object_dist_end":0.37051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.54666,0.11645,0.01602],"object_pos_start":[0.54666,0.11645,0.01602],"object_to_goal_dist_end":0.24469,"object_to_goal_dist_start":0.24469,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5060.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57557,0.2244,0.24161],"tcp_start":[0.57396,0.21769,0.37139],"tcp_to_object_dist_end":0.25176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54666,0.11645,0.01602],"object_pos_start":[0.54666,0.11645,0.01602],"object_to_goal_dist_end":0.24469,"object_to_goal_dist_start":0.24469,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57153,0.22247,0.26223],"tcp_start":[0.57557,0.2244,0.24161],"tcp_to_object_dist_end":0.26922,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15789,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13602,"descend_1.grasp_z_offset":0.0123,"lift_1.lift_height":0.15808,"transport_to_goal.transport_height":0.20292,"transport_to_goal.transport_speed":0.17547},"optimized_scores":{"best_composite_score":0.13317,"best_fitness_score":0.53317,"best_task_score":0.14483},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4969.0,"contact_point_centroid":[0.55587,0.01701,-0.00217],"force_p95":0.12369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52008,"mean_force":0.13143,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58267,0.14939,0.32131]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.5353,-0.02005,-0.00137],"force_p95":0.32552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38204,"mean_force":0.07043,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52139,-0.02023,0.0482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":511.0,"contact_point_centroid":[0.53498,0.00534,0.16126],"force_p95":0.2285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29128,"mean_force":0.12639,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52854,-0.01319,0.16333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10222.0,"contact_point_centroid":[0.53125,-0.00155,0.12726],"force_p95":0.10994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26889,"mean_force":0.07794,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52636,-0.02034,0.12654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11159.0,"contact_point_centroid":[0.53114,-0.03904,0.12726],"force_p95":0.10283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26606,"mean_force":0.07246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52639,-0.02034,0.12677]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02123,-0.00209],"force_p95":0.14862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20206,"mean_force":0.1296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52362,-0.02028,0.04813]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":791.0,"contact_point_centroid":[0.53493,-0.02919,0.16216],"force_p95":0.1384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19846,"mean_force":0.08404,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52892,-0.01145,0.16471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4341.0,"contact_point_centroid":[0.52354,-0.00107,0.04827],"force_p95":0.07478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14272,"mean_force":0.04949,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52244,-0.02025,0.04677]},{"body_a":"world","body_b":"grasp_target","contact_count":640.0,"contact_point_centroid":[0.53702,-0.02132,-0.0018],"force_p95":0.13763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12339,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51229,-0.00754,0.24874]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52764,-0.0182,0.12494]},{"body_a":"world","body_b":"grasp_target","contact_count":2644.0,"contact_point_centroid":[0.55589,0.01702,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60509,0.22182,0.25303]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55589,0.01702,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60071,0.22182,0.218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4948.0,"contact_point_centroid":[0.52343,-0.03941,0.04816],"force_p95":0.07111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07279,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52245,-0.02025,0.04677]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5031.0,"contact_point_centroid":[0.58515,0.15544,0.32953],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58476,0.15544,0.32729]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2833.0,"contact_point_centroid":[0.6057,0.22186,0.2551],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60509,0.22183,0.25285]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.60364,0.22285,0.21672],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60291,0.22281,0.21473]}],"total_contact_groups":16},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55589,0.01702,0.01602],"final_tcp_position":[0.6072,0.22459,0.22668],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.52008,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":640.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52611,-0.01606,0.1929],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53116,-0.02039,0.05731],"tcp_start":[0.52611,-0.01606,0.1929],"tcp_to_object_dist_end":0.03185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02057,0.02566],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31635,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14637,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11089.0,"raw_peak_contact_force":0.20206,"subtask_id":"grasp_1","tcp_end":[0.52241,-0.02025,0.04673],"tcp_start":[0.53116,-0.02039,0.05731],"tcp_to_object_dist_end":0.02562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":404.0,"n_steps_budget":870.0,"object_pos_end":[0.53469,-0.02028,0.12743],"object_pos_start":[0.53697,-0.02057,0.02566],"object_to_goal_dist_end":0.27136,"object_to_goal_dist_start":0.31635,"object_z_max":0.13788,"peak_contact_force":0.12541,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21463.0,"raw_peak_contact_force":0.38204,"tcp_end":[0.52775,-0.02037,0.15837],"tcp_start":[0.52241,-0.02025,0.04673],"tcp_to_object_dist_end":0.0317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55589,0.01702,0.01602],"object_pos_start":[0.53469,-0.02028,0.12743],"object_to_goal_dist_end":0.28983,"object_to_goal_dist_start":0.27136,"object_z_max":0.13972,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11302.0,"raw_peak_contact_force":1.52008,"subtask_id":"transport_arc","tcp_end":[0.60513,0.2149,0.38128],"tcp_start":[0.52775,-0.02037,0.15837],"tcp_to_object_dist_end":0.41832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.55589,0.01702,0.01602],"object_pos_start":[0.55589,0.01702,0.01602],"object_to_goal_dist_end":0.28983,"object_to_goal_dist_start":0.28983,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5477.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60403,0.22326,0.21777],"tcp_start":[0.60513,0.2149,0.38128],"tcp_to_object_dist_end":0.2925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55589,0.01702,0.01602],"object_pos_start":[0.55589,0.01702,0.01602],"object_to_goal_dist_end":0.28983,"object_to_goal_dist_start":0.28983,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59948,0.22124,0.2373],"tcp_start":[0.60403,0.22326,0.21777],"tcp_to_object_dist_end":0.30426,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```