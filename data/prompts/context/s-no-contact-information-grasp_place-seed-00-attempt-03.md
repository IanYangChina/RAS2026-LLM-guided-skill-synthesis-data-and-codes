## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0443 | 0.32 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0357 | 0.27 | ✅ accepted |
| 1 | approach → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1914 | 0.17 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1716 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.044) — your mutation base

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
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descent_z:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
- id: release_object
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
  parameters:
    release_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_from_place
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
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

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
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_z: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract_from_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.044
- **task_score** (E): 0.316
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1412 |
| descend_grasp | 1.00 | 0.1237 |
| grasp_object | 1.00 | 0.0117 |
| lift_object | 1.00 | 0.1410 |
| transport_to_goal | 1.00 | 0.1960 |
| descend_to_place | 1.00 | 0.0142 |
| release_object | 1.00 | 0.0215 |
| retract_from_place | 1.00 | 0.0674 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.001, 0.163) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.495, 0.001, 0.163)→(0.492, 0.001, 0.039) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.039)→(0.484, 0.000, 0.031) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.031)→(0.492, 0.000, 0.171) | (0.497, 0.000, 0.026)→(0.512, 0.001, 0.162) | 0.266→0.209 |
| transport_to_goal | approach | 1.00 / step_budget | (0.492, 0.000, 0.171)→(0.570, 0.161, 0.229) | (0.512, 0.001, 0.162)→(0.592, 0.147, 0.050) | 0.209→0.142 |
| descend_to_place | descend | 1.00 / step_budget | (0.570, 0.161, 0.229)→(0.574, 0.171, 0.221) | (0.592, 0.147, 0.050)→(0.598, 0.152, 0.010) | 0.142→0.183 |
| release_object | release | 1.00 / step_budget | (0.574, 0.171, 0.221)→(0.569, 0.169, 0.242) | (0.598, 0.152, 0.010)→(0.597, 0.152, 0.016) | 0.183→0.177 |
| retract_from_place | retract | 1.00 / step_budget | (0.569, 0.169, 0.242)→(0.579, 0.181, 0.307) | (0.597, 0.152, 0.016)→(0.597, 0.152, 0.016) | 0.177→0.177 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.406
- phase_score: 0.309
- phase_breakdown.lift_object_score: 0.098
- phase_breakdown.place_goal_score: 0.470
- phase_breakdown.reach_grasp_score: 0.222
- grasp_place_fitness: 0.677

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.677
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.406
- **Median Q (composite search score)**: -0.043
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: lift_object.lift_height
- **Final σ (mean)**: 0.420


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92715,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10793,"approach_object.generator.speed":0.14233,"descend_grasp.grasp_z":0.00305,"descend_to_place.descent_z":0.01659,"grasp_object.grasp_offset":-0.00465,"lift_object.lift_height":0.15,"release_object.release_time":0.4898,"retract_from_place.retract_speed":0.15015,"transport_to_goal.arc_height":0.02008,"transport_to_goal.transport_speed":0.16789},"optimized_scores":{"best_composite_score":-0.08663,"best_fitness_score":0.59337,"best_task_score":0.23002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.5744,0.07564,-0.00476],"force_p95":1.02102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16656,"mean_force":0.26024,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53889,0.1023,0.24612]},{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51152,-0.02215,-0.00149],"force_p95":0.5691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60695,"mean_force":0.17167,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49913,-0.0223,0.02951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3500.0,"contact_point_centroid":[0.50442,-0.00322,0.08185],"force_p95":0.11269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30896,"mean_force":0.07322,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50191,-0.02221,0.07928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1795.0,"contact_point_centroid":[0.5195,0.02293,0.17541],"force_p95":0.13285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30288,"mean_force":0.09032,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51335,0.00464,0.17487]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3875.0,"contact_point_centroid":[0.50443,-0.04107,0.07974],"force_p95":0.10777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29269,"mean_force":0.06798,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50182,-0.02221,0.07805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.51845,-0.01738,0.1728],"force_p95":0.17023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23376,"mean_force":0.10467,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51257,0.00122,0.1715]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02281,-0.00206],"force_p95":0.14114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19168,"mean_force":0.12771,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50146,-0.02236,0.0297]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.5137,-0.02302,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50352,-0.00935,0.22966]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.57389,0.07567,-0.00193],"force_p95":0.12928,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13034,"mean_force":0.12456,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54632,0.13099,0.25355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4090.0,"contact_point_centroid":[0.50091,-0.00313,0.03118],"force_p95":0.07788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12703,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50027,-0.02233,0.02842]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5739,0.07565,-0.00199],"force_p95":0.12325,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12379,"mean_force":0.12266,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54413,0.13524,0.24968]},{"body_a":"world","body_b":"grasp_target","contact_count":1484.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50711,-0.02093,0.09619]},{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.5739,0.07565,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.54614,0.141,0.30491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.50093,-0.04144,0.03025],"force_p95":0.06989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08768,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50027,-0.02233,0.02842]},{"body_a":"left_finger","body_b":"right_finger","contact_count":212.0,"contact_point_centroid":[0.54257,0.11422,0.25373],"force_p95":0.01519,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.0117,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54212,0.11422,0.25159]},{"body_a":"left_finger","body_b":"right_finger","contact_count":145.0,"contact_point_centroid":[0.54693,0.13098,0.2559],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54632,0.13097,0.25357]}],"total_contact_groups":17},"final_pose_error":0.02956,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.5739,0.07565,0.01602],"final_tcp_position":[0.55049,0.14757,0.34294],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.50844,-0.01943,0.15683],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13097,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50855,-0.02252,0.03743],"tcp_start":[0.50844,-0.01943,0.15683],"tcp_to_object_dist_end":0.01253,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51357,-0.02225,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26529,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50024,-0.02233,0.02839],"tcp_start":[0.50855,-0.02252,0.03743],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":240.0,"n_steps_budget":930.0,"object_pos_end":[0.52816,-0.02203,0.14034],"object_pos_start":[0.51357,-0.02225,0.02579],"object_to_goal_dist_end":0.19367,"object_to_goal_dist_start":0.26529,"object_z_max":0.13988,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50804,-0.02216,0.14635],"tcp_start":[0.50024,-0.02233,0.02839],"tcp_to_object_dist_end":0.021,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.57398,0.07547,0.0164],"object_pos_start":[0.52816,-0.02203,0.14034],"object_to_goal_dist_end":0.22015,"object_to_goal_dist_start":0.19367,"object_z_max":0.18911,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.54566,0.12733,0.25664],"tcp_start":[0.50804,-0.02216,0.14635],"tcp_to_object_dist_end":0.2474,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":34.0,"n_steps_budget":1000.0,"object_pos_end":[0.57394,0.07559,0.016],"object_pos_start":[0.57398,0.07547,0.0164],"object_to_goal_dist_end":0.22048,"object_to_goal_dist_start":0.22015,"object_z_max":0.0164,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54757,0.13568,0.24807],"tcp_start":[0.54566,0.12733,0.25664],"tcp_to_object_dist_end":0.24117,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5739,0.07565,0.01602],"object_pos_start":[0.57394,0.07559,0.016],"object_to_goal_dist_end":0.22044,"object_to_goal_dist_start":0.22048,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.54303,0.13486,0.27003],"tcp_start":[0.54757,0.13568,0.24807],"tcp_to_object_dist_end":0.26264,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.5739,0.07565,0.01602],"object_pos_start":[0.5739,0.07565,0.01602],"object_to_goal_dist_end":0.22044,"object_to_goal_dist_start":0.22044,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55049,0.14757,0.34294],"tcp_start":[0.54303,0.13486,0.27003],"tcp_to_object_dist_end":0.33555,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89809,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08982,"approach_object.generator.speed":0.17356,"descend_grasp.grasp_z":0.01003,"descend_to_place.descent_z":0.0248,"grasp_object.grasp_offset":-0.01348,"lift_object.lift_height":0.16772,"release_object.release_time":0.29311,"retract_from_place.retract_speed":0.11624,"transport_to_goal.arc_height":0.0205,"transport_to_goal.transport_speed":0.1149},"optimized_scores":{"best_composite_score":-0.00345,"best_fitness_score":0.67655,"best_task_score":0.40553},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.57952,0.21254,-0.00845],"force_p95":1.71252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.12722,"mean_force":0.71027,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55105,0.21115,0.19415]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49902,0.04287,-0.00162],"force_p95":0.48636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51553,"mean_force":0.1503,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48716,0.04296,0.03718]},{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.5787,0.21209,-0.00487],"force_p95":0.34166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47277,"mean_force":0.1279,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55426,0.22268,0.18745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4280.0,"contact_point_centroid":[0.49215,0.06174,0.09157],"force_p95":0.11014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30534,"mean_force":0.0677,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48987,0.04283,0.08969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3832.0,"contact_point_centroid":[0.4923,0.02382,0.09342],"force_p95":0.11331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29884,"mean_force":0.07269,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48995,0.04283,0.09081]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2153.0,"contact_point_centroid":[0.51637,0.0721,0.18141],"force_p95":0.16842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28343,"mean_force":0.10442,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51067,0.09071,0.18011]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04473,-0.00217],"force_p95":0.17176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24305,"mean_force":0.13542,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48944,0.04319,0.0372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2843.0,"contact_point_centroid":[0.51955,0.11789,0.18335],"force_p95":0.11517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17939,"mean_force":0.08183,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51354,0.09971,0.18263]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3706.0,"contact_point_centroid":[0.48951,0.02384,0.03908],"force_p95":0.08742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1571,"mean_force":0.05665,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4883,0.04309,0.03598]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49831,0.01877,0.22011]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57884,0.21287,-0.00193],"force_p95":0.13061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13325,"mean_force":0.12138,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55194,0.22741,0.18073]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4957,0.04117,0.09066]},{"body_a":"world","body_b":"grasp_target","contact_count":612.0,"contact_point_centroid":[0.57884,0.21286,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.55427,0.23293,0.23288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.48835,0.06218,0.03839],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08157,"mean_force":0.0422,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4883,0.04309,0.03598]},{"body_a":"left_finger","body_b":"right_finger","contact_count":39.0,"contact_point_centroid":[0.5563,0.22737,0.18391],"force_p95":0.01585,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01585,"mean_force":0.01414,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55577,0.22734,0.18164]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.55485,0.22867,0.17844],"force_p95":0.01305,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01339,"mean_force":0.01073,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55425,0.22864,0.17621]}],"total_contact_groups":16},"final_pose_error":0.02986,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57884,0.21286,0.01602],"final_tcp_position":[0.55938,0.23981,0.26778],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49772,0.03878,0.13815],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11235,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.4963,0.0438,0.04461],"tcp_start":[0.49772,0.03878,0.13815],"tcp_to_object_dist_end":0.01926,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04327,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24365,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.48827,0.04308,0.03594],"tcp_start":[0.4963,0.0438,0.04461],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":257.0,"n_steps_budget":990.0,"object_pos_end":[0.51491,0.04308,0.15014],"object_pos_start":[0.50114,0.04327,0.02543],"object_to_goal_dist_end":0.20779,"object_to_goal_dist_start":0.24365,"object_z_max":0.14968,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.49607,0.04291,0.164],"tcp_start":[0.48827,0.04308,0.03594],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.57976,0.21866,-0.00084],"object_pos_start":[0.51491,0.04308,0.15014],"object_to_goal_dist_end":0.1507,"object_to_goal_dist_start":0.20779,"object_z_max":0.17419,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55321,0.21759,0.19328],"tcp_start":[0.49607,0.04291,0.164],"tcp_to_object_dist_end":0.19593,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.57891,0.21392,0.01645],"object_pos_start":[0.57976,0.21866,-0.00084],"object_to_goal_dist_end":0.13473,"object_to_goal_dist_start":0.1507,"object_z_max":0.01636,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55624,0.22878,0.17998],"tcp_start":[0.55321,0.21759,0.19328],"tcp_to_object_dist_end":0.16577,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57884,0.21286,0.01602],"object_pos_start":[0.57891,0.21392,0.01645],"object_to_goal_dist_end":0.13538,"object_to_goal_dist_start":0.13473,"object_z_max":0.01681,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.55055,0.22671,0.20076],"tcp_start":[0.55624,0.22878,0.17998],"tcp_to_object_dist_end":0.18741,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":153.0,"n_steps_budget":600.0,"object_pos_end":[0.57884,0.21286,0.01602],"object_pos_start":[0.57884,0.21286,0.01602],"object_to_goal_dist_end":0.13538,"object_to_goal_dist_start":0.13538,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55938,0.23981,0.26778],"tcp_start":[0.55055,0.22671,0.20076],"tcp_to_object_dist_end":0.25395,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93373,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14396,"approach_object.generator.speed":0.1749,"descend_grasp.grasp_z":0.00051,"descend_to_place.descent_z":0.05421,"grasp_object.grasp_offset":-0.01572,"lift_object.lift_height":0.20743,"release_object.release_time":0.15874,"retract_from_place.retract_speed":0.18723,"transport_to_goal.arc_height":0.02156,"transport_to_goal.transport_speed":0.18453},"optimized_scores":{"best_composite_score":-0.0429,"best_fitness_score":0.6371,"best_task_score":0.31279},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":44.0,"contact_point_centroid":[0.63989,0.16706,-0.00681],"force_p95":1.58641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53614,"mean_force":1.05785,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61765,0.14613,0.23413]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63866,0.16716,-0.00325],"force_p95":0.30838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73004,"mean_force":0.13454,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61553,0.14689,0.2346]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47381,-0.01949,-0.00146],"force_p95":0.62179,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6349,"mean_force":0.20487,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46297,-0.01952,0.02881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2631.0,"contact_point_centroid":[0.52598,0.01697,0.22544],"force_p95":0.18533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3026,"mean_force":0.11261,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52025,0.03554,0.22551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5105.0,"contact_point_centroid":[0.46819,-0.0005,0.10562],"force_p95":0.11288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29054,"mean_force":0.0717,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46572,-0.01947,0.10322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5486.0,"contact_point_centroid":[0.4681,-0.03837,0.10328],"force_p95":0.11116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28559,"mean_force":0.06779,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46561,-0.01947,0.10149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3282.0,"contact_point_centroid":[0.52878,0.05629,0.22602],"force_p95":0.15665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27453,"mean_force":0.09353,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52256,0.03817,0.22621]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1895,"mean_force":0.127,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46527,-0.01958,0.02879]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.47616,-0.02015,-0.00184],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48914,-0.00769,0.24814]},{"body_a":"world","body_b":"grasp_target","contact_count":1992.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47376,-0.0179,0.11327]},{"body_a":"world","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.63872,0.1672,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.61955,0.15085,0.281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5007.0,"contact_point_centroid":[0.46391,-0.00033,0.0302],"force_p95":0.06702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09385,"mean_force":0.04328,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.01955,0.02769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.46406,-0.0388,0.02965],"force_p95":0.06671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08291,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46416,-0.01955,0.02769]},{"body_a":"left_finger","body_b":"right_finger","contact_count":58.0,"contact_point_centroid":[0.61703,0.14735,0.23179],"force_p95":0.01604,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01849,"mean_force":0.0122,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61692,0.14734,0.2291]}],"total_contact_groups":14},"final_pose_error":0.02978,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63872,0.1672,0.01602],"final_tcp_position":[0.62589,0.15561,0.31098],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47814,-0.01616,0.19338],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16742,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47199,-0.01972,0.03546],"tcp_start":[0.47814,-0.01616,0.19338],"tcp_to_object_dist_end":0.01033,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01958,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46412,-0.01955,0.02766],"tcp_start":[0.47199,-0.01972,0.03546],"tcp_to_object_dist_end":0.01205,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.49393,-0.01952,0.19671],"object_pos_start":[0.47603,-0.01958,0.0258],"object_to_goal_dist_end":0.22558,"object_to_goal_dist_start":0.28822,"object_z_max":0.19624,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47196,-0.01948,0.20395],"tcp_start":[0.46412,-0.01955,0.02766],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.62224,0.14605,0.13577],"object_pos_start":[0.49393,-0.01952,0.19671],"object_to_goal_dist_end":0.05656,"object_to_goal_dist_start":0.22558,"object_z_max":0.21785,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.61111,0.13762,0.23632],"tcp_start":[0.47196,-0.01948,0.20395],"tcp_to_object_dist_end":0.10151,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.63966,0.16771,-0.00254],"object_pos_start":[0.62224,0.14605,0.13577],"object_to_goal_dist_end":0.19292,"object_to_goal_dist_start":0.05656,"object_z_max":0.13577,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.61888,0.1475,0.23425],"tcp_start":[0.61111,0.13762,0.23632],"tcp_to_object_dist_end":0.23856,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63872,0.1672,0.01602],"object_pos_start":[0.63966,0.16771,-0.00254],"object_to_goal_dist_end":0.17433,"object_to_goal_dist_start":0.19292,"object_z_max":0.01671,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.61432,0.14647,0.25403],"tcp_start":[0.61888,0.1475,0.23425],"tcp_to_object_dist_end":0.24015,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":138.0,"n_steps_budget":600.0,"object_pos_end":[0.63872,0.1672,0.01602],"object_pos_start":[0.63872,0.1672,0.01602],"object_to_goal_dist_end":0.17433,"object_to_goal_dist_start":0.17433,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62589,0.15561,0.31098],"tcp_start":[0.61432,0.14647,0.25403],"tcp_to_object_dist_end":0.29546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```