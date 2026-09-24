## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4591 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4587 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0883 | 0.33 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0365 | 0.33 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0443 | 0.32 | ✅ accepted |

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
| approach_object | 1.00 | 0.1634 |
| descend_grasp | 1.00 | 0.1043 |
| grasp_object | 1.00 | 0.0117 |
| lift_object | 1.00 | 0.1218 |
| transport_to_goal | 1.00 | 0.2248 |
| descend_to_place | 1.00 | 0.0674 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.000, 0.141) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.000, 0.141)→(0.492, 0.001, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.036)→(0.484, 0.000, 0.028) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.028)→(0.492, 0.000, 0.149) | (0.497, 0.000, 0.026)→(0.512, 0.000, 0.144) | 0.266→0.211 |
| transport_to_goal | approach | 1.00 / step_budget | (0.492, 0.000, 0.149)→(0.573, 0.167, 0.266) | (0.512, 0.000, 0.144)→(0.587, 0.167, 0.250) | 0.211→0.067 |
| descend_to_place | descend | 1.00 / step_budget | (0.573, 0.167, 0.266)→(0.578, 0.180, 0.200) | (0.587, 0.167, 0.250)→(0.586, 0.180, 0.181) | 0.067→0.011 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.712
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.362
- phase_breakdown.lift_object_score: 0.079
- phase_breakdown.place_goal_score: 0.598
- phase_breakdown.reach_grasp_score: 0.194
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.459
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.398


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40323,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.06449,"approach_object.generator.speed":0.08689,"descend_grasp.grasp_z":0.00305,"descend_to_place.descend_speed":0.06495,"descend_to_place.place_z_adjust":-0.00757,"grasp_object.grasp_offset":-0.00863,"lift_object.lift_height":0.15151,"transport_to_goal.transport_speed":0.03983},"optimized_scores":{"best_composite_score":0.45783,"best_fitness_score":0.97783,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51153,-0.02212,-0.00149],"force_p95":0.56754,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.605,"mean_force":0.17207,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49877,-0.02222,0.02947]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3487.0,"contact_point_centroid":[0.50443,-0.00317,0.08243],"force_p95":0.11354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30787,"mean_force":0.07471,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50171,-0.02214,0.0799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3848.0,"contact_point_centroid":[0.50443,-0.04098,0.08033],"force_p95":0.10906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29303,"mean_force":0.06959,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50161,-0.02214,0.07864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3063.0,"contact_point_centroid":[0.55212,0.12236,0.25843],"force_p95":0.13045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20714,"mean_force":0.08489,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54837,0.14108,0.25898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3198.0,"contact_point_centroid":[0.55199,0.15963,0.25713],"force_p95":0.12074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20461,"mean_force":0.07704,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5484,0.14124,0.25805]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.0228,-0.00207],"force_p95":0.14312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19625,"mean_force":0.12816,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5011,-0.02229,0.02964]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5700.0,"contact_point_centroid":[0.53161,0.03746,0.22202],"force_p95":0.1113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16462,"mean_force":0.08059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52658,0.05595,0.22107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5144.0,"contact_point_centroid":[0.53254,0.07775,0.22542],"force_p95":0.11658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15763,"mean_force":0.08648,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52746,0.05913,0.22423]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.5137,-0.02302,-0.00191],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50356,-0.00979,0.20785]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.50068,-0.00306,0.03111],"force_p95":0.0782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12784,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49991,-0.02226,0.02837]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50708,-0.02128,0.07465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4932.0,"contact_point_centroid":[0.50068,-0.04136,0.03018],"force_p95":0.07021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08475,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49991,-0.02226,0.02837]}],"total_contact_groups":12},"final_pose_error":0.00978,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55437,0.14717,0.20293],"final_tcp_position":[0.54996,0.14772,0.22237],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.50852,-0.02019,0.11329],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08747,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50818,-0.02244,0.03736],"tcp_start":[0.50852,-0.02019,0.11329],"tcp_to_object_dist_end":0.01263,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51357,-0.02219,0.02577],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26527,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.49988,-0.02226,0.02834],"tcp_start":[0.50818,-0.02244,0.03736],"tcp_to_object_dist_end":0.01393,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":244.0,"n_steps_budget":930.0,"object_pos_end":[0.52855,-0.02201,0.14199],"object_pos_start":[0.51357,-0.02219,0.02577],"object_to_goal_dist_end":0.1929,"object_to_goal_dist_start":0.26527,"object_z_max":0.14154,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50808,-0.02209,0.14826],"tcp_start":[0.49988,-0.02226,0.02834],"tcp_to_object_dist_end":0.02141,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.56213,0.13439,0.28221],"object_pos_start":[0.52855,-0.02201,0.14199],"object_to_goal_dist_end":0.06315,"object_to_goal_dist_start":0.1929,"object_z_max":0.2819,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.54793,0.1345,0.29837],"tcp_start":[0.50808,-0.02209,0.14826],"tcp_to_object_dist_end":0.02151,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.55437,0.14717,0.20293],"object_pos_start":[0.56213,0.13439,0.28221],"object_to_goal_dist_end":0.01958,"object_to_goal_dist_start":0.06315,"object_z_max":0.28249,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54996,0.14772,0.22237],"tcp_start":[0.54793,0.1345,0.29837],"tcp_to_object_dist_end":0.01994,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47982,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11209,"approach_object.generator.speed":0.17029,"descend_grasp.grasp_z":2e-05,"descend_to_place.descend_speed":0.07516,"descend_to_place.place_z_adjust":0.01072,"grasp_object.grasp_offset":-0.0216,"lift_object.lift_height":0.15067,"transport_to_goal.transport_speed":0.02091},"optimized_scores":{"best_composite_score":0.4594,"best_fitness_score":0.9794,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49887,0.04266,-0.00163],"force_p95":0.62225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65302,"mean_force":0.19863,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48709,0.04305,0.02723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49191,0.06176,0.07871],"force_p95":0.10775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31192,"mean_force":0.06577,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4897,0.04283,0.07682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3655.0,"contact_point_centroid":[0.49204,0.02381,0.08055],"force_p95":0.11332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30116,"mean_force":0.07091,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48978,0.04283,0.07789]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04463,-0.00217],"force_p95":0.17389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26189,"mean_force":0.1362,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48939,0.04328,0.02726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2433.0,"contact_point_centroid":[0.56029,0.21185,0.19456],"force_p95":0.13488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24519,"mean_force":0.09353,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55617,0.23046,0.19578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2402.0,"contact_point_centroid":[0.5604,0.24899,0.19381],"force_p95":0.12924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22658,"mean_force":0.087,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55624,0.23061,0.19529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3757.0,"contact_point_centroid":[0.48931,0.02397,0.02907],"force_p95":0.08624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1505,"mean_force":0.05556,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04318,0.02604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4978.0,"contact_point_centroid":[0.52938,0.15202,0.188],"force_p95":0.11111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14903,"mean_force":0.08352,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52437,0.13328,0.1863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5542.0,"contact_point_centroid":[0.52993,0.11633,0.18819],"force_p95":0.10601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14185,"mean_force":0.07717,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52491,0.13488,0.18706]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.13668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49846,0.01826,0.23142]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49575,0.04085,0.09645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5095.0,"contact_point_centroid":[0.48864,0.06232,0.02814],"force_p95":0.07455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08794,"mean_force":0.04437,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04318,0.02605]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56873,0.23841,0.14603],"final_tcp_position":[0.55904,0.23902,0.16351],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49789,0.03801,0.16024],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13444,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.49635,0.04391,0.03465],"tcp_start":[0.49789,0.03801,0.16024],"tcp_to_object_dist_end":0.00996,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04314,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24378,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.4882,0.04317,0.02601],"tcp_start":[0.49635,0.04391,0.03465],"tcp_to_object_dist_end":0.0129,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":243.0,"n_steps_budget":960.0,"object_pos_end":[0.51595,0.04276,0.14286],"object_pos_start":[0.50108,0.04314,0.02543],"object_to_goal_dist_end":0.20787,"object_to_goal_dist_start":0.24378,"object_z_max":0.1424,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.49574,0.04279,0.14671],"tcp_start":[0.4882,0.04317,0.02601],"tcp_to_object_dist_end":0.02057,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.5707,0.22281,0.21522],"object_pos_start":[0.51595,0.04276,0.14286],"object_to_goal_dist_end":0.07218,"object_to_goal_dist_start":0.20787,"object_z_max":0.21503,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55495,0.22277,0.22886],"tcp_start":[0.49574,0.04279,0.14671],"tcp_to_object_dist_end":0.02084,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.56873,0.23841,0.14603],"object_pos_start":[0.5707,0.22281,0.21522],"object_to_goal_dist_end":0.0078,"object_to_goal_dist_start":0.07218,"object_z_max":0.21536,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55904,0.23902,0.16351],"tcp_start":[0.55495,0.22277,0.22886],"tcp_to_object_dist_end":0.02,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36398,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09857,"approach_object.generator.speed":0.07095,"descend_grasp.grasp_z":0.00198,"descend_to_place.descend_speed":0.04247,"descend_to_place.place_z_adjust":0.01868,"grasp_object.grasp_offset":-0.01342,"lift_object.lift_height":0.15686,"transport_to_goal.transport_speed":0.03599},"optimized_scores":{"best_composite_score":0.46012,"best_fitness_score":0.98012,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47385,-0.0195,-0.00146],"force_p95":0.58689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60675,"mean_force":0.19592,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46291,-0.01951,0.03017]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3918.0,"contact_point_centroid":[0.46718,-0.00039,0.08519],"force_p95":0.10929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28768,"mean_force":0.06706,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46548,-0.01947,0.08258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4310.0,"contact_point_centroid":[0.46721,-0.03845,0.08395],"force_p95":0.10367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28177,"mean_force":0.06231,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46543,-0.01947,0.08214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1794.0,"contact_point_centroid":[0.62261,0.16657,0.24013],"force_p95":0.16059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25884,"mean_force":0.09716,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61924,0.14837,0.24356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1767.0,"contact_point_centroid":[0.62298,0.13012,0.24064],"force_p95":0.15548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25625,"mean_force":0.09628,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61919,0.1483,0.24404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6112.0,"contact_point_centroid":[0.54649,0.04222,0.21014],"force_p95":0.11354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18997,"mean_force":0.08346,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54126,0.06073,0.20916]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18967,"mean_force":0.12707,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46517,-0.01956,0.03014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5707.0,"contact_point_centroid":[0.54926,0.0823,0.21247],"force_p95":0.116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18175,"mean_force":0.08731,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54397,0.06373,0.21138]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.47616,-0.02015,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48797,-0.00822,0.22572]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47279,-0.01839,0.09164]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5064.0,"contact_point_centroid":[0.46376,-0.00029,0.03166],"force_p95":0.06605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09552,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46406,-0.01954,0.02904]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.46363,-0.0388,0.03115],"force_p95":0.06514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08137,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46406,-0.01954,0.02904]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63361,0.1546,0.19273],"final_tcp_position":[0.62468,0.15459,0.21435],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47633,-0.01715,0.14804],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12206,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47186,-0.01971,0.0368],"tcp_start":[0.47633,-0.01715,0.14804],"tcp_to_object_dist_end":0.01162,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01958,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46403,-0.01954,0.02901],"tcp_start":[0.47186,-0.01971,0.0368],"tcp_to_object_dist_end":0.01243,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":244.0,"n_steps_budget":960.0,"object_pos_end":[0.49036,-0.01935,0.14726],"object_pos_start":[0.47604,-0.01958,0.0258],"object_to_goal_dist_end":0.23152,"object_to_goal_dist_start":0.28822,"object_z_max":0.14679,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47109,-0.01947,0.1532],"tcp_start":[0.46403,-0.01954,0.02901],"tcp_to_object_dist_end":0.02017,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.62939,0.14323,0.25282],"object_pos_start":[0.49036,-0.01935,0.14726],"object_to_goal_dist_end":0.06483,"object_to_goal_dist_start":0.23152,"object_z_max":0.25263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.61592,0.1433,0.27006],"tcp_start":[0.47109,-0.01947,0.1532],"tcp_to_object_dist_end":0.02188,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.63361,0.1546,0.19273],"object_pos_start":[0.62939,0.14323,0.25282],"object_to_goal_dist_end":0.00577,"object_to_goal_dist_start":0.06483,"object_z_max":0.25293,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.62468,0.15459,0.21435],"tcp_start":[0.61592,0.1433,0.27006],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```