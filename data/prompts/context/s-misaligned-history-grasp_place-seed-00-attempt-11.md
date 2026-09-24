## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.0190 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 16  | -0.0266 | 0.95 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1723 | 0.78 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12  | -0.3721 | 0.31 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17  | -0.0249 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.954, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.025) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.15
- id: lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.15
- id: place
  weight: 0.2
- id: place_fine
  offset:
  - 0.01
  - 0.0
  - 0.02
  weight: 0.3
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
    - 0.1
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
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_grasp
- id: descend_to_grasp
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
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp
- id: grasp_action
  type: grasp
  control: impedance_control
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
    grasp_max_width:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: guards.check_grasp.threshold
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.04
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    lift_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: lift
- id: transport_to_goal
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place
- id: fine_placement
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.01
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.x
        mode: replace
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_fine

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_action** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_max_width: status=consumed; consumers=guards.check_grasp.threshold (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.04
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **fine_placement** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.01, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.025
- **task_score** (E): 0.953
- **fitness_score**: 0.945  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.970

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.67 | 1.00 | 0.1258 |
| descend_to_grasp | 1.00 | 1.00 | 0.1280 |
| grasp_action | 1.00 | 1.00 | 0.0118 |
| lift_object | 0.33 | 1.00 | 0.1081 |
| transport_to_goal | 1.00 | 1.00 | 0.1857 |
| fine_placement | 1.00 | 1.00 | 0.0395 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.004, 0.178) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 8.607 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.004, 0.178)→(0.493, 0.001, 0.050) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp_action | grasp | 1.00 / step_budget | (0.493, 0.001, 0.050)→(0.485, 0.001, 0.042) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.667 | 0.153 | 0.222 |
| lift_object | lift | 0.33 / step_budget | (0.485, 0.001, 0.042)→(0.484, 0.001, 0.150) | (0.497, 0.001, 0.026)→(0.498, 0.001, 0.133) | 0.266→0.221 | 1.00 / 35.000 | 0.096 | 0.497 |
| transport_to_goal | approach | 1.00 / step_budget | (0.484, 0.001, 0.150)→(0.567, 0.155, 0.174) | (0.498, 0.001, 0.133)→(0.579, 0.155, 0.151) | 0.221→0.049 | 1.00 / 27.667 | 0.108 | 0.219 |
| fine_placement | approach | 1.00 / step_budget | (0.567, 0.155, 0.174)→(0.577, 0.182, 0.198) | (0.579, 0.155, 0.151)→(0.583, 0.182, 0.170) | 0.049→0.017 | 1.00 / 23.333 | 0.108 | 0.366 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.394
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.512
- phase_breakdown.lift_score: 0.285
- phase_breakdown.place_score: 0.451
- phase_breakdown.pre_grasp_score: 0.441
- phase_breakdown.place_fine_score: 0.620
- phase_breakdown.grasp_score: 0.699
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.005
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89041,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13541,"approach_object.approach_speed":0.10772,"approach_object.approach_tolerance":0.06946,"descend_to_grasp.descend_speed":0.10953,"descend_to_grasp.descend_tolerance":0.01127,"descend_to_grasp.grasp_offset_z":0.01757,"fine_placement.place_offset_x":-0.00639,"fine_placement.place_offset_y":-0.00433,"fine_placement.place_offset_z":0.02315,"fine_placement.place_speed":0.09532,"fine_placement.place_tolerance":0.0123,"grasp_action.grasp_max_width":0.03821,"lift_object.lift_height":0.14857,"lift_object.lift_speed":0.07198,"lift_object.lift_tolerance":0.06113,"transport_to_goal.transport_speed":0.24672,"transport_to_goal.transport_tolerance":0.04162},"optimized_scores":{"best_composite_score":-0.00514,"best_fitness_score":0.96486,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.51136,-0.022,-0.00158],"force_p95":0.40502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45417,"mean_force":0.23365,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49948,-0.02171,0.04539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2085.0,"contact_point_centroid":[0.49804,-0.04084,0.08365],"force_p95":0.13991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29434,"mean_force":0.06437,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49842,-0.02167,0.08117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1789.0,"contact_point_centroid":[0.49858,-0.00241,0.08387],"force_p95":0.14168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28866,"mean_force":0.07039,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49846,-0.02167,0.0811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4560.0,"contact_point_centroid":[0.54758,0.15199,0.2178],"force_p95":0.10358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23287,"mean_force":0.08013,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54243,0.13335,0.21705]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51373,-0.02291,-0.00211],"force_p95":0.15214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2127,"mean_force":0.13082,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.5019,-0.02177,0.04559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3361.0,"contact_point_centroid":[0.51936,0.01779,0.16258],"force_p95":0.11107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20067,"mean_force":0.06389,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51742,0.03684,0.16001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4468.0,"contact_point_centroid":[0.54765,0.11491,0.21816],"force_p95":0.10638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18628,"mean_force":0.08012,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54247,0.13353,0.21736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.52085,0.05917,0.16397],"force_p95":0.10725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16195,"mean_force":0.06228,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51835,0.04016,0.16142]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.5137,-0.02302,-0.0014],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12481,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50432,-0.00426,0.27311]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12566,"mean_force":0.12264,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50749,-0.0165,0.13717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4908.0,"contact_point_centroid":[0.5013,-0.00256,0.04715],"force_p95":0.06956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10937,"mean_force":0.04404,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50075,-0.02174,0.04431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.50127,-0.04102,0.04615],"force_p95":0.07207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07421,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50075,-0.02174,0.04432]}],"total_contact_groups":12},"final_pose_error":0.01227,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55323,0.1441,0.20632],"final_tcp_position":[0.5441,0.14389,0.23393],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.45417,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02586],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26573,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12598,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":216.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50879,-0.01062,0.2333],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20787,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02586],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26573,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.12566,"subtask_id":"grasp","tcp_end":[0.50888,-0.0219,0.05341],"tcp_start":[0.50879,-0.01062,0.2333],"tcp_to_object_dist_end":0.02783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51364,-0.02217,0.0256],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26537,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14807,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11680.0,"raw_peak_contact_force":0.2127,"tcp_end":[0.50072,-0.02174,0.04428],"tcp_start":[0.50888,-0.0219,0.05341],"tcp_to_object_dist_end":0.02272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.51088,-0.02183,0.11243],"object_pos_start":[0.51364,-0.02217,0.0256],"object_to_goal_dist_end":0.20968,"object_to_goal_dist_start":0.26537,"object_z_max":0.11131,"peak_contact_force":0.08603,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3942.0,"raw_peak_contact_force":0.45417,"subtask_id":"lift","tcp_end":[0.4996,-0.02167,0.13177],"tcp_start":[0.50072,-0.02174,0.04428],"tcp_to_object_dist_end":0.02239,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.55911,0.11938,0.17646],"object_pos_start":[0.51088,-0.02183,0.11243],"object_to_goal_dist_end":0.05604,"object_to_goal_dist_start":0.20968,"object_z_max":0.17616,"peak_contact_force":0.11524,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6681.0,"raw_peak_contact_force":0.20067,"subtask_id":"place","tcp_end":[0.54277,0.11939,0.19938],"tcp_start":[0.4996,-0.02167,0.13177],"tcp_to_object_dist_end":0.02815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.55323,0.1441,0.20632],"object_pos_start":[0.55911,0.11938,0.17646],"object_to_goal_dist_end":0.01742,"object_to_goal_dist_start":0.05604,"object_z_max":0.20626,"peak_contact_force":0.09301,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9028.0,"raw_peak_contact_force":0.23287,"subtask_id":"place_fine","tcp_end":[0.5441,0.14389,0.23393],"tcp_start":[0.54277,0.11939,0.19938],"tcp_to_object_dist_end":0.02908,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2418,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11896,"approach_object.approach_speed":0.04277,"approach_object.approach_tolerance":0.02324,"descend_to_grasp.descend_speed":0.04884,"descend_to_grasp.descend_tolerance":0.01165,"descend_to_grasp.grasp_offset_z":0.01031,"fine_placement.place_offset_x":-0.00753,"fine_placement.place_offset_y":0.00259,"fine_placement.place_offset_z":0.02192,"fine_placement.place_speed":0.13679,"fine_placement.place_tolerance":0.01266,"grasp_action.grasp_max_width":0.04419,"lift_object.lift_height":0.17197,"lift_object.lift_speed":0.12843,"lift_object.lift_tolerance":0.04092,"transport_to_goal.transport_speed":0.0699,"transport_to_goal.transport_tolerance":0.04045},"optimized_scores":{"best_composite_score":0.00191,"best_fitness_score":0.97191,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.49837,0.04308,-0.00164],"force_p95":0.53877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55036,"mean_force":0.22483,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48666,0.04283,0.03897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3823.0,"contact_point_centroid":[0.55549,0.2453,0.15071],"force_p95":0.1053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41862,"mean_force":0.08235,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.5494,0.22683,0.14982]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3082.0,"contact_point_centroid":[0.487,0.02352,0.09692],"force_p95":0.11429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39437,"mean_force":0.07036,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48553,0.04266,0.0941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3457.0,"contact_point_centroid":[0.48688,0.06171,0.09623],"force_p95":0.11255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33997,"mean_force":0.06533,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48555,0.04266,0.09416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3294.0,"contact_point_centroid":[0.55546,0.20869,0.15198],"force_p95":0.11665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33951,"mean_force":0.09059,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54948,0.22729,0.15007]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04474,-0.00218],"force_p95":0.17354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2426,"mean_force":0.13581,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48944,0.04308,0.03907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2682.0,"contact_point_centroid":[0.52024,0.101,0.15828],"force_p95":0.11988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19763,"mean_force":0.08992,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51514,0.11963,0.15664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3651.0,"contact_point_centroid":[0.48965,0.02373,0.04101],"force_p95":0.09035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15869,"mean_force":0.05739,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4883,0.04298,0.03785]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49845,0.01736,0.23732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2809.0,"contact_point_centroid":[0.52248,0.14361,0.15751],"force_p95":0.11152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13148,"mean_force":0.08405,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51718,0.12508,0.15584]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49583,0.04014,0.1076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5374.0,"contact_point_centroid":[0.4883,0.06207,0.04034],"force_p95":0.07361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0794,"mean_force":0.04184,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48831,0.04298,0.03785]}],"total_contact_groups":12},"final_pose_error":0.01262,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56275,0.24178,0.13518],"final_tcp_position":[0.55224,0.24179,0.15842],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":25.57362,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":25.57362,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.49799,0.03684,0.17003],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp","tcp_end":[0.49633,0.04369,0.04653],"tcp_start":[0.49799,0.03684,0.17003],"tcp_to_object_dist_end":0.02112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04321,0.02541],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24371,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16369,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10825.0,"raw_peak_contact_force":0.2426,"tcp_end":[0.48827,0.04298,0.03781],"tcp_start":[0.49633,0.04369,0.04653],"tcp_to_object_dist_end":0.01788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":184.0,"n_steps_budget":840.0,"object_pos_end":[0.50446,0.04299,0.155],"object_pos_start":[0.50115,0.04321,0.02541],"object_to_goal_dist_end":0.21075,"object_to_goal_dist_start":0.24371,"object_z_max":0.1543,"peak_contact_force":0.11243,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6602.0,"raw_peak_contact_force":0.55036,"subtask_id":"lift","tcp_end":[0.48624,0.04267,0.16912],"tcp_start":[0.48827,0.04298,0.03781],"tcp_to_object_dist_end":0.02305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.56403,0.20804,0.12486],"object_pos_start":[0.50446,0.04299,0.155],"object_to_goal_dist_end":0.04286,"object_to_goal_dist_start":0.21075,"object_z_max":0.15708,"peak_contact_force":0.11352,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5491.0,"raw_peak_contact_force":0.19763,"subtask_id":"place","tcp_end":[0.54872,0.20839,0.14403],"tcp_start":[0.48624,0.04267,0.16912],"tcp_to_object_dist_end":0.02454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.56275,0.24178,0.13518],"object_pos_start":[0.56403,0.20804,0.12486],"object_to_goal_dist_end":0.01211,"object_to_goal_dist_start":0.04286,"object_z_max":0.13515,"peak_contact_force":0.11107,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7117.0,"raw_peak_contact_force":0.41862,"subtask_id":"place_fine","tcp_end":[0.55224,0.24179,0.15842],"tcp_start":[0.54872,0.20839,0.14403],"tcp_to_object_dist_end":0.0255,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94521,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.05679,"approach_object.approach_speed":0.0987,"approach_object.approach_tolerance":0.04407,"descend_to_grasp.descend_speed":0.09875,"descend_to_grasp.descend_tolerance":0.01221,"descend_to_grasp.grasp_offset_z":0.01304,"fine_placement.place_offset_x":0.00718,"fine_placement.place_offset_y":0.00264,"fine_placement.place_offset_z":0.02108,"fine_placement.place_speed":0.09639,"fine_placement.place_tolerance":0.01061,"grasp_action.grasp_max_width":0.05652,"lift_object.lift_height":0.17221,"lift_object.lift_speed":0.10653,"lift_object.lift_tolerance":0.06739,"transport_to_goal.transport_speed":0.19617,"transport_to_goal.transport_tolerance":0.03275},"optimized_scores":{"best_composite_score":-0.07155,"best_fitness_score":0.89845,"best_task_score":0.85967},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":61.0,"contact_point_centroid":[0.47319,-0.01952,-0.00158],"force_p95":0.46152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48765,"mean_force":0.25609,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46357,-0.01903,0.04362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11647.0,"contact_point_centroid":[0.62177,0.16854,0.18486],"force_p95":0.09806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44696,"mean_force":0.07191,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.62212,0.15006,0.18769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10029.0,"contact_point_centroid":[0.62023,0.13075,0.18491],"force_p95":0.11271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3394,"mean_force":0.08215,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.62141,0.14947,0.18695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.46234,-0.03823,0.08879],"force_p95":0.14734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29908,"mean_force":0.0664,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46231,-0.01897,0.08693]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.46221,0.00027,0.087],"force_p95":0.1509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.282,"mean_force":0.06835,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46223,-0.01897,0.08484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6398.0,"contact_point_centroid":[0.53855,0.04095,0.16501],"force_p95":0.09879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25995,"mean_force":0.05811,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53814,0.06006,0.16334]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02007,-0.00209],"force_p95":0.14878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2093,"mean_force":0.12969,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46623,-0.01909,0.04365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6101.0,"contact_point_centroid":[0.53771,0.07785,0.16461],"force_p95":0.09453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18685,"mean_force":0.05929,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53693,0.05877,0.16304]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.47616,-0.02015,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49126,-0.00728,0.21911]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47554,-0.01735,0.08849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5299.0,"contact_point_centroid":[0.46448,0.00016,0.04382],"force_p95":0.0668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11294,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46513,-0.01906,0.04255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.46477,-0.03835,0.04397],"force_p95":0.06786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07536,"mean_force":0.04224,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46514,-0.01906,0.04255]}],"total_contact_groups":12},"final_pose_error":0.01165,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63316,0.15952,0.1674],"final_tcp_position":[0.6339,0.15987,0.20061],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.48765,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":696.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48083,-0.01547,0.12999],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp","tcp_end":[0.47288,-0.01922,0.05047],"tcp_start":[0.48083,-0.01547,0.12999],"tcp_to_object_dist_end":0.02469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01938,0.02566],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28815,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14599,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12376.0,"raw_peak_contact_force":0.2093,"tcp_end":[0.46511,-0.01906,0.04252],"tcp_start":[0.47288,-0.01922,0.05047],"tcp_to_object_dist_end":0.02012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.47954,-0.01912,0.1309],"object_pos_start":[0.47609,-0.01938,0.02566],"object_to_goal_dist_end":0.24157,"object_to_goal_dist_start":0.28815,"object_z_max":0.12965,"peak_contact_force":0.08969,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4049.0,"raw_peak_contact_force":0.48765,"subtask_id":"lift","tcp_end":[0.46479,-0.01898,0.14809],"tcp_start":[0.46511,-0.01906,0.04252],"tcp_to_object_dist_end":0.02266,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.61388,0.13791,0.15127],"object_pos_start":[0.47954,-0.01912,0.1309],"object_to_goal_dist_end":0.04756,"object_to_goal_dist_start":0.24157,"object_z_max":0.15122,"peak_contact_force":0.09519,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12499.0,"raw_peak_contact_force":0.25995,"subtask_id":"place","tcp_end":[0.61012,0.13792,0.1778],"tcp_start":[0.46479,-0.01898,0.14809],"tcp_to_object_dist_end":0.0268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.63316,0.15952,0.1674],"object_pos_start":[0.61388,0.13791,0.15127],"object_to_goal_dist_end":0.02268,"object_to_goal_dist_start":0.04756,"object_z_max":0.1674,"peak_contact_force":0.12037,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21676.0,"raw_peak_contact_force":0.44696,"subtask_id":"place_fine","tcp_end":[0.6339,0.15987,0.20061],"tcp_start":[0.61012,0.13792,0.1778],"tcp_to_object_dist_end":0.03322,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```