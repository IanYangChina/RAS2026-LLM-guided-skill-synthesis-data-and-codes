## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5097 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5096 | 1.00 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1736 | 0.39 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1339 | 0.31 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3008 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=0.510) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: lift_height
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.21
  weight: 0.3
- id: place_target
  target_entity: object
  weight: 0.7
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
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
    orientation:
      mode: keep_current
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
    offset_along_axis:
      distance: 0.21
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.21
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_height
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
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
    speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_target

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.21, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.510
- **task_score** (E): 1.000
- **fitness_score**: 0.980  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0864 |
| descend_1 | 1.00 | 1.00 | 0.1877 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1510 |
| transport_1 | 1.00 | 1.00 | 0.2347 |
| descend_2 | 1.00 | 1.00 | 0.0356 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, -0.012, 0.222) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 8.534 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.492, -0.012, 0.222)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.134 | 0.180 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.477, -0.015, 0.177) | (0.493, -0.015, 0.026)→(0.492, -0.015, 0.171) | 0.281→0.240 | 1.00 / 31.333 | 0.094 | 0.671 |
| transport_1 | approach | 1.00 / step_budget | (0.477, -0.015, 0.177)→(0.624, 0.164, 0.204) | (0.492, -0.015, 0.171)→(0.628, 0.164, 0.184) | 0.240→0.024 | 1.00 / 32.333 | 0.106 | 0.183 |
| descend_2 | descend | 1.00 / step_budget | (0.624, 0.164, 0.204)→(0.629, 0.170, 0.170) | (0.628, 0.164, 0.184)→(0.634, 0.171, 0.148) | 0.024→0.018 | 1.00 / 30.333 | 0.104 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.131
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.632
- phase_breakdown.place_target_score: 0.821
- phase_breakdown.lift_height_score: 0.189
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.511
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.421


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83439,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.199,"approach_1.speed":0.0102,"descend_1.speed":0.04631,"descend_2.speed":0.12909,"lift_1.lift_distance":0.16617,"lift_1.speed":0.06345,"transport_1.speed":0.19758},"optimized_scores":{"best_composite_score":0.51057,"best_fitness_score":0.98057,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.47323,-0.01931,-0.00137],"force_p95":0.57498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65959,"mean_force":0.1748,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46294,-0.01959,0.02851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8364.0,"contact_point_centroid":[0.46163,-0.00045,0.09816],"force_p95":0.09723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29499,"mean_force":0.05955,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46044,-0.01951,0.09601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8816.0,"contact_point_centroid":[0.46164,-0.03853,0.09567],"force_p95":0.09615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29176,"mean_force":0.05722,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46042,-0.01951,0.094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.62677,0.13278,0.21413],"force_p95":0.1194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2747,"mean_force":0.09134,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62122,0.15161,0.21246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1541.0,"contact_point_centroid":[0.62501,0.17001,0.21286],"force_p95":0.1008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21637,"mean_force":0.07017,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62117,0.15156,0.21269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8112.0,"contact_point_centroid":[0.54342,0.04698,0.20072],"force_p95":0.11692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2104,"mean_force":0.08164,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53996,0.06583,0.19982]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18686,"mean_force":0.12661,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46512,-0.01964,0.02835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9286.0,"contact_point_centroid":[0.54856,0.08987,0.20209],"force_p95":0.10236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.172,"mean_force":0.06843,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54524,0.07137,0.20168]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.47616,-0.02015,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48907,-0.0073,0.2704]},{"body_a":"world","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47366,-0.01791,0.13533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.46372,-0.00036,0.02992],"force_p95":0.06582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09359,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.464,-0.01961,0.02726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5399.0,"contact_point_centroid":[0.46359,-0.03886,0.02942],"force_p95":0.06479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08782,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46401,-0.01961,0.02726]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63204,0.15505,0.17144],"final_tcp_position":[0.62429,0.15485,0.19521],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.65959,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47789,-0.01613,0.23783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2792.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47184,-0.01978,0.03502],"tcp_start":[0.47789,-0.01613,0.23783],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01963,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28824,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13517,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12265.0,"raw_peak_contact_force":0.18686,"tcp_end":[0.46397,-0.01961,0.02723],"tcp_start":[0.47184,-0.01978,0.03502],"tcp_to_object_dist_end":0.01214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.4778,-0.01951,0.16708],"object_pos_start":[0.47603,-0.01963,0.02582],"object_to_goal_dist_end":0.23676,"object_to_goal_dist_start":0.28824,"object_z_max":0.16679,"peak_contact_force":0.10717,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17258.0,"raw_peak_contact_force":0.65959,"subtask_id":"lift_height","tcp_end":[0.46051,-0.01949,0.17375],"tcp_start":[0.46397,-0.01961,0.02723],"tcp_to_object_dist_end":0.01854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.62622,0.14884,0.20523],"object_pos_start":[0.4778,-0.01951,0.16708],"object_to_goal_dist_end":0.01912,"object_to_goal_dist_start":0.23676,"object_z_max":0.20519,"peak_contact_force":0.1172,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17398.0,"raw_peak_contact_force":0.2104,"tcp_end":[0.61947,0.14884,0.22815],"tcp_start":[0.46051,-0.01949,0.17375],"tcp_to_object_dist_end":0.02389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.63204,0.15505,0.17144],"object_pos_start":[0.62622,0.14884,0.20523],"object_to_goal_dist_end":0.01904,"object_to_goal_dist_start":0.01912,"object_z_max":0.20523,"peak_contact_force":0.11645,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2637.0,"raw_peak_contact_force":0.2747,"subtask_id":"place_target","tcp_end":[0.62429,0.15485,0.19521],"tcp_start":[0.61947,0.14884,0.22815],"tcp_to_object_dist_end":0.025,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18637,"approach_1.speed":0.07583,"descend_1.speed":0.01711,"descend_2.speed":0.08816,"lift_1.lift_distance":0.15001,"lift_1.speed":0.05159,"transport_1.speed":0.19197},"optimized_scores":{"best_composite_score":0.51123,"best_fitness_score":0.98123,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45578,-0.02538,-0.00142],"force_p95":0.55814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63677,"mean_force":0.164,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44588,-0.02557,0.0288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8102.0,"contact_point_centroid":[0.44359,-0.00629,0.0921],"force_p95":0.07825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28135,"mean_force":0.05392,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44357,-0.02546,0.0896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8699.0,"contact_point_centroid":[0.44351,-0.04458,0.09208],"force_p95":0.07458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28004,"mean_force":0.05098,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44356,-0.02546,0.09012]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02614,-0.00206],"force_p95":0.14042,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19327,"mean_force":0.1275,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.448,-0.02565,0.02871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.61937,0.21839,0.13811],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17615,"mean_force":0.05114,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61915,0.1992,0.13632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.61945,0.1801,0.13829],"force_p95":0.07767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.161,"mean_force":0.04975,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61915,0.1992,0.13632]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.45856,-0.02632,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48136,-0.01038,0.26312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14524.0,"contact_point_centroid":[0.53156,0.10679,0.15731],"force_p95":0.07498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12732,"mean_force":0.04954,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53141,0.0877,0.15534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14197.0,"contact_point_centroid":[0.53261,0.06981,0.15737],"force_p95":0.07653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1263,"mean_force":0.05065,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53245,0.08899,0.15537]},{"body_a":"world","body_b":"grasp_target","contact_count":2684.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45701,-0.02391,0.12891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4814.0,"contact_point_centroid":[0.4469,-0.00637,0.02998],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09875,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.02561,0.02769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5418.0,"contact_point_centroid":[0.44638,-0.04484,0.02941],"force_p95":0.06506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0825,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44692,-0.02561,0.02769]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62175,0.20329,0.09971],"final_tcp_position":[0.62241,0.20322,0.11762],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":25.35692,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":25.35692,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46216,-0.02208,0.22468],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2684.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4545,-0.02587,0.0349],"tcp_start":[0.46216,-0.02208,0.22468],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02562,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30325,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13745,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12032.0,"raw_peak_contact_force":0.19327,"tcp_end":[0.44689,-0.0256,0.02766],"tcp_start":[0.4545,-0.02587,0.0349],"tcp_to_object_dist_end":0.01171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.45504,-0.02547,0.15286],"object_pos_start":[0.45844,-0.02562,0.02579],"object_to_goal_dist_end":0.29456,"object_to_goal_dist_start":0.30325,"object_z_max":0.15257,"peak_contact_force":0.08011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16879.0,"raw_peak_contact_force":0.63677,"subtask_id":"lift_height","tcp_end":[0.44353,-0.02544,0.15809],"tcp_start":[0.44689,-0.0256,0.02766],"tcp_to_object_dist_end":0.01264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.61565,0.19573,0.13791],"object_pos_start":[0.45504,-0.02547,0.15286],"object_to_goal_dist_end":0.03052,"object_to_goal_dist_start":0.29456,"object_z_max":0.15323,"peak_contact_force":0.07858,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28721.0,"raw_peak_contact_force":0.12732,"tcp_end":[0.61752,0.19566,0.15536],"tcp_start":[0.44353,-0.02544,0.15809],"tcp_to_object_dist_end":0.01755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.62175,0.20329,0.09971],"object_pos_start":[0.61565,0.19573,0.13791],"object_to_goal_dist_end":0.01738,"object_to_goal_dist_start":0.03052,"object_z_max":0.13791,"peak_contact_force":0.07712,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5080.0,"raw_peak_contact_force":0.17615,"subtask_id":"place_target","tcp_end":[0.62241,0.20322,0.11762],"tcp_start":[0.61752,0.19566,0.15536],"tcp_to_object_dist_end":0.01792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32319,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16953,"approach_1.speed":0.08096,"descend_1.speed":0.01907,"descend_2.speed":0.13103,"lift_1.lift_distance":0.19564,"lift_1.speed":0.06029,"transport_1.speed":0.15582},"optimized_scores":{"best_composite_score":0.50728,"best_fitness_score":0.97728,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.54068,0.00048,-0.00138],"force_p95":0.57278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71796,"mean_force":0.18683,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52877,0.00084,0.02531]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11249.0,"contact_point_centroid":[0.52739,-0.01825,0.11289],"force_p95":0.08575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32108,"mean_force":0.05866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52605,0.0008,0.11085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11389.0,"contact_point_centroid":[0.52743,0.01983,0.10956],"force_p95":0.08598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31154,"mean_force":0.05812,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52608,0.0008,0.10773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.64158,0.13064,0.21389],"force_p95":0.11836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28342,"mean_force":0.08114,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63799,0.14961,0.21347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1678.0,"contact_point_centroid":[0.6406,0.16806,0.21356],"force_p95":0.09448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22103,"mean_force":0.06341,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.638,0.14961,0.21346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6240.0,"contact_point_centroid":[0.58362,0.0551,0.21383],"force_p95":0.11987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21228,"mean_force":0.08864,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5808,0.07403,0.21311]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15974,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53125,0.00089,0.02563]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7819.0,"contact_point_centroid":[0.58665,0.09632,0.21429],"force_p95":0.09871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1518,"mean_force":0.06547,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58372,0.07789,0.21393]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51667,0.00046,0.25179]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53581,0.00098,0.11872]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53096,-0.01833,0.0269],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11053,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53,0.00087,0.0242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53091,0.01995,0.02601],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09648,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53,0.00087,0.0242]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64718,0.15351,0.17412],"final_tcp_position":[0.64071,0.15321,0.19642],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.71796,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53588,0.00096,0.2046],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5387,0.00103,0.03428],"tcp_start":[0.53588,0.00096,0.2046],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12963,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15974,"tcp_end":[0.52996,0.00087,0.02416],"tcp_start":[0.5387,0.00103,0.03428],"tcp_to_object_dist_end":0.01429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.54235,0.00085,0.19407],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.18924,"object_to_goal_dist_start":0.25053,"object_z_max":0.19382,"peak_contact_force":0.09357,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22723.0,"raw_peak_contact_force":0.71796,"subtask_id":"lift_height","tcp_end":[0.52651,0.00081,0.20024],"tcp_start":[0.52996,0.00087,0.02416],"tcp_to_object_dist_end":0.017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.64166,0.14648,0.2081],"object_pos_start":[0.54235,0.00085,0.19407],"object_to_goal_dist_end":0.02142,"object_to_goal_dist_start":0.18924,"object_z_max":0.20808,"peak_contact_force":0.12195,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14059.0,"raw_peak_contact_force":0.21228,"tcp_end":[0.63649,0.14633,0.22968],"tcp_start":[0.52651,0.00081,0.20024],"tcp_to_object_dist_end":0.0222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.64718,0.15351,0.17412],"object_pos_start":[0.64166,0.14648,0.2081],"object_to_goal_dist_end":0.01759,"object_to_goal_dist_start":0.02142,"object_z_max":0.2081,"peak_contact_force":0.11807,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2938.0,"raw_peak_contact_force":0.28342,"subtask_id":"place_target","tcp_end":[0.64071,0.15321,0.19642],"tcp_start":[0.63649,0.14633,0.22968],"tcp_to_object_dist_end":0.02322,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```