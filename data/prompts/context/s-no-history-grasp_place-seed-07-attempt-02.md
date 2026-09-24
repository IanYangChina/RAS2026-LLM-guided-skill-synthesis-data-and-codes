## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

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

## Current Skill (Q=0.164) — your mutation base

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
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_goal
  weight: 0.4
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
    - 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_contact
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
- id: lift_1
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
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.05]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.164
- **task_score** (E): 0.324
- **fitness_score**: 0.644  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1683 |
| descend_1 | 1.00 | 1.00 | 0.1036 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.1624 |
| transport_1 | 0.00 | 1.00 | 0.1246 |
| descend_2 | 1.00 | 1.00 | 0.0849 |
| release_1 | 1.00 | 1.00 | 0.0216 |
| retract_1 | 1.00 | 1.00 | 0.1119 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.505, 0.022, 0.034) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.500, 0.022, 0.028)→(0.500, 0.022, 0.028) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.333 | 0.148 | 0.200 |
| lift_1 | lift | 0.67 / step_budget | (0.500, 0.022, 0.028)→(0.505, 0.022, 0.191) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.181) | 0.274→0.216 | 1.00 / 40.000 | 0.077 | 0.724 |
| transport_1 | approach | 0.00 / step_budget | (0.505, 0.022, 0.191)→(0.561, 0.127, 0.213) | (0.514, 0.022, 0.181)→(0.562, 0.128, 0.198) | 0.216→0.097 | 1.00 / 39.667 | 0.072 | 0.130 |
| descend_2 | descend | 1.00 / step_budget | (0.561, 0.127, 0.213)→(0.598, 0.195, 0.188) | (0.562, 0.128, 0.198)→(0.599, 0.197, 0.169) | 0.097→0.032 | 1.00 / 40.333 | 0.075 | 0.131 |
| release_1 | release | 1.00 / step_budget | (0.598, 0.195, 0.188)→(0.592, 0.193, 0.209) | (0.599, 0.197, 0.169)→(0.586, 0.197, 0.020) | 0.032→0.176 | 1.00 / 4.000 | 0.116 | 1.666 |
| retract_1 | retract | 1.00 / step_budget | (0.592, 0.193, 0.209)→(0.590, 0.193, 0.320) | (0.586, 0.197, 0.020)→(0.584, 0.195, 0.023) | 0.176→0.174 | 1.00 / 4.000 | 0.123 | 0.140 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.447
- phase_score: 0.575
- phase_breakdown.lift_object_score: 0.783
- phase_breakdown.place_goal_score: 0.199
- phase_breakdown.reach_object_score: 0.822
- phase_breakdown.grasp_contact_score: 0.869
- grasp_place_fitness: 0.706

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.706
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.447
- **Median Q (composite search score)**: 0.138
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47638,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0786,"descend_1.speed":0.03702,"descend_2.speed":0.03169,"lift_1.lift_height":0.18727,"retract_1.retract_height":0.138,"transport_1.speed":0.08921},"optimized_scores":{"best_composite_score":0.22578,"best_fitness_score":0.70578,"best_task_score":0.4474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":299.0,"contact_point_centroid":[0.60927,0.16523,-0.00477],"force_p95":0.76042,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13223,"mean_force":0.23151,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6146,0.16716,0.1478]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50861,0.03753,-0.00121],"force_p95":0.50381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73012,"mean_force":0.1031,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5003,0.03835,0.0302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18622.0,"contact_point_centroid":[0.50173,0.0575,0.1123],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3377,"mean_force":0.05367,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50265,0.03837,0.10989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21016.0,"contact_point_centroid":[0.50369,0.01932,0.10883],"force_p95":0.07495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30944,"mean_force":0.04838,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5025,0.03836,0.10747]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51258,0.03962,-0.00214],"force_p95":0.15533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21107,"mean_force":0.13274,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50218,0.03852,0.02891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6057.0,"contact_point_centroid":[0.50292,0.01941,0.02956],"force_p95":0.07492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16774,"mean_force":0.04346,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5017,0.03848,0.02838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1217.0,"contact_point_centroid":[0.61471,0.18692,0.13849],"force_p95":0.06944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15437,"mean_force":0.04215,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61905,0.16847,0.1351]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1237.0,"contact_point_centroid":[0.62327,0.14962,0.13547],"force_p95":0.07072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15034,"mean_force":0.04271,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61902,0.16846,0.13504]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12640.0,"contact_point_centroid":[0.59758,0.1668,0.15993],"force_p95":0.06984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13863,"mean_force":0.04819,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60154,0.14825,0.15684]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5026,0.01776,0.21866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12640.0,"contact_point_centroid":[0.60547,0.12943,0.15753],"force_p95":0.07113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13016,"mean_force":0.04941,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60154,0.14825,0.15684]},{"body_a":"world","body_b":"grasp_target","contact_count":3132.0,"contact_point_centroid":[0.60916,0.16515,-0.00198],"force_p95":0.12317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12519,"mean_force":0.12257,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61148,0.16628,0.21818]},{"body_a":"world","body_b":"grasp_target","contact_count":1424.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50572,0.03748,0.08555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20124.0,"contact_point_centroid":[0.54846,0.06535,0.18761],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12058,"mean_force":0.04889,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54579,0.08433,0.18626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19796.0,"contact_point_centroid":[0.54399,0.10392,0.18877],"force_p95":0.06976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11513,"mean_force":0.04894,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54636,0.08501,0.18622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5358.0,"contact_point_centroid":[0.50105,0.05772,0.03094],"force_p95":0.08402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0876,"mean_force":0.04962,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5017,0.03849,0.02839]}],"total_contact_groups":16},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60916,0.16515,0.02602],"final_tcp_position":[0.61197,0.16638,0.2821],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.13223,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50751,0.0363,0.13767],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1424.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50694,0.0389,0.03419],"tcp_start":[0.50751,0.0363,0.13767],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03892,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21297,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15261,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13219.0,"raw_peak_contact_force":0.21107,"tcp_end":[0.50168,0.03848,0.02836],"tcp_start":[0.50168,0.03848,0.02836],"tcp_to_object_dist_end":0.01116,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51709,0.03944,0.18162],"object_pos_start":[0.51248,0.03894,0.02562],"object_to_goal_dist_end":0.17679,"object_to_goal_dist_start":0.21294,"object_z_max":0.18143,"peak_contact_force":0.08029,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39782.0,"raw_peak_contact_force":0.73012,"subtask_id":"lift_object","tcp_end":[0.50791,0.03861,0.19127],"tcp_start":[0.50168,0.03848,0.02836],"tcp_to_object_dist_end":0.01334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57636,0.12233,0.17156],"object_pos_start":[0.51709,0.03944,0.18162],"object_to_goal_dist_end":0.07646,"object_to_goal_dist_start":0.17679,"object_z_max":0.18176,"peak_contact_force":0.07072,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39920.0,"raw_peak_contact_force":0.12058,"subtask_id":"place_goal","tcp_end":[0.57971,0.12234,0.18623],"tcp_start":[0.50791,0.03861,0.19127],"tcp_to_object_dist_end":0.01505,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.61941,0.16974,0.12136],"object_pos_start":[0.57636,0.12233,0.17156],"object_to_goal_dist_end":0.02519,"object_to_goal_dist_start":0.07646,"object_z_max":0.17156,"peak_contact_force":0.0711,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":25280.0,"raw_peak_contact_force":0.13863,"tcp_end":[0.62086,0.16887,0.13858],"tcp_start":[0.57971,0.12234,0.18623],"tcp_to_object_dist_end":0.0173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60907,0.1651,0.02645],"object_pos_start":[0.61941,0.16974,0.12136],"object_to_goal_dist_end":0.12024,"object_to_goal_dist_start":0.02519,"object_z_max":0.12136,"peak_contact_force":0.1138,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2753.0,"raw_peak_contact_force":1.13223,"tcp_end":[0.6145,0.16713,0.15884],"tcp_start":[0.62086,0.16887,0.13858],"tcp_to_object_dist_end":0.13252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.60916,0.16515,0.02602],"object_pos_start":[0.60907,0.1651,0.02645],"object_to_goal_dist_end":0.12065,"object_to_goal_dist_start":0.12024,"object_z_max":0.02647,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3132.0,"raw_peak_contact_force":0.12519,"tcp_end":[0.61197,0.16638,0.2821],"tcp_start":[0.6145,0.16713,0.15884],"tcp_to_object_dist_end":0.2561,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26639,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09429,"descend_1.speed":0.02626,"descend_2.speed":0.04516,"lift_1.lift_height":0.24175,"retract_1.retract_height":0.0905,"transport_1.speed":0.14979},"optimized_scores":{"best_composite_score":0.1295,"best_fitness_score":0.6095,"best_task_score":0.25384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.56363,0.21646,-0.00786],"force_p95":1.2724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90723,"mean_force":0.39514,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57234,0.22299,0.23669]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.47971,0.04621,-0.00122],"force_p95":0.4322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68556,"mean_force":0.08544,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47109,0.04711,0.03102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17996.0,"contact_point_centroid":[0.47114,0.0662,0.11218],"force_p95":0.08021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32858,"mean_force":0.05519,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47215,0.04704,0.10959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21416.0,"contact_point_centroid":[0.47355,0.02805,0.10991],"force_p95":0.07495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31881,"mean_force":0.04754,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4721,0.04704,0.10874]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48279,0.04858,-0.00216],"force_p95":0.15973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22219,"mean_force":0.13429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47296,0.04731,0.02953]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5766.0,"contact_point_centroid":[0.47462,0.02821,0.03033],"force_p95":0.08138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18651,"mean_force":0.04554,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47249,0.04727,0.02905]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.56371,0.21656,-0.002],"force_p95":0.13549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16985,"mean_force":0.12126,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57007,0.22208,0.28062]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48924,0.02169,0.21927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20721.0,"contact_point_centroid":[0.50892,0.08383,0.21517],"force_p95":0.07036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13509,"mean_force":0.0477,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5056,0.10264,0.21366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18886.0,"contact_point_centroid":[0.50412,0.12425,0.21793],"force_p95":0.07592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13268,"mean_force":0.05115,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50723,0.10545,0.21495]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47739,0.04596,0.08615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1349.0,"contact_point_centroid":[0.58222,0.20613,0.22066],"force_p95":0.0658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10872,"mean_force":0.03911,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57552,0.22439,0.21964]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1323.0,"contact_point_centroid":[0.56981,0.24243,0.22399],"force_p95":0.06456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10863,"mean_force":0.03858,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57555,0.2244,0.21969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17855.0,"contact_point_centroid":[0.55219,0.2117,0.23007],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10517,"mean_force":0.04751,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55768,0.19357,0.22681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17765.0,"contact_point_centroid":[0.56318,0.17502,0.2275],"force_p95":0.07053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10265,"mean_force":0.04903,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55759,0.19344,0.22683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5365.0,"contact_point_centroid":[0.47158,0.06649,0.03153],"force_p95":0.08749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1015,"mean_force":0.04982,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47249,0.04727,0.02906]}],"total_contact_groups":16},"final_pose_error":0.01417,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5636,0.21636,0.02602],"final_tcp_position":[0.57024,0.22212,0.32052],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.90723,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48016,0.04447,0.13839],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47758,0.04775,0.03431],"tcp_start":[0.48016,0.04447,0.13839],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04772,0.02554],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29094,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15591,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12935.0,"raw_peak_contact_force":0.22219,"tcp_end":[0.47247,0.04726,0.02903],"tcp_start":[0.47247,0.04726,0.02903],"tcp_to_object_dist_end":0.01083,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48506,0.0482,0.18121],"object_pos_start":[0.48272,0.04775,0.02557],"object_to_goal_dist_end":0.2108,"object_to_goal_dist_start":0.2909,"object_z_max":0.18102,"peak_contact_force":0.07968,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39551.0,"raw_peak_contact_force":0.68556,"subtask_id":"lift_object","tcp_end":[0.47614,0.04725,0.1921],"tcp_start":[0.47247,0.04726,0.02903],"tcp_to_object_dist_end":0.0141,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53692,0.15484,0.22227],"object_pos_start":[0.48506,0.0482,0.18121],"object_to_goal_dist_end":0.08699,"object_to_goal_dist_start":0.2108,"object_z_max":0.22225,"peak_contact_force":0.07012,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39607.0,"raw_peak_contact_force":0.13509,"subtask_id":"place_goal","tcp_end":[0.53555,0.15386,0.23767],"tcp_start":[0.47614,0.04725,0.1921],"tcp_to_object_dist_end":0.01549,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.57842,0.22682,0.20424],"object_pos_start":[0.53692,0.15484,0.22227],"object_to_goal_dist_end":0.02655,"object_to_goal_dist_start":0.08699,"object_z_max":0.22227,"peak_contact_force":0.06644,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":35620.0,"raw_peak_contact_force":0.10517,"tcp_end":[0.57689,0.22482,0.22284],"tcp_start":[0.53555,0.15386,0.23767],"tcp_to_object_dist_end":0.01877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56913,0.22089,0.02187],"object_pos_start":[0.57842,0.22682,0.20424],"object_to_goal_dist_end":0.20915,"object_to_goal_dist_start":0.02655,"object_z_max":0.20424,"peak_contact_force":0.16943,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2863.0,"raw_peak_contact_force":1.90723,"tcp_end":[0.5723,0.22299,0.24402],"tcp_start":[0.57689,0.22482,0.22284],"tcp_to_object_dist_end":0.22218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5636,0.21636,0.02602],"object_pos_start":[0.56913,0.22089,0.02187],"object_to_goal_dist_end":0.20566,"object_to_goal_dist_start":0.20915,"object_z_max":0.02675,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.16985,"tcp_end":[0.57024,0.22212,0.32052],"tcp_start":[0.5723,0.22299,0.24402],"tcp_to_object_dist_end":0.29463,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53629,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07058,"descend_1.speed":0.0346,"descend_2.speed":0.04986,"lift_1.lift_height":0.20374,"retract_1.retract_height":0.15023,"transport_1.speed":0.14784},"optimized_scores":{"best_composite_score":0.13774,"best_fitness_score":0.61774,"best_task_score":0.27192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":178.0,"contact_point_centroid":[0.57864,0.20415,-0.008],"force_p95":1.14372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95888,"mean_force":0.41141,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58971,0.18987,0.21589]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53383,-0.02074,-0.00113],"force_p95":0.5345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75775,"mean_force":0.09936,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52423,-0.02094,0.0293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19223.0,"contact_point_centroid":[0.52544,-0.04019,0.11043],"force_p95":0.07633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33289,"mean_force":0.05233,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52623,-0.02103,0.10803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21541.0,"contact_point_centroid":[0.5265,-0.00193,0.10747],"force_p95":0.07082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33166,"mean_force":0.04767,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52612,-0.02102,0.10595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1205.0,"contact_point_centroid":[0.58847,0.21002,0.20138],"force_p95":0.08827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21675,"mean_force":0.05635,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59292,0.19106,0.19792]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53702,-0.0214,-0.00204],"force_p95":0.13596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16538,"mean_force":0.12641,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5262,-0.02097,0.02815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18484.0,"contact_point_centroid":[0.57735,0.17039,0.20844],"force_p95":0.07635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14961,"mean_force":0.0523,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58118,0.15174,0.20545]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1246.0,"contact_point_centroid":[0.59876,0.17315,0.19836],"force_p95":0.06866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14399,"mean_force":0.0401,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5933,0.1912,0.19864]},{"body_a":"world","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5137,-0.00964,0.21804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21995.0,"contact_point_centroid":[0.55036,0.02661,0.20212],"force_p95":0.06703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13465,"mean_force":0.04543,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54915,0.04568,0.20068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20743.0,"contact_point_centroid":[0.58626,0.1347,0.20547],"force_p95":0.06851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13382,"mean_force":0.04762,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58169,0.15322,0.20532]},{"body_a":"world","body_b":"grasp_target","contact_count":3492.0,"contact_point_centroid":[0.57961,0.2036,-0.002],"force_p95":0.12311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12513,"mean_force":0.12111,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58739,0.18908,0.28856]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52905,-0.0203,0.08495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19909.0,"contact_point_centroid":[0.54751,0.06382,0.20268],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11626,"mean_force":0.04945,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54885,0.04471,0.20044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6416.0,"contact_point_centroid":[0.52592,-0.00185,0.02888],"force_p95":0.06803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09995,"mean_force":0.04144,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5257,-0.02096,0.02759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5306.0,"contact_point_centroid":[0.52443,-0.0402,0.03027],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08608,"mean_force":0.04944,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5257,-0.02096,0.02759]}],"total_contact_groups":16},"final_pose_error":0.01436,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57961,0.2036,0.01602],"final_tcp_position":[0.58799,0.18924,0.35874],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.95888,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53011,-0.01963,0.13691],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53109,-0.02103,0.03385],"tcp_start":[0.53011,-0.01963,0.13691],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02126,0.02585],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3168,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13606,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.16538,"tcp_end":[0.52568,-0.02096,0.02756],"tcp_start":[0.52568,-0.02096,0.02756],"tcp_to_object_dist_end":0.01135,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54092,-0.02151,0.17944],"object_pos_start":[0.53689,-0.02129,0.02586],"object_to_goal_dist_end":0.26025,"object_to_goal_dist_start":0.31681,"object_z_max":0.17925,"peak_contact_force":0.07189,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40908.0,"raw_peak_contact_force":0.75775,"subtask_id":"lift_object","tcp_end":[0.53122,-0.02115,0.18842],"tcp_start":[0.52568,-0.02096,0.02756],"tcp_to_object_dist_end":0.01322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57405,0.10541,0.20162],"object_pos_start":[0.54092,-0.02151,0.17944],"object_to_goal_dist_end":0.12774,"object_to_goal_dist_start":0.26025,"object_z_max":0.20158,"peak_contact_force":0.07537,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41904.0,"raw_peak_contact_force":0.13465,"subtask_id":"place_goal","tcp_end":[0.56778,0.10379,0.21609],"tcp_start":[0.53122,-0.02115,0.18842],"tcp_to_object_dist_end":0.01585,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59815,0.1941,0.1828],"object_pos_start":[0.57405,0.10541,0.20162],"object_to_goal_dist_end":0.04343,"object_to_goal_dist_start":0.12774,"object_z_max":0.20162,"peak_contact_force":0.08884,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39227.0,"raw_peak_contact_force":0.14961,"tcp_end":[0.59476,0.19149,0.20181],"tcp_start":[0.56778,0.10379,0.21609],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58003,0.20383,0.01135],"object_pos_start":[0.59815,0.1941,0.1828],"object_to_goal_dist_end":0.19982,"object_to_goal_dist_start":0.04343,"object_z_max":0.1828,"peak_contact_force":0.06546,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2629.0,"raw_peak_contact_force":1.95888,"tcp_end":[0.58967,0.18987,0.22275],"tcp_start":[0.59476,0.19149,0.20181],"tcp_to_object_dist_end":0.21208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.57961,0.2036,0.01602],"object_pos_start":[0.58003,0.20383,0.01135],"object_to_goal_dist_end":0.19534,"object_to_goal_dist_start":0.19982,"object_z_max":0.01664,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.12513,"tcp_end":[0.58799,0.18924,0.35874],"tcp_start":[0.58967,0.18987,0.22275],"tcp_to_object_dist_end":0.34312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```