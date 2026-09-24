## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1488 | 0.19 | ❌ rejected |
| 3 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1969 | 0.28 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2195 | 0.23 | ❌ rejected |
| 1 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2558 | 0.29 | ✅ accepted |
| 0 | descend → grasp → approach → descend → release | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.0443 | 0.16 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.149) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  weight: 0.5
phases:
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
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
  - id: bilateral_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
- id: transport_1
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
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_2
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
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place
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
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.149
- **task_score** (E): 0.186
- **fitness_score**: 0.569  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2646 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 1.00 | 0.1029 |
| transport_1 | 0.67 | 1.00 | 0.2692 |
| descend_2 | 1.00 | 1.00 | 0.1317 |
| release_1 | 1.00 | 1.00 | 0.0203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.040) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.040)→(0.508, -0.001, 0.031) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 42.333 | 0.170 | 0.259 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.031)→(0.504, -0.001, 0.134) | (0.522, -0.001, 0.025)→(0.519, -0.001, 0.118) | 0.290→0.244 | 1.00 / 21.667 | 0.131 | 0.630 |
| transport_1 | approach | 0.67 / step_budget | (0.504, -0.001, 0.134)→(0.586, 0.161, 0.329) | (0.519, -0.001, 0.118)→(0.542, 0.063, 0.016) | 0.244→0.256 | 1.00 / 8.000 | 3249.641 | 1.979 |
| descend_2 | descend | 1.00 / step_budget | (0.586, 0.161, 0.329)→(0.603, 0.202, 0.208) | (0.542, 0.063, 0.016)→(0.542, 0.063, 0.016) | 0.256→0.256 | 1.00 / 8.333 | 91003.528 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.202, 0.208)→(0.598, 0.200, 0.227) | (0.542, 0.063, 0.016)→(0.542, 0.063, 0.016) | 0.256→0.256 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.221
- phase_score: 0.771
- phase_breakdown.pre_grasp_score: 0.890
- phase_breakdown.lift_clear_score: 0.579
- phase_breakdown.place_score: 0.838
- grasp_place_fitness: 0.592

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.592
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.221
- **Median Q (composite search score)**: 0.154
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.299


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44545,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00492,"descend_2.place_z_offset":-0.01067,"lift_1.lift_height":0.1134,"transport_1.approach_height":0.13091,"transport_1.arc_height":0.0511,"transport_1.transport_speed":0.04958},"optimized_scores":{"best_composite_score":0.17226,"best_fitness_score":0.59226,"best_task_score":0.22103},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.52958,0.1784,-0.00374],"force_p95":0.87797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34352,"mean_force":0.20814,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54366,0.16955,0.32923]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.47926,0.0431,-0.00145],"force_p95":0.54061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75866,"mean_force":0.09855,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4697,0.04506,0.02796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10709.0,"contact_point_centroid":[0.46935,0.06374,0.07223],"force_p95":0.10201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32199,"mean_force":0.06211,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46735,0.04484,0.07058]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48286,0.04815,-0.00234],"force_p95":0.21809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30894,"mean_force":0.14832,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47243,0.04533,0.02686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9887.0,"contact_point_centroid":[0.46959,0.02587,0.07498],"force_p95":0.10845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29732,"mean_force":0.06525,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46736,0.04484,0.07296]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7653.0,"contact_point_centroid":[0.48683,0.09195,0.20996],"force_p95":0.1346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25413,"mean_force":0.08748,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48271,0.07351,0.21114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7902.0,"contact_point_centroid":[0.48499,0.05257,0.20477],"force_p95":0.13725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2389,"mean_force":0.08263,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4811,0.07097,0.20619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4679.0,"contact_point_centroid":[0.47135,0.02594,0.02811],"force_p95":0.08036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1647,"mean_force":0.04579,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4713,0.04523,0.02573]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48848,0.02289,0.16528]},{"body_a":"world","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.52877,0.17937,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12268,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56679,0.20775,0.28371]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52877,0.17937,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57292,0.22204,0.22667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5705.0,"contact_point_centroid":[0.47069,0.06477,0.02711],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08497,"mean_force":0.04156,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47131,0.04523,0.02574]},{"body_a":"left_finger","body_b":"right_finger","contact_count":785.0,"contact_point_centroid":[0.54522,0.17152,0.3326],"force_p95":0.01267,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01088,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5449,0.17151,0.33049]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1504.0,"contact_point_centroid":[0.56728,0.20775,0.28602],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01039,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56677,0.20773,0.2838]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57554,0.22306,0.22485],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01007,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57496,0.22303,0.22262]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52877,0.17937,0.01602],"final_tcp_position":[0.57638,0.22346,0.22618],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.34352,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3316.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47916,0.04592,0.03373],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04548,0.02485],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29285,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20092,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12184.0,"raw_peak_contact_force":0.30894,"tcp_end":[0.47128,0.04522,0.0257],"tcp_start":[0.47916,0.04592,0.03373],"tcp_to_object_dist_end":0.01137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.48442,0.04521,0.11728],"object_pos_start":[0.48261,0.04548,0.02485],"object_to_goal_dist_end":0.23672,"object_to_goal_dist_start":0.29285,"object_z_max":0.11718,"peak_contact_force":0.11716,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20742.0,"raw_peak_contact_force":0.75866,"subtask_id":"lift_clear","tcp_end":[0.46736,0.04485,0.12767],"tcp_start":[0.47128,0.04522,0.0257],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52877,0.17936,0.01602],"object_pos_start":[0.48442,0.04521,0.11728],"object_to_goal_dist_end":0.22642,"object_to_goal_dist_start":0.23672,"object_z_max":0.26771,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17144.0,"raw_peak_contact_force":2.34352,"tcp_end":[0.55886,0.19354,0.34195],"tcp_start":[0.46736,0.04485,0.12767],"tcp_to_object_dist_end":0.32762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.52877,0.17937,0.01602],"object_pos_start":[0.52877,0.17936,0.01602],"object_to_goal_dist_end":0.22642,"object_to_goal_dist_start":0.22642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2904.0,"raw_peak_contact_force":0.12268,"subtask_id":"place","tcp_end":[0.57638,0.22346,0.22618],"tcp_start":[0.55886,0.19354,0.34195],"tcp_to_object_dist_end":0.21995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52877,0.17937,0.01602],"object_pos_start":[0.52877,0.17937,0.01602],"object_to_goal_dist_end":0.22642,"object_to_goal_dist_start":0.22642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57175,0.22146,0.24643],"tcp_start":[0.57638,0.22346,0.22618],"tcp_to_object_dist_end":0.23814,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7122,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00587,"descend_2.place_z_offset":0.02497,"lift_1.lift_height":0.10808,"transport_1.approach_height":0.18356,"transport_1.arc_height":0.0573,"transport_1.transport_speed":0.05094},"optimized_scores":{"best_composite_score":0.12033,"best_fitness_score":0.54033,"best_task_score":0.134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2542.0,"contact_point_centroid":[0.5389,0.006,-0.00243],"force_p95":0.12564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90872,"mean_force":0.14046,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54992,0.07195,0.2938]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.53409,-0.01933,-0.00119],"force_p95":0.40701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5644,"mean_force":0.0828,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52033,-0.02002,0.0353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7920.0,"contact_point_centroid":[0.52149,-0.00115,0.07776],"force_p95":0.11089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32913,"mean_force":0.07634,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51777,-0.01996,0.07557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8610.0,"contact_point_centroid":[0.52146,-0.03866,0.07639],"force_p95":0.10566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30984,"mean_force":0.07151,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51779,-0.01996,0.07473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.52422,0.00833,0.16004],"force_p95":0.182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24195,"mean_force":0.11888,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51848,-0.01006,0.1612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.52428,-0.02768,0.16056],"force_p95":0.14702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22927,"mean_force":0.09817,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51859,-0.00969,0.16224]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02108,-0.00211],"force_p95":0.15586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22484,"mean_force":0.13142,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52321,-0.02007,0.03491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.52318,-0.00084,0.03622],"force_p95":0.07983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14436,"mean_force":0.05187,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52199,-0.02005,0.03352]},{"body_a":"world","body_b":"grasp_target","contact_count":3292.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5141,-0.01005,0.17005]},{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.53888,0.00604,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59005,0.17996,0.28984]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53888,0.00604,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60136,0.21847,0.23303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4983.0,"contact_point_centroid":[0.52311,-0.03918,0.03533],"force_p95":0.07227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0829,"mean_force":0.04461,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52199,-0.02005,0.03353]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2484.0,"contact_point_centroid":[0.55199,0.07636,0.30144],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01589,"mean_force":0.01057,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55164,0.07636,0.29915]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2071.0,"contact_point_centroid":[0.59051,0.17999,0.29194],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01054,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59005,0.17998,0.28983]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.60406,0.21947,0.23168],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01006,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60335,0.21945,0.22951]}],"total_contact_groups":15},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53888,0.00604,0.01602],"final_tcp_position":[0.60473,0.21966,0.23311],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273010.33753,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3292.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53042,-0.02016,0.04327],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02013,0.02562],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31604,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14941,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10860.0,"raw_peak_contact_force":0.22484,"tcp_end":[0.52196,-0.02004,0.03349],"tcp_start":[0.53042,-0.02016,0.04327],"tcp_to_object_dist_end":0.01693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53254,-0.02004,0.1121],"object_pos_start":[0.53694,-0.02013,0.02562],"object_to_goal_dist_end":0.27665,"object_to_goal_dist_start":0.31604,"object_z_max":0.11199,"peak_contact_force":0.11273,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16675.0,"raw_peak_contact_force":0.5644,"subtask_id":"lift_clear","tcp_end":[0.5178,-0.01995,0.12917],"tcp_start":[0.52196,-0.02004,0.03349],"tcp_to_object_dist_end":0.02256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53888,0.00604,0.01602],"object_pos_start":[0.53254,-0.02004,0.1121],"object_to_goal_dist_end":0.30148,"object_to_goal_dist_start":0.27665,"object_z_max":0.17559,"peak_contact_force":9748.67816,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9910.0,"raw_peak_contact_force":1.90872,"tcp_end":[0.57674,0.14111,0.35155],"tcp_start":[0.5178,-0.01995,0.12917],"tcp_to_object_dist_end":0.36368,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.53888,0.00604,0.01602],"object_pos_start":[0.53888,0.00604,0.01602],"object_to_goal_dist_end":0.30148,"object_to_goal_dist_start":0.30148,"object_z_max":0.01602,"peak_contact_force":273010.33753,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4031.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.60473,0.21966,0.23311],"tcp_start":[0.57674,0.14111,0.35155],"tcp_to_object_dist_end":0.3116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53888,0.00604,0.01602],"object_pos_start":[0.53888,0.00604,0.01602],"object_to_goal_dist_end":0.30148,"object_to_goal_dist_start":0.30148,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60023,0.2179,0.25243],"tcp_start":[0.60473,0.21966,0.23311],"tcp_to_object_dist_end":0.32332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43043,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00668,"descend_2.place_z_offset":-0.02159,"lift_1.lift_height":0.12349,"transport_1.approach_height":0.12344,"transport_1.arc_height":0.05027,"transport_1.transport_speed":0.04051},"optimized_scores":{"best_composite_score":0.15368,"best_fitness_score":0.57368,"best_task_score":0.20212},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2313.0,"contact_point_centroid":[0.55912,0.00302,-0.00249],"force_p95":0.14523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68567,"mean_force":0.14244,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58118,0.07605,0.27008]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.5424,-0.02642,-0.00125],"force_p95":0.39793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5669,"mean_force":0.08452,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52831,-0.02741,0.03515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8540.0,"contact_point_centroid":[0.53012,-0.00858,0.08497],"force_p95":0.11352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32631,"mean_force":0.08054,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52577,-0.02733,0.08287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9143.0,"contact_point_centroid":[0.5301,-0.04599,0.08361],"force_p95":0.10912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31558,"mean_force":0.07668,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52579,-0.02733,0.08191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1930.0,"contact_point_centroid":[0.53518,0.00297,0.17147],"force_p95":0.1828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25937,"mean_force":0.12498,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52976,-0.01518,0.1745]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54568,-0.02895,-0.00216],"force_p95":0.16884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24324,"mean_force":0.13466,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53125,-0.0275,0.03477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2354.0,"contact_point_centroid":[0.53508,-0.03282,0.1712],"force_p95":0.15243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20659,"mean_force":0.10683,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52989,-0.01503,0.17451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4063.0,"contact_point_centroid":[0.53141,-0.00825,0.03602],"force_p95":0.08167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14961,"mean_force":0.05193,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53002,-0.02747,0.03334]},{"body_a":"world","body_b":"grasp_target","contact_count":3356.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51821,-0.01382,0.16988]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.55915,0.00307,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62458,0.15552,0.22785]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55915,0.00307,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62323,0.16067,0.1629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5034.0,"contact_point_centroid":[0.5313,-0.04665,0.03513],"force_p95":0.07452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08157,"mean_force":0.04452,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53003,-0.02747,0.03334]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2243.0,"contact_point_centroid":[0.58448,0.08133,0.27588],"force_p95":0.01136,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.0106,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58418,0.08133,0.27359]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1443.0,"contact_point_centroid":[0.62512,0.15553,0.23005],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01042,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62458,0.15552,0.22784]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.6266,0.16153,0.16132],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.0101,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62595,0.16151,0.15934]}],"total_contact_groups":15},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55915,0.00307,0.01602],"final_tcp_position":[0.62785,0.16195,0.1634],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.68567,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3356.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.02767,0.04337],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02766,0.02547],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2601,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16002,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10897.0,"raw_peak_contact_force":0.24324,"tcp_end":[0.52999,-0.02746,0.0333],"tcp_start":[0.53853,-0.02767,0.04337],"tcp_to_object_dist_end":0.0174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54015,-0.02723,0.12545],"object_pos_start":[0.54553,-0.02766,0.02547],"object_to_goal_dist_end":0.21947,"object_to_goal_dist_start":0.2601,"object_z_max":0.12534,"peak_contact_force":0.16306,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17831.0,"raw_peak_contact_force":0.5669,"subtask_id":"lift_clear","tcp_end":[0.52592,-0.02732,0.14414],"tcp_start":[0.52999,-0.02746,0.0333],"tcp_to_object_dist_end":0.0235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.55915,0.00307,0.01602],"object_pos_start":[0.54015,-0.02723,0.12545],"object_to_goal_dist_end":0.23983,"object_to_goal_dist_start":0.21947,"object_z_max":0.18167,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8840.0,"raw_peak_contact_force":1.68567,"tcp_end":[0.62286,0.14982,0.29223],"tcp_start":[0.52592,-0.02732,0.14414],"tcp_to_object_dist_end":0.31919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.55915,0.00307,0.01602],"object_pos_start":[0.55915,0.00307,0.01602],"object_to_goal_dist_end":0.23983,"object_to_goal_dist_start":0.23983,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2791.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.62785,0.16195,0.1634],"tcp_start":[0.62286,0.14982,0.29223],"tcp_to_object_dist_end":0.22735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55915,0.00307,0.01602],"object_pos_start":[0.55915,0.00307,0.01602],"object_to_goal_dist_end":0.23983,"object_to_goal_dist_start":0.23983,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6216,0.16015,0.18228],"tcp_start":[0.62785,0.16195,0.1634],"tcp_to_object_dist_end":0.23711,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```