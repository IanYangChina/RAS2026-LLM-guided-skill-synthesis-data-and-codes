## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → grasp → approach → descend → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0249 | 0.19 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1365 | 0.19 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1399 | 0.31 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0981 | 0.24 | ✅ accepted |
| 9 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=0.025) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.4
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.6
phases:
- id: approach_obj
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
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
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: continue
- id: transport
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_place
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release
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
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_obj** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=continue, threshold=1.0
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.025
- **task_score** (E): 0.188
- **fitness_score**: 0.555  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1681 |
| descend_grasp | 1.00 | 1.00 | 0.0816 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.1095 |
| re_grasp | 1.00 | 1.00 | 0.0122 |
| transport | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.056)→(0.498, 0.021, 0.047) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.150 | 0.202 |
| lift | lift | 1.00 / step_budget | (0.516, 0.025, 0.329)→(0.518, 0.045, 0.222) | (0.511, 0.022, 0.026)→(0.519, 0.025, 0.158) | 0.274→0.215 | 1.00 / 8.333 | 3249.740 | 1.792 |
| re_grasp | grasp | 1.00 / step_budget | (0.518, 0.045, 0.222)→(0.512, 0.045, 0.211) | (0.521, 0.049, 0.016)→(0.521, 0.049, 0.016) | 0.259→0.259 | 1.00 / 8.333 | 0.123 | 0.123 |
| transport | approach | 0.00 / guard_failure | (0.512, 0.045, 0.211)→(0.512, 0.045, 0.211) | (0.521, 0.049, 0.016)→(0.521, 0.049, 0.016) | 0.259→0.259 | 1.00 / 9.000 | 182003.582 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.275
- phase_score: 0.052
- phase_breakdown.reach_object_score: 0.065
- phase_breakdown.reach_goal_score: 0.043
- grasp_place_fitness: 0.597

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.597
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.275
- **Median Q (composite search score)**: 0.007
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: transport.transport_arc_height
- **Final σ (mean)**: 0.425


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07463,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.09763,"descend_grasp.descend_z":0.02346,"descend_place.place_offset_z":0.02215,"lift.lift_height":0.19029,"retract.retract_speed":0.07396,"transport.transport_arc_height":0.03,"transport.transport_speed":0.06242},"optimized_scores":{"best_composite_score":0.06678,"best_fitness_score":0.59678,"best_task_score":0.27532},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1875.0,"contact_point_centroid":[0.52264,0.07169,-0.00255],"force_p95":0.27614,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84135,"mean_force":0.14716,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5149,0.04487,0.27925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8216.0,"contact_point_centroid":[0.50516,0.05674,0.12175],"force_p95":0.12037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34811,"mean_force":0.07278,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50176,0.03811,0.12155]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7617.0,"contact_point_centroid":[0.50515,0.01927,0.12262],"force_p95":0.1392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26113,"mean_force":0.07799,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50187,0.03811,0.12283]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03964,-0.00213],"force_p95":0.15832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21469,"mean_force":0.13198,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03827,0.0502]},{"body_a":"world","body_b":"grasp_target","contact_count":2080.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13223,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.50278,0.01777,0.21873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4336.0,"contact_point_centroid":[0.49963,0.01899,0.04969],"force_p95":0.07542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13052,"mean_force":0.04953,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4994,0.03818,0.04892]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50639,0.03744,0.09778]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.52307,0.07317,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"re_grasp","phase_type":"grasp","tcp_position_centroid":[0.51434,0.06598,0.2153]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.52307,0.07317,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51349,0.06586,0.21382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4992.0,"contact_point_centroid":[0.49989,0.05736,0.04969],"force_p95":0.07289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07456,"mean_force":0.04416,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49941,0.03818,0.04893]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1741.0,"contact_point_centroid":[0.51653,0.04579,0.29424],"force_p95":0.01223,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01608,"mean_force":0.01066,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5161,0.04578,0.29201]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1932.0,"contact_point_centroid":[0.51473,0.066,0.21761],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01039,"phase_index":4.0,"phase_name":"re_grasp","phase_type":"grasp","tcp_position_centroid":[0.51434,0.06598,0.2153]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.51384,0.06588,0.21589],"force_p95":0.01083,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01083,"mean_force":0.01083,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51349,0.06586,0.21382]}],"total_contact_groups":13},"final_pose_error":0.17605,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52307,0.07317,0.01602],"final_tcp_position":[0.51347,0.06585,0.21379],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.72685,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50771,0.03626,0.13805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50739,0.03882,0.05797],"tcp_start":[0.50771,0.03626,0.13805],"tcp_to_object_dist_end":0.03237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.0387,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21314,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1554,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11128.0,"raw_peak_contact_force":0.21469,"tcp_end":[0.49937,0.03817,0.04889],"tcp_start":[0.50739,0.03882,0.05797],"tcp_to_object_dist_end":0.02678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1109.0,"n_steps_budget":1000.0,"object_pos_end":[0.51976,0.03978,0.16579],"object_pos_start":[0.51248,0.0387,0.02554],"object_to_goal_dist_end":0.17227,"object_to_goal_dist_start":0.21314,"object_z_max":0.18713,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19449.0,"raw_peak_contact_force":1.84135,"tcp_end":[0.51944,0.06646,0.22454],"tcp_start":[0.51704,0.03947,0.33648],"tcp_to_object_dist_end":0.06453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52307,0.07317,0.01602],"object_pos_start":[0.52307,0.07317,0.01602],"object_to_goal_dist_end":0.19348,"object_to_goal_dist_start":0.19348,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"re_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3732.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.51349,0.06586,0.21382],"tcp_start":[0.51944,0.06646,0.22454],"tcp_to_object_dist_end":0.19817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52307,0.07317,0.01602],"object_pos_start":[0.52307,0.07317,0.01602],"object_to_goal_dist_end":0.19348,"object_to_goal_dist_start":0.19348,"object_z_max":0.01602,"peak_contact_force":273004.72685,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.51347,0.06585,0.21379],"tcp_start":[0.51349,0.06586,0.21382],"tcp_to_object_dist_end":0.19814,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3956,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.03956,"descend_grasp.descend_z":0.02187,"descend_place.place_offset_z":0.02062,"lift.lift_height":0.15832,"retract.retract_speed":0.09162,"transport.transport_arc_height":0.0429,"transport.transport_speed":0.04401},"optimized_scores":{"best_composite_score":0.0075,"best_fitness_score":0.5375,"best_task_score":0.1548},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":947.0,"contact_point_centroid":[0.49403,0.06937,-0.00307],"force_p95":0.5911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98337,"mean_force":0.17696,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48679,0.0556,0.22072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8553.0,"contact_point_centroid":[0.477,0.06555,0.12533],"force_p95":0.12869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34256,"mean_force":0.07272,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47387,0.04689,0.12492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7923.0,"contact_point_centroid":[0.47691,0.02803,0.12587],"force_p95":0.14003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26247,"mean_force":0.07694,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47392,0.04689,0.12587]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04863,-0.00215],"force_p95":0.16353,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22143,"mean_force":0.13319,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47155,0.04704,0.04967]},{"body_a":"world","body_b":"grasp_target","contact_count":2232.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.48923,0.02172,0.21917]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.49491,0.07153,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":4.0,"phase_name":"re_grasp","phase_type":"grasp","tcp_position_centroid":[0.48502,0.06905,0.17352]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47807,0.04596,0.09739]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49491,0.07153,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48409,0.06891,0.17221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4337.0,"contact_point_centroid":[0.47041,0.02767,0.04941],"force_p95":0.07634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11279,"mean_force":0.04971,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47046,0.04693,0.04853]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5512.0,"contact_point_centroid":[0.46995,0.06611,0.04986],"force_p95":0.06924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07194,"mean_force":0.0403,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47047,0.04693,0.04854]},{"body_a":"left_finger","body_b":"right_finger","contact_count":785.0,"contact_point_centroid":[0.48905,0.05781,0.23301],"force_p95":0.01353,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.01099,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48863,0.05779,0.23078]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1897.0,"contact_point_centroid":[0.48551,0.06907,0.17576],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01105,"mean_force":0.01057,"phase_index":4.0,"phase_name":"re_grasp","phase_type":"grasp","tcp_position_centroid":[0.48502,0.06905,0.17352]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.48639,0.06896,0.17568],"force_p95":0.00946,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00946,"mean_force":0.00946,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48409,0.06891,0.17221]}],"total_contact_groups":13},"final_pose_error":0.28024,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49491,0.07153,0.01602],"final_tcp_position":[0.48408,0.06891,0.17218],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.98337,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48027,0.04449,0.13847],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47813,0.04768,0.0566],"tcp_start":[0.48027,0.04449,0.13847],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04752,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29112,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16039,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11649.0,"raw_peak_contact_force":0.22143,"tcp_end":[0.47043,0.04693,0.04851],"tcp_start":[0.47813,0.04768,0.0566],"tcp_to_object_dist_end":0.02609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":894.0,"n_steps_budget":870.0,"object_pos_end":[0.49113,0.04802,0.13639],"object_pos_start":[0.48268,0.04752,0.02548],"object_to_goal_dist_end":0.22313,"object_to_goal_dist_start":0.29112,"object_z_max":0.19522,"peak_contact_force":0.12264,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18208.0,"raw_peak_contact_force":1.98337,"tcp_end":[0.49061,0.06965,0.18181],"tcp_start":[0.48728,0.04766,0.27517],"tcp_to_object_dist_end":0.05031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49491,0.07153,0.01602],"object_pos_start":[0.49491,0.07153,0.01602],"object_to_goal_dist_end":0.27984,"object_to_goal_dist_start":0.27984,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"re_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3697.0,"raw_peak_contact_force":0.12265,"subtask_id":"reach_object","tcp_end":[0.48409,0.06891,0.17221],"tcp_start":[0.49061,0.06965,0.18181],"tcp_to_object_dist_end":0.15658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49491,0.07153,0.01602],"object_pos_start":[0.49491,0.07153,0.01602],"object_to_goal_dist_end":0.27984,"object_to_goal_dist_start":0.27984,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.48408,0.06891,0.17218],"tcp_start":[0.48409,0.06891,0.17221],"tcp_to_object_dist_end":0.15656,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67251,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.05413,"descend_grasp.descend_z":0.02002,"descend_place.place_offset_z":0.01121,"lift.lift_height":0.22386,"retract.retract_speed":0.05795,"transport.transport_arc_height":0.09817,"transport.transport_speed":0.0437},"optimized_scores":{"best_composite_score":0.00045,"best_fitness_score":0.53045,"best_task_score":0.1325},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2402.0,"contact_point_centroid":[0.54564,0.00089,-0.00245],"force_p95":0.2033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55069,"mean_force":0.14135,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53991,-0.01348,0.30645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7844.0,"contact_point_centroid":[0.52849,-0.00198,0.12081],"force_p95":0.12628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28835,"mean_force":0.07794,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5247,-0.02076,0.11897]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7958.0,"contact_point_centroid":[0.52845,-0.03953,0.11896],"force_p95":0.12926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2756,"mean_force":0.07693,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52459,-0.02076,0.1175]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16963,"mean_force":0.12669,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5242,-0.02083,0.04573]},{"body_a":"world","body_b":"grasp_target","contact_count":2344.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51379,-0.00965,0.21788]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52958,-0.02026,0.09526]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5459,0.00162,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"re_grasp","phase_type":"grasp","tcp_position_centroid":[0.53896,-0.00123,0.24919]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5459,0.00162,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53818,-0.00124,0.24758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.52341,-0.00163,0.04746],"force_p95":0.06569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12254,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.523,-0.02081,0.04433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4899.0,"contact_point_centroid":[0.52385,-0.04007,0.04613],"force_p95":0.06944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08739,"mean_force":0.04506,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.523,-0.02081,0.04433]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2267.0,"contact_point_centroid":[0.54138,-0.01269,0.3224],"force_p95":0.01137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01596,"mean_force":0.01064,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54112,-0.01269,0.32004]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1928.0,"contact_point_centroid":[0.53942,-0.00123,0.25148],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01041,"phase_index":4.0,"phase_name":"re_grasp","phase_type":"grasp","tcp_position_centroid":[0.53895,-0.00123,0.24918]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.53854,-0.00125,0.24965],"force_p95":0.01077,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01077,"mean_force":0.01077,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53818,-0.00124,0.24758]}],"total_contact_groups":13},"final_pose_error":0.26404,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5459,0.00162,0.01602],"final_tcp_position":[0.53817,-0.00124,0.24755],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273005.89731,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2344.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53019,-0.01962,0.13686],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53135,-0.02096,0.05421],"tcp_start":[0.53019,-0.01962,0.13686],"tcp_to_object_dist_end":0.02875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02091,0.0258],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31654,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13451,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11736.0,"raw_peak_contact_force":0.16963,"tcp_end":[0.52297,-0.02081,0.0443],"tcp_start":[0.53135,-0.02096,0.05421],"tcp_to_object_dist_end":0.02318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1273.0,"n_steps_budget":1000.0,"object_pos_end":[0.54689,-0.01248,0.17181],"object_pos_start":[0.53694,-0.02091,0.0258],"object_to_goal_dist_end":0.251,"object_to_goal_dist_start":0.31654,"object_z_max":0.19069,"peak_contact_force":9748.97396,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20471.0,"raw_peak_contact_force":1.55069,"tcp_end":[0.54356,-0.00124,0.25911],"tcp_start":[0.54462,-0.01317,0.37596],"tcp_to_object_dist_end":0.08808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5459,0.00162,0.01602],"object_pos_start":[0.5459,0.00162,0.01602],"object_to_goal_dist_end":0.30317,"object_to_goal_dist_start":0.30317,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"re_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3728.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53818,-0.00124,0.24758],"tcp_start":[0.54356,-0.00124,0.25911],"tcp_to_object_dist_end":0.23171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5459,0.00162,0.01602],"object_pos_start":[0.5459,0.00162,0.01602],"object_to_goal_dist_end":0.30317,"object_to_goal_dist_start":0.30317,"object_z_max":0.01602,"peak_contact_force":273005.89731,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53817,-0.00124,0.24755],"tcp_start":[0.53818,-0.00124,0.24758],"tcp_to_object_dist_end":0.23168,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```