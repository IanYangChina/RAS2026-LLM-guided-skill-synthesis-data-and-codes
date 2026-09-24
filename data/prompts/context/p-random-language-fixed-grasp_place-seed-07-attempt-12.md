## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3672 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3920 | 0.26 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | 16 | -0.1848 | 0.52 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0176 | 0.85 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3643 | 0.33 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.367) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
  target_entity: None
- id: descend_1
  anchor: object
  target_entity: None
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  target_entity: None
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
  target_entity: None
- id: release_1
  target_entity: None
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
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
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
    orientation:
      mode: none
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    tolerance: 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
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
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    lift_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: abort
  retries:
    max_attempts: 0
    strategy: repeat
- id: transport_arc
  type: approach
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
      tolerance: 0.1
  parameters:
    transport_altitude:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: transport_grasp_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: continue
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: transport_arc
- id: place_1
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
      tolerance: 0.1
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.0
  - retries: max_attempts=0, strategy=repeat
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_altitude: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=transport_grasp_guard, when=during_phase, predicate=bilateral_grasp, on_failure=continue, threshold=0.0
  - retries: max_attempts=0, strategy=repeat
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]

## Design Metrics

- **Composite score**: -0.367
- **task_score** (E): 0.308
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0728 |
| descend_1 | 1.00 | 1.00 | 0.2065 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1263 |
| transport_arc | 0.00 | 1.00 | 0.1107 |
| place_1 | 0.33 | 1.00 | 0.1209 |
| release_1 | 1.00 | 1.00 | 0.0145 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.241) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.019, 0.241)→(0.506, 0.022, 0.035) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.035)→(0.497, 0.021, 0.026) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.149 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.021, 0.026)→(0.494, 0.021, 0.152) | (0.511, 0.022, 0.026)→(0.508, 0.021, 0.147) | 0.274→0.228 | 1.00 / 33.333 | 0.091 | 0.674 |
| transport_arc | approach | 0.00 / step_budget | (0.494, 0.021, 0.152)→(0.530, 0.088, 0.230) | (0.508, 0.021, 0.147)→(0.527, 0.075, 0.142) | 0.228→0.188 | 1.00 / 23.333 | 0.119 | 0.654 |
| place_1 | descend | 0.33 / step_budget | (0.530, 0.088, 0.230)→(0.584, 0.174, 0.193) | (0.527, 0.075, 0.142)→(0.552, 0.119, 0.037) | 0.188→0.196 | 1.00 / 19.000 | 0.109 | 0.816 |
| release_1 | approach | 1.00 / step_budget | (0.584, 0.174, 0.193)→(0.578, 0.172, 0.180) | (0.552, 0.119, 0.037)→(0.549, 0.118, 0.031) | 0.196→0.202 | 1.00 / 18.000 | 0.113 | 0.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.567
- phase_score: 0.299
- phase_breakdown.approach_1_score: 0.041
- phase_breakdown.transport_arc_score: 0.054
- phase_breakdown.release_1_score: 0.301
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.726
- grasp_place_fitness: 0.762

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.762
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: -0.417
- **K-run variance**: 0.0085
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40097,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1522,"approach_1.approach_tol":0.03645,"approach_1.speed":0.06594,"descend_1.descend_speed":0.08858,"descend_1.descend_tol":0.02399,"descend_1.grasp_z_offset":0.00027,"grasp_1.grasp_duration":2.1838,"lift_1.lift_height":0.17804,"lift_1.lift_speed":0.05694,"lift_1.lift_tol":0.02083,"place_1.place_speed":0.1811,"place_1.place_tol":0.03827,"place_1.place_z_offset":-0.03806,"release_1.hold_duration":1.7894,"transport_arc.transport_altitude":0.16297,"transport_arc.transport_speed":0.03636,"transport_arc.transport_tol":0.02273},"optimized_scores":{"best_composite_score":-0.23755,"best_fitness_score":0.76245,"best_task_score":0.56732},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50942,0.03778,-0.00148],"force_p95":0.55436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68432,"mean_force":0.17566,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49798,0.03815,0.02711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10566.0,"contact_point_centroid":[0.49602,0.05701,0.10313],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32076,"mean_force":0.05452,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49544,0.03795,0.10102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10050.0,"contact_point_centroid":[0.49612,0.01884,0.10756],"force_p95":0.08218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3068,"mean_force":0.05625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49544,0.03795,0.10507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11620.0,"contact_point_centroid":[0.5831,0.11208,0.15359],"force_p95":0.09542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26646,"mean_force":0.0654,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58311,0.13126,0.1523]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03937,-0.00213],"force_p95":0.16169,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24602,"mean_force":0.13315,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50032,0.03836,0.0271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14278.0,"contact_point_centroid":[0.58325,0.14934,0.15378],"force_p95":0.07485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22122,"mean_force":0.05164,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58243,0.13057,0.15325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7929.0,"contact_point_centroid":[0.61382,0.1474,0.0914],"force_p95":0.08631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19288,"mean_force":0.05771,"phase_index":6.0,"phase_name":"release_1","phase_type":"approach","tcp_position_centroid":[0.61328,0.16662,0.08976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10109.0,"contact_point_centroid":[0.61391,0.18553,0.09062],"force_p95":0.06774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18045,"mean_force":0.04367,"phase_index":6.0,"phase_name":"release_1","phase_type":"approach","tcp_position_centroid":[0.61316,0.16658,0.08955]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4054.0,"contact_point_centroid":[0.49979,0.01906,0.02863],"force_p95":0.08103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14565,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49913,0.03826,0.02583]},{"body_a":"world","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50273,0.01702,0.24463]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50627,0.03692,0.11144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18982.0,"contact_point_centroid":[0.51802,0.04408,0.20324],"force_p95":0.07826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09366,"mean_force":0.05249,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51749,0.06319,0.20201]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.49975,0.05743,0.02764],"force_p95":0.07349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08708,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03826,0.02584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19562.0,"contact_point_centroid":[0.51888,0.08307,0.20365],"force_p95":0.07479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08479,"mean_force":0.05092,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51826,0.064,0.2027]}],"total_contact_groups":14},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60895,0.16618,0.06231],"final_tcp_position":[0.62006,0.1685,0.10174],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.68432,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1560.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50766,0.03511,0.18945],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1940.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5074,0.03894,0.03482],"tcp_start":[0.50766,0.03511,0.18945],"tcp_to_object_dist_end":0.01021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03824,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21347,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1529,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.24602,"subtask_id":"grasp_1","tcp_end":[0.4991,0.03825,0.0258],"tcp_start":[0.5074,0.03894,0.03482],"tcp_to_object_dist_end":0.0133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.50814,0.03808,0.17837],"object_pos_start":[0.51239,0.03824,0.02556],"object_to_goal_dist_end":0.18289,"object_to_goal_dist_start":0.21347,"object_z_max":0.1781,"peak_contact_force":0.07992,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20702.0,"raw_peak_contact_force":0.68432,"tcp_end":[0.49569,0.03797,0.18416],"tcp_start":[0.4991,0.03825,0.0258],"tcp_to_object_dist_end":0.01374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54615,0.08457,0.20626],"object_pos_start":[0.50814,0.03808,0.17837],"object_to_goal_dist_end":0.13459,"object_to_goal_dist_start":0.18289,"object_z_max":0.20622,"peak_contact_force":0.07824,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38544.0,"raw_peak_contact_force":0.09366,"subtask_id":"transport_arc","tcp_end":[0.53856,0.08461,0.22099],"tcp_start":[0.49569,0.03797,0.18416],"tcp_to_object_dist_end":0.01658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.61532,0.16849,0.07898],"object_pos_start":[0.54615,0.08457,0.20626],"object_to_goal_dist_end":0.06729,"object_to_goal_dist_start":0.13459,"object_z_max":0.20626,"peak_contact_force":0.08042,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":25898.0,"raw_peak_contact_force":0.26646,"tcp_end":[0.62006,0.1685,0.10174],"tcp_start":[0.53856,0.08461,0.22099],"tcp_to_object_dist_end":0.02325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60895,0.16618,0.06231],"object_pos_start":[0.61532,0.16849,0.07898],"object_to_goal_dist_end":0.08502,"object_to_goal_dist_start":0.06729,"object_z_max":0.07898,"peak_contact_force":0.09293,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18038.0,"raw_peak_contact_force":0.19288,"subtask_id":"release_1","tcp_end":[0.61194,0.16623,0.08742],"tcp_start":[0.62006,0.1685,0.10174],"tcp_to_object_dist_end":0.02529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3373,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23854,"approach_1.approach_tol":0.02055,"approach_1.speed":0.0929,"descend_1.descend_speed":0.07943,"descend_1.descend_tol":0.01947,"descend_1.grasp_z_offset":0.00092,"grasp_1.grasp_duration":1.42739,"lift_1.lift_height":0.14158,"lift_1.lift_speed":0.03185,"lift_1.lift_tol":0.01559,"place_1.place_speed":0.03735,"place_1.place_tol":0.03506,"place_1.place_z_offset":0.04306,"release_1.hold_duration":1.6775,"transport_arc.transport_altitude":0.17148,"transport_arc.transport_speed":0.07834,"transport_arc.transport_tol":0.03046},"optimized_scores":{"best_composite_score":-0.41716,"best_fitness_score":0.58284,"best_task_score":0.20552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2663.0,"contact_point_centroid":[0.51569,0.15178,-0.00243],"force_p95":0.12519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05856,"mean_force":0.14136,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.52911,0.15212,0.23681]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47859,0.04645,-0.00165],"force_p95":0.5419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56397,"mean_force":0.25412,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46929,0.04683,0.0286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8345.0,"contact_point_centroid":[0.46702,0.06575,0.08878],"force_p95":0.07894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26822,"mean_force":0.05279,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46684,0.04659,0.08696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2463.0,"contact_point_centroid":[0.50845,0.13334,0.21939],"force_p95":0.14019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25821,"mean_force":0.09408,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.50545,0.11548,0.22401]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04843,-0.00216],"force_p95":0.1692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2536,"mean_force":0.13522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4715,0.04706,0.02884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14734.0,"contact_point_centroid":[0.4838,0.09317,0.18488],"force_p95":0.10405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2464,"mean_force":0.06772,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48113,0.07422,0.18358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15550.0,"contact_point_centroid":[0.48357,0.05545,0.18469],"force_p95":0.10628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23245,"mean_force":0.06388,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48114,0.07424,0.1836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.50798,0.09657,0.21939],"force_p95":0.14928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23212,"mean_force":0.09636,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.50496,0.11466,0.2238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8338.0,"contact_point_centroid":[0.46705,0.02744,0.08898],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.232,"mean_force":0.05187,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46684,0.04659,0.08701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5003.0,"contact_point_centroid":[0.47017,0.02771,0.03058],"force_p95":0.07035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15323,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04695,0.02771]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.4827,0.04873,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49132,0.01858,0.28427]},{"body_a":"world","body_b":"grasp_target","contact_count":2988.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47981,0.0432,0.15126]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51558,0.1518,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"approach","tcp_position_centroid":[0.53801,0.17068,0.23471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5539.0,"contact_point_centroid":[0.46998,0.0663,0.02995],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08366,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04695,0.02772]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2645.0,"contact_point_centroid":[0.53056,0.15354,0.23961],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01053,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.53004,0.15352,0.23734]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1936.0,"contact_point_centroid":[0.53861,0.17071,0.23692],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01037,"phase_index":6.0,"phase_name":"release_1","phase_type":"approach","tcp_position_centroid":[0.53801,0.17068,0.23471]}],"total_contact_groups":16},"final_pose_error":0.07516,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51558,0.1518,0.01602],"final_tcp_position":[0.5423,0.17201,0.24435],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.05856,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48347,0.03884,0.26959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2988.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47827,0.04772,0.03573],"tcp_start":[0.48347,0.03884,0.26959],"tcp_to_object_dist_end":0.01072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04714,0.02544],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29141,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16144,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12342.0,"raw_peak_contact_force":0.2536,"subtask_id":"grasp_1","tcp_end":[0.47035,0.04695,0.02768],"tcp_start":[0.47827,0.04772,0.03573],"tcp_to_object_dist_end":0.01246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.47733,0.04668,0.14526],"object_pos_start":[0.4826,0.04714,0.02544],"object_to_goal_dist_end":0.22667,"object_to_goal_dist_start":0.29141,"object_z_max":0.14497,"peak_contact_force":0.07683,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16775.0,"raw_peak_contact_force":0.56397,"tcp_end":[0.4668,0.04659,0.14965],"tcp_start":[0.47035,0.04695,0.02768],"tcp_to_object_dist_end":0.01141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51261,0.10392,0.20506],"object_pos_start":[0.47733,0.04668,0.14526],"object_to_goal_dist_end":0.14509,"object_to_goal_dist_start":0.22667,"object_z_max":0.20505,"peak_contact_force":0.15599,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30284.0,"raw_peak_contact_force":0.2464,"subtask_id":"transport_arc","tcp_end":[0.50003,0.10387,0.22395],"tcp_start":[0.4668,0.04659,0.14965],"tcp_to_object_dist_end":0.02269,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51558,0.1518,0.01602],"object_pos_start":[0.51261,0.10392,0.20506],"object_to_goal_dist_end":0.23733,"object_to_goal_dist_start":0.14509,"object_z_max":0.20506,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10007.0,"raw_peak_contact_force":2.05856,"tcp_end":[0.5423,0.17201,0.24435],"tcp_start":[0.50003,0.10387,0.22395],"tcp_to_object_dist_end":0.23077,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51558,0.1518,0.01602],"object_pos_start":[0.51558,0.1518,0.01602],"object_to_goal_dist_end":0.23733,"object_to_goal_dist_start":0.23733,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53722,0.17042,0.23296],"tcp_start":[0.5423,0.17201,0.24435],"tcp_to_object_dist_end":0.21881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3615,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23488,"approach_1.approach_tol":0.02727,"approach_1.speed":0.12461,"descend_1.descend_speed":0.01391,"descend_1.descend_tol":0.03927,"descend_1.grasp_z_offset":6e-05,"grasp_1.grasp_duration":0.80564,"lift_1.lift_height":0.11786,"lift_1.lift_speed":0.16568,"lift_1.lift_tol":0.03976,"place_1.place_speed":0.07297,"place_1.place_tol":0.02797,"place_1.place_z_offset":0.03336,"release_1.hold_duration":2.11112,"transport_arc.transport_altitude":0.243,"transport_arc.transport_speed":0.19578,"transport_arc.transport_tol":0.03023},"optimized_scores":{"best_composite_score":-0.44683,"best_fitness_score":0.55317,"best_task_score":0.15095},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2162.0,"contact_point_centroid":[0.52448,0.03733,-0.00241],"force_p95":0.17287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62116,"mean_force":0.14809,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54193,0.05072,0.21084]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.53349,-0.02028,-0.00134],"force_p95":0.72908,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77494,"mean_force":0.1666,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52163,-0.02083,0.0257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4445.0,"contact_point_centroid":[0.52205,-0.00184,0.06993],"force_p95":0.11166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35761,"mean_force":0.07418,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51917,-0.02077,0.06751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.52217,-0.03959,0.06789],"force_p95":0.10849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33237,"mean_force":0.06949,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51921,-0.02077,0.06619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3336.0,"contact_point_centroid":[0.52749,-0.02121,0.1416],"force_p95":0.1847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32073,"mean_force":0.10755,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52226,-0.00271,0.14161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4005.0,"contact_point_centroid":[0.52783,0.01636,0.14196],"force_p95":0.16513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30651,"mean_force":0.09826,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52254,-0.00183,0.1427]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02112,-0.00204],"force_p95":0.13596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17731,"mean_force":0.12645,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52421,-0.02087,0.0258]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51313,-0.00876,0.28137]},{"body_a":"world","body_b":"grasp_target","contact_count":3032.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52845,-0.01929,0.14813]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52368,0.03721,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5717,0.13479,0.2359]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.52368,0.03721,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"approach","tcp_position_centroid":[0.58544,0.18057,0.22245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.52383,-0.00165,0.02713],"force_p95":0.07686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11327,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52297,-0.02085,0.0244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.52383,-0.03994,0.02621],"force_p95":0.06889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0932,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52297,-0.02085,0.0244]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2123.0,"contact_point_centroid":[0.54311,0.05302,0.21616],"force_p95":0.01143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54281,0.05302,0.21386]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4281.0,"contact_point_centroid":[0.57222,0.13486,0.23816],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01042,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57173,0.13485,0.23589]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1942.0,"contact_point_centroid":[0.58614,0.18059,0.22468],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01035,"phase_index":6.0,"phase_name":"release_1","phase_type":"approach","tcp_position_centroid":[0.58544,0.18057,0.22245]}],"total_contact_groups":16},"final_pose_error":0.05063,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52368,0.03721,0.01602],"final_tcp_position":[0.58994,0.18195,0.2337],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.62116,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":904.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52784,-0.01764,0.26486],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":758.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3032.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53159,-0.021,0.03423],"tcp_start":[0.52784,-0.01764,0.26486],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02073,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13286,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10802.0,"raw_peak_contact_force":0.17731,"subtask_id":"grasp_1","tcp_end":[0.52294,-0.02085,0.02437],"tcp_start":[0.53159,-0.021,0.03423],"tcp_to_object_dist_end":0.01401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.53928,-0.02075,0.11731],"object_pos_start":[0.53688,-0.02073,0.02584],"object_to_goal_dist_end":0.27371,"object_to_goal_dist_start":0.31639,"object_z_max":0.11706,"peak_contact_force":0.11577,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9361.0,"raw_peak_contact_force":0.77494,"tcp_end":[0.51896,-0.02076,0.12266],"tcp_start":[0.52294,-0.02085,0.02437],"tcp_to_object_dist_end":0.02101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52368,0.03721,0.01602],"object_pos_start":[0.53928,-0.02075,0.11731],"object_to_goal_dist_end":0.28363,"object_to_goal_dist_start":0.27371,"object_z_max":0.14239,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11626.0,"raw_peak_contact_force":1.62116,"subtask_id":"transport_arc","tcp_end":[0.55177,0.07637,0.2445],"tcp_start":[0.51896,-0.02076,0.12266],"tcp_to_object_dist_end":0.23351,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52368,0.03721,0.01602],"object_pos_start":[0.52368,0.03721,0.01602],"object_to_goal_dist_end":0.28363,"object_to_goal_dist_start":0.28363,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8281.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58994,0.18195,0.2337],"tcp_start":[0.55177,0.07637,0.2445],"tcp_to_object_dist_end":0.26967,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52368,0.03721,0.01602],"object_pos_start":[0.52368,0.03721,0.01602],"object_to_goal_dist_end":0.28363,"object_to_goal_dist_start":0.28363,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3742.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58462,0.18029,0.22041],"tcp_start":[0.58994,0.18195,0.2337],"tcp_to_object_dist_end":0.25683,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```