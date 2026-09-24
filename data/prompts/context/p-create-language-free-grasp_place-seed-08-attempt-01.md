## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2558 | 0.29 | ✅ accepted |
| 0 | descend → grasp → approach → descend → release | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.0443 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.256) — your mutation base

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

- **Composite score**: 0.256
- **task_score** (E): 0.292
- **fitness_score**: 0.626  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2679 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1040 |
| transport_1 | 0.67 | 1.00 | 0.2689 |
| descend_2 | 1.00 | 1.00 | 0.1055 |
| release_1 | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.037) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.031)→(0.511, -0.001, 0.031) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.333 | 0.166 | 0.254 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.031)→(0.507, -0.001, 0.135) | (0.522, -0.001, 0.025)→(0.522, -0.001, 0.122) | 0.290→0.241 | 1.00 / 24.667 | 0.106 | 0.655 |
| transport_1 | approach | 0.67 / step_budget | (0.507, -0.001, 0.135)→(0.598, 0.185, 0.306) | (0.522, -0.001, 0.122)→(0.603, 0.185, 0.281) | 0.241→0.081 | 1.00 / 16.000 | 0.140 | 0.171 |
| descend_2 | descend | 1.00 / step_budget | (0.598, 0.185, 0.306)→(0.604, 0.203, 0.203) | (0.603, 0.185, 0.281)→(0.603, 0.208, 0.114) | 0.081→0.092 | 1.00 / 18.000 | 55984.005 | 0.793 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.203, 0.203)→(0.599, 0.201, 0.222) | (0.603, 0.208, 0.114)→(0.604, 0.206, 0.019) | 0.092→0.187 | 1.00 / 2.667 | 0.267 | 1.153 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.348
- phase_score: 0.742
- phase_breakdown.pre_grasp_score: 0.810
- phase_breakdown.lift_clear_score: 0.530
- phase_breakdown.place_score: 0.842
- grasp_place_fitness: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.652
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.348
- **Median Q (composite search score)**: 0.249
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.232


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42544,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00833,"descend_2.place_z_offset":-0.01795,"lift_1.lift_height":0.13107,"transport_1.approach_height":0.10002,"transport_1.transport_speed":0.04605},"optimized_scores":{"best_composite_score":0.23583,"best_fitness_score":0.60583,"best_task_score":0.2385},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":416.0,"contact_point_centroid":[0.57877,0.24395,-0.00557],"force_p95":1.15407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83574,"mean_force":0.26049,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57703,0.22455,0.24081]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.47937,0.04395,-0.00142],"force_p95":0.53945,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76121,"mean_force":0.09556,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47275,0.04534,0.02767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13375.0,"contact_point_centroid":[0.47135,0.06424,0.08138],"force_p95":0.09114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33885,"mean_force":0.0581,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47036,0.04512,0.0794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14006.0,"contact_point_centroid":[0.47138,0.02613,0.08374],"force_p95":0.08657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30115,"mean_force":0.05488,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47036,0.04512,0.08197]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48283,0.04804,-0.00238],"force_p95":0.21071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29523,"mean_force":0.15053,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47479,0.04556,0.0259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.57828,0.23763,0.30087],"force_p95":0.17297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25249,"mean_force":0.08802,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57506,0.22049,0.30599]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":254.0,"contact_point_centroid":[0.57967,0.20235,0.30345],"force_p95":0.21406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24832,"mean_force":0.14225,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5751,0.22043,0.30829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11528.0,"contact_point_centroid":[0.52332,0.14763,0.22423],"force_p95":0.12938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17129,"mean_force":0.08166,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51915,0.12915,0.22453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11525.0,"contact_point_centroid":[0.52171,0.1089,0.22202],"force_p95":0.12836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16978,"mean_force":0.08147,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51808,0.12739,0.2228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5678.0,"contact_point_centroid":[0.47453,0.02632,0.02741],"force_p95":0.08073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16165,"mean_force":0.04544,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47436,0.04551,0.02546]},{"body_a":"world","body_b":"grasp_target","contact_count":3356.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48845,0.02293,0.16345]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5785,0.24377,-0.00199],"force_p95":0.12472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12788,"mean_force":0.12299,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57444,0.22459,0.22157]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.47451,0.06495,0.02737],"force_p95":0.08166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08745,"mean_force":0.04523,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47437,0.04551,0.02547]},{"body_a":"left_finger","body_b":"right_finger","contact_count":270.0,"contact_point_centroid":[0.5781,0.2252,0.23547],"force_p95":0.01447,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01144,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57743,0.22517,0.23312]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.5772,0.2256,0.21979],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00997,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57652,0.22556,0.21753]}],"total_contact_groups":15},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5785,0.24377,0.01602],"final_tcp_position":[0.578,0.22614,0.22121],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.83574,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3356.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47914,0.04593,0.03042],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04574,0.02487],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29268,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19266,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13674.0,"raw_peak_contact_force":0.29523,"tcp_end":[0.47434,0.0455,0.02544],"tcp_start":[0.47434,0.04551,0.02544],"tcp_to_object_dist_end":0.00828,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.4869,0.04552,0.13641],"object_pos_start":[0.4826,0.04572,0.02493],"object_to_goal_dist_end":0.2269,"object_to_goal_dist_start":0.29265,"object_z_max":0.1363,"peak_contact_force":0.10609,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27532.0,"raw_peak_contact_force":0.76121,"subtask_id":"lift_clear","tcp_end":[0.47054,0.04515,0.14507],"tcp_start":[0.47434,0.0455,0.02544],"tcp_to_object_dist_end":0.01852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.5819,0.21992,0.29088],"object_pos_start":[0.4869,0.04552,0.13641],"object_to_goal_dist_end":0.06105,"object_to_goal_dist_start":0.2269,"object_z_max":0.29074,"peak_contact_force":0.14327,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23053.0,"raw_peak_contact_force":0.17129,"tcp_end":[0.57512,0.21987,0.31425],"tcp_start":[0.47054,0.04515,0.14507],"tcp_to_object_dist_end":0.02433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.57852,0.24391,0.01631],"object_pos_start":[0.5819,0.21992,0.29088],"object_to_goal_dist_end":0.21473,"object_to_goal_dist_start":0.06105,"object_z_max":0.29091,"peak_contact_force":0.12796,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1440.0,"raw_peak_contact_force":1.83574,"subtask_id":"place","tcp_end":[0.578,0.22614,0.22121],"tcp_start":[0.57512,0.21987,0.31425],"tcp_to_object_dist_end":0.20567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5785,0.24377,0.01602],"object_pos_start":[0.57852,0.24391,0.01631],"object_to_goal_dist_end":0.21501,"object_to_goal_dist_start":0.21473,"object_z_max":0.01631,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12788,"tcp_end":[0.57325,0.224,0.24131],"tcp_start":[0.578,0.22614,0.22121],"tcp_to_object_dist_end":0.22622,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45673,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00497,"descend_2.place_z_offset":-0.00789,"lift_1.lift_height":0.11287,"transport_1.approach_height":0.16111,"transport_1.transport_speed":0.05618},"optimized_scores":{"best_composite_score":0.24919,"best_fitness_score":0.61919,"best_task_score":0.28845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.5958,0.20941,-0.00734],"force_p95":1.21244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69545,"mean_force":0.40589,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59977,0.2189,0.21582]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.53412,-0.01952,-0.0012],"force_p95":0.40389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56322,"mean_force":0.08037,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52364,-0.02006,0.0381]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":579.0,"contact_point_centroid":[0.60662,0.23872,0.19541],"force_p95":0.19665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46415,"mean_force":0.10274,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60295,0.22037,0.19949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":787.0,"contact_point_centroid":[0.60602,0.20198,0.19572],"force_p95":0.1925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42055,"mean_force":0.08995,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6029,0.22035,0.19938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10492.0,"contact_point_centroid":[0.52264,-0.00099,0.08392],"force_p95":0.10089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30303,"mean_force":0.06168,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52107,-0.02,0.08186]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11301.0,"contact_point_centroid":[0.52268,-0.03893,0.08218],"force_p95":0.09696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30208,"mean_force":0.05837,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52106,-0.02,0.08067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3444.0,"contact_point_centroid":[0.60246,0.21958,0.25073],"force_p95":0.15979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29236,"mean_force":0.09861,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5982,0.20179,0.25298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3870.0,"contact_point_centroid":[0.60197,0.18261,0.25366],"force_p95":0.16807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25267,"mean_force":0.10441,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59782,0.20068,0.25594]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02111,-0.00214],"force_p95":0.15396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22229,"mean_force":0.13253,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52577,-0.02011,0.03686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11753.0,"contact_point_centroid":[0.55662,0.09209,0.21837],"force_p95":0.13198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17912,"mean_force":0.07972,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55205,0.07354,0.21809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12494.0,"contact_point_centroid":[0.55696,0.05598,0.21915],"force_p95":0.1155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15271,"mean_force":0.07598,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5524,0.07443,0.21892]},{"body_a":"world","body_b":"grasp_target","contact_count":3304.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5141,-0.01006,0.16958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5808.0,"contact_point_centroid":[0.52526,-0.00088,0.03862],"force_p95":0.06999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11093,"mean_force":0.04513,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52531,-0.02009,0.03631]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6272.0,"contact_point_centroid":[0.52512,-0.03933,0.03815],"force_p95":0.06892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07319,"mean_force":0.04311,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52531,-0.02009,0.03632]}],"total_contact_groups":14},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6037,0.21305,0.02162],"final_tcp_position":[0.60491,0.22089,0.20415],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.69545,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3304.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53039,-0.02017,0.04233],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02033,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3162,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14822,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13884.0,"raw_peak_contact_force":0.22229,"tcp_end":[0.52528,-0.02009,0.03629],"tcp_start":[0.52528,-0.02009,0.03629],"tcp_to_object_dist_end":0.01583,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53533,-0.02006,0.1194],"object_pos_start":[0.53696,-0.02031,0.02562],"object_to_goal_dist_end":0.27346,"object_to_goal_dist_start":0.31617,"object_z_max":0.11929,"peak_contact_force":0.10603,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21940.0,"raw_peak_contact_force":0.56322,"subtask_id":"lift_clear","tcp_end":[0.52117,-0.02,0.13669],"tcp_start":[0.52528,-0.02009,0.03629],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59648,0.18007,0.28896],"object_pos_start":[0.53533,-0.02006,0.1194],"object_to_goal_dist_end":0.09548,"object_to_goal_dist_start":0.27346,"object_z_max":0.2888,"peak_contact_force":0.15267,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24247.0,"raw_peak_contact_force":0.17912,"tcp_end":[0.59147,0.17983,0.31615],"tcp_start":[0.52117,-0.02,0.13669],"tcp_to_object_dist_end":0.02764,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.60487,0.21974,0.17136],"object_pos_start":[0.59648,0.18007,0.28896],"object_to_goal_dist_end":0.03733,"object_to_goal_dist_start":0.09548,"object_z_max":0.28901,"peak_contact_force":0.15569,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7314.0,"raw_peak_contact_force":0.29236,"subtask_id":"place","tcp_end":[0.60491,0.22089,0.20415],"tcp_start":[0.59147,0.17983,0.31615],"tcp_to_object_dist_end":0.03281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6037,0.21305,0.02162],"object_pos_start":[0.60487,0.21974,0.17136],"object_to_goal_dist_end":0.18649,"object_to_goal_dist_start":0.03733,"object_z_max":0.17136,"peak_contact_force":0.27025,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1538.0,"raw_peak_contact_force":1.69545,"tcp_end":[0.59974,0.21889,0.22333],"tcp_start":[0.60491,0.22089,0.20415],"tcp_to_object_dist_end":0.20183,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41256,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00089,"descend_2.place_z_offset":-0.00129,"lift_1.lift_height":0.10427,"transport_1.approach_height":0.12629,"transport_1.transport_speed":0.02845},"optimized_scores":{"best_composite_score":0.28244,"best_fitness_score":0.65244,"best_task_score":0.34824},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.61694,0.15346,-0.00911],"force_p95":1.40805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63545,"mean_force":0.59274,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62263,0.16083,0.19396]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.54255,-0.02678,-0.00126],"force_p95":0.45952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64099,"mean_force":0.09211,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53163,-0.02751,0.03328]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":963.0,"contact_point_centroid":[0.63026,0.14334,0.17694],"force_p95":0.18648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3741,"mean_force":0.10227,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62605,0.16192,0.17869]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":970.0,"contact_point_centroid":[0.63096,0.18001,0.17736],"force_p95":0.15094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33502,"mean_force":0.08227,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6262,0.16196,0.17894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10226.0,"contact_point_centroid":[0.53078,-0.04631,0.07326],"force_p95":0.09865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32069,"mean_force":0.05875,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52902,-0.02742,0.07185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9393.0,"contact_point_centroid":[0.5307,-0.00839,0.07493],"force_p95":0.10413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31277,"mean_force":0.06265,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52903,-0.02742,0.07289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2505.0,"contact_point_centroid":[0.63102,0.14089,0.22863],"force_p95":0.16353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25035,"mean_force":0.10803,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62678,0.15928,0.23186]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02892,-0.00219],"force_p95":0.16657,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24386,"mean_force":0.13638,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53381,-0.02759,0.03204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2655.0,"contact_point_centroid":[0.63091,0.17721,0.22773],"force_p95":0.1456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23781,"mean_force":0.0961,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62679,0.15932,0.23111]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12145.0,"contact_point_centroid":[0.57774,0.07913,0.19826],"force_p95":0.12465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16284,"mean_force":0.07806,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57362,0.06065,0.19894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12164.0,"contact_point_centroid":[0.57654,0.0399,0.19642],"force_p95":0.12353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15719,"mean_force":0.07857,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57241,0.0584,0.19691]},{"body_a":"world","body_b":"grasp_target","contact_count":3432.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51818,-0.01383,0.1671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6071.0,"contact_point_centroid":[0.53304,-0.00832,0.03436],"force_p95":0.06977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11542,"mean_force":0.04319,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53333,-0.02756,0.03147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6626.0,"contact_point_centroid":[0.5329,-0.04687,0.0338],"force_p95":0.06973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07881,"mean_force":0.04133,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53334,-0.02756,0.03148]}],"total_contact_groups":14},"final_pose_error":0.00969,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63001,0.15982,0.0188],"final_tcp_position":[0.62844,0.16255,0.18392],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53852,-0.02769,0.03766],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02782,0.02545],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26023,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15817,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14501.0,"raw_peak_contact_force":0.24386,"tcp_end":[0.53331,-0.02756,0.03145],"tcp_start":[0.53331,-0.02756,0.03145],"tcp_to_object_dist_end":0.01361,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.5447,-0.02751,0.11005],"object_pos_start":[0.54553,-0.02779,0.02548],"object_to_goal_dist_end":0.22198,"object_to_goal_dist_start":0.26019,"object_z_max":0.10994,"peak_contact_force":0.1048,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19767.0,"raw_peak_contact_force":0.64099,"subtask_id":"lift_clear","tcp_end":[0.52905,-0.02742,0.12302],"tcp_start":[0.53331,-0.02756,0.03145],"tcp_to_object_dist_end":0.02033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63172,0.156,0.26179],"object_pos_start":[0.5447,-0.02751,0.11005],"object_to_goal_dist_end":0.08535,"object_to_goal_dist_start":0.22198,"object_z_max":0.26166,"peak_contact_force":0.12472,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24309.0,"raw_peak_contact_force":0.16284,"tcp_end":[0.62625,0.15612,0.28675],"tcp_start":[0.52905,-0.02742,0.12302],"tcp_to_object_dist_end":0.02555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.62577,0.16121,0.15468],"object_pos_start":[0.63172,0.156,0.26179],"object_to_goal_dist_end":0.02364,"object_to_goal_dist_start":0.08535,"object_z_max":0.26181,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5160.0,"raw_peak_contact_force":0.25035,"subtask_id":"place","tcp_end":[0.62844,0.16255,0.18392],"tcp_start":[0.62625,0.15612,0.28675],"tcp_to_object_dist_end":0.0294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63001,0.15982,0.0188],"object_pos_start":[0.62577,0.16121,0.15468],"object_to_goal_dist_end":0.15823,"object_to_goal_dist_start":0.02364,"object_z_max":0.15468,"peak_contact_force":0.40775,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2049.0,"raw_peak_contact_force":1.63545,"tcp_end":[0.62258,0.16082,0.20269],"tcp_start":[0.62844,0.16255,0.18392],"tcp_to_object_dist_end":0.18404,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```