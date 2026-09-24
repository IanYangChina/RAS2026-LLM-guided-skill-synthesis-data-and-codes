## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5039 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5096 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5047 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5097 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5098 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.504) — your mutation base

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

- **Composite score**: 0.504
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0732 |
| descend_1 | 1.00 | 1.00 | 0.1901 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 1.00 | 1.00 | 0.1383 |
| transport_1 | 1.00 | 1.00 | 0.2284 |
| descend_2 | 1.00 | 1.00 | 0.0265 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.011, 0.235) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 9.927 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.493, -0.011, 0.235)→(0.489, -0.015, 0.045) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 11.385 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.489, -0.015, 0.045)→(0.480, -0.015, 0.036) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 43.000 | 0.142 | 0.182 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.036)→(0.476, -0.015, 0.174) | (0.493, -0.015, 0.026)→(0.491, -0.015, 0.158) | 0.281→0.244 | 1.00 / 29.667 | 0.099 | 0.523 |
| transport_1 | approach | 1.00 / step_budget | (0.476, -0.015, 0.174)→(0.618, 0.156, 0.202) | (0.491, -0.015, 0.158)→(0.623, 0.158, 0.185) | 0.244→0.029 | 1.00 / 38.333 | 0.081 | 0.245 |
| descend_2 | descend | 1.00 / step_budget | (0.618, 0.156, 0.202)→(0.625, 0.165, 0.178) | (0.623, 0.158, 0.185)→(0.633, 0.168, 0.161) | 0.029→0.009 | 1.00 / 37.333 | 0.080 | 0.314 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.530
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.569
- phase_breakdown.place_target_score: 0.670
- phase_breakdown.lift_height_score: 0.333
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.504
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26641,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18781,"approach_1.speed":0.07021,"descend_1.speed":0.02752,"descend_2.speed":0.0573,"lift_1.lift_distance":0.15233,"lift_1.speed":0.06647,"transport_1.speed":0.1172},"optimized_scores":{"best_composite_score":0.50432,"best_fitness_score":0.97432,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.47292,-0.01923,-0.00137],"force_p95":0.45506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50996,"mean_force":0.14194,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46257,-0.01929,0.03753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.61186,0.16407,0.21879],"force_p95":0.07996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31167,"mean_force":0.05413,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61581,0.14549,0.21579]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9279.0,"contact_point_centroid":[0.46126,-0.00025,0.10268],"force_p95":0.07638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27962,"mean_force":0.05097,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45997,-0.01924,0.10103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7561.0,"contact_point_centroid":[0.45997,-0.03845,0.1035],"force_p95":0.08114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27672,"mean_force":0.06029,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45997,-0.01924,0.10088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.6197,0.12665,0.21658],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2248,"mean_force":0.05269,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61581,0.14549,0.21579]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02018,-0.00207],"force_p95":0.14421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1907,"mean_force":0.12807,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46488,-0.01932,0.03745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7779.0,"contact_point_centroid":[0.54256,0.04635,0.19862],"force_p95":0.10568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18484,"mean_force":0.0604,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53947,0.0653,0.19688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8373.0,"contact_point_centroid":[0.53657,0.08184,0.19836],"force_p95":0.08688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16709,"mean_force":0.05439,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53734,0.06308,0.19607]},{"body_a":"world","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.47616,-0.02015,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49048,-0.00663,0.26986]},{"body_a":"world","body_b":"grasp_target","contact_count":1552.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47546,-0.01686,0.14186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5300.0,"contact_point_centroid":[0.46439,-0.00021,0.03785],"force_p95":0.06497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.115,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46371,-0.0193,0.0363]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4430.0,"contact_point_centroid":[0.46317,-0.03858,0.03901],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08111,"mean_force":0.04912,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46372,-0.0193,0.0363]}],"total_contact_groups":12},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62543,0.15206,0.18697],"final_tcp_position":[0.61991,0.14985,0.20331],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":29.53523,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":29.53523,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48042,-0.01442,0.23619],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1552.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.47238,-0.01942,0.04518],"tcp_start":[0.48042,-0.01442,0.23619],"tcp_to_object_dist_end":0.01954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01979,0.02575],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28836,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14354,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11530.0,"raw_peak_contact_force":0.1907,"tcp_end":[0.46368,-0.0193,0.03627],"tcp_start":[0.47238,-0.01942,0.04518],"tcp_to_object_dist_end":0.01626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.47316,-0.01986,0.15403],"object_pos_start":[0.47607,-0.01979,0.02575],"object_to_goal_dist_end":0.24166,"object_to_goal_dist_start":0.28836,"object_z_max":0.15376,"peak_contact_force":0.08589,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16918.0,"raw_peak_contact_force":0.50996,"subtask_id":"lift_height","tcp_end":[0.46011,-0.01924,0.16913],"tcp_start":[0.46368,-0.0193,0.03627],"tcp_to_object_dist_end":0.01997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.61572,0.143,0.20889],"object_pos_start":[0.47316,-0.01986,0.15403],"object_to_goal_dist_end":0.02941,"object_to_goal_dist_start":0.24166,"object_z_max":0.20878,"peak_contact_force":0.07295,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16152.0,"raw_peak_contact_force":0.18484,"tcp_end":[0.61266,0.14155,0.22506],"tcp_start":[0.46011,-0.01924,0.16913],"tcp_to_object_dist_end":0.01652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.62543,0.15206,0.18697],"object_pos_start":[0.61572,0.143,0.20889],"object_to_goal_dist_end":0.00981,"object_to_goal_dist_start":0.02941,"object_z_max":0.20892,"peak_contact_force":0.07357,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.31167,"subtask_id":"place_target","tcp_end":[0.61991,0.14985,0.20331],"tcp_start":[0.61266,0.14155,0.22506],"tcp_to_object_dist_end":0.01739,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.392,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19995,"approach_1.speed":0.05313,"descend_1.speed":0.01987,"descend_2.speed":0.13201,"lift_1.lift_distance":0.16969,"lift_1.speed":0.08852,"transport_1.speed":0.17287},"optimized_scores":{"best_composite_score":0.50444,"best_fitness_score":0.97444,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.45628,-0.02506,-0.00143],"force_p95":0.44216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48935,"mean_force":0.11198,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44573,-0.02513,0.03836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1420.0,"contact_point_centroid":[0.60936,0.2106,0.14719],"force_p95":0.09432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32859,"mean_force":0.0568,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61414,0.19231,0.14352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8085.0,"contact_point_centroid":[0.53527,0.06828,0.17137],"force_p95":0.12651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30169,"mean_force":0.06924,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53143,0.08714,0.16991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7692.0,"contact_point_centroid":[0.44393,-0.04424,0.11093],"force_p95":0.09118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26696,"mean_force":0.06315,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44331,-0.02505,0.10825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9443.0,"contact_point_centroid":[0.44532,-0.00616,0.10963],"force_p95":0.08192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26691,"mean_force":0.05314,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4433,-0.02505,0.10807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1490.0,"contact_point_centroid":[0.61882,0.17367,0.14358],"force_p95":0.08779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24855,"mean_force":0.05335,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61424,0.19244,0.14313]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8603.0,"contact_point_centroid":[0.52897,0.10412,0.17253],"force_p95":0.10115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21041,"mean_force":0.05657,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53023,0.08564,0.1701]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4586,-0.02633,-0.0021],"force_p95":0.15152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20219,"mean_force":0.13005,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44806,-0.02519,0.03801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.44769,-0.00606,0.03824],"force_p95":0.06524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15187,"mean_force":0.04133,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44692,-0.02516,0.03692]},{"body_a":"world","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.45856,-0.02632,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4848,-0.00855,0.27423]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46093,-0.02196,0.14658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4447.0,"contact_point_centroid":[0.4461,-0.04443,0.03965],"force_p95":0.08014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08168,"mean_force":0.04913,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44692,-0.02516,0.03693]}],"total_contact_groups":12},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62516,0.20192,0.10922],"final_tcp_position":[0.61872,0.19814,0.12708],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.48935,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":532.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4681,-0.01872,0.2454],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.45541,-0.02537,0.04529],"tcp_start":[0.4681,-0.01872,0.2454],"tcp_to_object_dist_end":0.01954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02575,0.02565],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30335,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15015,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11534.0,"raw_peak_contact_force":0.20219,"tcp_end":[0.44689,-0.02516,0.0369],"tcp_start":[0.45541,-0.02537,0.04529],"tcp_to_object_dist_end":0.01618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.45817,-0.02597,0.16945],"object_pos_start":[0.45851,-0.02575,0.02565],"object_to_goal_dist_end":0.29576,"object_to_goal_dist_start":0.30335,"object_z_max":0.16918,"peak_contact_force":0.10458,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17210.0,"raw_peak_contact_force":0.48935,"subtask_id":"lift_height","tcp_end":[0.44359,-0.02506,0.18713],"tcp_start":[0.44689,-0.02516,0.0369],"tcp_to_object_dist_end":0.02293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.61511,0.18967,0.14001],"object_pos_start":[0.45817,-0.02597,0.16945],"object_to_goal_dist_end":0.03521,"object_to_goal_dist_start":0.29576,"object_z_max":0.16965,"peak_contact_force":0.07935,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16688.0,"raw_peak_contact_force":0.30169,"tcp_end":[0.61071,0.18686,0.15767],"tcp_start":[0.44359,-0.02506,0.18713],"tcp_to_object_dist_end":0.01841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.62516,0.20192,0.10922],"object_pos_start":[0.61511,0.18967,0.14001],"object_to_goal_dist_end":0.0094,"object_to_goal_dist_start":0.03521,"object_z_max":0.14001,"peak_contact_force":0.07765,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2910.0,"raw_peak_contact_force":0.32859,"subtask_id":"place_target","tcp_end":[0.61872,0.19814,0.12708],"tcp_start":[0.61071,0.18686,0.15767],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2471,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17805,"approach_1.speed":0.05156,"descend_1.speed":0.02837,"descend_2.speed":0.09745,"lift_1.lift_distance":0.15102,"lift_1.speed":0.07406,"transport_1.speed":0.12402},"optimized_scores":{"best_composite_score":0.50306,"best_fitness_score":0.97306,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54131,0.00096,-0.00137],"force_p95":0.48577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57059,"mean_force":0.14419,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52767,0.00078,0.0347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6822.0,"contact_point_centroid":[0.52756,0.01973,0.09466],"force_p95":0.10741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31961,"mean_force":0.07001,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52484,0.00073,0.09245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":842.0,"contact_point_centroid":[0.63174,0.16227,0.21836],"force_p95":0.09495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30278,"mean_force":0.06423,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63372,0.14361,0.21655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7590.0,"contact_point_centroid":[0.52756,-0.01812,0.09182],"force_p95":0.10395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29818,"mean_force":0.06416,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52487,0.00073,0.09026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.63907,0.12522,0.21672],"force_p95":0.1028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29013,"mean_force":0.07265,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63377,0.14368,0.21638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4640.0,"contact_point_centroid":[0.58605,0.05587,0.19503],"force_p95":0.12584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24734,"mean_force":0.08064,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5803,0.07422,0.19437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.58396,0.09535,0.19717],"force_p95":0.11472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21589,"mean_force":0.07389,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58208,0.07655,0.19537]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00115,-0.00203],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15447,"mean_force":0.12534,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53017,0.00083,0.035]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.54431,0.00113,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1233,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51441,0.0004,0.26281]},{"body_a":"world","body_b":"grasp_target","contact_count":1420.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53365,0.0009,0.13504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53032,-0.01824,0.03515],"force_p95":0.06864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10177,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52891,0.00081,0.03355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.53043,0.02003,0.03603],"force_p95":0.07527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09379,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52891,0.00081,0.03355]}],"total_contact_groups":12},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64704,0.15102,0.18698],"final_tcp_position":[0.63709,0.14801,0.20474],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":33.90985,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":724.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53158,0.00084,0.22299],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":33.90985,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53815,0.001,0.04458],"tcp_start":[0.53158,0.00084,0.22299],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00104,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25033,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13355,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10790.0,"raw_peak_contact_force":0.15447,"tcp_end":[0.52888,0.00081,0.03351],"tcp_start":[0.53815,0.001,0.04458],"tcp_to_object_dist_end":0.0171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.54174,0.00085,0.15048],"object_pos_start":[0.54418,0.00104,0.02587],"object_to_goal_dist_end":0.19386,"object_to_goal_dist_start":0.25033,"object_z_max":0.15023,"peak_contact_force":0.1077,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14493.0,"raw_peak_contact_force":0.57059,"subtask_id":"lift_height","tcp_end":[0.52496,0.00073,0.16517],"tcp_start":[0.52888,0.00081,0.03351],"tcp_to_object_dist_end":0.02231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.63947,0.14233,0.20641],"object_pos_start":[0.54174,0.00085,0.15048],"object_to_goal_dist_end":0.02343,"object_to_goal_dist_start":0.19386,"object_z_max":0.20626,"peak_contact_force":0.09006,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9585.0,"raw_peak_contact_force":0.24734,"tcp_end":[0.63149,0.14002,0.22408],"tcp_start":[0.52496,0.00073,0.16517],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":49.0,"n_steps_budget":1000.0,"object_pos_end":[0.64704,0.15102,0.18698],"object_pos_start":[0.63947,0.14233,0.20641],"object_to_goal_dist_end":0.0082,"object_to_goal_dist_start":0.02343,"object_z_max":0.20649,"peak_contact_force":0.08787,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1562.0,"raw_peak_contact_force":0.30278,"subtask_id":"place_target","tcp_end":[0.63709,0.14801,0.20474],"tcp_start":[0.63149,0.14002,0.22408],"tcp_to_object_dist_end":0.02058,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```