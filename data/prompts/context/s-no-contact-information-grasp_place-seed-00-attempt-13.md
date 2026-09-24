## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4561 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4595 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3976 | 0.88 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4541 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4559 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.456) — your mutation base

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

- **Composite score**: 0.456
- **task_score** (E): 1.000
- **fitness_score**: 0.976  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1409 |
| descend_grasp | 1.00 | 0.1241 |
| grasp_object | 1.00 | 0.0117 |
| lift_object | 1.00 | 0.1364 |
| transport_to_goal | 1.00 | 0.2198 |
| descend_to_place | 1.00 | 0.0685 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.000, 0.163) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.000, 0.163)→(0.492, 0.001, 0.039) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.039)→(0.484, 0.000, 0.031) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.031)→(0.481, 0.000, 0.167) | (0.497, 0.000, 0.026)→(0.501, 0.000, 0.159) | 0.266→0.212 |
| transport_to_goal | approach | 1.00 / step_budget | (0.481, 0.000, 0.167)→(0.572, 0.166, 0.267) | (0.501, 0.000, 0.159)→(0.585, 0.166, 0.248) | 0.212→0.065 |
| descend_to_place | descend | 1.00 / step_budget | (0.572, 0.166, 0.267)→(0.578, 0.180, 0.201) | (0.585, 0.166, 0.248)→(0.584, 0.180, 0.177) | 0.065→0.012 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.633
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.380
- phase_breakdown.lift_object_score: 0.099
- phase_breakdown.place_goal_score: 0.627
- phase_breakdown.reach_grasp_score: 0.183
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
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69892,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10713,"approach_object.generator.speed":0.12869,"descend_grasp.grasp_z":0.00011,"descend_to_place.descend_speed":0.06151,"descend_to_place.place_z_adjust":0.00237,"grasp_object.grasp_offset":-0.01305,"lift_object.lift_height":0.16951,"transport_to_goal.transport_speed":0.07042},"optimized_scores":{"best_composite_score":0.45868,"best_fitness_score":0.97868,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.51096,-0.0218,-0.00149],"force_p95":0.67307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71018,"mean_force":0.22786,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49887,-0.02231,0.02662]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3997.0,"contact_point_centroid":[0.49948,-0.00327,0.08835],"force_p95":0.11301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33936,"mean_force":0.07406,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49687,-0.02225,0.08581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4437.0,"contact_point_centroid":[0.49954,-0.0411,0.08602],"force_p95":0.10942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31436,"mean_force":0.06843,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49688,-0.02225,0.08427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1979.0,"contact_point_centroid":[0.55108,0.12169,0.2626],"force_p95":0.16473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24589,"mean_force":0.11109,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54759,0.14013,0.26686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2170.0,"contact_point_centroid":[0.55046,0.15817,0.26196],"force_p95":0.15814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23048,"mean_force":0.10064,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5476,0.14019,0.2665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4385.0,"contact_point_centroid":[0.52611,0.07454,0.23111],"force_p95":0.14049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21515,"mean_force":0.09654,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52077,0.05605,0.23089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4627.0,"contact_point_centroid":[0.52466,0.0327,0.22691],"force_p95":0.14115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2137,"mean_force":0.09415,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51919,0.05113,0.22666]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02279,-0.00206],"force_p95":0.14071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19398,"mean_force":0.12764,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50141,-0.02237,0.02684]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.5137,-0.02302,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50352,-0.00937,0.2292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.50088,-0.00314,0.02833],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1241,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50022,-0.02234,0.02557]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50712,-0.02096,0.0942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.5009,-0.04145,0.02739],"force_p95":0.06975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08982,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50022,-0.02234,0.02557]}],"total_contact_groups":12},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55303,0.14662,0.20878],"final_tcp_position":[0.54975,0.14732,0.23211],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.50847,-0.01948,0.15584],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12997,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50853,-0.02253,0.03457],"tcp_start":[0.50847,-0.01948,0.15584],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51356,-0.02224,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26528,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50019,-0.02234,0.02553],"tcp_start":[0.50853,-0.02253,0.03457],"tcp_to_object_dist_end":0.01337,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.51813,-0.02215,0.16165],"object_pos_start":[0.51356,-0.02224,0.02579],"object_to_goal_dist_end":0.18746,"object_to_goal_dist_start":0.26528,"object_z_max":0.16118,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.49704,-0.02223,0.16551],"tcp_start":[0.50019,-0.02234,0.02553],"tcp_to_object_dist_end":0.02145,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.56041,0.13378,0.28045],"object_pos_start":[0.51813,-0.02215,0.16165],"object_to_goal_dist_end":0.06146,"object_to_goal_dist_start":0.18746,"object_z_max":0.28018,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.54675,0.13385,0.29952],"tcp_start":[0.49704,-0.02223,0.16551],"tcp_to_object_dist_end":0.02345,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.55303,0.14662,0.20878],"object_pos_start":[0.56041,0.13378,0.28045],"object_to_goal_dist_end":0.01418,"object_to_goal_dist_start":0.06146,"object_z_max":0.28069,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54975,0.14732,0.23211],"tcp_start":[0.54675,0.13385,0.29952],"tcp_to_object_dist_end":0.02357,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35573,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12849,"approach_object.generator.speed":0.08481,"descend_grasp.grasp_z":0.00018,"descend_to_place.descend_speed":0.05262,"descend_to_place.place_z_adjust":0.01641,"grasp_object.grasp_offset":-0.00158,"lift_object.lift_height":0.16919,"transport_to_goal.transport_speed":0.03178},"optimized_scores":{"best_composite_score":0.45946,"best_fitness_score":0.97946,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49867,0.04267,-0.00161],"force_p95":0.68323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70489,"mean_force":0.23138,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4869,0.04306,0.02728]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4139.0,"contact_point_centroid":[0.48726,0.02384,0.08832],"force_p95":0.11331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32999,"mean_force":0.07085,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48504,0.04286,0.08567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4640.0,"contact_point_centroid":[0.48719,0.06179,0.08673],"force_p95":0.1081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32954,"mean_force":0.06558,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48504,0.04286,0.08484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2115.0,"contact_point_centroid":[0.55872,0.24804,0.19516],"force_p95":0.17387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29934,"mean_force":0.10329,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55528,0.22998,0.19911]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04462,-0.00217],"force_p95":0.1733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26112,"mean_force":0.13609,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48944,0.04331,0.02731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1949.0,"contact_point_centroid":[0.55878,0.21201,0.19518],"force_p95":0.18511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24301,"mean_force":0.1057,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55538,0.23017,0.19855]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3715.0,"contact_point_centroid":[0.48943,0.02397,0.02916],"force_p95":0.08627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15107,"mean_force":0.05627,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48827,0.0432,0.02609]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49857,0.01785,0.23954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5083.0,"contact_point_centroid":[0.5234,0.11275,0.19723],"force_p95":0.10807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13699,"mean_force":0.08125,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51792,0.13124,0.19613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4492.0,"contact_point_centroid":[0.52254,0.14808,0.19699],"force_p95":0.11565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13596,"mean_force":0.08906,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51721,0.12938,0.19545]},{"body_a":"world","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49583,0.04054,0.10447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5269.0,"contact_point_centroid":[0.48841,0.06232,0.02844],"force_p95":0.07313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08693,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48828,0.0432,0.02609]}],"total_contact_groups":12},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56831,0.23865,0.14662],"final_tcp_position":[0.55876,0.23884,0.16861],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49796,0.03736,0.17631],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15052,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.49639,0.04393,0.0347],"tcp_start":[0.49796,0.03736,0.17631],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04315,0.02544],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24377,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.48825,0.04319,0.02606],"tcp_start":[0.49639,0.04393,0.0347],"tcp_to_object_dist_end":0.01286,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.50563,0.04283,0.16159],"object_pos_start":[0.50109,0.04315,0.02544],"object_to_goal_dist_end":0.21094,"object_to_goal_dist_start":0.24377,"object_z_max":0.16112,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.4852,0.04286,0.16573],"tcp_start":[0.48825,0.04319,0.02606],"tcp_to_object_dist_end":0.02085,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.56955,0.22204,0.21624],"object_pos_start":[0.50563,0.04283,0.16159],"object_to_goal_dist_end":0.0733,"object_to_goal_dist_start":0.21094,"object_z_max":0.2161,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55364,0.2221,0.23067],"tcp_start":[0.4852,0.04286,0.16573],"tcp_to_object_dist_end":0.02148,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.56831,0.23865,0.14662],"object_pos_start":[0.56955,0.22204,0.21624],"object_to_goal_dist_end":0.00733,"object_to_goal_dist_start":0.0733,"object_z_max":0.21632,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55876,0.23884,0.16861],"tcp_start":[0.55364,0.2221,0.23067],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38158,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10829,"approach_object.generator.speed":0.13453,"descend_grasp.grasp_z":0.01368,"descend_to_place.descend_speed":0.0718,"descend_to_place.place_z_adjust":0.00459,"grasp_object.grasp_offset":-0.02612,"lift_object.lift_height":0.1592,"transport_to_goal.transport_speed":0.04457},"optimized_scores":{"best_composite_score":0.45009,"best_fitness_score":0.97009,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.47364,-0.01991,-0.00149],"force_p95":0.46883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4741,"mean_force":0.15926,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46298,-0.01948,0.04192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4133.0,"contact_point_centroid":[0.46277,-0.00032,0.09956],"force_p95":0.11001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28858,"mean_force":0.06749,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4613,-0.01942,0.09697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3029.0,"contact_point_centroid":[0.62442,0.1306,0.23423],"force_p95":0.12248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28527,"mean_force":0.07482,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61943,0.14924,0.23292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4536.0,"contact_point_centroid":[0.46282,-0.03843,0.09854],"force_p95":0.106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28166,"mean_force":0.06313,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46129,-0.01942,0.09673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2829.0,"contact_point_centroid":[0.62444,0.16794,0.23394],"force_p95":0.1301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26656,"mean_force":0.07927,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61947,0.14927,0.23272]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02007,-0.00206],"force_p95":0.13937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18797,"mean_force":0.12719,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46537,-0.01953,0.04194]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6011.0,"contact_point_centroid":[0.54129,0.04204,0.22034],"force_p95":0.10576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15789,"mean_force":0.08025,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53592,0.0606,0.21863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5718.0,"contact_point_centroid":[0.54383,0.08193,0.22217],"force_p95":0.10987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13989,"mean_force":0.08279,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5385,0.06329,0.22036]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48829,-0.00817,0.23027]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4731,-0.0183,0.10241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4835.0,"contact_point_centroid":[0.46431,-0.00029,0.0432],"force_p95":0.0681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10127,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46428,-0.01951,0.04083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5154.0,"contact_point_centroid":[0.46416,-0.03872,0.04273],"force_p95":0.06686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08457,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46428,-0.01951,0.04084]}],"total_contact_groups":12},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63085,0.15476,0.17525],"final_tcp_position":[0.62488,0.15509,0.2008],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47677,-0.017,0.15768],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1317,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47198,-0.01968,0.04864],"tcp_start":[0.47677,-0.017,0.15768],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01965,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46425,-0.01951,0.04081],"tcp_start":[0.47198,-0.01968,0.04864],"tcp_to_object_dist_end":0.01912,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":250.0,"n_steps_budget":990.0,"object_pos_end":[0.47893,-0.01934,0.15299],"object_pos_start":[0.47607,-0.01965,0.02578],"object_to_goal_dist_end":0.23769,"object_to_goal_dist_start":0.28825,"object_z_max":0.1525,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.46141,-0.0194,0.17033],"tcp_start":[0.46425,-0.01951,0.04081],"tcp_to_object_dist_end":0.02465,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.62478,0.14274,0.24734],"object_pos_start":[0.47893,-0.01934,0.15299],"object_to_goal_dist_end":0.06,"object_to_goal_dist_start":0.23769,"object_z_max":0.24715,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.61487,0.14303,0.27144],"tcp_start":[0.46141,-0.0194,0.17033],"tcp_to_object_dist_end":0.02606,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.63085,0.15476,0.17525],"object_pos_start":[0.62478,0.14274,0.24734],"object_to_goal_dist_end":0.01543,"object_to_goal_dist_start":0.06,"object_z_max":0.24743,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.62488,0.15509,0.2008],"tcp_start":[0.61487,0.14303,0.27144],"tcp_to_object_dist_end":0.02625,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```