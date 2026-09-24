## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5094 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5097 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5097 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5098 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5039 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.509) — your mutation base

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

- **Composite score**: 0.509
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1395 |
| descend_1 | 1.00 | 1.00 | 0.1336 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1483 |
| transport_1 | 1.00 | 1.00 | 0.2373 |
| descend_2 | 1.00 | 1.00 | 0.0353 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, -0.013, 0.168) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 17.174 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.492, -0.013, 0.168)→(0.488, -0.015, 0.034) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.034)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.134 | 0.177 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.477, -0.015, 0.174) | (0.493, -0.015, 0.026)→(0.491, -0.015, 0.169) | 0.281→0.242 | 1.00 / 32.333 | 0.090 | 0.683 |
| transport_1 | approach | 1.00 / step_budget | (0.477, -0.015, 0.174)→(0.625, 0.164, 0.204) | (0.491, -0.015, 0.169)→(0.627, 0.164, 0.185) | 0.242→0.025 | 1.00 / 35.667 | 0.088 | 0.156 |
| descend_2 | descend | 1.00 / step_budget | (0.625, 0.164, 0.204)→(0.629, 0.170, 0.170) | (0.627, 0.164, 0.185)→(0.633, 0.171, 0.149) | 0.025→0.017 | 1.00 / 33.333 | 0.103 | 0.207 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.141
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.640
- phase_breakdown.place_target_score: 0.820
- phase_breakdown.lift_height_score: 0.219
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.510
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.528


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1037,"average_solve_count":270.0,"average_success_count":270.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11354,"approach_1.speed":0.08779,"descend_1.speed":0.0237,"descend_2.speed":0.11915,"lift_1.lift_distance":0.19539,"lift_1.speed":0.05427,"transport_1.speed":0.17883},"optimized_scores":{"best_composite_score":0.51031,"best_fitness_score":0.98031,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.47329,-0.01983,-0.00139],"force_p95":0.54917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64996,"mean_force":0.18564,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46273,-0.01964,0.02805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11024.0,"contact_point_centroid":[0.46057,-0.00042,0.11451],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29157,"mean_force":0.05445,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46035,-0.01956,0.11201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11534.0,"contact_point_centroid":[0.46054,-0.03866,0.11317],"force_p95":0.07613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28971,"mean_force":0.05252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46035,-0.01956,0.11104]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02002,-0.00204],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17511,"mean_force":0.12614,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46492,-0.01968,0.02802]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.6212,0.17042,0.21536],"force_p95":0.0699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16617,"mean_force":0.04443,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62081,0.15121,0.21236]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11147.0,"contact_point_centroid":[0.53965,0.04674,0.21709],"force_p95":0.08023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16539,"mean_force":0.0546,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54032,0.06596,0.21506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2378.0,"contact_point_centroid":[0.62091,0.13194,0.21572],"force_p95":0.07227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15262,"mean_force":0.04802,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62077,0.15116,0.21264]},{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48688,-0.00881,0.22706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12849.0,"contact_point_centroid":[0.54056,0.08533,0.21719],"force_p95":0.07226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13113,"mean_force":0.04789,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54062,0.06631,0.21508]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47178,-0.01894,0.0937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.46357,-0.00041,0.02978],"force_p95":0.06609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09112,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4638,-0.01966,0.02693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46344,-0.03891,0.02927],"force_p95":0.06459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08737,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4638,-0.01966,0.02693]}],"total_contact_groups":12},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62559,0.15491,0.17442],"final_tcp_position":[0.62416,0.15471,0.19501],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.64996,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1792.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47489,-0.01816,0.15321],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47158,-0.01983,0.03465],"tcp_start":[0.47489,-0.01816,0.15321],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01968,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13347,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17511,"tcp_end":[0.46377,-0.01966,0.0269],"tcp_start":[0.47158,-0.01983,0.03465],"tcp_to_object_dist_end":0.01231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.47215,-0.01951,0.19661],"object_pos_start":[0.47603,-0.01968,0.02584],"object_to_goal_dist_end":0.23947,"object_to_goal_dist_start":0.28826,"object_z_max":0.19633,"peak_contact_force":0.08094,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22638.0,"raw_peak_contact_force":0.64996,"subtask_id":"lift_height","tcp_end":[0.46065,-0.01955,0.2028],"tcp_start":[0.46377,-0.01966,0.0269],"tcp_to_object_dist_end":0.01306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.61908,0.14831,0.20951],"object_pos_start":[0.47215,-0.01951,0.19661],"object_to_goal_dist_end":0.02551,"object_to_goal_dist_start":0.23947,"object_z_max":0.2095,"peak_contact_force":0.07373,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23996.0,"raw_peak_contact_force":0.16539,"tcp_end":[0.61873,0.14801,0.22967],"tcp_start":[0.46065,-0.01955,0.2028],"tcp_to_object_dist_end":0.02017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.62559,0.15491,0.17442],"object_pos_start":[0.61908,0.14831,0.20951],"object_to_goal_dist_end":0.01719,"object_to_goal_dist_start":0.02551,"object_z_max":0.20951,"peak_contact_force":0.07134,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5045.0,"raw_peak_contact_force":0.16617,"subtask_id":"place_target","tcp_end":[0.62416,0.15471,0.19501],"tcp_start":[0.61873,0.14801,0.22967],"tcp_to_object_dist_end":0.02064,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18248,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19979,"approach_1.speed":0.06072,"descend_1.speed":0.02656,"descend_2.speed":0.13579,"lift_1.lift_distance":0.15731,"lift_1.speed":0.05191,"transport_1.speed":0.14936},"optimized_scores":{"best_composite_score":0.51129,"best_fitness_score":0.98129,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45576,-0.02537,-0.00142],"force_p95":0.55867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63819,"mean_force":0.16693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44592,-0.02556,0.02884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8610.0,"contact_point_centroid":[0.44361,-0.00628,0.09571],"force_p95":0.07805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28148,"mean_force":0.05366,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4436,-0.02545,0.09325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9209.0,"contact_point_centroid":[0.44352,-0.04457,0.09552],"force_p95":0.07453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27976,"mean_force":0.0509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44359,-0.02545,0.09357]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02614,-0.00206],"force_p95":0.14071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19364,"mean_force":0.12756,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44804,-0.02563,0.02875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2560.0,"contact_point_centroid":[0.61928,0.21822,0.13839],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17391,"mean_force":0.05113,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61905,0.19903,0.13659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2560.0,"contact_point_centroid":[0.61935,0.17993,0.13857],"force_p95":0.07663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15886,"mean_force":0.04972,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61905,0.19903,0.13659]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.45856,-0.02632,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48186,-0.01015,0.26917]},{"body_a":"world","body_b":"grasp_target","contact_count":2844.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4575,-0.02368,0.13503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15683.0,"contact_point_centroid":[0.53177,0.107,0.16099],"force_p95":0.07648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12131,"mean_force":0.0485,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53162,0.088,0.15912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13543.0,"contact_point_centroid":[0.53318,0.0705,0.16129],"force_p95":0.08165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11414,"mean_force":0.05556,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53301,0.08972,0.15909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4814.0,"contact_point_centroid":[0.44694,-0.00636,0.02999],"force_p95":0.06808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0989,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44696,-0.0256,0.02773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.44641,-0.04483,0.02941],"force_p95":0.06509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08234,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44696,-0.0256,0.02773]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62205,0.20328,0.09978],"final_tcp_position":[0.62238,0.20315,0.11773],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":21.03465,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":21.03465,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":968.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46306,-0.02164,0.23725],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2844.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45454,-0.02586,0.03494],"tcp_start":[0.46306,-0.02164,0.23725],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02561,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13767,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12033.0,"raw_peak_contact_force":0.19364,"tcp_end":[0.44693,-0.02559,0.0277],"tcp_start":[0.45454,-0.02586,0.03494],"tcp_to_object_dist_end":0.01167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.45502,-0.02545,0.16008],"object_pos_start":[0.45844,-0.02561,0.02579],"object_to_goal_dist_end":0.29559,"object_to_goal_dist_start":0.30324,"object_z_max":0.1598,"peak_contact_force":0.07949,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17897.0,"raw_peak_contact_force":0.63819,"subtask_id":"lift_height","tcp_end":[0.44363,-0.02543,0.16558],"tcp_start":[0.44693,-0.02559,0.0277],"tcp_to_object_dist_end":0.01265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.61588,0.19551,0.13837],"object_pos_start":[0.45502,-0.02545,0.16008],"object_to_goal_dist_end":0.03087,"object_to_goal_dist_start":0.29559,"object_z_max":0.1604,"peak_contact_force":0.07766,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29226.0,"raw_peak_contact_force":0.12131,"tcp_end":[0.61739,0.19542,0.15587],"tcp_start":[0.44363,-0.02543,0.16558],"tcp_to_object_dist_end":0.01756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.62205,0.20328,0.09978],"object_pos_start":[0.61588,0.19551,0.13837],"object_to_goal_dist_end":0.01718,"object_to_goal_dist_start":0.03087,"object_z_max":0.13837,"peak_contact_force":0.07592,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5120.0,"raw_peak_contact_force":0.17391,"subtask_id":"place_target","tcp_end":[0.62238,0.20315,0.11773],"tcp_start":[0.61739,0.19542,0.15587],"tcp_to_object_dist_end":0.01795,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72105,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07656,"approach_1.speed":0.07157,"descend_1.speed":0.04195,"descend_2.speed":0.14385,"lift_1.lift_distance":0.15034,"lift_1.speed":0.07018,"transport_1.speed":0.17649},"optimized_scores":{"best_composite_score":0.50652,"best_fitness_score":0.97652,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5402,0.00071,-0.00138],"force_p95":0.62483,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76099,"mean_force":0.21083,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52834,0.00083,0.0248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7686.0,"contact_point_centroid":[0.52717,-0.01824,0.08807],"force_p95":0.09746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33691,"mean_force":0.06211,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52551,0.00079,0.08607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8032.0,"contact_point_centroid":[0.52705,0.01979,0.0853],"force_p95":0.09857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32462,"mean_force":0.05997,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52554,0.00079,0.08339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":967.0,"contact_point_centroid":[0.64387,0.16878,0.21236],"force_p95":0.14663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2812,"mean_force":0.09371,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63866,0.1505,0.21366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.64388,0.13214,0.2114],"force_p95":0.16171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26228,"mean_force":0.11118,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63872,0.15059,0.21313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6825.0,"contact_point_centroid":[0.58566,0.0578,0.19053],"force_p95":0.12253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18053,"mean_force":0.08505,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58193,0.07657,0.18998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7842.0,"contact_point_centroid":[0.58787,0.09659,0.19181],"force_p95":0.10716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17932,"mean_force":0.07593,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58311,0.07813,0.19075]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.1318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16119,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53081,0.00088,0.02511]},{"body_a":"world","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51721,0.00049,0.20586]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53625,0.00099,0.07322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53068,-0.01834,0.02636],"force_p95":0.07603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1104,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52956,0.00086,0.02368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.5306,0.01994,0.02548],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09222,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52956,0.00086,0.02368]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65003,0.15401,0.17411],"final_tcp_position":[0.64093,0.15354,0.19696],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":30.36498,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":30.36498,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53713,0.00099,0.11335],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53825,0.00102,0.03371],"tcp_start":[0.53713,0.00099,0.11335],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12968,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16119,"tcp_end":[0.52953,0.00086,0.02364],"tcp_start":[0.53825,0.00102,0.03371],"tcp_to_object_dist_end":0.01479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.54441,0.00084,0.15107],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.1923,"object_to_goal_dist_start":0.25053,"object_z_max":0.15082,"peak_contact_force":0.1095,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15798.0,"raw_peak_contact_force":0.76099,"subtask_id":"lift_height","tcp_end":[0.52551,0.0008,0.15457],"tcp_start":[0.52953,0.00086,0.02364],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.6468,0.14837,0.20598],"object_pos_start":[0.54441,0.00084,0.15107],"object_to_goal_dist_end":0.01779,"object_to_goal_dist_start":0.1923,"object_z_max":0.20591,"peak_contact_force":0.11221,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14667.0,"raw_peak_contact_force":0.18053,"tcp_end":[0.63762,0.14805,0.22719],"tcp_start":[0.52551,0.0008,0.15457],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.65003,0.15401,0.17411],"object_pos_start":[0.6468,0.14837,0.20598],"object_to_goal_dist_end":0.01764,"object_to_goal_dist_start":0.01779,"object_z_max":0.20598,"peak_contact_force":0.16192,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1739.0,"raw_peak_contact_force":0.2812,"subtask_id":"place_target","tcp_end":[0.64093,0.15354,0.19696],"tcp_start":[0.63762,0.14805,0.22719],"tcp_to_object_dist_end":0.0246,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```