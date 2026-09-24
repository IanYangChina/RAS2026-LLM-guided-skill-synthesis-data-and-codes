## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1399 | 0.31 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0981 | 0.24 | ✅ accepted |
| 9 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 8 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1116 | 0.19 | ❌ rejected |

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

## Current Skill (Q=0.140) — your mutation base

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

- **Composite score**: 0.140
- **task_score** (E): 0.313
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1681 |
| descend_grasp | 1.00 | 1.00 | 0.0834 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.1050 |
| transport | 0.67 | 1.00 | 0.2490 |
| descend_place | 1.00 | 0.67 | 0.0914 |
| release | 1.00 | 1.00 | 0.0201 |
| retract | 1.00 | 1.00 | 0.0734 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.054) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.054)→(0.498, 0.021, 0.045) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 45.000 | 0.149 | 0.204 |
| lift | lift | 1.00 / step_budget | (0.498, 0.021, 0.045)→(0.505, 0.022, 0.150) | (0.511, 0.022, 0.026)→(0.521, 0.022, 0.126) | 0.274→0.225 | 1.00 / 23.667 | 0.108 | 0.409 |
| transport | approach | 0.67 / step_budget | (0.505, 0.022, 0.150)→(0.594, 0.184, 0.311) | (0.521, 0.022, 0.126)→(0.592, 0.178, 0.201) | 0.225→0.101 | 1.00 / 16.333 | 0.127 | 0.869 |
| descend_place | descend | 1.00 / step_budget | (0.594, 0.184, 0.311)→(0.602, 0.205, 0.224) | (0.592, 0.178, 0.201)→(0.594, 0.200, 0.130) | 0.101→0.068 | 0.67 / 8.333 | 91001.840 | 0.265 |
| release | release | 1.00 / step_budget | (0.602, 0.205, 0.224)→(0.597, 0.203, 0.243) | (0.594, 0.200, 0.130)→(0.593, 0.206, 0.017) | 0.068→0.180 | 1.00 / 3.667 | 0.106 | 1.180 |
| retract | retract | 1.00 / step_budget | (0.597, 0.203, 0.243)→(0.604, 0.208, 0.316) | (0.593, 0.206, 0.017)→(0.589, 0.206, 0.019) | 0.180→0.178 | 1.00 / 4.000 | 0.124 | 0.158 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.408
- phase_score: 0.615
- phase_breakdown.reach_object_score: 0.592
- phase_breakdown.reach_goal_score: 0.631
- grasp_place_fitness: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.667
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.408
- **Median Q (composite search score)**: 0.132
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.406


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74641,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.09927,"descend_grasp.descend_z":0.02003,"descend_place.place_offset_z":0.01952,"lift.lift_height":0.17067,"retract.retract_height":0.16923,"transport.transport_speed":0.06396},"optimized_scores":{"best_composite_score":0.18725,"best_fitness_score":0.66725,"best_task_score":0.40765},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":878.0,"contact_point_centroid":[0.60094,0.14489,-0.00342],"force_p95":0.66029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25601,"mean_force":0.17793,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60165,0.14571,0.26395]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51077,0.0378,-0.00144],"force_p95":0.35948,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41406,"mean_force":0.08332,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49828,0.03809,0.04676]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7439.0,"contact_point_centroid":[0.50414,0.05695,0.10602],"force_p95":0.10288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28482,"mean_force":0.06387,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50119,0.03808,0.10375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4299.0,"contact_point_centroid":[0.54106,0.0527,0.20077],"force_p95":0.14766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28076,"mean_force":0.08407,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53495,0.07137,0.20097]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6417.0,"contact_point_centroid":[0.50384,0.0191,0.10432],"force_p95":0.1118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26763,"mean_force":0.07133,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50111,0.03808,0.10278]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.0396,-0.00213],"force_p95":0.15848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21833,"mean_force":0.13207,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5005,0.03829,0.04659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4671.0,"contact_point_centroid":[0.54319,0.09186,0.20288],"force_p95":0.11717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19677,"mean_force":0.07947,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53681,0.07343,0.20274]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.50278,0.01778,0.21865]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50636,0.03748,0.09584]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.60089,0.14488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6197,0.16676,0.22676]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60089,0.14488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61813,0.16878,0.17223]},{"body_a":"world","body_b":"grasp_target","contact_count":1692.0,"contact_point_centroid":[0.60089,0.14488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.6194,0.16947,0.24287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4379.0,"contact_point_centroid":[0.49977,0.01897,0.04737],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11419,"mean_force":0.04918,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49935,0.0382,0.04531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5244.0,"contact_point_centroid":[0.49988,0.05737,0.04747],"force_p95":0.07081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07283,"mean_force":0.04232,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49935,0.0382,0.04531]},{"body_a":"left_finger","body_b":"right_finger","contact_count":750.0,"contact_point_centroid":[0.60537,0.14928,0.26909],"force_p95":0.01309,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01592,"mean_force":0.01082,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60488,0.14926,0.26699]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1188.0,"contact_point_centroid":[0.62019,0.16676,0.22925],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61968,0.16674,0.22705]}],"total_contact_groups":17},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60089,0.14488,0.01602],"final_tcp_position":[0.6245,0.17136,0.29473],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273005.3896,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50771,0.03631,0.13783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50737,0.03885,0.05433],"tcp_start":[0.50771,0.03631,0.13783],"tcp_to_object_dist_end":0.02879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03867,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21317,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15474,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11423.0,"raw_peak_contact_force":0.21833,"tcp_end":[0.49932,0.0382,0.04528],"tcp_start":[0.50737,0.03885,0.05433],"tcp_to_object_dist_end":0.02372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":435.0,"n_steps_budget":960.0,"object_pos_end":[0.52322,0.03893,0.15191],"object_pos_start":[0.51247,0.03867,0.02554],"object_to_goal_dist_end":0.16965,"object_to_goal_dist_start":0.21317,"object_z_max":0.15166,"peak_contact_force":0.10757,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13936.0,"raw_peak_contact_force":0.41406,"tcp_end":[0.50774,0.03832,0.17693],"tcp_start":[0.49932,0.0382,0.04528],"tcp_to_object_dist_end":0.02942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.60089,0.14488,0.01602],"object_pos_start":[0.52322,0.03893,0.15191],"object_to_goal_dist_end":0.1346,"object_to_goal_dist_start":0.16965,"object_z_max":0.20132,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10598.0,"raw_peak_contact_force":2.25601,"subtask_id":"reach_goal","tcp_end":[0.61833,0.16404,0.27961],"tcp_start":[0.50774,0.03832,0.17693],"tcp_to_object_dist_end":0.26487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.60089,0.14488,0.01602],"object_pos_start":[0.60089,0.14488,0.01602],"object_to_goal_dist_end":0.1346,"object_to_goal_dist_start":0.1346,"object_z_max":0.01602,"peak_contact_force":273005.3896,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62257,0.17013,0.17266],"tcp_start":[0.61833,0.16404,0.27961],"tcp_to_object_dist_end":0.16014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60089,0.14488,0.01602],"object_pos_start":[0.60089,0.14488,0.01602],"object_to_goal_dist_end":0.1346,"object_to_goal_dist_start":0.1346,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61657,0.16825,0.19164],"tcp_start":[0.62257,0.17013,0.17266],"tcp_to_object_dist_end":0.17786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":780.0,"object_pos_end":[0.60089,0.14488,0.01602],"object_pos_start":[0.60089,0.14488,0.01602],"object_to_goal_dist_end":0.1346,"object_to_goal_dist_start":0.1346,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1692.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6245,0.17136,0.29473],"tcp_start":[0.61657,0.16825,0.19164],"tcp_to_object_dist_end":0.28096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26154,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.05578,"descend_grasp.descend_z":0.02007,"descend_place.place_offset_z":0.02406,"lift.lift_height":0.13403,"retract.retract_height":0.14486,"transport.transport_speed":0.02754},"optimized_scores":{"best_composite_score":0.10069,"best_fitness_score":0.58069,"best_task_score":0.23672},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.57702,0.25471,-0.00422],"force_p95":0.93209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73276,"mean_force":0.21367,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57368,0.22242,0.26329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1437.0,"contact_point_centroid":[0.57415,0.19392,0.31071],"force_p95":0.18386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41405,"mean_force":0.11738,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57069,0.21222,0.31465]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48097,0.04622,-0.00145],"force_p95":0.35576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40141,"mean_force":0.08163,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46948,0.04682,0.04822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5490.0,"contact_point_centroid":[0.47356,0.06585,0.08995],"force_p95":0.10294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28395,"mean_force":0.06097,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47202,0.04682,0.08868]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4958.0,"contact_point_centroid":[0.47335,0.02778,0.09016],"force_p95":0.1075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25546,"mean_force":0.06493,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47204,0.04682,0.08896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1791.0,"contact_point_centroid":[0.57498,0.23079,0.30462],"force_p95":0.14468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23915,"mean_force":0.09726,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57127,0.2133,0.30935]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04861,-0.00215],"force_p95":0.16297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22277,"mean_force":0.13334,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47154,0.04705,0.04784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11514.0,"contact_point_centroid":[0.52496,0.14288,0.23677],"force_p95":0.12266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17025,"mean_force":0.08123,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51968,0.12447,0.2373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10545.0,"contact_point_centroid":[0.52502,0.10676,0.2373],"force_p95":0.12195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15975,"mean_force":0.08855,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52017,0.12531,0.2384]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.48932,0.02169,0.21929]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.57693,0.25519,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12285,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57583,0.22453,0.31826]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4781,0.04596,0.09645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.46966,0.02769,0.04869],"force_p95":0.07123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11513,"mean_force":0.04506,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47044,0.04694,0.0467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5515.0,"contact_point_centroid":[0.47,0.06621,0.04855],"force_p95":0.07004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07219,"mean_force":0.04063,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47045,0.04694,0.04671]}],"total_contact_groups":14},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57693,0.25519,0.01602],"final_tcp_position":[0.57957,0.22728,0.35572],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.73276,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48034,0.04447,0.13861],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47813,0.04768,0.05476],"tcp_start":[0.48034,0.04447,0.13861],"tcp_to_object_dist_end":0.02912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04753,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29112,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15934,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12130.0,"raw_peak_contact_force":0.22277,"tcp_end":[0.47042,0.04694,0.04667],"tcp_start":[0.47813,0.04768,0.05476],"tcp_to_object_dist_end":0.0245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":299.0,"n_steps_budget":720.0,"object_pos_end":[0.49217,0.04757,0.1157],"object_pos_start":[0.48268,0.04753,0.02547],"object_to_goal_dist_end":0.23257,"object_to_goal_dist_start":0.29112,"object_z_max":0.11543,"peak_contact_force":0.10976,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10526.0,"raw_peak_contact_force":0.40141,"tcp_end":[0.47746,0.04707,0.14022],"tcp_start":[0.47042,0.04694,0.04667],"tcp_to_object_dist_end":0.0286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57333,0.20712,0.30965],"object_pos_start":[0.49217,0.04757,0.1157],"object_to_goal_dist_end":0.08254,"object_to_goal_dist_start":0.23257,"object_z_max":0.30947,"peak_contact_force":0.1244,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22059.0,"raw_peak_contact_force":0.17025,"subtask_id":"reach_goal","tcp_end":[0.56808,0.20667,0.34426],"tcp_start":[0.47746,0.04707,0.14022],"tcp_to_object_dist_end":0.03501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.57507,0.23495,0.17144],"object_pos_start":[0.57333,0.20712,0.30965],"object_to_goal_dist_end":0.05975,"object_to_goal_dist_start":0.08254,"object_z_max":0.30971,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3228.0,"raw_peak_contact_force":0.41405,"subtask_id":"reach_goal","tcp_end":[0.57723,0.22399,0.26169],"tcp_start":[0.56808,0.20667,0.34426],"tcp_to_object_dist_end":0.09094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57693,0.25519,0.016],"object_pos_start":[0.57507,0.23495,0.17144],"object_to_goal_dist_end":0.21615,"object_to_goal_dist_start":0.05975,"object_z_max":0.17144,"peak_contact_force":0.12287,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":606.0,"raw_peak_contact_force":1.73276,"tcp_end":[0.57331,0.2222,0.28177],"tcp_start":[0.57723,0.22399,0.26169],"tcp_to_object_dist_end":0.26784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.57693,0.25519,0.01602],"object_pos_start":[0.57693,0.25519,0.016],"object_to_goal_dist_end":0.21613,"object_to_goal_dist_start":0.21615,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.12285,"tcp_end":[0.57957,0.22728,0.35572],"tcp_start":[0.57331,0.2222,0.28177],"tcp_to_object_dist_end":0.34085,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42291,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.09171,"descend_grasp.descend_z":0.02013,"descend_place.place_offset_z":0.02663,"lift.lift_height":0.12639,"retract.retract_height":0.10896,"transport.transport_speed":0.04165},"optimized_scores":{"best_composite_score":0.13188,"best_fitness_score":0.61188,"best_task_score":0.29559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.59096,0.21783,-0.00795],"force_p95":1.46135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68405,"mean_force":0.43282,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60061,0.21804,0.24897]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.53542,-0.02077,-0.00135],"force_p95":0.34616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41123,"mean_force":0.0775,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52204,-0.02078,0.04578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.60802,0.23774,0.22812],"force_p95":0.12637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39368,"mean_force":0.08593,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60338,0.21941,0.23199]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":587.0,"contact_point_centroid":[0.60801,0.20108,0.22858],"force_p95":0.12527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37317,"mean_force":0.08609,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60338,0.21941,0.232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4773.0,"contact_point_centroid":[0.52728,-0.00184,0.0847],"force_p95":0.10904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27061,"mean_force":0.0684,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5248,-0.02078,0.08224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4889.0,"contact_point_centroid":[0.52744,-0.03971,0.0838],"force_p95":0.10792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26569,"mean_force":0.06747,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52477,-0.02078,0.08199]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2869.0,"contact_point_centroid":[0.60379,0.18052,0.27328],"force_p95":0.14885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25906,"mean_force":0.09126,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59841,0.19875,0.27458]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2474.0,"contact_point_centroid":[0.60413,0.21739,0.27296],"force_p95":0.15896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24906,"mean_force":0.10215,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59849,0.19901,0.27409]},{"body_a":"world","body_b":"grasp_target","contact_count":671.0,"contact_point_centroid":[0.59203,0.2178,-0.00227],"force_p95":0.19802,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22898,"mean_force":0.1278,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60345,0.22185,0.27767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12476.0,"contact_point_centroid":[0.56604,0.09788,0.21826],"force_p95":0.09886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18184,"mean_force":0.07576,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56026,0.07915,0.21714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13044.0,"contact_point_centroid":[0.5665,0.06217,0.21964],"force_p95":0.09505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17197,"mean_force":0.07295,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56081,0.08084,0.21862]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02124,-0.00204],"force_p95":0.13479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16973,"mean_force":0.12637,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52422,-0.02083,0.04586]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.5139,-0.00964,0.21805]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52963,-0.02025,0.09543]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5078.0,"contact_point_centroid":[0.52351,-0.00163,0.04757],"force_p95":0.06546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09476,"mean_force":0.04265,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52302,-0.0208,0.04446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4900.0,"contact_point_centroid":[0.52386,-0.04007,0.04626],"force_p95":0.06928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08847,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52302,-0.0208,0.04446]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58981,0.21782,0.02602],"final_tcp_position":[0.60662,0.22511,0.29708],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.68405,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53029,-0.0196,0.13709],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53137,-0.02096,0.05434],"tcp_start":[0.53029,-0.0196,0.13709],"tcp_to_object_dist_end":0.02888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02094,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31656,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13301,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11778.0,"raw_peak_contact_force":0.16973,"tcp_end":[0.52299,-0.0208,0.04443],"tcp_start":[0.53137,-0.02096,0.05434],"tcp_to_object_dist_end":0.02326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":308.0,"n_steps_budget":690.0,"object_pos_end":[0.54688,-0.02083,0.11071],"object_pos_start":[0.53694,-0.02094,0.02582],"object_to_goal_dist_end":0.27417,"object_to_goal_dist_start":0.31656,"object_z_max":0.11047,"peak_contact_force":0.10639,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9741.0,"raw_peak_contact_force":0.41123,"tcp_end":[0.53123,-0.02084,0.1333],"tcp_start":[0.52299,-0.0208,0.04443],"tcp_to_object_dist_end":0.02747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60079,0.18264,0.27837],"object_pos_start":[0.54688,-0.02083,0.11071],"object_to_goal_dist_end":0.08463,"object_to_goal_dist_start":0.27417,"object_z_max":0.2782,"peak_contact_force":0.13481,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25520.0,"raw_peak_contact_force":0.18184,"subtask_id":"reach_goal","tcp_end":[0.59424,0.18255,0.30902],"tcp_start":[0.53123,-0.02084,0.1333],"tcp_to_object_dist_end":0.03134,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.60753,0.21889,0.203],"object_pos_start":[0.60079,0.18264,0.27837],"object_to_goal_dist_end":0.01029,"object_to_goal_dist_start":0.08463,"object_z_max":0.27842,"peak_contact_force":0.13182,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5343.0,"raw_peak_contact_force":0.25906,"subtask_id":"reach_goal","tcp_end":[0.60505,0.21976,0.2365],"tcp_start":[0.59424,0.18255,0.30902],"tcp_to_object_dist_end":0.03361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60151,0.21722,0.01938],"object_pos_start":[0.60753,0.21889,0.203],"object_to_goal_dist_end":0.18854,"object_to_goal_dist_start":0.01029,"object_z_max":0.203,"peak_contact_force":0.073,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1359.0,"raw_peak_contact_force":1.68405,"tcp_end":[0.60059,0.21803,0.25562],"tcp_start":[0.60505,0.21976,0.2365],"tcp_to_object_dist_end":0.23625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":600.0,"object_pos_end":[0.58981,0.21782,0.02602],"object_pos_start":[0.60151,0.21722,0.01938],"object_to_goal_dist_end":0.18282,"object_to_goal_dist_start":0.18854,"object_z_max":0.02814,"peak_contact_force":0.12558,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":671.0,"raw_peak_contact_force":0.22898,"tcp_end":[0.60662,0.22511,0.29708],"tcp_start":[0.60059,0.21803,0.25562],"tcp_to_object_dist_end":0.27168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```