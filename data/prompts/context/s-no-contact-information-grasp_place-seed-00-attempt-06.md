## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4587 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0883 | 0.33 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0365 | 0.33 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0443 | 0.32 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0357 | 0.27 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=0.459) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
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
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_object
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
  parameters:
    grasp_offset:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: lift_object
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
    - 0.25
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.03
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
  subtask_id: place_goal
- id: descend_to_place
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
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_adjust:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_offset: status=consumed; consumers=target.offset.z (replace)
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_adjust: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.459
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1641 |
| descend_grasp | 1.00 | 0.1022 |
| grasp_object | 1.00 | 0.0117 |
| lift_object | 1.00 | 0.1337 |
| transport_to_goal | 1.00 | 0.2180 |
| descend_to_place | 1.00 | 0.0724 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.000, 0.140) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.000, 0.140)→(0.492, 0.001, 0.038) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.038)→(0.484, 0.000, 0.029) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.029)→(0.492, 0.000, 0.163) | (0.497, 0.000, 0.026)→(0.512, 0.000, 0.155) | 0.266→0.209 |
| transport_to_goal | approach | 1.00 / step_budget | (0.492, 0.000, 0.163)→(0.573, 0.166, 0.267) | (0.512, 0.000, 0.155)→(0.586, 0.166, 0.249) | 0.209→0.066 |
| descend_to_place | descend | 1.00 / step_budget | (0.573, 0.166, 0.267)→(0.578, 0.181, 0.196) | (0.586, 0.166, 0.249)→(0.583, 0.180, 0.173) | 0.066→0.014 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.337
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.468
- phase_breakdown.lift_object_score: 0.108
- phase_breakdown.place_goal_score: 0.792
- phase_breakdown.reach_grasp_score: 0.199
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.459
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.402


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6978,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08819,"approach_object.generator.speed":0.16712,"descend_grasp.grasp_z":0.00546,"descend_to_place.descend_speed":0.05664,"descend_to_place.place_z_adjust":0.00775,"grasp_object.grasp_offset":-0.0121,"lift_object.lift_height":0.16485,"transport_to_goal.transport_speed":0.06681},"optimized_scores":{"best_composite_score":0.45721,"best_fitness_score":0.97721,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51159,-0.02216,-0.00149],"force_p95":0.5349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56968,"mean_force":0.16165,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49908,-0.02227,0.03203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.50473,-0.00323,0.0897],"force_p95":0.11332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30865,"mean_force":0.07506,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50197,-0.02218,0.0872]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4145.0,"contact_point_centroid":[0.50471,-0.04102,0.08733],"force_p95":0.10912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2918,"mean_force":0.07015,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50185,-0.02219,0.08562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1801.0,"contact_point_centroid":[0.5523,0.12186,0.26456],"force_p95":0.16948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2353,"mean_force":0.10993,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54834,0.14026,0.26813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1878.0,"contact_point_centroid":[0.55167,0.1583,0.26375],"force_p95":0.16163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22925,"mean_force":0.10407,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54834,0.1403,0.26783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4192.0,"contact_point_centroid":[0.53217,0.07326,0.22832],"force_p95":0.13574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19653,"mean_force":0.09857,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52651,0.05464,0.22718]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02282,-0.00206],"force_p95":0.14196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19036,"mean_force":0.12787,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5014,-0.02233,0.03222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.53169,0.03389,0.22576],"force_p95":0.12214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18676,"mean_force":0.08733,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52589,0.05225,0.22504]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.5137,-0.02302,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50355,-0.00958,0.21967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.50088,-0.0031,0.0337],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12934,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50022,-0.0223,0.03094]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50713,-0.02112,0.08761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4925.0,"contact_point_centroid":[0.5009,-0.0414,0.03277],"force_p95":0.07007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08566,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50022,-0.0223,0.03095]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55257,0.14632,0.21394],"final_tcp_position":[0.54995,0.14705,0.23758],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.50851,-0.01982,0.13695],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1111,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50847,-0.02249,0.03996],"tcp_start":[0.50851,-0.01982,0.13695],"tcp_to_object_dist_end":0.0149,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51358,-0.02224,0.02577],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.2653,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50019,-0.0223,0.03091],"tcp_start":[0.50847,-0.02249,0.03996],"tcp_to_object_dist_end":0.01434,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.52861,-0.02215,0.15222],"object_pos_start":[0.51358,-0.02224,0.02577],"object_to_goal_dist_end":0.18901,"object_to_goal_dist_start":0.2653,"object_z_max":0.15177,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50834,-0.02215,0.16137],"tcp_start":[0.50019,-0.0223,0.03091],"tcp_to_object_dist_end":0.02223,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.55964,0.13394,0.279],"object_pos_start":[0.52861,-0.02215,0.15222],"object_to_goal_dist_end":0.05995,"object_to_goal_dist_start":0.18901,"object_z_max":0.27872,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.54783,0.13386,0.29905],"tcp_start":[0.50834,-0.02215,0.16137],"tcp_to_object_dist_end":0.02327,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.55257,0.14632,0.21394],"object_pos_start":[0.55964,0.13394,0.279],"object_to_goal_dist_end":0.00978,"object_to_goal_dist_start":0.05995,"object_z_max":0.27924,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54995,0.14705,0.23758],"tcp_start":[0.54783,0.13386,0.29905],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31765,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11886,"approach_object.generator.speed":0.10661,"descend_grasp.grasp_z":0.00032,"descend_to_place.descend_speed":0.04571,"descend_to_place.place_z_adjust":-0.00178,"grasp_object.grasp_offset":-0.01309,"lift_object.lift_height":0.16174,"transport_to_goal.transport_speed":0.03097},"optimized_scores":{"best_composite_score":0.45943,"best_fitness_score":0.97943,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49885,0.04268,-0.00162],"force_p95":0.62652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65157,"mean_force":0.19957,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48711,0.04306,0.0275]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4356.0,"contact_point_centroid":[0.49209,0.06175,0.08322],"force_p95":0.10863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31292,"mean_force":0.06693,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48976,0.04284,0.08133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3919.0,"contact_point_centroid":[0.49228,0.02384,0.08543],"force_p95":0.11392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30398,"mean_force":0.07182,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48987,0.04284,0.08283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2542.0,"contact_point_centroid":[0.55923,0.24821,0.18655],"force_p95":0.16557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27255,"mean_force":0.10231,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55589,0.23017,0.19069]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04463,-0.00217],"force_p95":0.17347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26102,"mean_force":0.13612,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48943,0.0433,0.02753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2305.0,"contact_point_centroid":[0.55923,0.21202,0.18722],"force_p95":0.18818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23842,"mean_force":0.10659,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5559,0.23018,0.19077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3721.0,"contact_point_centroid":[0.48941,0.02397,0.02938],"force_p95":0.0863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15167,"mean_force":0.05615,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48827,0.04319,0.02631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4586.0,"contact_point_centroid":[0.52877,0.14888,0.19272],"force_p95":0.11479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14983,"mean_force":0.08758,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52353,0.13017,0.19118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5173.0,"contact_point_centroid":[0.52955,0.11359,0.19305],"force_p95":0.10746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14224,"mean_force":0.08006,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52417,0.13209,0.19197]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.50118,0.04505,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49849,0.01814,0.23465]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49583,0.04075,0.09989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5211.0,"contact_point_centroid":[0.48848,0.06231,0.02859],"force_p95":0.07347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08712,"mean_force":0.04337,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48827,0.04319,0.02631]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56742,0.2392,0.12791],"final_tcp_position":[0.55906,0.23942,0.15139],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49801,0.0378,0.16682],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14102,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.49638,0.04392,0.03492],"tcp_start":[0.49801,0.0378,0.16682],"tcp_to_object_dist_end":0.01017,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04315,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24377,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.48824,0.04318,0.02628],"tcp_start":[0.49638,0.04392,0.03492],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.51665,0.0429,0.15329],"object_pos_start":[0.50109,0.04315,0.02543],"object_to_goal_dist_end":0.20764,"object_to_goal_dist_start":0.24377,"object_z_max":0.15283,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.496,0.04281,0.15789],"tcp_start":[0.48824,0.04318,0.02628],"tcp_to_object_dist_end":0.02116,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.57048,0.2223,0.21527],"object_pos_start":[0.51665,0.0429,0.15329],"object_to_goal_dist_end":0.07237,"object_to_goal_dist_start":0.20764,"object_z_max":0.21511,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55484,0.22234,0.22986],"tcp_start":[0.496,0.04281,0.15789],"tcp_to_object_dist_end":0.02139,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.56742,0.2392,0.12791],"object_pos_start":[0.57048,0.2223,0.21527],"object_to_goal_dist_end":0.01992,"object_to_goal_dist_start":0.07237,"object_z_max":0.21538,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55906,0.23942,0.15139],"tcp_start":[0.55484,0.22234,0.22986],"tcp_to_object_dist_end":0.02492,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50224,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.06603,"approach_object.generator.speed":0.17725,"descend_grasp.grasp_z":0.00315,"descend_to_place.descend_speed":0.07497,"descend_to_place.place_z_adjust":0.00263,"grasp_object.grasp_offset":-0.00945,"lift_object.lift_height":0.17206,"transport_to_goal.transport_speed":0.03066},"optimized_scores":{"best_composite_score":0.45947,"best_fitness_score":0.97947,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47389,-0.01948,-0.00147],"force_p95":0.57086,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5889,"mean_force":0.18858,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46287,-0.01945,0.03142]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4216.0,"contact_point_centroid":[0.46746,-0.00037,0.09194],"force_p95":0.11108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28806,"mean_force":0.06904,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4655,-0.01941,0.08937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4628.0,"contact_point_centroid":[0.46746,-0.03837,0.09051],"force_p95":0.10546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28307,"mean_force":0.06427,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46544,-0.01941,0.08872]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2308.0,"contact_point_centroid":[0.62318,0.16702,0.23225],"force_p95":0.1621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26955,"mean_force":0.09803,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61942,0.14862,0.235]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2528.0,"contact_point_centroid":[0.62326,0.13047,0.23338],"force_p95":0.14909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26425,"mean_force":0.08945,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61943,0.14864,0.23499]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02001,-0.00206],"force_p95":0.13994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19152,"mean_force":0.12735,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46514,-0.01951,0.0314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5343.0,"contact_point_centroid":[0.54896,0.08154,0.22035],"force_p95":0.11643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16389,"mean_force":0.08875,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54352,0.06296,0.21915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5861.0,"contact_point_centroid":[0.54614,0.04145,0.21821],"force_p95":0.11282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15464,"mean_force":0.08294,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5408,0.05994,0.21717]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48759,-0.00854,0.20895]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47253,-0.01859,0.07626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5061.0,"contact_point_centroid":[0.46374,-0.00023,0.03295],"force_p95":0.06619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09782,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46403,-0.01948,0.0303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5413.0,"contact_point_centroid":[0.4636,-0.03874,0.03243],"force_p95":0.06535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07989,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46403,-0.01948,0.0303]}],"total_contact_groups":12},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63026,0.15453,0.17765],"final_tcp_position":[0.62506,0.15511,0.19886],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47568,-0.01761,0.11553],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08955,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47182,-0.01965,0.03806],"tcp_start":[0.47568,-0.01761,0.11553],"tcp_to_object_dist_end":0.01282,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01954,0.02579],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.464,-0.01948,0.03027],"tcp_start":[0.47182,-0.01965,0.03806],"tcp_to_object_dist_end":0.01285,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.49119,-0.01937,0.16083],"object_pos_start":[0.47605,-0.01954,0.02579],"object_to_goal_dist_end":0.22891,"object_to_goal_dist_start":0.2882,"object_z_max":0.16036,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47139,-0.01943,0.16866],"tcp_start":[0.464,-0.01948,0.03027],"tcp_to_object_dist_end":0.0213,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.62846,0.14274,0.25328],"object_pos_start":[0.49119,-0.01937,0.16083],"object_to_goal_dist_end":0.06543,"object_to_goal_dist_start":0.22891,"object_z_max":0.2531,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.61554,0.14282,0.27111],"tcp_start":[0.47139,-0.01943,0.16866],"tcp_to_object_dist_end":0.02202,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.63026,0.15453,0.17765],"object_pos_start":[0.62846,0.14274,0.25328],"object_to_goal_dist_end":0.01326,"object_to_goal_dist_start":0.06543,"object_z_max":0.25337,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.62506,0.15511,0.19886],"tcp_start":[0.61554,0.14282,0.27111],"tcp_to_object_dist_end":0.02185,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```