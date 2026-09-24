## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0023 | 0.33 | ✅ accepted |
| 13 | approach → descend → grasp → lift → grasp → approach → descend → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0249 | 0.19 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1365 | 0.19 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1399 | 0.31 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0981 | 0.24 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.002) — your mutation base

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
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.06
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
  parameters:
    grasp_lateral_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: add
    grasp_lateral_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: add
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
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
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_lateral_x: status=consumed; consumers=retry.offset.x (add)
    - grasp_lateral_y: status=consumed; consumers=retry.offset.y (add)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=continue, threshold=1.0
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
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

- **Composite score**: -0.002
- **task_score** (E): 0.331
- **fitness_score**: 0.628  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1681 |
| descend_grasp | 1.00 | 1.00 | 0.0825 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.1568 |
| transport | 1.00 | 1.00 | 0.2417 |
| descend_place | 1.00 | 1.00 | 0.1134 |
| release | 1.00 | 1.00 | 0.0200 |
| retract | 1.00 | 1.00 | 0.0802 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.055)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.333 | 0.154 | 0.203 |
| lift | lift | 1.00 / step_budget | (0.498, 0.021, 0.046)→(0.506, 0.022, 0.203) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.177) | 0.274→0.218 | 1.00 / 34.000 | 0.091 | 0.405 |
| transport | approach | 1.00 / step_budget | (0.506, 0.022, 0.203)→(0.600, 0.200, 0.329) | (0.514, 0.022, 0.177)→(0.599, 0.208, 0.199) | 0.218→0.140 | 1.00 / 23.667 | 91003.796 | 0.784 |
| descend_place | descend | 1.00 / step_budget | (0.600, 0.200, 0.329)→(0.603, 0.207, 0.216) | (0.599, 0.208, 0.199)→(0.589, 0.214, 0.117) | 0.140→0.082 | 1.00 / 18.000 | 0.118 | 0.237 |
| release | release | 1.00 / step_budget | (0.603, 0.207, 0.216)→(0.598, 0.205, 0.235) | (0.589, 0.214, 0.117)→(0.585, 0.214, 0.025) | 0.082→0.171 | 1.00 / 4.000 | 0.130 | 1.135 |
| retract | retract | 1.00 / step_budget | (0.598, 0.205, 0.235)→(0.604, 0.208, 0.315) | (0.585, 0.214, 0.025)→(0.583, 0.216, 0.026) | 0.171→0.170 | 1.00 / 4.000 | 0.123 | 0.140 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.549
- phase_breakdown.reach_object_score: 0.594
- phase_breakdown.reach_goal_score: 0.520
- grasp_place_fitness: 0.686

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.686
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: -0.018
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35273,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.07732,"descend_grasp.descend_z":0.02018,"descend_place.place_offset_z":0.00974,"grasp.grasp_lateral_x":0.0065,"grasp.grasp_lateral_y":-0.003,"lift.lift_height":0.20405,"lift.lift_speed":0.04975,"retract.retract_height":0.11572,"transport.transport_speed":0.04766},"optimized_scores":{"best_composite_score":0.05648,"best_fitness_score":0.68648,"best_task_score":0.44641},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":276.0,"contact_point_centroid":[0.60598,0.17146,-0.00513],"force_p95":0.80694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45731,"mean_force":0.24938,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61638,0.16817,0.17146]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.5099,0.03794,-0.00148],"force_p95":0.38523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42439,"mean_force":0.11192,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49829,0.0381,0.04667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11970.0,"contact_point_centroid":[0.50224,0.05718,0.12563],"force_p95":0.08008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28452,"mean_force":0.05327,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50169,0.03809,0.1237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":701.0,"contact_point_centroid":[0.61998,0.18829,0.15433],"force_p95":0.11252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26427,"mean_force":0.07669,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62038,0.16949,0.15816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11099.0,"contact_point_centroid":[0.50196,0.01894,0.12875],"force_p95":0.08154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26324,"mean_force":0.05605,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50194,0.03809,0.12712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.61936,0.15087,0.15458],"force_p95":0.09639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23182,"mean_force":0.06583,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62042,0.1695,0.15822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4743.0,"contact_point_centroid":[0.61812,0.18437,0.22695],"force_p95":0.11088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21942,"mean_force":0.06755,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61882,0.16571,0.22836]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.0396,-0.00213],"force_p95":0.15867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21827,"mean_force":0.13213,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50048,0.03829,0.04671]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4423.0,"contact_point_centroid":[0.61728,0.14665,0.22803],"force_p95":0.11459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2064,"mean_force":0.07163,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61883,0.1657,0.22879]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.50264,0.01776,0.21866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4336.0,"contact_point_centroid":[0.49967,0.01896,0.04737],"force_p95":0.07734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13648,"mean_force":0.04956,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49933,0.0382,0.04543]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.60585,0.17146,-0.00196],"force_p95":0.12996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13468,"mean_force":0.12208,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61887,0.16932,0.21109]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50628,0.03747,0.09588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12103.0,"contact_point_centroid":[0.5635,0.08309,0.24492],"force_p95":0.07448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0978,"mean_force":0.05106,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56307,0.10219,0.24431]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12103.0,"contact_point_centroid":[0.56422,0.12128,0.24532],"force_p95":0.075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09564,"mean_force":0.05109,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56307,0.10219,0.24431]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5244.0,"contact_point_centroid":[0.49992,0.05736,0.04756],"force_p95":0.07086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07283,"mean_force":0.0423,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49933,0.0382,0.04543]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60585,0.17147,0.02602],"final_tcp_position":[0.62317,0.17096,0.24131],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.45731,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50758,0.03629,0.13781],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50735,0.03885,0.05445],"tcp_start":[0.50758,0.03629,0.13781],"tcp_to_object_dist_end":0.02891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03862,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15553,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11380.0,"raw_peak_contact_force":0.21827,"tcp_end":[0.4993,0.0382,0.04539],"tcp_start":[0.50735,0.03885,0.05445],"tcp_to_object_dist_end":0.02383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.51587,0.03868,0.18559],"object_pos_start":[0.51247,0.03862,0.02554],"object_to_goal_dist_end":0.17899,"object_to_goal_dist_start":0.2132,"object_z_max":0.18532,"peak_contact_force":0.07793,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23161.0,"raw_peak_contact_force":0.42439,"tcp_end":[0.50827,0.03831,0.21014],"tcp_start":[0.4993,0.0382,0.04539],"tcp_to_object_dist_end":0.0257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.62091,0.16295,0.25298],"object_pos_start":[0.51587,0.03868,0.18559],"object_to_goal_dist_end":0.10858,"object_to_goal_dist_start":0.17899,"object_z_max":0.25288,"peak_contact_force":0.07567,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24206.0,"raw_peak_contact_force":0.0978,"subtask_id":"reach_goal","tcp_end":[0.61741,0.16283,0.28078],"tcp_start":[0.50827,0.03831,0.21014],"tcp_to_object_dist_end":0.02802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.61279,0.16964,0.13242],"object_pos_start":[0.62091,0.16295,0.25298],"object_to_goal_dist_end":0.01964,"object_to_goal_dist_start":0.10858,"object_z_max":0.25298,"peak_contact_force":0.11713,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9166.0,"raw_peak_contact_force":0.21942,"subtask_id":"reach_goal","tcp_end":[0.62256,0.17009,0.16276],"tcp_start":[0.61741,0.16283,0.28078],"tcp_to_object_dist_end":0.03188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60582,0.17089,0.02634],"object_pos_start":[0.61279,0.16964,0.13242],"object_to_goal_dist_end":0.12067,"object_to_goal_dist_start":0.01964,"object_z_max":0.13242,"peak_contact_force":0.11358,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1793.0,"raw_peak_contact_force":1.45731,"tcp_end":[0.61631,0.16815,0.18172],"tcp_start":[0.62256,0.17009,0.16276],"tcp_to_object_dist_end":0.15576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":600.0,"object_pos_end":[0.60585,0.17147,0.02602],"object_pos_start":[0.60582,0.17089,0.02634],"object_to_goal_dist_end":0.12098,"object_to_goal_dist_start":0.12067,"object_z_max":0.02652,"peak_contact_force":0.12264,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.13468,"tcp_end":[0.62317,0.17096,0.24131],"tcp_start":[0.61631,0.16815,0.18172],"tcp_to_object_dist_end":0.21599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24211,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.06207,"descend_grasp.descend_z":0.02271,"descend_place.place_offset_z":0.02169,"grasp.grasp_lateral_x":0.00445,"grasp.grasp_lateral_y":0.00536,"lift.lift_height":0.18566,"lift.lift_speed":0.05472,"retract.retract_height":0.1491,"transport.transport_speed":0.05742},"optimized_scores":{"best_composite_score":-0.04536,"best_fitness_score":0.58464,"best_task_score":0.25132},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":250.0,"contact_point_centroid":[0.56034,0.24657,-0.00817],"force_p95":1.408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.11086,"mean_force":0.38626,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57133,0.21187,0.3557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7240.0,"contact_point_centroid":[0.51622,0.09549,0.25285],"force_p95":0.14802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38044,"mean_force":0.09401,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51448,0.11412,0.25609]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.48068,0.04621,-0.00155],"force_p95":0.30757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36569,"mean_force":0.08368,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46947,0.0468,0.05072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9381.0,"contact_point_centroid":[0.51325,0.12915,0.25045],"force_p95":0.1089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35433,"mean_force":0.07362,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51269,0.11093,0.25291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6486.0,"contact_point_centroid":[0.47298,0.02775,0.10915],"force_p95":0.1205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32254,"mean_force":0.07777,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47202,0.0468,0.10976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9355.0,"contact_point_centroid":[0.47291,0.06535,0.11754],"force_p95":0.096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27457,"mean_force":0.05757,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47256,0.04683,0.11717]},{"body_a":"world","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.55557,0.24819,-0.00203],"force_p95":0.19138,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23853,"mean_force":0.12749,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57702,0.22288,0.31183]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04868,-0.00217],"force_p95":0.1728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22098,"mean_force":0.13486,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47157,0.04704,0.05038]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.48929,0.02171,0.21923]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4154.0,"contact_point_centroid":[0.47075,0.02765,0.05007],"force_p95":0.0918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.137,"mean_force":0.05526,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47048,0.04693,0.04924]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55492,0.24836,-0.00199],"force_p95":0.12267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12275,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57577,0.22502,0.26137]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47812,0.04594,0.09776]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.55492,0.24836,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57667,0.22577,0.3199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5497.0,"contact_point_centroid":[0.46996,0.06591,0.05032],"force_p95":0.06903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07423,"mean_force":0.03956,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47048,0.04693,0.04924]},{"body_a":"left_finger","body_b":"right_finger","contact_count":260.0,"contact_point_centroid":[0.57311,0.2144,0.3606],"force_p95":0.01451,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01143,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57281,0.21438,0.35826]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1161.0,"contact_point_centroid":[0.57747,0.22284,0.31541],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.577,0.22281,0.31316]}],"total_contact_groups":17},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55492,0.24836,0.02602],"final_tcp_position":[0.57984,0.22758,0.35975],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273011.22215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48032,0.04445,0.13864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47814,0.04767,0.0573],"tcp_start":[0.48032,0.04445,0.13864],"tcp_to_object_dist_end":0.03163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48275,0.04748,0.02531],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29124,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17379,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11451.0,"raw_peak_contact_force":0.22098,"tcp_end":[0.47045,0.04692,0.04921],"tcp_start":[0.47814,0.04767,0.0573],"tcp_to_object_dist_end":0.02688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.48417,0.04841,0.16245],"object_pos_start":[0.48275,0.04748,0.02531],"object_to_goal_dist_end":0.21618,"object_to_goal_dist_start":0.29124,"object_z_max":0.16218,"peak_contact_force":0.11854,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15932.0,"raw_peak_contact_force":0.36569,"tcp_end":[0.47842,0.0471,0.1917],"tcp_start":[0.47045,0.04692,0.04921],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.56255,0.24559,0.02923],"object_pos_start":[0.48417,0.04841,0.16245],"object_to_goal_dist_end":0.20287,"object_to_goal_dist_start":0.21618,"object_z_max":0.28882,"peak_contact_force":273011.22215,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17131.0,"raw_peak_contact_force":2.11086,"subtask_id":"reach_goal","tcp_end":[0.57601,0.21986,0.36383],"tcp_start":[0.47842,0.0471,0.1917],"tcp_to_object_dist_end":0.33586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.55491,0.24836,0.02602],"object_pos_start":[0.56255,0.24559,0.02923],"object_to_goal_dist_end":0.20716,"object_to_goal_dist_start":0.20287,"object_z_max":0.02923,"peak_contact_force":0.12276,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2211.0,"raw_peak_contact_force":0.23853,"subtask_id":"reach_goal","tcp_end":[0.57875,0.2264,0.26112],"tcp_start":[0.57601,0.21986,0.36383],"tcp_to_object_dist_end":0.23732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55492,0.24836,0.02602],"object_pos_start":[0.55491,0.24836,0.02602],"object_to_goal_dist_end":0.20715,"object_to_goal_dist_start":0.20716,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12275,"tcp_end":[0.57484,0.22451,0.28107],"tcp_start":[0.57875,0.2264,0.26112],"tcp_to_object_dist_end":0.25694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":630.0,"object_pos_end":[0.55492,0.24836,0.02602],"object_pos_start":[0.55492,0.24836,0.02602],"object_to_goal_dist_end":0.20715,"object_to_goal_dist_start":0.20715,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57984,0.22758,0.35975],"tcp_start":[0.57484,0.22451,0.28107],"tcp_to_object_dist_end":0.33531,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60714,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.0693,"descend_grasp.descend_z":0.02006,"descend_place.place_offset_z":0.00725,"grasp.grasp_lateral_x":-0.00083,"grasp.grasp_lateral_y":-0.00042,"lift.lift_height":0.20043,"lift.lift_speed":0.04966,"retract.retract_height":0.1562,"transport.transport_speed":0.07633},"optimized_scores":{"best_composite_score":-0.01795,"best_fitness_score":0.61205,"best_task_score":0.29578},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.58851,0.22697,-0.00749],"force_p95":1.16988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82488,"mean_force":0.38008,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60219,0.22289,0.23503]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.53364,-0.02056,-0.00141],"force_p95":0.39798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42551,"mean_force":0.13734,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52203,-0.02079,0.04548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12356.0,"contact_point_centroid":[0.52594,-0.03993,0.12357],"force_p95":0.0764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26763,"mean_force":0.05241,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52557,-0.02079,0.12105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11931.0,"contact_point_centroid":[0.5259,-0.00163,0.12516],"force_p95":0.07746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26681,"mean_force":0.05391,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52569,-0.02079,0.12268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4469.0,"contact_point_centroid":[0.60633,0.23849,0.2805],"force_p95":0.10588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25445,"mean_force":0.06722,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60573,0.22032,0.28195]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4103.0,"contact_point_centroid":[0.60623,0.20127,0.28194],"force_p95":0.13646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23949,"mean_force":0.08904,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60572,0.22026,0.28292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":765.0,"contact_point_centroid":[0.60458,0.20571,0.21556],"force_p95":0.10243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22583,"mean_force":0.06722,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60521,0.22432,0.21897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":677.0,"contact_point_centroid":[0.60513,0.24304,0.2152],"force_p95":0.11193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22548,"mean_force":0.07683,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60513,0.22428,0.21878]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02124,-0.00205],"force_p95":0.13515,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16966,"mean_force":0.12648,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5242,-0.02083,0.04578]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.58834,0.22691,-0.00198],"force_p95":0.12699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16255,"mean_force":0.11997,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60431,0.22436,0.29265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17002.0,"contact_point_centroid":[0.56863,0.07742,0.27198],"force_p95":0.07886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14305,"mean_force":0.05321,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56712,0.0964,0.27119]},{"body_a":"world","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.5138,-0.00965,0.21784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15948.0,"contact_point_centroid":[0.56824,0.11447,0.27116],"force_p95":0.08672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1353,"mean_force":0.05651,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5668,0.09541,0.27058]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52959,-0.02025,0.0953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5078.0,"contact_point_centroid":[0.52344,-0.00164,0.0475],"force_p95":0.0655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0958,"mean_force":0.04267,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.523,-0.0208,0.04438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4899.0,"contact_point_centroid":[0.52386,-0.04007,0.04618],"force_p95":0.06934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08739,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.523,-0.0208,0.04438]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58833,0.22691,0.02602],"final_tcp_position":[0.60828,0.22655,0.34393],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.82488,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53021,-0.01961,0.13691],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53135,-0.02096,0.05425],"tcp_start":[0.53021,-0.01961,0.13691],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02095,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31657,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13332,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11777.0,"raw_peak_contact_force":0.16966,"tcp_end":[0.52297,-0.0208,0.04434],"tcp_start":[0.53135,-0.02096,0.05425],"tcp_to_object_dist_end":0.02321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.54076,-0.02094,0.18365],"object_pos_start":[0.53694,-0.02095,0.02581],"object_to_goal_dist_end":0.25932,"object_to_goal_dist_start":0.31657,"object_z_max":0.18339,"peak_contact_force":0.07505,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24377.0,"raw_peak_contact_force":0.42551,"tcp_end":[0.53259,-0.02086,0.20677],"tcp_start":[0.52297,-0.0208,0.04434],"tcp_to_object_dist_end":0.02453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":918.0,"n_steps_budget":1000.0,"object_pos_end":[0.61344,0.21643,0.31395],"object_pos_start":[0.54076,-0.02094,0.18365],"object_to_goal_dist_end":0.10718,"object_to_goal_dist_start":0.25932,"object_z_max":0.31384,"peak_contact_force":0.09159,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32950.0,"raw_peak_contact_force":0.14305,"subtask_id":"reach_goal","tcp_end":[0.60541,0.21625,0.3421],"tcp_start":[0.53259,-0.02086,0.20677],"tcp_to_object_dist_end":0.02927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.60003,0.22411,0.19272],"object_pos_start":[0.61344,0.21643,0.31395],"object_to_goal_dist_end":0.0183,"object_to_goal_dist_start":0.10718,"object_z_max":0.31395,"peak_contact_force":0.1128,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8572.0,"raw_peak_contact_force":0.25445,"subtask_id":"reach_goal","tcp_end":[0.60692,0.22495,0.22358],"tcp_start":[0.60541,0.21625,0.3421],"tcp_to_object_dist_end":0.03163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59305,0.22301,0.02231],"object_pos_start":[0.60003,0.22411,0.19272],"object_to_goal_dist_end":0.18596,"object_to_goal_dist_start":0.0183,"object_z_max":0.19272,"peak_contact_force":0.15518,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1634.0,"raw_peak_contact_force":1.82488,"tcp_end":[0.60217,0.22288,0.24238],"tcp_start":[0.60692,0.22495,0.22358],"tcp_to_object_dist_end":0.22026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":780.0,"object_pos_end":[0.58833,0.22691,0.02602],"object_pos_start":[0.59305,0.22301,0.02231],"object_to_goal_dist_end":0.18272,"object_to_goal_dist_start":0.18596,"object_z_max":0.02677,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.16255,"tcp_end":[0.60828,0.22655,0.34393],"tcp_start":[0.60217,0.22288,0.24238],"tcp_to_object_dist_end":0.31853,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```