## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0883 | 0.33 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0365 | 0.33 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0443 | 0.32 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0357 | 0.27 | ✅ accepted |
| 1 | approach → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1914 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.088) — your mutation base

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
    - 0.05
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
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
    place_height_adjust:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
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
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_height_adjust: status=consumed; consumers=target.offset.z (replace)
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

- **Composite score**: 0.088
- **task_score** (E): 0.327
- **fitness_score**: 0.643  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1312 |
| descend_grasp | 1.00 | 0.1380 |
| grasp_object | 1.00 | 0.0118 |
| lift_object | 1.00 | 0.1351 |
| transport_to_goal | 1.00 | 0.2218 |
| descend_to_contact | 1.00 | 0.0086 |
| release_object | 1.00 | 0.0215 |
| retract_from_place | 1.00 | 0.0436 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.001, 0.173) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.495, 0.001, 0.173)→(0.492, 0.001, 0.035) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.035)→(0.484, 0.000, 0.027) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.027)→(0.492, 0.000, 0.161) | (0.497, 0.000, 0.026)→(0.513, 0.001, 0.157) | 0.266→0.211 |
| transport_to_goal | approach | 1.00 / step_budget | (0.492, 0.000, 0.161)→(0.576, 0.174, 0.253) | (0.513, 0.001, 0.157)→(0.584, 0.180, 0.178) | 0.211→0.065 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.576, 0.174, 0.253)→(0.575, 0.174, 0.244) | (0.584, 0.180, 0.178)→(0.583, 0.180, 0.168) | 0.065→0.058 |
| release_object | release | 1.00 / step_budget | (0.575, 0.174, 0.244)→(0.571, 0.172, 0.265) | (0.583, 0.180, 0.168)→(0.575, 0.183, 0.012) | 0.058→0.175 |
| retract_from_place | retract | 1.00 / step_budget | (0.571, 0.172, 0.265)→(0.578, 0.180, 0.307) | (0.575, 0.183, 0.012)→(0.575, 0.185, 0.016) | 0.175→0.171 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.416
- phase_score: 0.160
- phase_breakdown.lift_object_score: 0.151
- phase_breakdown.place_goal_score: 0.155
- phase_breakdown.reach_grasp_score: 0.186
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.416
- **Median Q (composite search score)**: 0.082
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.735,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12847,"approach_object.generator.speed":0.06376,"descend_grasp.grasp_z":0.0004,"descend_to_contact.contact_force_threshold":3.04635,"descend_to_contact.descend_speed":0.03492,"grasp_object.grasp_offset":-0.01907,"lift_object.lift_height":0.15475,"release_object.release_time":0.23297,"retract_from_place.retract_speed":0.16718,"transport_to_goal.transport_speed":0.07156},"optimized_scores":{"best_composite_score":0.0501,"best_fitness_score":0.6051,"best_task_score":0.25263},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":348.0,"contact_point_centroid":[0.55042,0.13982,-0.00595],"force_p95":1.16196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23836,"mean_force":0.28391,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54558,0.14026,0.29594]},{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51147,-0.02213,-0.00149],"force_p95":0.61224,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6492,"mean_force":0.18809,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49914,-0.02232,0.02692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3668.0,"contact_point_centroid":[0.50458,-0.00325,0.08237],"force_p95":0.11295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3101,"mean_force":0.07397,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50193,-0.02222,0.07985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4050.0,"contact_point_centroid":[0.50455,-0.04106,0.08006],"force_p95":0.10948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29357,"mean_force":0.06867,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50182,-0.02222,0.07836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.55245,0.12638,0.28001],"force_p95":0.25228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27688,"mean_force":0.07889,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54872,0.14141,0.28548]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.55663,0.15593,0.27884],"force_p95":0.26211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26562,"mean_force":0.23721,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5491,0.14113,0.28621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.55661,0.1587,0.2789],"force_p95":0.24086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24532,"mean_force":0.16813,"phase_index":5.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5491,0.14094,0.28618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7388.0,"contact_point_centroid":[0.53114,0.07616,0.21412],"force_p95":0.1427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23534,"mean_force":0.09324,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52655,0.05778,0.21502]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.0228,-0.00206],"force_p95":0.14063,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19346,"mean_force":0.12762,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50148,-0.02238,0.02711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7322.0,"contact_point_centroid":[0.53094,0.03782,0.21298],"force_p95":0.13469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18836,"mean_force":0.09396,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52619,0.05624,0.21378]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7.0,"contact_point_centroid":[0.55252,0.12383,0.28096],"force_p95":0.15224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15688,"mean_force":0.12583,"phase_index":5.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5491,0.14094,0.28618]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.5137,-0.02302,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50334,-0.00902,0.24017]},{"body_a":"world","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.55021,0.13948,-0.00193],"force_p95":0.12676,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.127,"mean_force":0.12349,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.54726,0.14333,0.32403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.50092,-0.00315,0.02859],"force_p95":0.0778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12417,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50029,-0.02235,0.02583]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50706,-0.02072,0.10491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.50094,-0.04145,0.02766],"force_p95":0.06973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08953,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50029,-0.02235,0.02583]}],"total_contact_groups":16},"final_pose_error":0.02977,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55021,0.13949,0.01601],"final_tcp_position":[0.54989,0.14708,0.34287],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.50826,-0.01898,0.17707],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1512,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.5086,-0.02254,0.03484],"tcp_start":[0.50826,-0.01898,0.17707],"tcp_to_object_dist_end":0.0102,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51356,-0.02225,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26529,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50026,-0.02235,0.0258],"tcp_start":[0.5086,-0.02254,0.03484],"tcp_to_object_dist_end":0.0133,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":255.0,"n_steps_budget":990.0,"object_pos_end":[0.52913,-0.0221,0.14722],"object_pos_start":[0.51356,-0.02225,0.02579],"object_to_goal_dist_end":0.1908,"object_to_goal_dist_start":0.26529,"object_z_max":0.14676,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50816,-0.02215,0.1511],"tcp_start":[0.50026,-0.02235,0.0258],"tcp_to_object_dist_end":0.02133,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":699.0,"n_steps_budget":1000.0,"object_pos_end":[0.55768,0.13984,0.26119],"object_pos_start":[0.52913,-0.0221,0.14722],"object_to_goal_dist_end":0.04109,"object_to_goal_dist_start":0.1908,"object_z_max":0.26157,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.5491,0.14094,0.28618],"tcp_start":[0.50816,-0.02215,0.1511],"tcp_to_object_dist_end":0.02644,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5577,0.13985,0.26099],"object_pos_start":[0.55768,0.13984,0.26119],"object_to_goal_dist_end":0.04091,"object_to_goal_dist_start":0.04109,"object_z_max":0.26119,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54911,0.14109,0.28621],"tcp_start":[0.5491,0.14094,0.28618],"tcp_to_object_dist_end":0.02667,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55015,0.13957,0.0167],"object_pos_start":[0.5577,0.13985,0.26099],"object_to_goal_dist_end":0.20568,"object_to_goal_dist_start":0.04091,"object_z_max":0.26099,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_goal","tcp_end":[0.54555,0.14025,0.30864],"tcp_start":[0.54911,0.14109,0.28621],"tcp_to_object_dist_end":0.29198,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":83.0,"n_steps_budget":600.0,"object_pos_end":[0.55021,0.13949,0.01601],"object_pos_start":[0.55015,0.13957,0.0167],"object_to_goal_dist_end":0.20637,"object_to_goal_dist_start":0.20568,"object_z_max":0.0167,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.54989,0.14708,0.34287],"tcp_start":[0.54555,0.14025,0.30864],"tcp_to_object_dist_end":0.32695,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71429,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10766,"approach_object.generator.speed":0.14679,"descend_grasp.grasp_z":0.00087,"descend_to_contact.contact_force_threshold":3.40138,"descend_to_contact.descend_speed":0.0185,"grasp_object.grasp_offset":-0.01458,"lift_object.lift_height":0.18946,"release_object.release_time":0.47903,"retract_from_place.retract_speed":0.13238,"transport_to_goal.transport_speed":0.06361},"optimized_scores":{"best_composite_score":0.13249,"best_fitness_score":0.68749,"best_task_score":0.41638},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.55538,0.25391,-0.00342],"force_p95":0.69427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03533,"mean_force":0.18664,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55325,0.22867,0.21785]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49882,0.04267,-0.00162],"force_p95":0.62814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64889,"mean_force":0.19777,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48703,0.04304,0.02806]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4943.0,"contact_point_centroid":[0.49246,0.06173,0.09455],"force_p95":0.11324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31558,"mean_force":0.06993,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48981,0.04283,0.09262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4597.0,"contact_point_centroid":[0.49287,0.0239,0.09859],"force_p95":0.11411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30803,"mean_force":0.07344,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49005,0.04283,0.09616]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5381.0,"contact_point_centroid":[0.5259,0.14225,0.19539],"force_p95":0.14596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26222,"mean_force":0.09753,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52126,0.12398,0.19674]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04464,-0.00217],"force_p95":0.17383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26063,"mean_force":0.13615,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48939,0.04328,0.02808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5400.0,"contact_point_centroid":[0.52369,0.09803,0.19445],"force_p95":0.15495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25533,"mean_force":0.09385,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51875,0.11636,0.1954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3759.0,"contact_point_centroid":[0.4893,0.02397,0.02989],"force_p95":0.08627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15313,"mean_force":0.05555,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04317,0.02686]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.50118,0.04505,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49842,0.01838,0.22914]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49573,0.04093,0.0947]},{"body_a":"world","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.55496,0.25414,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.55462,0.23243,0.2515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5079.0,"contact_point_centroid":[0.48866,0.06232,0.02893],"force_p95":0.07537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08754,"mean_force":0.04447,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04317,0.02686]}],"total_contact_groups":12},"final_pose_error":0.02965,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55496,0.25414,0.01602],"final_tcp_position":[0.55824,0.23784,0.26864],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49786,0.03819,0.15582],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13003,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.49634,0.0439,0.03547],"tcp_start":[0.49786,0.03819,0.15582],"tcp_to_object_dist_end":0.01068,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04315,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24377,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.4882,0.04316,0.02683],"tcp_start":[0.49634,0.0439,0.03547],"tcp_to_object_dist_end":0.01296,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.51824,0.04316,0.17903],"object_pos_start":[0.50109,0.04315,0.02543],"object_to_goal_dist_end":0.20943,"object_to_goal_dist_start":0.24377,"object_z_max":0.17858,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.4965,0.04284,0.18563],"tcp_start":[0.4882,0.04316,0.02683],"tcp_to_object_dist_end":0.02272,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.56301,0.24942,0.03828],"object_pos_start":[0.51824,0.04316,0.17903],"object_to_goal_dist_end":0.1086,"object_to_goal_dist_start":0.20943,"object_z_max":0.18776,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55686,0.2297,0.21636],"tcp_start":[0.4965,0.04284,0.18563],"tcp_to_object_dist_end":0.17927,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.56309,0.24992,0.03488],"object_pos_start":[0.56301,0.24942,0.03828],"object_to_goal_dist_end":0.11202,"object_to_goal_dist_start":0.1086,"object_z_max":0.03828,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55682,0.22989,0.21633],"tcp_start":[0.55686,0.2297,0.21636],"tcp_to_object_dist_end":0.18266,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55496,0.25415,0.01602],"object_pos_start":[0.56309,0.24992,0.03488],"object_to_goal_dist_end":0.13142,"object_to_goal_dist_start":0.11202,"object_z_max":0.03488,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_goal","tcp_end":[0.55213,0.22807,0.2377],"tcp_start":[0.55682,0.22989,0.21633],"tcp_to_object_dist_end":0.22323,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":82.0,"n_steps_budget":600.0,"object_pos_end":[0.55496,0.25414,0.01602],"object_pos_start":[0.55496,0.25415,0.01602],"object_to_goal_dist_end":0.13143,"object_to_goal_dist_start":0.13142,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55824,0.23784,0.26864],"tcp_start":[0.55213,0.22807,0.2377],"tcp_to_object_dist_end":0.25317,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39113,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13655,"approach_object.generator.speed":0.1029,"descend_grasp.grasp_z":0.00012,"descend_to_contact.contact_force_threshold":2.71493,"descend_to_contact.descend_speed":0.04425,"grasp_object.grasp_offset":-0.01672,"lift_object.lift_height":0.15089,"release_object.release_time":0.33587,"retract_from_place.retract_speed":0.19434,"transport_to_goal.transport_speed":0.04255},"optimized_scores":{"best_composite_score":0.08219,"best_fitness_score":0.63719,"best_task_score":0.31279},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.62068,0.16026,-0.01042],"force_p95":1.57875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95728,"mean_force":0.6078,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61495,0.14891,0.24433]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47385,-0.01951,-0.00147],"force_p95":0.61266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63389,"mean_force":0.20829,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46305,-0.01953,0.0283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":607.0,"contact_point_centroid":[0.62181,0.13166,0.22115],"force_p95":0.12983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31291,"mean_force":0.09152,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61799,0.14988,0.22569]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1010.0,"contact_point_centroid":[0.62313,0.16843,0.23894],"force_p95":0.14619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28898,"mean_force":0.09651,"phase_index":5.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.62017,0.15027,0.24345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3858.0,"contact_point_centroid":[0.46714,-0.00041,0.08197],"force_p95":0.10799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28611,"mean_force":0.06604,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46554,-0.01949,0.07937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":909.0,"contact_point_centroid":[0.62393,0.13206,0.23925],"force_p95":0.14319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28426,"mean_force":0.10263,"phase_index":5.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.62017,0.15027,0.24345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4221.0,"contact_point_centroid":[0.46721,-0.03848,0.08075],"force_p95":0.10253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2822,"mean_force":0.06162,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4655,-0.01949,0.07891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":622.0,"contact_point_centroid":[0.62076,0.16825,0.22073],"force_p95":0.1684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27093,"mean_force":0.09622,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61786,0.14984,0.22542]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.62076,0.16082,-0.00234],"force_p95":0.13112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20445,"mean_force":0.11151,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.61997,0.15243,0.27863]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18927,"mean_force":0.12697,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46526,-0.01958,0.02828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11171.0,"contact_point_centroid":[0.54893,0.04683,0.2],"force_p95":0.11628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17515,"mean_force":0.07974,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54463,0.06541,0.1998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11166.0,"contact_point_centroid":[0.5508,0.08612,0.20126],"force_p95":0.11581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17482,"mean_force":0.07929,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54657,0.06757,0.20121]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.47616,-0.02015,-0.00185],"force_p95":0.13717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.489,-0.00778,0.24461]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47362,-0.018,0.10951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.46382,-0.00034,0.02972],"force_p95":0.06597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09491,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46414,-0.01956,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.46405,-0.03881,0.02914],"force_p95":0.06668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08295,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46414,-0.01956,0.02718]}],"total_contact_groups":16},"final_pose_error":0.02998,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62075,0.16073,0.01602],"final_tcp_position":[0.62617,0.15629,0.31064],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47789,-0.01637,0.18603],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16006,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47196,-0.01973,0.03494],"tcp_start":[0.47789,-0.01637,0.18603],"tcp_to_object_dist_end":0.00987,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01961,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28824,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46411,-0.01956,0.02715],"tcp_start":[0.47196,-0.01973,0.03494],"tcp_to_object_dist_end":0.01199,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":237.0,"n_steps_budget":960.0,"object_pos_end":[0.49036,-0.01935,0.14366],"object_pos_start":[0.47603,-0.01961,0.02581],"object_to_goal_dist_end":0.23222,"object_to_goal_dist_start":0.28824,"object_z_max":0.14319,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47103,-0.01949,0.14757],"tcp_start":[0.46411,-0.01956,0.02715],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.63079,0.14995,0.23497],"object_pos_start":[0.49036,-0.01935,0.14366],"object_to_goal_dist_end":0.0459,"object_to_goal_dist_start":0.23222,"object_z_max":0.23489,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.6213,0.15004,0.25563],"tcp_start":[0.47103,-0.01949,0.14757],"tcp_to_object_dist_end":0.02273,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":101.0,"n_steps_budget":1000.0,"object_pos_end":[0.6279,0.15026,0.20774],"object_pos_start":[0.63079,0.14995,0.23497],"object_to_goal_dist_end":0.02016,"object_to_goal_dist_start":0.0459,"object_z_max":0.23498,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.61969,0.15033,0.23012],"tcp_start":[0.6213,0.15004,0.25563],"tcp_to_object_dist_end":0.02384,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61998,0.15633,0.0036],"object_pos_start":[0.6279,0.15026,0.20774],"object_to_goal_dist_end":0.18678,"object_to_goal_dist_start":0.02016,"object_z_max":0.20774,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_goal","tcp_end":[0.61493,0.14891,0.24946],"tcp_start":[0.61969,0.15033,0.23012],"tcp_to_object_dist_end":0.24602,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.62075,0.16073,0.01602],"object_pos_start":[0.61998,0.15633,0.0036],"object_to_goal_dist_end":0.17433,"object_to_goal_dist_start":0.18678,"object_z_max":0.01693,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62617,0.15629,0.31064],"tcp_start":[0.61493,0.14891,0.24946],"tcp_to_object_dist_end":0.29471,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```