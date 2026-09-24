## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | 16 | -0.1848 | 0.52 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0176 | 0.85 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3643 | 0.33 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.1693 | 0.71 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3888 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.185) — your mutation base

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

- **Composite score**: -0.185
- **task_score** (E): 0.515
- **fitness_score**: 0.735  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.920

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0512 |
| descend_1 | 1.00 | 1.00 | 0.2330 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1991 |
| transport_arc | 1.00 | 1.00 | 0.1409 |
| place_1 | 1.00 | 1.00 | 0.1173 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.018, 0.271) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.018, 0.271)→(0.506, 0.022, 0.038) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.038)→(0.498, 0.021, 0.029) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.148 | 0.219 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.029)→(0.495, 0.021, 0.228) | (0.511, 0.022, 0.026)→(0.505, 0.021, 0.219) | 0.274→0.219 | 1.00 / 39.000 | 0.053 | 0.560 |
| transport_arc | approach | 1.00 / time_limit | (0.495, 0.021, 0.228)→(0.552, 0.130, 0.294) | (0.505, 0.021, 0.219)→(0.560, 0.130, 0.271) | 0.219→0.129 | 1.00 / 23.333 | 0.130 | 0.197 |
| place_1 | descend | 1.00 / step_budget | (0.552, 0.130, 0.294)→(0.601, 0.204, 0.231) | (0.560, 0.130, 0.271)→(0.601, 0.195, 0.095) | 0.129→0.116 | 1.00 / 14.667 | 91003.532 | 1.221 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.850
- phase_score: 0.269
- phase_breakdown.approach_1_score: 0.008
- phase_breakdown.transport_arc_score: 0.063
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.834
- grasp_place_fitness: 0.901

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.901
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.850
- **Median Q (composite search score)**: -0.230
- **K-run variance**: 0.0147
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.337


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.125,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27699,"approach_1.approach_tol":0.01394,"approach_1.speed":0.14635,"descend_1.descend_speed":0.27169,"descend_1.descend_tol":0.01962,"descend_1.grasp_z_offset":0.0038,"grasp_1.grasp_duration":1.63134,"lift_1.lift_height":0.16263,"lift_1.lift_speed":0.01659,"lift_1.lift_tol":0.01127,"place_1.place_speed":0.24841,"place_1.place_tol":0.04732,"place_1.place_z_offset":0.03209,"transport_arc.transport_altitude":0.22433,"transport_arc.transport_max_time":5.69281,"transport_arc.transport_speed":0.08023},"optimized_scores":{"best_composite_score":-0.23039,"best_fitness_score":0.68961,"best_task_score":0.42281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":486.0,"contact_point_centroid":[0.62623,0.1669,-0.00387],"force_p95":0.76575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66925,"mean_force":0.21127,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61615,0.16385,0.17156]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.50835,0.03802,-0.0016],"force_p95":0.47742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51159,"mean_force":0.22376,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.498,0.03823,0.03005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7316.0,"contact_point_centroid":[0.56693,0.09203,0.19257],"force_p95":0.16271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28562,"mean_force":0.09768,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56253,0.11058,0.19421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10799.0,"contact_point_centroid":[0.49541,0.05714,0.09914],"force_p95":0.07613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25614,"mean_force":0.05128,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49548,0.03803,0.0972]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10095.0,"contact_point_centroid":[0.49555,0.01886,0.09947],"force_p95":0.07932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24743,"mean_force":0.05352,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49548,0.03803,0.09693]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8740.0,"contact_point_centroid":[0.57076,0.13186,0.19205],"force_p95":0.11479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24177,"mean_force":0.0794,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56577,0.11381,0.19281]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03943,-0.00213],"force_p95":0.15969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23809,"mean_force":0.1325,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03844,0.03049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16184.0,"contact_point_centroid":[0.50977,0.03467,0.19168],"force_p95":0.0923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15115,"mean_force":0.06097,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50785,0.05362,0.19023]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4064.0,"contact_point_centroid":[0.49985,0.01914,0.032],"force_p95":0.08073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14613,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49924,0.03834,0.02921]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.51251,0.03972,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50348,0.01781,0.29892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16413.0,"contact_point_centroid":[0.5107,0.07327,0.19252],"force_p95":0.08611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13,"mean_force":0.05998,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50852,0.05432,0.1912]},{"body_a":"world","body_b":"grasp_target","contact_count":2600.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5069,0.03636,0.16795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.49983,0.0575,0.03102],"force_p95":0.07332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08699,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49924,0.03834,0.02922]},{"body_a":"left_finger","body_b":"right_finger","contact_count":242.0,"contact_point_centroid":[0.61971,0.16681,0.1728],"force_p95":0.01433,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01145,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61913,0.16679,0.17034]}],"total_contact_groups":14},"final_pose_error":0.0108,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62659,0.16672,0.01604],"final_tcp_position":[0.62102,0.16883,0.16936],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.66925,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50814,0.03383,0.3002],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2600.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50746,0.03901,0.0382],"tcp_start":[0.50814,0.03383,0.3002],"tcp_to_object_dist_end":0.0132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03837,0.02557],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21337,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15174,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10860.0,"raw_peak_contact_force":0.23809,"subtask_id":"grasp_1","tcp_end":[0.49921,0.03834,0.02918],"tcp_start":[0.50746,0.03901,0.0382],"tcp_to_object_dist_end":0.01368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.50659,0.03813,0.16517],"object_pos_start":[0.51241,0.03837,0.02557],"object_to_goal_dist_end":0.18194,"object_to_goal_dist_start":0.21337,"object_z_max":0.1649,"peak_contact_force":0.07959,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20998.0,"raw_peak_contact_force":0.51159,"tcp_end":[0.49567,0.03804,0.17236],"tcp_start":[0.49921,0.03834,0.02918],"tcp_to_object_dist_end":0.01307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53765,0.07146,0.19865],"object_pos_start":[0.50659,0.03813,0.16517],"object_to_goal_dist_end":0.14552,"object_to_goal_dist_start":0.18194,"object_z_max":0.19862,"peak_contact_force":0.11139,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32597.0,"raw_peak_contact_force":0.15115,"subtask_id":"transport_arc","tcp_end":[0.52554,0.07158,0.21587],"tcp_start":[0.49567,0.03804,0.17236],"tcp_to_object_dist_end":0.02105,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":949.0,"n_steps_budget":1000.0,"object_pos_end":[0.62659,0.16672,0.01604],"object_pos_start":[0.53765,0.07146,0.19865],"object_to_goal_dist_end":0.12912,"object_to_goal_dist_start":0.14552,"object_z_max":0.19865,"peak_contact_force":0.12424,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16784.0,"raw_peak_contact_force":1.66925,"tcp_end":[0.62102,0.16883,0.16936],"tcp_start":[0.52554,0.07158,0.21587],"tcp_to_object_dist_end":0.15344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46835,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23901,"approach_1.approach_tol":0.00522,"approach_1.speed":0.08472,"descend_1.descend_speed":0.08042,"descend_1.descend_tol":0.0213,"descend_1.grasp_z_offset":0.00744,"grasp_1.grasp_duration":2.96669,"lift_1.lift_height":0.26746,"lift_1.lift_speed":0.04537,"lift_1.lift_tol":0.02399,"place_1.place_speed":0.17878,"place_1.place_tol":0.04999,"place_1.place_z_offset":0.04786,"transport_arc.transport_altitude":0.15919,"transport_arc.transport_max_time":1.87579,"transport_arc.transport_speed":0.25082},"optimized_scores":{"best_composite_score":-0.01881,"best_fitness_score":0.90119,"best_task_score":0.84971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47859,0.04605,-0.00155],"force_p95":0.52746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54666,"mean_force":0.20347,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46944,0.04684,0.03532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16943.0,"contact_point_centroid":[0.46724,0.06578,0.16016],"force_p95":0.07549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29808,"mean_force":0.05135,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46723,0.04662,0.15837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16944.0,"contact_point_centroid":[0.46718,0.02747,0.16113],"force_p95":0.07526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25488,"mean_force":0.05074,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46724,0.04663,0.1592]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.0485,-0.00216],"force_p95":0.16686,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24317,"mean_force":0.13447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47159,0.04707,0.03522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17276.0,"contact_point_centroid":[0.50874,0.09342,0.31687],"force_p95":0.08886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23584,"mean_force":0.05756,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50744,0.11253,0.31538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3229.0,"contact_point_centroid":[0.56824,0.18867,0.3203],"force_p95":0.16397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22108,"mean_force":0.09484,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56706,0.20762,0.32223]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4027.0,"contact_point_centroid":[0.56714,0.22595,0.31958],"force_p95":0.10567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21764,"mean_force":0.06407,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56733,0.20806,0.32099]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19351.0,"contact_point_centroid":[0.50995,0.13366,0.31757],"force_p95":0.07689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18762,"mean_force":0.0513,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50877,0.11467,0.31656]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.4827,0.04873,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49132,0.01858,0.28445]},{"body_a":"world","body_b":"grasp_target","contact_count":2900.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47986,0.0432,0.1548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.47023,0.02771,0.03685],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12232,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47048,0.04696,0.03409]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5535.0,"contact_point_centroid":[0.47005,0.06629,0.03625],"force_p95":0.07052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07793,"mean_force":0.04096,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47048,0.04696,0.0341]}],"total_contact_groups":12},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57255,0.22254,0.25216],"final_tcp_position":[0.57624,0.22243,0.28338],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.54666,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48347,0.03884,0.26996],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2900.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4783,0.04772,0.04212],"tcp_start":[0.48347,0.03884,0.26996],"tcp_to_object_dist_end":0.01672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48263,0.04729,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2913,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16013,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12361.0,"raw_peak_contact_force":0.24317,"subtask_id":"grasp_1","tcp_end":[0.47045,0.04695,0.03406],"tcp_start":[0.4783,0.04772,0.04212],"tcp_to_object_dist_end":0.01492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.47644,0.04676,0.26763],"object_pos_start":[0.48263,0.04729,0.02545],"object_to_goal_dist_end":0.21367,"object_to_goal_dist_start":0.2913,"object_z_max":0.26735,"peak_contact_force":0.06999,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33973.0,"raw_peak_contact_force":0.54666,"tcp_end":[0.46799,0.0467,0.28184],"tcp_start":[0.47045,0.04695,0.03406],"tcp_to_object_dist_end":0.01653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56448,0.19442,0.3328],"object_pos_start":[0.47644,0.04676,0.26763],"object_to_goal_dist_end":0.10935,"object_to_goal_dist_start":0.21367,"object_z_max":0.33275,"peak_contact_force":0.12168,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36627.0,"raw_peak_contact_force":0.23584,"subtask_id":"transport_arc","tcp_end":[0.55929,0.19439,0.36216],"tcp_start":[0.46799,0.0467,0.28184],"tcp_to_object_dist_end":0.02982,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.57255,0.22254,0.25216],"object_pos_start":[0.56448,0.19442,0.3328],"object_to_goal_dist_end":0.02443,"object_to_goal_dist_start":0.10935,"object_z_max":0.3328,"peak_contact_force":0.10797,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7256.0,"raw_peak_contact_force":0.22108,"tcp_end":[0.57624,0.22243,0.28338],"tcp_start":[0.55929,0.19439,0.36216],"tcp_to_object_dist_end":0.03144,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43868,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21035,"approach_1.approach_tol":0.0331,"approach_1.speed":0.1145,"descend_1.descend_speed":0.13527,"descend_1.descend_tol":0.03008,"descend_1.grasp_z_offset":0.0004,"grasp_1.grasp_duration":1.51605,"lift_1.lift_height":0.22586,"lift_1.lift_speed":0.02856,"lift_1.lift_tol":0.03202,"place_1.place_speed":0.19484,"place_1.place_tol":0.03467,"place_1.place_z_offset":0.03785,"transport_arc.transport_altitude":0.16105,"transport_arc.transport_max_time":4.18586,"transport_arc.transport_speed":0.21492},"optimized_scores":{"best_composite_score":-0.30531,"best_fitness_score":0.61469,"best_task_score":0.27382},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1205.0,"contact_point_centroid":[0.60395,0.19499,-0.00313],"force_p95":0.54694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77343,"mean_force":0.1674,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59725,0.19985,0.25182]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.53267,-0.02037,-0.00146],"force_p95":0.58481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62078,"mean_force":0.23819,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52181,-0.02083,0.02574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1217.0,"contact_point_centroid":[0.57968,0.12303,0.2839],"force_p95":0.20269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33504,"mean_force":0.14277,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57546,0.14095,0.28792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1899.0,"contact_point_centroid":[0.57905,0.15841,0.28394],"force_p95":0.15198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29544,"mean_force":0.09505,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57544,0.14088,0.28796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13958.0,"contact_point_centroid":[0.51971,-0.00165,0.12814],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28253,"mean_force":0.05524,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51923,-0.02077,0.12566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14652.0,"contact_point_centroid":[0.51967,-0.03984,0.12562],"force_p95":0.07686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27102,"mean_force":0.05321,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51922,-0.02077,0.12348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14009.0,"contact_point_centroid":[0.54251,0.02325,0.26071],"force_p95":0.10781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2041,"mean_force":0.06979,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54023,0.04221,0.2599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16049.0,"contact_point_centroid":[0.54363,0.06325,0.26166],"force_p95":0.08783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19461,"mean_force":0.06143,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54102,0.04447,0.26106]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02113,-0.00204],"force_p95":0.13599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17694,"mean_force":0.12645,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52422,-0.02087,0.02624]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51299,-0.00874,0.27121]},{"body_a":"world","body_b":"grasp_target","contact_count":2444.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5287,-0.01944,0.13797]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.52384,-0.00165,0.02757],"force_p95":0.07686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11391,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52298,-0.02085,0.02484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.52383,-0.03994,0.02665],"force_p95":0.06891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0931,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02085,0.02485]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1118.0,"contact_point_centroid":[0.59881,0.20288,0.25232],"force_p95":0.01241,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01062,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5984,0.20287,0.25008]}],"total_contact_groups":14},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60393,0.19493,0.01602],"final_tcp_position":[0.60537,0.22146,0.23927],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273010.36304,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5282,-0.01794,0.24361],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2444.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53161,-0.021,0.03468],"tcp_start":[0.5282,-0.01794,0.24361],"tcp_to_object_dist_end":0.01022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02073,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13289,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10803.0,"raw_peak_contact_force":0.17694,"subtask_id":"grasp_1","tcp_end":[0.52295,-0.02085,0.02481],"tcp_start":[0.53161,-0.021,0.03468],"tcp_to_object_dist_end":0.01396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.53179,-0.02075,0.22513],"object_pos_start":[0.53688,-0.02073,0.02584],"object_to_goal_dist_end":0.26122,"object_to_goal_dist_start":0.31639,"object_z_max":0.22486,"peak_contact_force":0.01017,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28702.0,"raw_peak_contact_force":0.62078,"tcp_end":[0.51988,-0.02078,0.23103],"tcp_start":[0.52295,-0.02085,0.02481],"tcp_to_object_dist_end":0.01329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57803,0.12357,0.28145],"object_pos_start":[0.53179,-0.02075,0.22513],"object_to_goal_dist_end":0.13183,"object_to_goal_dist_start":0.26122,"object_z_max":0.28141,"peak_contact_force":0.15829,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30058.0,"raw_peak_contact_force":0.2041,"subtask_id":"transport_arc","tcp_end":[0.57017,0.12324,0.30359],"tcp_start":[0.51988,-0.02078,0.23103],"tcp_to_object_dist_end":0.02349,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.60393,0.19493,0.01602],"object_pos_start":[0.57803,0.12357,0.28145],"object_to_goal_dist_end":0.19429,"object_to_goal_dist_start":0.13183,"object_z_max":0.28145,"peak_contact_force":273010.36304,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5439.0,"raw_peak_contact_force":1.77343,"tcp_end":[0.60537,0.22146,0.23927],"tcp_start":[0.57017,0.12324,0.30359],"tcp_to_object_dist_end":0.22483,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```